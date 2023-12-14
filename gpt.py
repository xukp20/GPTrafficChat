"""
    GPT4 interface
"""

import random
import string, json

import requests, os
from requests import Response

# read from ./base_url.txt
with open(os.path.join(os.path.dirname(__file__), "base_url.txt"), "r") as f:
    BASE_URL = f.read()

class CommonException(Exception):
    pass

def generate_uuid(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# old handler
# def handle_reply(response: Response) -> str:
#     if response.status_code == 200:
#         reply = response.json()
#         status = reply['status']
#         info = reply['info']
#         uuid = reply['uuid']
#         if status == 0:
#             return info
#         else:
#             raise CommonException(f"Failed in requesting, uuid: {uuid}, status code: {status}, info: {info}")
#     else:
#         raise CommonException("Connection Error")

def handle_reply(response: Response) -> str:
    try:
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        raise CommonException(f"Error: {e.response.status_code}, {e.response.reason}, {response.text}")
    except Exception as e:
        raise CommonException("Unknown: " + str(e))


def send_request(apikey: str, request: json) -> str:
    url = BASE_URL + "requestazuremessage"
    body = {
        "type": "RequestAzureMessage",
        "apikey": apikey,
        "request": request,
        "uuid": {"id": generate_uuid()}
    }
    response = requests.post(url, json=body)

    return handle_reply(response)

# get api key
try: 
    with open("azure_key.txt", "r") as f:
        apikey = f.read()
except:
    print("Please provide your API key in azure_key.txt")
    exit(1)

# use backoff
from backoff import on_exception, expo, constant
from tqdm import tqdm

def backoff_hdlr(details):
    # show error
    tqdm.write("Exception: {exception}".format(**details))
    tqdm.write("Backing off {wait:0.1f} seconds afters {tries} tries "
            "calling function {target}".format(**details))

EXCEPTION_RETRY = 10
# set the base of exponential backoff to 20 seconds
# handle all openai error
from openai.error import APIError, RateLimitError, APIConnectionError
exception_list = (APIError, RateLimitError, APIConnectionError)
@on_exception(expo, CommonException, max_tries=EXCEPTION_RETRY, base=2, factor=5, on_backoff=backoff_hdlr)
# @on_exception(constant, CommonException, max_tries=EXCEPTION_RETRY, interval=5, on_backoff=backoff_hdlr)
def gpt_call(messages, max_tokens, temperature=0.0, top_p=1, frequency_penalty=0, presence_penalty=0, seed=None, model="gpt-4-1106-preview"):
    request = {
        "frequency_penalty": frequency_penalty,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "presence_penalty": presence_penalty,
        "stream": False,
        "messages": messages,
        "model": model
    }
    if seed is not None:
        request['seed'] = seed

    response = json.loads(send_request(apikey, request))
    # print(response)
    return response['choices'][0]['message']['content']

def single_gpt_call(
    system, prompt, max_tokens, temperature=0.0, top_p=1, frequency_penalty=0, presence_penalty=0, seed=None, model="gpt-4-1106-preview"
):
    messages = [
        {
            "role": "system",
            "content": system
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return gpt_call(messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty, seed, model)


### Tools
TOKEN_LOG_ENABLE = False
try:
    import tiktoken
    TOKEN_LOG_ENABLE = True
    def num_tokens_from_messages(messages, model="gpt-4"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":
            return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
        elif model == "gpt-4" or model == "gpt-4-1106-preview":
            return num_tokens_from_messages(messages, model="gpt-4-0314")
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens


    def single_text_tokens(text, model="gpt-4"):
        """Returns the number of tokens used by a single text."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
        
except ImportError:
    print("Warning: tiktoken not found, token logger disabled.")


def money_calculator(input_tokens, output_tokens, model="gpt-4-1106-preview"):
    """Returns the money spent on a conversation."""
    if model == "gpt-3.5-turbo":
        return input_tokens / 1000 * 0.001 + output_tokens / 1000 * 0.002
    elif model == "gpt-4-1106-preview":
        return input_tokens / 1000 * 0.01 + output_tokens / 1000 * 0.03
    elif model == "gpt-4-32k":
        return input_tokens / 1000 * 0.06 + output_tokens / 1000 * 0.12
    else:
        raise NotImplementedError(f"""money_calculator() is not implemented for model {model}.""")
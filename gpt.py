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

def handle_reply(response: Response) -> str:
    if response.status_code == 200:
        reply = response.json()
        status = reply['status']
        info = reply['info']
        uuid = reply['uuid']
        if status == 0:
            return info
        else:
            raise CommonException(f"Failed in requesting, uuid: {uuid}, status code: {status}, info: {info}")
    else:
        raise CommonException("Connection Error")


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
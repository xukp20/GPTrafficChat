# GPTrafficChat
Chat interface based on streamlit to use GPTraffic backend.

## Requirements
Install streamlit with pip:
```bash
pip install streamlit
```

Install backoff for api retry:
```bash
pip install backoff
```


Put the base url of backend (end with /api/) in this dir, in a file named `base_url.txt`.

Put the key of backend in this dir, in a file named `azure_key.txt`.

## Usage
Run the app with:
```bash
streamlit run chat.py
```

## Note
Maybe not be able to occupy the port on the server, try local instead.

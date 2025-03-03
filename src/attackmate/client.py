import requests

json_rpc_url = "http://192.168.10.65:8000/attackmate"


command_request = {
    "jsonrpc": "2.0",
    "method": "do_command",
    "params": {
        "type": "debug",
        "cmd": "hello world",
        "args": [],
        "timeout": 10
    },
    "id": 1
}

response = requests.post(json_rpc_url, json=command_request)
print(response.json())

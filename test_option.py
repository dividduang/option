import httpx

def get_config(apikey):
    url = 'http://127.0.0.1:8000/api/v1/option/get-config'
    headers = {
        'api-key': apikey
    }

    response = httpx.get(url, headers=headers)

    print(response.json())



def save_config():
    url = 'http://127.0.0.1:8000/api/v1/option/save-config'
    data = {
        "name": "邮箱",
        "config_data": {"to":["djr@qq.com"],"cc":["djren@qq.com"]}
    }

    response = httpx.post(url, json=data)
    print(response.json())
    return response.json()['data']

apikey = save_config()

get_config(apikey)
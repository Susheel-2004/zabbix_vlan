import requests
import json

ZABBIX_URL = ''
ZABBIX_USER = ''
ZABBIX_PASSWORD = ''

auth_params = {
    'username': ZABBIX_USER,
    'password': ZABBIX_PASSWORD
}
auth_data = {
    'jsonrpc': '2.0',
    'method': 'user.login',
    'params': auth_params,
    'id': 1
}
auth_response = requests.post(ZABBIX_URL, headers={'Content-Type': 'application/json-rpc'}, data=json.dumps(auth_data))
# print(auth_response.json())
auth_token = auth_response.json().get('result')

# Function to make API calls
def zabbix_api(method, params):
    headers = {'Content-Type': 'application/json-rpc'}
    data = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'auth': auth_token,
        'id': 1
    }
    response = requests.post(ZABBIX_URL, headers=headers, data=json.dumps(data))
    return response.json()



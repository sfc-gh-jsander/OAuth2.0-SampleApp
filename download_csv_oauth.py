import requests

url = "XXXXXXXXX/api/files/XXXX/XXXX/TEST_NAMED_STAGE/test.csv.gz"

payload={}
headers = {
  'User-Agent': 'reg-tests',
  'X-Snowflake-Authorization-Token-Type': 'OAUTH',
  'Authorization': 'Bearer XXXXXXX'
}

response = requests.request("GET", url, headers=headers, data=payload)

filename = "test.csv.gz"
open(filename, 'wb').write(response.content)

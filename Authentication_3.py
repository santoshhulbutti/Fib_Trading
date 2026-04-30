# When we validate the auth code to generate the access token, a refresh token is also sent in the response.

# The refresh token has a validity of 15 days. A new access token can be generated using the refresh token as long as the refresh token is valid.

import requests
from fyers_apiv3 import fyersModel

# Read the refresh token generated before. This refresh token will be used to authenticate user, without any extra browser steps.
refresh_token = open("fyers_refresh_token.txt",'r').read()
client_id = open("fyers_client_id.txt",'r').read()
url = 'https://api-t1.fyers.in/api/v3/validate-refresh-token'
headers = {
    'Content-Type': 'application/json',
}

"""
You need to generate appIdHash of your fyers api.
SHA-256 of api_id + app_secret. Eg: SHA-256 of app_id:app_secret is c452a072cf51992ddfdc01e40cdeb517ffe4dd931d9d39be25dad69ffef2b58b.
You can use this online tool for reference (https://emn178.github.io/online-tools/sha256.html)

for e.g.,   client_id = "TIA57SU3G1-200"
            secret_key = "nNUf3zJTDFcquIJb"
            Then open given website and enter TIA57SU3G1-200:nNUf3zJTDFcquIJb to generate a AppIdHash value. Use it below.
"""
data = {
"grant_type": "refresh_token",
"appIdHash": "e086b4f750f881bd408e38b38e5cb2131ee6ceb914dd07ab147f19a1483fdb8a",
"refresh_token": refresh_token,
"pin": "4679"
}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
print(response.json())

try:
    access_token = response.json()["access_token"]
    print("token: ",access_token)
except Exception as e:
    print(e, response)
# Successful Response
# {'s': 'ok', 'code': 288, 'message': '', 'access_token': 'eyJsjjfvnskdjnvkee3445vdfvb *************** }

# In this way access token is generated which can be used further to login, we can save this in a file.
#sove client id and access token to file
with open("fyers_access_token.txt", 'w') as file:
    file.write(access_token)

# Once you have generated accessToken now we can call multiple trading related or data related apis
# after that in order to do so we need to first initialize the fyerModel object with all the requried params.
"""
fyerModel object takes following values as arguments
1. accessToken : this is the one which you received from above
2. client_id : this is basically the app_id for the particular app you logged into
"""
fyers = fyersModel. FyersModel(token=access_token, is_async=False, client_id=client_id, log_path="")
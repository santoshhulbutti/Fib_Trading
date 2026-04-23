import webbrowser

#pip install pya3 flask xlwings pandas requests ta pandas_ta pyotp websocket-client logzero fyers_apiv3 urllib3 whl pyyaml websockets Twisted protobuf --upgrade


# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel

# Replace these values with your actual API credentials
client_id = "5O51INNWQV-100"
secret_key = "5XLXFN43SZ"
redirect_uri = "https://www.google.com/"
response_type = "code"
state = "sample_state"
grant_type = "authorization_code"

# Create a session model with the provided credentials
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type = grant_type
)

# Generate the auth code using the session model
generateTokenUrl = session.generate_authcode()

# Print the url received in the response
print(generateTokenUrl)

# This will open the link in a new browser window.
#webbrowser.open(generateTokenUrl, new=1)

# Continue to log in and click on COPY button on webpage to copy Auth Code Generated..

auth_code = input("Enter Auth Code: ")
session.set_token(auth_code)
response = session.generate_token()

# Here is the access token which will be used further for creating Fyers instance of your account.
try:
    access_token = response["access_token"]
    print("token: ",access_token)
except Exception as e:
    print(e,response)

with open("fyers_client_id.txt", 'w') as file:
    file.write(client_id)
with open("fyers_access_token.txt", 'w') as file:
    file.write(access_token)


# Once you have generated accessToken now we can call multiple trading related or data related apis
# after that in order to do so we need to first initialize the fyerModel object with all the requried params.
"""
fyerModel object takes following values as arguments
1. accessToken : this is the one which you received from above
2. client_id : this is basically the app_id for the particular app you logged into
"""
fyers = fyersModel. FyersModel(token=access_token,is_async=False,client_id=client_id,log_path="")
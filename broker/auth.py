# ==========================================
# FYERS AUTHENTICATION
# ==========================================

from fyers_apiv3 import fyersModel
from config.settings import CLIENT_ID, SECRET_KEY, REDIRECT_URI


def get_access_token():
    """
    Manual login flow (recommended initially)
    """

    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )

    # Step 1: Generate login URL
    auth_url = session.generate_authcode()
    print("\n🔐 Login URL:\n", auth_url)

    # Step 2: Paste auth code
    auth_code = input("\nEnter Auth Code: ")

    # Step 3: Generate token
    session.set_token(auth_code)
    response = session.generate_token()

    if "access_token" not in response:
        raise Exception(f"Auth Failed: {response}")

    # Here is the access token which will be used further for creating Fyers instance of your account.
    try:
        access_token = response["access_token"]
        print("token: ", access_token)
        with open("fyers_access_token.txt", 'w') as file:
            file.write(access_token)
        with open("fyers_client_id.txt", 'w') as file:
            file.write(CLIENT_ID)

    except Exception as e:
        print(e, response)


    print("✅ Auth Successful")

    return response["access_token"]
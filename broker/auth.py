# ==========================================
# FYERS AUTHENTICATION
# ==========================================

from fyers_apiv3 import fyersModel
import os
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
    print("\n Login URL:\n", auth_url)

    # Step 2: Paste auth code
    auth_code = input("\nEnter Auth Code: ")

    # Step 3: Generate token
    session.set_token(auth_code)
    response = session.generate_token()

    if "access_token" not in response:
        raise Exception(f"Auth Failed: {response}")

    print("Authentication Successful")
    # os.environ["FYERS_ACCESS_TOKEN"] = response["access_token"]
    return response["access_token"]
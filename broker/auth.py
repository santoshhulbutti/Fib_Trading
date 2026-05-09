# ==========================================
# FYERS AUTHENTICATION
# ==========================================

from fyers_apiv3 import fyersModel
import os
from utils.logger import log, error_log
from config.settings import CLIENT_ID, SECRET_KEY, REDIRECT_URI


def get_access_token():
    """
    Manual login flow (recommended initially)
    """

    log("AUTHENTICATION STARTED...")

    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )

    # Step 1: Generate login URL
    auth_url = session.generate_authcode()
    print("\n LOGIN URL:\n", auth_url)

    # Step 2: Paste auth code
    auth_code = input("\nENTER AUTHENTICATION CODE: ")

    # Step 3: Generate token
    session.set_token(auth_code)
    response = session.generate_token()

    if "access_token" not in response:
        error_log("AUTHENTICATION FAILED")
        raise Exception(f"AUTHENTICATION FAILED...: {response}")


    log("AUTHENTICATION SUCCESSFUL...")
    # os.environ["FYERS_ACCESS_TOKEN"] = response["access_token"]
    return response["access_token"]
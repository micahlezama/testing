import webbrowser
from colorama import Fore, Style
import crypto
import network
from classes.Game import GameAccount


class AccountService:
    @staticmethod
    def login(account: GameAccount) -> GameAccount:
        authorization = 'Basic ' + crypto.basic(account.identifier)
        nonce = crypto.nonce()

       # print(f"[DEBUG] Attempting login for {account.identifier}")
       # print(f"[DEBUG] Unique ID: {account.unique_id}")
       # print(f"[DEBUG] Authorization Header: {authorization}")

        try:
            req = network.post_auth_signin(
                authorization=authorization,
                nonce=nonce,
                unique_id=account.unique_id
            )
        except Exception as e:
           # print(f"[ERROR] Exception during network call: {e}")
            raise

       # print("[DEBUG] Initial response:", req)

        # Handle CAPTCHA if required
        if isinstance(req, dict) and 'captcha_url' in req:
            captcha_url = req['captcha_url']
            captcha_session_key = req.get('captcha_session_key')

           # print("[DEBUG] CAPTCHA detected:")
           # print(f"  URL: {captcha_url}")
           # print(f"  Session Key: {captcha_session_key}")

            webbrowser.open(captcha_url, new=2)
           # print(
              #  'Opening captcha in browser. Press' +
               # Fore.RED + Style.BRIGHT + ' ENTER ' +
               # Style.RESET_ALL + 'once you have solved it...'
          # )
            input()

            try:
                req = network.post_auth_signin(
                    authorization=authorization,
                    unique_id=account.unique_id,
                    nonce=nonce,
                    captcha_session_key=captcha_session_key
                )
            except Exception as e:
               # print(f"[ERROR] Exception during captcha signin: {e}")
                raise

           # print("[DEBUG] Response after captcha:", req)

        # Verify server returned a valid response
        if not isinstance(req, dict):
          #  print(f"[ERROR] Unexpected response type: {type(req)}")
            raise Exception("Expected dict response from network.post_auth_signin")

        # Log all keys from the server for inspection
       # print(f"[DEBUG] Response keys: {list(req.keys())}")

        if 'access_token' not in req:
           # print("[ERROR] Missing 'access_token' in response!")
           # print("[DEBUG] Full server response:")
           # print(req)
            raise Exception(f"Login failed. Server returned: {req}")

        if 'secret' not in req:
            print("[WARNING] Missing 'secret' in response. Continuing anyway.")

        # Assign tokens
        account.access_token = req['access_token']
        account.secret = req.get('secret', None)

       # print("[DEBUG] Login successful.")
       # print(f"[DEBUG] Access Token: {account.access_token[:8]}... (truncated)")
        # print(f"[DEBUG] Secret: {account.secret[:8] if account.secret else None}...")

        return account

import requests
import http.server
import socketserver
import json
import config
from urllib.parse import urlparse, parse_qs

PORT = 420
gt = 0

class PostRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global gt
        gt += 1
        if gt > 2:
            httpd.server_close()
            return

        print("--- Received GET Request ---")
        print(f"Path: {self.path}")
        print("Headers:")
        print(self.headers)
        
        # --- Ported PHP Code ---
        # 1. Define your OAuth variables
        token_url = 'https://oauth2.googleapis.com/token' # Example token URL
        google_client_id = '579337710789-endch2o4m7jfv38c7t89tqn7d8pcftdi.apps.googleusercontent.com'
        google_client_secret = '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'
        base_url = f'http://localhost:{PORT}' # Your redirect URI

        # 2. Parse the request URL to get the 'code' query parameter
        query_components = parse_qs(urlparse(self.path).query)
        auth_code = query_components.get('code', [None])[0]

        if auth_code:
            print(f"Authorization code received: {auth_code}")
            
            # 3. Exchange the authorization code for an access token
            payload = {
                'grant_type': 'authorization_code',
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'redirect_uri': base_url,
                'code': auth_code
            }
            
            try:
                headers = json.dumps({
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': config.game_platform.user_agent,
                    'Accept': '*/*'
                })
                response = requests.post(headers=headers, url=token_url, data=payload)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                token_data = response.json()
                
                print("\n--- Token Exchange Response ---")
                print(json.dumps(token_data, indent=2))
                print("-----------------------------\n")

            except requests.exceptions.RequestException as e:
                print(f"\n--- Error during token exchange: {e} ---")

        else:
            print("No 'code' parameter found in GET request.")
        # --- End of Ported Code ---

        print("---------------------------\n")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print("--- Received POST Request ---")
        print(f"Path: {self.path}")
        print("Headers:")
        print(self.headers)
        
        print("Body:")
        try:
            # Try to parse and pretty-print if it's JSON
            data = json.loads(post_data.decode('utf-8'))
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            # Otherwise, print as raw text
            print(post_data.decode('utf-8'))
        
        print("---------------------------\n")

        # Send a success response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'status': 'success', 'message': 'POST request received'}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def log_message(self, format, *args):
        # Silences the default logging to keep the output clean
        return

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), PostRequestHandler) as httpd:
        print(f"Starting server on http://localhost:{PORT}")
        print("Listening for POST requests...")
        httpd.serve_forever()
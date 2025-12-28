# ============================
# Imports (EXPLICIT)
# ============================
import os
import json
import signal
import requests
import webbrowser
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify
from werkzeug.wrappers import Request, Response        
from werkzeug.serving import make_server 
from dotenv import load_dotenv
from pathlib import Path
from threading import Thread
from time import sleep

def launch():
    # ============================
    # Environment loading
    # ============================
    BASE_DIR = Path(__file__).resolve().parent
    ENV_PATH = BASE_DIR / "discord.env"

    load_dotenv(ENV_PATH)
    print(f"🔧 Loading environment from: {ENV_PATH}")

    # ============================
    # Flask app
    # ============================
    app = Flask(__name__)

    # ============================
    # Discord App Info
    # ============================
    CLIENT_ID = "1431320716740919296"
    CLIENT_SECRET = "QppclEui2K3Bq3Rs9FfmmXl1oEOEuaWP"

    REDIRECT_URI = "http://localhost:5000/callback"
    LOCAL_CLIENT_REDIRECT = "http://localhost:5000/auth_success"

    DISCORD_API = "https://discord.com/api"
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    VERIFIED_ROLE_ID = os.getenv("VERIFIED_ROLE_ID")
    GUILD_ID = os.getenv("DISCORD_GUILD_ID")

    SUB_DB = BASE_DIR / "subscriptions.json"

    print("🔧 Loaded Discord Client Info:")
    print(f"CLIENT_ID: {CLIENT_ID}")
    print(f"CLIENT_SECRET present: {bool(CLIENT_SECRET)}")
    print(f"Guild ID: {GUILD_ID} | Verified Role ID: {VERIFIED_ROLE_ID}")

    # ============================
    # Helpers
    # ============================
    def load_subs():
        if not SUB_DB.exists():
            return {}
        with open(SUB_DB, "r") as f:
            return json.load(f)

    def save_subs(subs):
        with open(SUB_DB, "w") as f:
            json.dump(subs, f, indent=2)

    def has_verified_role(discord_id: str) -> bool:
        url = f"{DISCORD_API}/guilds/{GUILD_ID}/members/{discord_id}"
        headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            print(f"❌ Failed to fetch roles for {discord_id}: {resp.status_code}")
            return False

        return VERIFIED_ROLE_ID in resp.json().get("roles", [])

    # ============================
    # OAuth Routes
    # ============================
    @app.route("/login")
    def login():
        auth_url = (
            f"{DISCORD_API}/oauth2/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=guilds.members.read"
        )
        return redirect(auth_url)

    @app.route("/callback")
    def callback():
        code = request.args.get("code")

        token_resp = requests.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "scope": "identify",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ).json()

        if "access_token" not in token_resp:
            return jsonify(token_resp), 400

        user = requests.get(
            f"{DISCORD_API}/users/@me",
            headers={"Authorization": f"Bearer {token_resp['access_token']}"},
        ).json()

        discord_id = str(user["id"])
        username = user["username"]

        verified = has_verified_role(discord_id)

        subs = load_subs()
        subs[discord_id] = {
            "username": username,
            "active": verified,
            "verified_role": verified,
            "expires": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        }
        subs["token"] = token_resp['access_token']

        save_subs(subs)

        return redirect(f"{LOCAL_CLIENT_REDIRECT}?id={discord_id}&user={username}")

    @app.route("/auth_success")
    def success():
        global stated 
        did = request.args.get("discord_id")
        # --- CODE TO VERIFY ACCESS HERE ---
        # ----------------------------------
        stated['on'] = True 
        return "<p>Authentication successful!, you can close this window</p>"

    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        
    @app.get('/shutdown')
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'

    # ============================
    # API Routes
    # ============================
    @app.route("/api/check-access")
    def check_access():
        did = request.args.get("discord_id")
        subs = load_subs()
        user = subs.get(did)

        if not user or not user.get("active"):
            return jsonify({"status": "expired"}), 403

        if datetime.strptime(user["expires"], "%Y-%m-%d") < datetime.now():
            return jsonify({"status": "expired"}), 403

        return jsonify({"status": "active"})

    # ============================
    # Browser Open (WINDOWS SAFE)
    # ============================
    def open_browser():
        try:
            os.startfile("http://localhost:5000/login")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")

    def run_server(sd):
        global stated
        stated = sd
        stated['server'] = make_server("127.0.0.1", 5000, app)
        stated['server'].serve_forever()

    # ============================
    # Entry Point
    # ============================
    print("🚀 Starting Flask verification server...")
    state = {'on':False}
    fapp = Thread(target=run_server, args=(state,), daemon=True)
    fapp.start()

    sleep(5)
    open_browser()

    while fapp.is_alive() and not state['on']:
        print('Waiting for user authentication...')
        sleep(1)
    
    Thread(target=state['server'].shutdown, daemon=True).start()

    print('Starting bot...')
    import main
    main.main()

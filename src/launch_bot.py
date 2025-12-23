# ============================
# Imports (EXPLICIT)
# ============================
import os
import json
import requests
import webbrowser
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
from threading import Timer

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
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

REDIRECT_URI = "http://localhost:5000/callback"
LOCAL_CLIENT_REDIRECT = "http://127.0.0.1:6969/auth_success"

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
        f"&scope=identify"
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
    save_subs(subs)

    return redirect(f"{LOCAL_CLIENT_REDIRECT}?id={discord_id}&user={username}")

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

# ============================
# Entry Point
# ============================
if __name__ == "__main__":
    print("🚀 Starting Flask verification server...")

    # Open browser AFTER server starts
    Timer(1, open_browser).start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,        # MUST be False
        use_reloader=False # MUST be False
    )

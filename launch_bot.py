
# verify.py
import os, json, requests, threading, webbrowser
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv

from pathlib import Path

# Always load .env from the script’s directory (even when compiled)
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "discord.env"

load_dotenv(ENV_PATH)
print(f"🔧 Loading environment from: {ENV_PATH}")

app = Flask(__name__)

# ==== Discord App Info ====
CLIENT_ID = "1431702681616912414"
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"
LOCAL_CLIENT_REDIRECT = "http://127.0.0.1:6969/auth_success"
DISCORD_API = "https://discord.com/api"
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
VERIFIED_ROLE_ID = os.getenv("VERIFIED_ROLE_ID")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

SUB_DB = "subscriptions.json"

# ======================================================
# Helpers
# ======================================================
def load_subs():
    if not os.path.exists(SUB_DB):
        return {}
    with open(SUB_DB) as f:
        return json.load(f)

def save_subs(subs):
    with open(SUB_DB, "w") as f:
        json.dump(subs, f, indent=2)

def has_verified_role(discord_id: str) -> bool:
    """Check via Discord API if user has the required role."""
    url = f"{DISCORD_API}/guilds/{GUILD_ID}/members/{discord_id}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"❌ Failed to fetch roles for {discord_id}: {resp.status_code}")
        return False

    data = resp.json()
    roles = data.get("roles", [])
    return VERIFIED_ROLE_ID in roles

# ======================================================
# OAuth flow
# ======================================================
@app.route("/login")
def login():
    auth_url = (
        f"{DISCORD_API}/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
    )
    webbrowser.open(auth_url)
    return "Opening Discord login..."

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }
    token = requests.post(f"{DISCORD_API}/oauth2/token",
                          data=data,
                          headers={"Content-Type": "application/x-www-form-urlencoded"}).json()

    if "access_token" not in token:
        return jsonify({"error": "OAuth failed", "details": token}), 400

    user = requests.get(f"{DISCORD_API}/users/@me",
                        headers={"Authorization": f"Bearer {token['access_token']}"}).json()

    discord_id = str(user["id"])
    username = user["username"]

    # Automatically verify by role
    verified = has_verified_role(discord_id)
    subs = load_subs()
    subs[discord_id] = {
        "username": username,
        "active": verified,
        "verified_role": verified,
        "expires": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    }
    save_subs(subs)

    if verified:
        print(f"✅ {username} ({discord_id}) has verified role and active subscription.")
    else:
        print(f"❌ {username} ({discord_id}) does NOT have the required Discord role.")

    return redirect(f"{LOCAL_CLIENT_REDIRECT}?id={discord_id}&user={username}")

# ======================================================
# Subscription endpoints
# ======================================================
@app.route("/api/check-access")
def check_access():
    did = request.args.get("discord_id")
    subs = load_subs()
    user = subs.get(did)
    if not user:
        return jsonify({"status": "expired", "reason": "No record"}), 403
    if not user.get("active", False):
        return jsonify({"status": "expired", "reason": "Inactive"}), 403
    exp = datetime.strptime(user["expires"], "%Y-%m-%d")
    if exp < datetime.now():
        return jsonify({"status": "expired", "reason": "Expired"}), 403
    return jsonify({"status": "active"})

# Admin endpoints
@app.route("/api/list-subs")
def list_subs():
    return jsonify(load_subs())

@app.route("/api/toggle-sub", methods=["POST"])
def toggle_sub():
    data = request.get_json()
    did = str(data["discord_id"])
    subs = load_subs()
    if did not in subs:
        return jsonify({"error": "User not found"}), 404
    subs[did]["active"] = not subs[did]["active"]
    save_subs(subs)
    return jsonify({"discord_id": did, "new_status": subs[did]["active"]})

@app.route("/api/delete-sub", methods=["POST"])
def delete_sub():
    data = request.get_json()
    did = str(data["discord_id"])
    subs = load_subs()
    if did in subs:
        del subs[did]
        save_subs(subs)
        return jsonify({"deleted": did})
    return jsonify({"error": "User not found"}), 404

# ======================================================
if __name__ == "__main__":
    print(f"🔧 Loaded Discord Client Info:\nCLIENT_ID: {CLIENT_ID}\nCLIENT_SECRET present: {bool(CLIENT_SECRET)}")
    print(f"🔧 Guild ID: {GUILD_ID} | Verified Role ID: {VERIFIED_ROLE_ID}")
    print("🚀 Starting Flask verification server...\n")
    print("In launch_bot.py, starting bot...")
    input("Press [Enter] to exit...")
    app.run(debug=True)



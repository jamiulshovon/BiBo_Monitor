"""
set_github_secrets.py - Automatically encrypts and uploads BiBoTracker credentials
to GitHub Repository Secrets using libsodium SealedBox encryption.
"""

import os
import sys
import getpass
import base64
import json
import urllib.request
import subprocess
from nacl import public

REPO = "jamiulshovon/BiBo_Monitor"

def get_git_token():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def get_public_key(token):
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/public-key"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "BiBo-Monitor"
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    public_key_bytes = base64.b64decode(public_key_b64)
    public_key_obj = public.PublicKey(public_key_bytes)
    box = public.SealedBox(public_key_obj)
    encrypted = box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_secret(token: str, secret_name: str, key_id: str, encrypted_value: str):
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/{secret_name}"
    payload = json.dumps({
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "BiBo-Monitor"
    })
    with urllib.request.urlopen(req) as resp:
        return resp.status in (201, 204)

def trigger_workflow(token):
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/408985686/dispatches"
    payload = json.dumps({"ref": "main", "inputs": {"tag": "authenticated_test"}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "BiBo-Monitor"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (201, 204)
    except Exception as e:
        print("Dispatch error:", e)
        return False

def main():
    token = get_git_token()
    if not token:
        print("[ERROR] Could not automatically retrieve GitHub token from git credentials.")
        print(f"Please set your secrets directly at: https://github.com/{REPO}/settings/secrets/actions")
        sys.exit(1)

    print("=" * 60)
    print("Set BiBoTracker GitHub Actions Secrets")
    print(f"Target Repository: https://github.com/{REPO}")
    print("=" * 60)

    email = input("Enter your BiBoTracker Admin Email: ").strip()
    if not email:
        print("Email cannot be empty.")
        sys.exit(1)

    password = getpass.getpass("Enter your BiBoTracker Admin Password: ").strip()
    if not password:
        print("Password cannot be empty.")
        sys.exit(1)

    print("\n1. Fetching repository public key from GitHub...")
    key_info = get_public_key(token)
    key_id = key_info["key_id"]
    public_key = key_info["key"]

    print("2. Encrypting credentials with libsodium SealedBox...")
    enc_email = encrypt_secret(public_key, email)
    enc_password = encrypt_secret(public_key, password)

    print("3. Uploading BIBO_EMAIL secret to GitHub...")
    set_secret(token, "BIBO_EMAIL", key_id, enc_email)

    print("4. Uploading BIBO_PASSWORD secret to GitHub...")
    set_secret(token, "BIBO_PASSWORD", key_id, enc_password)

    print("\n[SUCCESS] Secrets successfully configured on GitHub Actions!")
    print("Triggering an automated test run now to verify dashboard capture...")
    if trigger_workflow(token):
        print("[SUCCESS] Test run dispatched in GitHub Actions!")
        print(f"Monitor live here: https://github.com/{REPO}/actions")
    else:
        print("Could not dispatch test run automatically. You can trigger it from GitHub Actions UI.")

if __name__ == "__main__":
    main()

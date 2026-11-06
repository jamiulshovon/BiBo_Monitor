"""
login_setup.py - One-time interactive login to save session cookies.

This opens a visible browser window, navigates to the admin login page,
and allows you to sign in. Once signed in, it saves the session state to `auth_state.json`.
Subsequent automated screenshots will use this saved session without asking for login again.
"""

import sys
import time
from playwright.sync_api import sync_playwright
import config

def main():
    print("=" * 60)
    print("BiBoTracker Admin - Session Login Setup")
    print("=" * 60)
    print("Opening browser window...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport=config.VIEWPORT)
        page = context.new_page()

        print(f"Navigating to {config.TARGET_URL} ...")
        page.goto(config.TARGET_URL)

        # If email/password are in config/.env, auto-fill them as convenience
        if config.BIBO_EMAIL:
            try:
                page.wait_for_selector('input[type="text"], input[type="email"]', timeout=5000)
                email_input = page.locator('input[type="text"], input[type="email"]').first
                email_input.fill(config.BIBO_EMAIL)
                print(f"Auto-filled email: {config.BIBO_EMAIL}")

                if config.BIBO_PASSWORD:
                    password_input = page.locator('input[type="password"]').first
                    password_input.fill(config.BIBO_PASSWORD)
                    print("Auto-filled password.")
            except Exception as e:
                print(f"Notice: Auto-fill skipped ({e})")

        print("\n>>> Please complete sign-in in the open browser window. <<<")
        print("Waiting for successful login (navigating away from /login)...")

        # Wait until the page URL is no longer /login
        try:
            page.wait_for_url(lambda u: "/login" not in u and "bibotracker.com/admin" in u, timeout=180000)
            # Give dashboard an extra couple seconds to finish initial hydration
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            # Check if current URL already passed login
            if "/login" not in page.url:
                pass
            else:
                print(f"\n[ERROR] Login timed out or did not complete: {e}")
                browser.close()
                sys.exit(1)

        print("\n[SUCCESS] Login detected! Dashboard reached:", page.url)

        # Save cookies & localStorage state
        context.storage_state(path=config.AUTH_STATE_PATH)
        print(f"[SUCCESS] Session saved to '{config.AUTH_STATE_PATH}'.")
        print("You can now run 'take_screenshot.py' or start the scheduler!")

        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    main()

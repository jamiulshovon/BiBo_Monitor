"""
take_screenshot.py - Captures BiBoTracker admin dashboard with timestamp banner.
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import config

# Bangladesh Standard Time (BST) is UTC+6
BD_TZ = timezone(timedelta(hours=6), name="BST")

def get_bd_time():
    """Returns the current datetime in Bangladesh Standard Time."""
    return datetime.now(BD_TZ)

def inject_timestamp_banner(page, bd_time_str, tag=""):
    """Injects a modern, high-contrast banner at the top of the page before screenshotting."""
    banner_text = f"Bangladesh Time (BST): {bd_time_str}"
    if tag:
        banner_text += f" [{tag}]"

    banner_js = """
    (bannerText) => {
        const existing = document.getElementById('bibo-monitor-banner');
        if (existing) existing.remove();

        const banner = document.createElement('div');
        banner.id = 'bibo-monitor-banner';
        banner.style.position = 'sticky';
        banner.style.top = '0';
        banner.style.left = '0';
        banner.style.width = '100%';
        banner.style.boxSizing = 'border-box';
        banner.style.backgroundColor = '#0f172a';
        banner.style.color = '#38bdf8';
        banner.style.borderBottom = '3px solid #0284c7';
        banner.style.padding = '12px 24px';
        banner.style.zIndex = '2147483647';
        banner.style.fontFamily = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
        banner.style.fontSize = '16px';
        banner.style.fontWeight = '700';
        banner.style.display = 'flex';
        banner.style.justifyContent = 'space-between';
        banner.style.alignItems = 'center';
        banner.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.4)';

        banner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">⏰</span>
                <span>${bannerText}</span>
            </div>
            <div style="font-size: 13px; color: #94a3b8; font-weight: 500;">
                BiBoTracker Admin Monitor
            </div>
        `;

        document.body.prepend(banner);
    }
    """
    try:
        page.evaluate(banner_js, banner_text)
    except Exception as e:
        print(f"Notice: Failed to inject banner ({e})")

def apply_zoom(page, zoom_level):
    """Applies CSS zoom out if requested."""
    if not zoom_level or str(zoom_level).strip() in ("100%", "1", "1.0"):
        return
    zoom_str = str(zoom_level).strip()
    if zoom_str.replace('.', '', 1).isdigit():
        val = float(zoom_str)
        if val <= 2.0:
            zoom_str = f"{int(val * 100)}%"
        else:
            zoom_str = f"{int(val)}%"
    elif not zoom_str.endswith("%"):
        zoom_str = f"{zoom_str}%"

    print(f"Applying zoom level: {zoom_str}")
    try:
        page.evaluate(f"() => {{ document.body.style.zoom = '{zoom_str}'; }}")
        page.wait_for_timeout(600)
    except Exception as e:
        print(f"Notice: Could not set zoom ({e})")

def expand_table_and_adjust_viewport(page):
    """
    Ensures that scrollable containers, fixed height flex layouts, and table wrappers
    are expanded so that all employees in the table are 100% visible from top to bottom
    without being cut off or hidden behind a scrollbar.
    """
    js_code = """
    () => {
        // 1. Unconstrain main layout wrappers
        document.documentElement.style.height = 'auto';
        document.documentElement.style.overflow = 'visible';
        document.body.style.height = 'auto';
        document.body.style.overflow = 'visible';

        const root = document.getElementById('root');
        if (root) {
            root.style.height = 'auto';
            root.style.minHeight = '100%';
            root.style.overflow = 'visible';
        }

        // 2. Expand all scroll containers and fixed screen heights
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.overflowY === 'auto' || style.overflowY === 'scroll' || style.overflow === 'hidden') {
                el.style.overflow = 'visible';
                el.style.overflowY = 'visible';
                el.style.maxHeight = 'none';
            }
            if (el.classList.contains('h-screen') || style.height.includes('100vh') || style.maxHeight.includes('100vh')) {
                el.style.height = 'auto';
                el.style.maxHeight = 'none';
                el.style.minHeight = '100vh';
            }
        });

        // 3. Specifically expand table and all its parent containers
        const table = document.querySelector('table');
        let tableBottom = 0;
        if (table) {
            let parent = table.parentElement;
            while (parent && parent !== document.body) {
                parent.style.height = 'auto';
                parent.style.maxHeight = 'none';
                parent.style.overflow = 'visible';
                parent.style.overflowY = 'visible';
                parent = parent.parentElement;
            }
            const rect = table.getBoundingClientRect();
            tableBottom = rect.bottom + window.scrollY;
        }

        // Return the total height needed to show everything
        const bodyHeight = document.body.scrollHeight;
        const docHeight = document.documentElement.scrollHeight;
        return Math.max(bodyHeight, docHeight, tableBottom + 120);
    }
    """
    try:
        content_height = page.evaluate(js_code)
        # Set viewport height to comfortably encompass all rows (min 1600px)
        needed_height = max(1600, int(content_height) + 100)
        page.set_viewport_size({"width": 1920, "height": needed_height})
        page.wait_for_timeout(800)
        page.evaluate("() => window.scrollTo(0, 0)")
        print(f"Auto-expanded layout: set viewport height to {needed_height}px to show all employees.")
    except Exception as e:
        print(f"Notice: Could not adjust viewport ({e})")

def attempt_auto_login(page, context):
    """Attempts to auto-login if credentials are present in config."""
    if not (config.BIBO_EMAIL and config.BIBO_PASSWORD):
        return False

    print("Attempting automated login with configured credentials...")
    try:
        page.wait_for_selector('input[type="text"], input[type="email"]', timeout=8000)
        email_el = page.locator('input[type="text"], input[type="email"]').first
        password_el = page.locator('input[type="password"]').first
        submit_btn = page.locator('button[type="submit"]').first

        email_el.fill(config.BIBO_EMAIL)
        password_el.fill(config.BIBO_PASSWORD)
        submit_btn.click()

        # Wait for navigation away from /login
        page.wait_for_url(lambda u: "/login" not in u and "bibotracker.com" in u, timeout=20000)
        page.wait_for_load_state("networkidle", timeout=15000)

        # Update saved session
        context.storage_state(path=config.AUTH_STATE_PATH)
        print(f"Auto-login successful! Updated '{config.AUTH_STATE_PATH}'.")
        return True
    except Exception as e:
        print(f"Auto-login failed: {e}")
        return False

def take_screenshot(tag="", target_url=None, zoom=None, headless=True):
    target_url = target_url or config.TARGET_URL or "https://bibotracker.com/admin"
    zoom_level = zoom or config.ZOOM_LEVEL
    os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)

    bd_now = get_bd_time()
    
    # Auto-detect tag if not provided
    if not tag or tag.lower() == "auto":
        hour = bd_now.hour
        minute = bd_now.minute
        if 5 <= hour <= 6:
            tag = "06AM"
        elif hour == 9 and minute < 45:
            tag = "09_40AM"
        elif 9 <= hour <= 11:
            tag = "10AM"
        elif (hour == 13 and minute >= 10) or (hour == 14 and minute <= 10):
            tag = "01_30PM"
        else:
            tag = bd_now.strftime("%I_%M%p")

    time_display = bd_now.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    filename_time = bd_now.strftime("%Y-%m-%d_%H-%M-%S")
    tag_slug = f"_{tag.replace(' ', '_')}" if tag else ""
    output_filename = f"bibo{tag_slug}_{filename_time}_BST.png"
    output_path = os.path.join(config.SCREENSHOTS_DIR, output_filename)

    print(f"[{time_display}] Starting screenshot capture...")
    print(f"Target URL: {target_url}")
    print(f"Configured Zoom: {zoom_level}")

    has_auth_file = os.path.exists(config.AUTH_STATE_PATH)
    if not has_auth_file:
        print(f"Notice: Session file '{config.AUTH_STATE_PATH}' not found.")
        print("Tip: Run 'python login_setup.py' once to log in and save your session.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        context_kwargs = {
            "viewport": config.VIEWPORT,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        if has_auth_file:
            context_kwargs["storage_state"] = config.AUTH_STATE_PATH

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        try:
            page.goto(target_url, wait_until="networkidle", timeout=45000)
        except PlaywrightTimeoutError:
            print("Notice: Page navigation reached network timeout; continuing with current DOM state...")

        # If redirected to login page, attempt auto-login
        if "/login" in page.url:
            print(f"Redirected to login: {page.url}")
            logged_in = attempt_auto_login(page, context)
            if not logged_in and not (config.BIBO_EMAIL and config.BIBO_PASSWORD):
                print("WARNING: Capturing login screen because user is not authenticated.")
                print("To fix this, please run 'python login_setup.py' to save your session.")

        # Allow extra time for client-side React table/cards to populate active users
        page.wait_for_timeout(4000)
        try:
            page.wait_for_selector('table tbody tr', timeout=5000)
        except Exception:
            pass

        # Expand scrollable containers and dynamically adjust viewport height so all rows are visible
        expand_table_and_adjust_viewport(page)

        # Apply CSS zoom if requested (defaults to 100% full scale)
        apply_zoom(page, zoom_level)

        # Inject visible timestamp header
        inject_timestamp_banner(page, time_display, tag=tag)

        # Capture full-page screenshot
        page.screenshot(path=output_path, full_page=True)
        print(f"[SUCCESS] Screenshot saved: {output_path}")

        browser.close()

    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture BiBoTracker admin dashboard")
    parser.add_argument("--tag", default="", help="Optional label (e.g. 06am, 10am, 02pm)")
    parser.add_argument("--url", default="", help="Override target URL")
    parser.add_argument("--zoom", default="", help="Zoom level (e.g. 80%, 75%, 90%)")
    parser.add_argument("--headful", action="store_true", help="Run browser visibly")

    args = parser.parse_args()
    take_screenshot(tag=args.tag, target_url=args.url or None, zoom=args.zoom or None, headless=not args.headful)

"""
take_screenshot.py - Captures BiBoTracker admin dashboard with timestamp banner.
Saves screenshots into fixed time folders (06-10_AM, 08-20_AM, 12-55_PM, 02-00_PM)
with date-only filenames (YYYY-MM-DD.png).
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import config

# Bangladesh Standard Time (BST) is UTC+6
BD_TZ = timezone(timedelta(hours=6), name="BST")

# Fixed schedule slots in Bangladesh Standard Time
FIXED_SLOTS = [
    (6, 10, "06-10_AM"),
    (8, 20, "08-20_AM"),
    (12, 55, "12-55_PM"),
    (14, 0, "02-00_PM"),
]

def get_bd_time():
    """Returns the current datetime in Bangladesh Standard Time."""
    return datetime.now(BD_TZ)

def resolve_folder(folder_arg="", tag_arg="", bd_dt=None):
    """
    Resolves the folder name into one of: 06-10_AM, 08-20_AM, 12-55_PM, 02-00_PM.
    Supports exact names, friendly aliases, or automatic closest-slot detection.
    """
    if bd_dt is None:
        bd_dt = get_bd_time()

    folder_map = {
        "06-10_am": "06-10_AM", "06-10": "06-10_AM", "0610": "06-10_AM", "6:10": "06-10_AM",
        "06:10": "06-10_AM", "06am": "06-10_AM", "6am": "06-10_AM", "bibo 6": "06-10_AM",
        "08-20_am": "08-20_AM", "08-20": "08-20_AM", "0820": "08-20_AM", "8:20": "08-20_AM",
        "08:20": "08-20_AM", "08_20am": "08-20_AM", "08am": "08-20_AM", "8am": "08-20_AM",
        "12-55_pm": "12-55_PM", "12-55": "12-55_PM", "1255": "12-55_PM", "12:55": "12-55_PM",
        "12_55pm": "12-55_PM", "12pm": "12-55_PM", "bibo 12": "12-55_PM",
        "02-00_pm": "02-00_PM", "02-00": "02-00_PM", "0200": "02-00_PM", "2:00": "02-00_PM",
        "02:00": "02-00_PM", "2pm": "02-00_PM", "02pm": "02-00_PM", "01_30pm": "02-00_PM",
        "14:00": "02-00_PM", "bibo 2": "02-00_PM"
    }

    # Check explicit folder_arg first
    cleaned_folder = (folder_arg or "").strip().lower()
    if cleaned_folder and cleaned_folder != "auto":
        if cleaned_folder in folder_map:
            return folder_map[cleaned_folder]
        for k, v in folder_map.items():
            if k in cleaned_folder:
                return v

    # Check explicit tag_arg next
    cleaned_tag = (tag_arg or "").strip().lower()
    if cleaned_tag and cleaned_tag != "auto":
        if cleaned_tag in folder_map:
            return folder_map[cleaned_tag]
        for k, v in folder_map.items():
            if k in cleaned_tag:
                return v

    # Auto-detect: find closest slot to current Bangladesh time
    current_minutes = bd_dt.hour * 60 + bd_dt.minute
    best_folder = FIXED_SLOTS[0][2]
    min_diff = 999999

    for h, m, f_name in FIXED_SLOTS:
        slot_minutes = h * 60 + m
        diff = abs(current_minutes - slot_minutes)
        if diff < min_diff:
            min_diff = diff
            best_folder = f_name

    return best_folder

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

def take_screenshot(folder="", tag="", target_url=None, zoom=None, headless=True):
    target_url = target_url or config.TARGET_URL or "https://bibotracker.com/admin"
    zoom_level = zoom or config.ZOOM_LEVEL

    bd_now = get_bd_time()
    folder_name = resolve_folder(folder_arg=folder, tag_arg=tag, bd_dt=bd_now)
    target_folder_dir = os.path.join(config.SCREENSHOTS_DIR, folder_name)
    os.makedirs(target_folder_dir, exist_ok=True)

    date_str = bd_now.strftime("%Y-%m-%d")
    output_filename = f"{date_str}.png"
    output_path = os.path.join(target_folder_dir, output_filename)

    time_display = bd_now.strftime("%Y-%m-%d %I:%M:%S %p %Z")

    print(f"[{time_display}] Starting screenshot capture...")
    print(f"Folder: {folder_name} | Filename: {output_filename}")
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
        inject_timestamp_banner(page, time_display, tag=folder_name)

        # Capture full-page screenshot
        page.screenshot(path=output_path, full_page=True)
        print(f"[SUCCESS] Screenshot saved: {output_path}")

        browser.close()

    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture BiBoTracker admin dashboard")
    parser.add_argument("--folder", default="", help="Time folder (06-10_AM, 08-20_AM, 12-55_PM, 02-00_PM)")
    parser.add_argument("--tag", default="", help="Optional label or slot alias")
    parser.add_argument("--url", default="", help="Override target URL")
    parser.add_argument("--zoom", default="", help="Zoom level (e.g. 80%, 75%, 90%)")
    parser.add_argument("--headful", action="store_true", help="Run browser visibly")

    args = parser.parse_args()
    take_screenshot(
        folder=args.folder,
        tag=args.tag,
        target_url=args.url or None,
        zoom=args.zoom or None,
        headless=not args.headful
    )

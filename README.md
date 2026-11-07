# BiBoTracker Admin Automated Screenshot Monitor

Automated screenshot monitoring system for [`https://bibotracker.com/admin`](https://bibotracker.com/admin) to track active users at **6:00 AM**, **9:28 AM**, **10:00 AM**, and **1:30 PM** (Bangladesh Standard Time - BST / UTC+6).

---

## 🚀 Features

- **Automated Login & Session Persistence**:
  - Handles the admin authentication wall seamlessly.
  - Option to log in once via browser (`login_setup.py`) or configure `.env` for zero-touch auto-login.
- **Embedded Bangladesh Timestamp**:
  - Automatically injects a high-visibility banner at the top of the page displaying the exact Bangladesh date & time before capture.
  - Formats image filenames with the exact timestamp (e.g., `bibo_06AM_2026-11-06_06-00-00_BST.png`).
- **Full Dashboard Capture**:
  - Captures full scrollable height (`full_page=True`) at high resolution (1920x1080 viewport).
- **Flexible Scheduling**:
  - **Native Windows Task Scheduler** (`setup_scheduler.ps1`) — runs silently in the background without needing a terminal open.
  - **Python Daemon** (`scheduler.py`) — runs continuously in a terminal.
  - **GitHub Actions** (`.github/workflows/scheduled_screenshot.yml`) — runs in the cloud 24/7 even if your PC is turned off.

---

## 📁 Project Structure

```
W:\BIbo\
│
├── take_screenshot.py       # Core screenshot engine with timestamp overlay
├── login_setup.py          # 1-time interactive login tool to save session
├── scheduler.py            # Continuous background scheduler
├── config.py               # Central configuration loader
├── setup_scheduler.ps1     # 1-click installer for Windows Task Scheduler
├── remove_scheduler.ps1    # Uninstaller for Windows Task Scheduler
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── screenshots/            # Directory where captures are saved
```

---

## 🛠️ Setup Guide

### Step 1: Authentication Setup

Since `bibotracker.com/admin` requires an admin login to view active users, choose either:

#### Option A: Quick Interactive Login (Recommended)
Run:
```powershell
python login_setup.py
```
A browser window will open. Simply log in with your admin credentials. Once you reach the dashboard, the script will automatically save your session to `auth_state.json`.

#### Option B: Automatic Login via `.env`
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Fill in your credentials:
```ini
BIBO_EMAIL=your_admin_email@example.com
BIBO_PASSWORD=your_password
```
*(If your session ever expires, the script will automatically log back in headlessly.)*

---

### Step 2: Test Screenshot
Run a manual test capture anytime:
```powershell
python take_screenshot.py --tag test
```
Check the [`screenshots/`](screenshots/) folder to see your test screenshot!

---

### Step 3: Enable the 3 Daily Schedules (6 AM, 10 AM, 2 PM BD Time)

#### Choice 1: Windows Task Scheduler (Recommended for Windows)
Run PowerShell as Administrator or standard user and execute:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1
```
This registers 3 daily silent background tasks in Windows:
- `BiBoTracker_0540AM` -> Every day at 05:40 AM
- `BiBoTracker_10AM` -> Every day at 10:00 AM
- `BiBoTracker_0130PM` -> Every day at 01:30 PM (13:30)

*To remove them later: `powershell -ExecutionPolicy Bypass -File .\remove_scheduler.ps1`*

#### Choice 2: Standalone Python Scheduler
If you want to keep a terminal window running in the background:
```powershell
python scheduler.py
```

#### Choice 3: 24/7 Cloud Monitoring with GitHub Actions (Zero Local PC Requirement)

If your computer is off or sleeping at 6:00 AM, GitHub Actions runs **100% in the cloud for free**:

1. **Create a Private GitHub Repo**:
   - Go to [github.com/new](https://github.com/new).
   - Name it `bibo-tracker-monitor` and set it to **Private**.
   - Do **not** check "Add a README" (your local repository already has everything).

2. **Push your code to GitHub**:
   In PowerShell (inside `W:\BIbo`):
   ```powershell
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
   git push -u origin main
   ```

3. **Set Workflow Write Permissions**:
   - On GitHub, go to **Settings** → **Actions** → **General**.
   - Scroll down to **Workflow permissions**.
   - Select **Read and write permissions** (allows GitHub Actions to commit screenshots into `screenshots/`).
   - Click **Save**.

4. **Add Admin Credentials in Secrets**:
   - Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
   - Add:
     - `BIBO_EMAIL`: Your BiBoTracker admin login email.
     - `BIBO_PASSWORD`: Your BiBoTracker admin password.
     - *(Optional)* `BIBO_TARGET_URL`: Defaults to `https://bibotracker.com/admin`.

5. **Schedule & Viewing**:
   - The workflow runs automatically at **05:40 AM**, **10:00 AM**, and **01:30 PM** Bangladesh Standard Time (UTC+6).
   - Screenshots are pushed directly to the `screenshots/` folder in your GitHub repository, so you can view them anytime from your mobile or PC!
   - You can also test it immediately by opening the **Actions** tab on GitHub, selecting **BiBoTracker Admin Screenshot Monitor**, and clicking **Run workflow**.

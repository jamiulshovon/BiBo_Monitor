# BiBoTracker Admin Automated Screenshot Monitor

Automated screenshot monitoring system for [`https://bibotracker.com/admin`](https://bibotracker.com/admin) to track active users at **6:00 AM**, **10:00 AM**, and **2:00 PM** (Bangladesh Standard Time - BST / UTC+6).

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
- `BiBoTracker_06AM` -> Every day at 06:00 AM
- `BiBoTracker_10AM` -> Every day at 10:00 AM
- `BiBoTracker_02PM` -> Every day at 02:00 PM (14:00)

*To remove them later: `powershell -ExecutionPolicy Bypass -File .\remove_scheduler.ps1`*

#### Choice 2: Standalone Python Scheduler
If you want to keep a terminal window running in the background:
```powershell
python scheduler.py
```

#### Choice 3: 24/7 Cloud Monitoring (GitHub Actions)
If your computer might be turned off or sleeping at 6 AM:
1. Push this folder to a private GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add `BIBO_EMAIL` and `BIBO_PASSWORD` secrets.
4. The workflow in `.github/workflows/scheduled_screenshot.yml` will automatically trigger at 6 AM, 10 AM, and 2 PM BD time every day in GitHub's cloud runners.

# BiBoTracker Admin Automated Screenshot Monitor

Automated screenshot monitoring system for [`https://bibotracker.com/admin`](https://bibotracker.com/admin) to track active users at **6:10 AM**, **8:20 AM**, **12:55 PM**, and **2:00 PM** (Bangladesh Standard Time - BST / UTC+6).

---

## 🚀 Features

- **Organized Time Folders**:
  Screenshots are saved into 4 fixed time folders inside `screenshots/`:
  - `screenshots/06-10_AM/`
  - `screenshots/08-20_AM/`
  - `screenshots/12-55_PM/`
  - `screenshots/02-00_PM/`
- **Clean Date-Only Filenames**:
  Every screenshot is named strictly by date: `YYYY-MM-DD.png` (e.g. `2026-11-09.png`).
- **Embedded Bangladesh Timestamp Banner**:
  Automatically injects a high-visibility banner at the top of the webpage before capture showing the exact date, time, and timezone.
- **Full Employee Viewport (No Scrollbars or Cutoffs)**:
  Dynamically un-restricts page height so all employees (all rows) are 100% visible from top to bottom.
- **Automated Login & Session Persistence**:
  Zero-touch auto-login using GitHub Actions secrets (`BIBO_EMAIL`, `BIBO_PASSWORD`) or local session `auth_state.json`.
- **Zero-Delay Triggering with cron-job.org & GitHub Actions**:
  Fires precisely at 6:10 AM, 8:20 AM, 12:55 PM, and 2:00 PM BST and commits screenshots directly to your GitHub repo.

---

## 📁 Project Structure

```
W:\BIbo\
│
├── take_screenshot.py       # Core screenshot engine with layout expansion & banner
├── login_setup.py          # 1-time interactive login tool to save session
├── scheduler.py            # Continuous background scheduler
├── config.py               # Central configuration loader
├── setup_scheduler.ps1     # 1-click installer for Windows Task Scheduler
├── remove_scheduler.ps1    # Uninstaller for Windows Task Scheduler
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── screenshots/            # Organized captures
    ├── 06-10_AM/           # 6:10 AM BST captures (YYYY-MM-DD.png)
    ├── 08-20_AM/           # 8:20 AM BST captures (YYYY-MM-DD.png)
    ├── 12-55_PM/           # 12:55 PM BST captures (YYYY-MM-DD.png)
    └── 02-00_PM/           # 2:00 PM BST captures (YYYY-MM-DD.png)
```

---

## 🛠️ Usage

### Manual Test Run
Capture a screenshot to a specific time folder:
```powershell
python take_screenshot.py --folder 08-20_AM
```
Or let the script auto-detect the closest scheduled slot:
```powershell
python take_screenshot.py
```

### GitHub Actions Manual Trigger
In your GitHub repo:
1. Go to **Actions** → **BiBoTracker Admin Screenshot Monitor**.
2. Click **Run workflow**.
3. Select the folder (or leave as `auto`) and click **Run workflow**.

---

## ⏰ Schedule Details (Bangladesh Time - BST)

| Time | Folder | Filename Format |
|---|---|---|
| **6:10 AM BST** | `screenshots/06-10_AM/` | `YYYY-MM-DD.png` |
| **8:20 AM BST** | `screenshots/08-20_AM/` | `YYYY-MM-DD.png` |
| **12:55 PM BST** | `screenshots/12-55_PM/` | `YYYY-MM-DD.png` |
| **2:00 PM BST** | `screenshots/02-00_PM/` | `YYYY-MM-DD.png` |

# GLaDOS Auto Check-in

Automated login and daily check-in script for GLaDOS VPN service.

## Features

- ✅ Automatically send verification code to email
- ✅ Automatically read verification code from Gmail (supports two email formats)
- ✅ Automatically login to GLaDOS
- ✅ Automatically perform daily check-in
- ✅ Save login session to avoid repeated login
- ✅ Support SOCKS5 proxy for Gmail connection
- ✅ Configuration file management for easy customization

## Requirements

- Python 3.7+
- Anaconda (recommended) or pip

## Installation

### 1. Create Anaconda Virtual Environment

```bash
# Create virtual environment
conda create -n glados-checkin python=3.11

# Activate virtual environment
conda activate glados-checkin
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gmail App Password

Due to Google's enhanced security, you need to use an App Specific Password:

1. Visit https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Select "Mail" and "Other (custom name)"
4. Enter a name like "GLaDOS Check-in"
5. Click "Generate" to get a 16-digit password
6. Copy this password to the `email.password` field in `config.yaml`

### 4. Configure config.yaml

Edit `config.yaml` file and set your email and app password:

```yaml
email:
  address: "your_email@gmail.com"  # Your Gmail address
  password: "your_app_password"     # Gmail App Specific Password
```

### 5. (Optional) Configure Proxy

If you need a proxy to access Gmail, configure the SOCKS5 proxy settings:

```yaml
proxy:
  socks5_host: "192.168.1.237"  # Proxy server address
  socks5_port: 7891              # SOCKS5 port (Clash: 7891, v2ray: 1080)
```

## Usage

### Run the Program

```bash
python3 glados_checkin.py
```

### First Run (Login Required)

The program will automatically:

1. Send verification code to your email
2. Wait and read verification code from Gmail
3. Login to GLaDOS with the verification code
4. Save session to `session.json` file
5. Perform daily check-in

### Subsequent Runs (Using Saved Session)

The program will directly use the saved session:
1. Load saved session
2. Perform daily check-in

### Example Output

First run:
```
==================================================
GLaDOS Auto Check-in
==================================================

Step 1: Requesting verification code...
✓ Verification code sent to user@gmail.com

Step 2: Waiting for verification code...
  (Check your Gmail inbox)
✓ Verification code found: 513544

Step 3: Logging in with code: 513544...
✓ Login successful
✓ Session saved to session.json

✓ Login process completed successfully!

Step 4: Performing daily check-in...
  Current points: {'email': 'user@gmail.com', 'points': 100}
✓ Check-in successful
  Response: {'message': 'Check-in successful', 'points': 105}
  User status: {'email': 'user@gmail.com', 'expire': 2024-12-31}

✓ All tasks completed successfully!
```

Subsequent run:
```
==================================================
GLaDOS Auto Check-in
==================================================
✓ Session loaded from session.json
✓ Using existing session (skip login)

Step 4: Performing daily check-in...
✓ Check-in successful

✓ All tasks completed successfully!
```

## Project Structure

```
auto-checkin/
├── config.yaml           # Configuration file
├── glados_checkin.py     # Main program
├── requirements.txt      # Python dependencies
├── session.json          # Login session (auto-generated)
├── README.md            # Chinese documentation
└── README_EN.md         # English documentation
```

## Configuration

The `config.yaml` file contains the following configuration options:

```yaml
# Email settings
email:
  address: "your_email@gmail.com"      # Gmail address
  password: ""                          # Gmail App Specific Password
  imap_server: "imap.gmail.com"         # IMAP server
  imap_port: 993                        # IMAP port

# Proxy settings (optional)
proxy:
  # SOCKS5 proxy for IMAP connection (e.g., Clash, v2ray, etc.)
  # Leave empty to disable proxy
  socks5_host: ""                       # Proxy server address, e.g., "192.168.1.237"
  socks5_port: 7891                     # SOCKS5 port (Clash: 7891, v2ray: 1080)

# GLaDOS settings
glados:
  base_url: "https://glados.cloud"        # GLaDOS website
  login_url: "https://glados.cloud/api/login"        # Login API
  auth_url: "https://glados.cloud/api/authorization" # Authorization API
  site: "glados.network"                # Site identifier

# Session settings
session:
  save_path: "session.json"             # Session save path
```

## Notes

1. **Gmail Security**:
   - Must use App Specific Password, not your account password
   - Ensure IMAP access is enabled for Gmail
   - Visit https://mail.google.com/mail/u/0/#settings/fwdandpop to confirm IMAP is enabled

2. **Proxy Configuration**:
   - If you cannot connect to Gmail, configure a SOCKS5 proxy
   - Ensure your proxy tool (such as Clash, v2ray) is running
   - Check your proxy tool configuration to confirm the SOCKS5 port

3. **Session Management**:
   - After successful login, the session will be saved to `session.json`
   - The program will prioritize using the saved session on next run
   - To re-login, delete the `session.json` file

4. **Daily Check-in**:
   - The program will automatically perform check-in after login
   - Check-in will display current points and user status
   - Recommended to use with scheduled tasks (e.g., cron) for automatic daily execution

5. **Verification Code Wait Time**:
   - Default wait time is 60 seconds to receive the verification code
   - Checks email every 2 seconds

## Scheduled Tasks

### Linux (crontab)

```bash
# Edit crontab
crontab -e

# Add daily check-in at 9 AM
0 9 * * * cd /path/to/auto-checkin && /path/to/anaconda3/envs/glados-checkin/bin/python glados_checkin.py >> checkin.log 2>&1
```

### Windows (Task Scheduler)

1. Open "Task Scheduler"
2. Create Basic Task
3. Set trigger (daily fixed time)
4. Set action: Run `python3 glados_checkin.py`
5. Set starting directory to project path

## Current Implementation

Implemented features:
- ✅ Send verification code
- ✅ Read Gmail verification code
- ✅ Login functionality
- ✅ Session management
- ✅ Daily check-in
- ✅ Proxy support

Optional enhancements:
- Scheduled task execution (using cron or Windows Task Scheduler)
- Logging
- Email notification of check-in results
- Multi-account support

## Troubleshooting

### Issue: Cannot connect to Gmail

**Solutions**:
1. Confirm IMAP is enabled: https://mail.google.com/mail/u/0/#settings/fwdandpop
2. Confirm you're using App Specific Password, not account password
3. If proxy is needed, configure proxy settings in `config.yaml`
4. Check firewall settings

### Issue: Verification code not received

**Solutions**:
1. Check spam folder
2. Confirm email address is correct
3. Wait longer (default is 60 seconds)

### Issue: Login failed

**Solutions**:
1. Confirm verification code is correct (Note: The program selects the verification code from the newest email)
2. Check network connection
3. Check error messages for details

### Issue: Check-in failed

**Solutions**:
1. Confirm session is valid (delete `session.json` to re-login)
2. Check network connection
3. Check error messages for details

## License

This project is open source and available under the MIT License.

## Contributing

Contributions, issues, and feature requests are welcome!

## Acknowledgments

- GLaDOS VPN service
- Gmail IMAP service

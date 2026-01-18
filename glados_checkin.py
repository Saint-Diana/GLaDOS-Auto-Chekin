#!/usr/bin/env python3
"""
GLaDOS Auto Check-in Script
Automates login and check-in process for GLaDOS VPN service
"""

import imaplib
import email
import re
import json
import time
import yaml
import socket
from pathlib import Path
from typing import Optional, Dict, Any
import requests


class Config:
    """Configuration manager"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def get(self, *keys, default=None):
        """Get nested config value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value


def create_imap_ssl_connection(host, port, socks5_proxy=None):
    """
    Create IMAP4_SSL connection with optional SOCKS5 proxy support.

    Args:
        host: IMAP server hostname
        port: IMAP server port
        socks5_proxy: Tuple of (socks5_host, socks5_port) or None

    Returns:
        imaplib.IMAP4_SSL instance
    """
    if socks5_proxy:
        import socks
        import ssl

        socks5_host, socks5_port = socks5_proxy

        class IMAP4SSLProxy(imaplib.IMAP4_SSL):
            """IMAP4_SSL with SOCKS5 proxy support"""

            def __init__(self, imap_host, imap_port, proxy_host, proxy_port):
                self._proxy_host = proxy_host
                self._proxy_port = proxy_port
                super().__init__(imap_host, imap_port)

            def _create_socket(self, timeout=None):
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, self._proxy_host,
                               self._proxy_port)
                sock.settimeout(timeout if timeout is not None else 10)
                sock.connect((self.host, self.port))

                context = ssl.create_default_context()
                return context.wrap_socket(sock, server_hostname=self.host)

        return IMAP4SSLProxy(host, port, socks5_host, socks5_port)
    else:
        return imaplib.IMAP4_SSL(host, port)


class GmailReader:
    """Gmail verification code reader"""

    def __init__(self, email_address: str, password: str, config: Config = None):
        self.email_address = email_address
        self.password = password
        self.config = config
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def connect(self):
        """Connect to Gmail IMAP server"""
        try:
            # Check if SOCKS5 proxy is configured
            socks5_host = self.config.get(
                'proxy', 'socks5_host', default='') if self.config else ''
            socks5_port = self.config.get(
                'proxy', 'socks5_port', default=None) if self.config else None

            if socks5_host and socks5_port:
                # Use SOCKS5 proxy
                print(f"  Using SOCKS5 proxy: {socks5_host}:{socks5_port}")
                mail = create_imap_ssl_connection(
                    self.imap_server,
                    self.imap_port,
                    socks5_proxy=(socks5_host, socks5_port)
                )
                mail.login(self.email_address, self.password)
                return mail
            else:
                # Direct connection without proxy
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
                mail.login(self.email_address, self.password)
                return mail
        except ImportError:
            raise Exception(
                "PySocks library not installed. Install it with: pip install pysocks")
        except Exception as e:
            raise Exception(f"Failed to connect to Gmail: {e}")

    def get_verification_code(self, wait_time: int = 60) -> Optional[str]:
        """
        Get verification code from GLaDOS email

        Args:
            wait_time: Maximum time to wait for email in seconds

        Returns:
            Verification code or None if not found
        """
        mail = self.connect()
        mail.select('INBOX')

        start_time = time.time()
        code = None

        # Search emails from today
        from datetime import datetime, timedelta
        date_str = datetime.now().strftime("%d-%b-%Y")

        while time.time() - start_time < wait_time and not code:
            # Search for all emails from GLaDOS (including seen and unseen)
            search_attempts = [
                f'(FROM "support@glados.network" SINCE {date_str})',
                f'(FROM "support@gladns.com" SINCE {date_str})',
            ]

            for search_criteria in search_attempts:
                status, messages = mail.search(None, search_criteria)

                if status == 'OK' and messages[0]:
                    # Get email IDs
                    email_ids = messages[0].split()
                    print(
                        f"  Found {len(email_ids)} emails for: {search_criteria}")

                    if email_ids:
                        # Find the newest email by checking dates
                        newest_email_id = None
                        newest_timestamp = 0

                        for email_id in email_ids:
                            # Fetch email headers only
                            status, msg_data = mail.fetch(
                                email_id, '(RFC822.HEADER)')
                            if status == 'OK':
                                raw_header = msg_data[0][1]
                                msg = email.message_from_bytes(raw_header)
                                email_date = email.utils.parsedate_tz(
                                    msg['Date'])

                                if email_date:
                                    from email.utils import mktime_tz
                                    timestamp = mktime_tz(email_date)
                                    if timestamp > newest_timestamp:
                                        newest_timestamp = timestamp
                                        newest_email_id = email_id

                        if newest_email_id:
                            print(
                                f"  Processing newest email: {newest_email_id}")

                            # Fetch the newest email
                            status, msg_data = mail.fetch(
                                newest_email_id, '(RFC822)')
                            if status == 'OK':
                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)

                                # Get email body
                                email_body = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/plain":
                                            email_body = part.get_payload(
                                                decode=True).decode('utf-8', errors='ignore')
                                            break
                                else:
                                    email_body = msg.get_payload(
                                        decode=True).decode('utf-8', errors='ignore')

                                # Extract verification code using multiple patterns
                                # Support two email formats (code length varies):
                                # 1. support@glados.network: *37188* (digits in asterisks)
                                # 2. support@gladns.com: Your code is 64207 (digits after text)
                                patterns = [
                                    # Format 1: Code wrapped in asterisks: *12345*
                                    r'\*(\d+)\*',
                                    # Format 1: Alternative format
                                    r'\*[^*]*\*(\d+)\*',
                                    # Format 2: "Your code is 12345"
                                    r'Your code is\s+(\d+)',
                                    # Format 2: Alternative phrasing
                                    r'code is\s+(\d+)',
                                    # Format 1: Code with asterisks between newlines
                                    r'\n\s*\*(\d+)\*\s*\n',
                                    # Fallback: digits between newlines
                                    r'\n\s*(\d+)\s*\n',
                                ]

                                for pattern in patterns:
                                    match = re.search(
                                        pattern, email_body, re.MULTILINE | re.IGNORECASE)
                                    if match:
                                        code = match.group(1)
                                        print(
                                            f"✓ Verification code found: {code}")
                                        break

                                if code:
                                    break
                                else:
                                    # Debug: print email body if no code found
                                    print(
                                        f"  Email body preview:\n{email_body[:400]}...")

                if code:
                    break

            # Wait before checking again
            if not code:
                time.sleep(2)

        mail.close()
        mail.logout()

        if not code:
            print("✗ Verification code not found in emails")

        return code


class GLaDOSClient:
    """GLaDOS API client"""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('glados', 'base_url')
        self.login_url = config.get('glados', 'login_url')
        self.auth_url = config.get('glados', 'auth_url')
        self.site = config.get('glados', 'site')
        self.email = config.get('email', 'address')

        # Initialize session
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6',
            'content-type': 'application/json',
            'origin': self.base_url,
            'referer': f'{self.base_url}/login',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        })

    def send_verification_code(self) -> bool:
        """
        Request verification code via email

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "address": self.email,
                "site": self.site
            }

            response = self.session.post(
                self.auth_url,
                json=payload,
                headers={
                    'authorization': '79954281403036535521505806358572-1440-2560'}
            )

            if response.status_code == 200:
                print(f"✓ Verification code sent to {self.email}")
                return True
            else:
                print(
                    f"✗ Failed to send verification code: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error sending verification code: {e}")
            return False

    def login(self, verification_code: str) -> bool:
        """
        Login with verification code

        Args:
            verification_code: 6-digit verification code from email

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "method": "email",
                "site": self.site,
                "email": self.email,
                "mailcode": verification_code
            }

            response = self.session.post(
                self.login_url,
                json=payload,
                headers={
                    'authorization': '79954281403036535521505806358572-1440-2560'}
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Login successful")
                return True
            else:
                print(f"✗ Login failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error during login: {e}")
            return False

    def save_session(self, session_path: str = "session.json") -> bool:
        """
        Save session cookies to file

        Args:
            session_path: Path to save session file

        Returns:
            True if successful, False otherwise
        """
        try:
            session_data = {
                'cookies': requests.utils.dict_from_cookiejar(self.session.cookies)
            }

            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Session saved to {session_path}")
            return True

        except Exception as e:
            print(f"✗ Error saving session: {e}")
            return False

    def load_session(self, session_path: str = "session.json") -> bool:
        """
        Load session cookies from file

        Args:
            session_path: Path to session file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not Path(session_path).exists():
                print(f"✗ Session file not found: {session_path}")
                return False

            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            self.session.cookies = requests.utils.cookiejar_from_dict(
                session_data['cookies'])
            print(f"✓ Session loaded from {session_path}")
            return True

        except Exception as e:
            print(f"✗ Error loading session: {e}")
            return False

    def checkin(self) -> bool:
        """
        Perform daily check-in

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get checkin URL from base_url
            checkin_url = f"{self.base_url}/api/user/checkin"
            points_url = f"{self.base_url}/api/user/points"
            status_url = f"{self.base_url}/api/user/status"

            # Optional: Get current points
            try:
                response = self.session.get(points_url)
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Current points: {data}")
            except:
                pass

            # Perform check-in
            payload = {"token": "glados.cloud"}
            response = self.session.post(
                checkin_url,
                json=payload,
                headers={'content-type': 'application/json;charset=UTF-8'}
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Check-in successful")
                print(f"  Response: {data}")

                # Optional: Get user status after check-in
                try:
                    response = self.session.get(status_url)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  User status: {data}")
                except:
                    pass

                return True
            else:
                print(f"✗ Check-in failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error during check-in: {e}")
            return False


def main():
    """Main function"""
    print("=" * 50)
    print("GLaDOS Auto Check-in")
    print("=" * 50)

    # Load configuration
    try:
        config = Config("config.yaml")
    except FileNotFoundError:
        print("✗ config.yaml not found. Please create it first.")
        return
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return

    # Check email password
    email_password = config.get('email', 'password')
    if not email_password:
        print("✗ Email password not set in config.yaml")
        print("  Please set your Gmail App Password:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Create an App Password")
        print("  3. Add it to config.yaml under email.password")
        return

    # Initialize clients
    glados = GLaDOSClient(config)
    gmail_reader = GmailReader(
        config.get('email', 'address'),
        config.get('email', 'password'),
        config=config
    )

    # Try to load existing session
    session_path = config.get('session', 'save_path', default='session.json')
    session_loaded = glados.load_session(session_path)

    if session_loaded:
        print("✓ Using existing session (skip login)")
    else:
        print("\nStep 1: Requesting verification code...")
        if not glados.send_verification_code():
            print("✗ Failed to send verification code")
            return

        print("\nStep 2: Waiting for verification code...")
        print("  (Check your Gmail inbox)")
        verification_code = gmail_reader.get_verification_code(wait_time=60)

        if not verification_code:
            print("✗ No verification code received")
            return

        print(f"\nStep 3: Logging in with code: {verification_code}...")
        if not glados.login(verification_code):
            print("\n✗ Login failed")
            return

        # Save session for future use
        glados.save_session(session_path)
        print("\n✓ Login process completed successfully!")

    # Perform check-in (whether using existing session or new login)
    print("\nStep 4: Performing daily check-in...")
    if glados.checkin():
        print("\n✓ All tasks completed successfully!")
    else:
        print("\n✗ Check-in failed (but login was successful)")


if __name__ == "__main__":
    main()

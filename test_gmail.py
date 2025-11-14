"""
Simple Gmail connection test script for debugging
"""

import imaplib
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
GMAIL_EMAIL = "phamtuan2xx3@gmail.com"
GMAIL_APP_PASSWORD = "elxkvsccnufclkfb"  # App password (16 characters)

print("=" * 60)
print("Gmail Connection Debug Test")
print("=" * 60)
print(f"Email: {GMAIL_EMAIL}")
print(f"App Password length: {len(GMAIL_APP_PASSWORD)} characters")
print(f"App Password (first 4 chars): {GMAIL_APP_PASSWORD[:4]}****")
print(f"App Password contains spaces: {' ' in GMAIL_APP_PASSWORD}")
if len(GMAIL_APP_PASSWORD) != 16:
    print(f"\n[WARNING] App password should be 16 characters, but got {len(GMAIL_APP_PASSWORD)}!")
    print("Gmail App Passwords are always 16 characters (without spaces).")
    print("Please check your app password and make sure it's correct.")
print("=" * 60)

# Test 1: Basic connection
print("\n[Test 1] Testing IMAP connection...")
try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    print("[OK] IMAP connection established")
except Exception as e:
    print(f"[ERROR] IMAP connection failed: {e}")
    sys.exit(1)

# Test 2: Login
print("\n[Test 2] Testing login...")
try:
    print(f"Attempting to login with email: {GMAIL_EMAIL}")
    print(f"App password length: {len(GMAIL_APP_PASSWORD)}")
    
    # Try login
    result = mail.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
    print(f"[OK] Login successful: {result}")
    
    # Test 3: List mailboxes
    print("\n[Test 3] Listing mailboxes...")
    try:
        status, mailboxes = mail.list()
        if status == "OK":
            print(f"[OK] Found {len(mailboxes)} mailboxes")
            print("Mailboxes:")
            for mb in mailboxes[:5]:  # Show first 5
                print(f"  - {mb.decode('utf-8', errors='ignore')[:80]}")
        else:
            print(f"[ERROR] Failed to list mailboxes: {status}")
    except Exception as e:
        print(f"[ERROR] Error listing mailboxes: {e}")
    
    # Test 4: Select inbox
    print("\n[Test 4] Selecting inbox...")
    try:
        status, data = mail.select("inbox")
        if status == "OK":
            print(f"[OK] Inbox selected")
            print(f"  Messages: {data[0].decode('utf-8')}")
        else:
            print(f"[ERROR] Failed to select inbox: {status}")
    except Exception as e:
        print(f"[ERROR] Error selecting inbox: {e}")
    
    # Test 5: Search for emails
    print("\n[Test 5] Searching for emails...")
    try:
        status, messages = mail.search(None, 'ALL')
        if status == "OK":
            email_ids = messages[0].split()
            print(f"[OK] Found {len(email_ids)} total emails")
        else:
            print(f"[ERROR] Failed to search: {status}")
    except Exception as e:
        print(f"[ERROR] Error searching: {e}")
    
    # Test 6: Search for unread emails
    print("\n[Test 6] Searching for unread emails...")
    try:
        status, messages = mail.search(None, 'UNSEEN')
        if status == "OK" and messages[0]:
            unread_ids = messages[0].split()
            print(f"[OK] Found {len(unread_ids)} unread emails")
        else:
            print("[OK] No unread emails found")
    except Exception as e:
        print(f"[ERROR] Error searching unread: {e}")
    
    # Test 7: Search for MegaLLM emails
    print("\n[Test 7] Searching for MegaLLM emails...")
    try:
        status, messages = mail.search(None, '(FROM "megallm.io")')
        if status == "OK" and messages[0]:
            megallm_ids = messages[0].split()
            print(f"[OK] Found {len(megallm_ids)} emails from megallm.io")
        else:
            print("[OK] No emails from megallm.io found")
    except Exception as e:
        print(f"[ERROR] Error searching MegaLLM: {e}")
    
    # Close connection
    print("\n[Cleanup] Closing connection...")
    try:
        mail.close()
        mail.logout()
        print("[OK] Connection closed")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    
except imaplib.IMAP4.error as e:
    print(f"\n[ERROR] Login failed with IMAP error: {e}")
    print("\nPossible issues:")
    print("1. App password is incorrect or expired")
    print("2. 2-Step Verification is not enabled")
    print("3. IMAP is not enabled in Gmail settings")
    print("4. Account is locked or requires additional verification")
    print("\nSolution:")
    print("1. Go to https://myaccount.google.com/apppasswords")
    print("2. Create a new App Password for 'Mail'")
    print("3. Copy the 16-character password (no spaces)")
    print("4. Update GMAIL_APP_PASSWORD in gmail_reader.py")
    sys.exit(1)
    
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


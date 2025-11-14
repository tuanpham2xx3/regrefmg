"""
Gmail Reader Module
Đọc mã xác minh từ Gmail
Có thể chạy độc lập để test: python gmail_reader.py
"""

import time
import re
import imaplib
import email
import sys
from email.header import decode_header
from email.utils import parsedate_to_datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        import codecs
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

# Configuration - có thể thay đổi hoặc import từ file config
GMAIL_EMAIL = "phamtuan2xx3@gmail.com"
GMAIL_APP_PASSWORD = "elxkvsccnufclkfb"  # App password without spaces (16 characters)

def connect_gmail(email_addr=None, app_password=None):
    """Kết nối đến Gmail IMAP server"""
    if email_addr is None:
        email_addr = GMAIL_EMAIL
    if app_password is None:
        app_password = GMAIL_APP_PASSWORD
    
    try:
        print(f"Connecting to Gmail: {email_addr}")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_addr, app_password)
        print("Connected successfully!")
        return mail
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        print(f"IMAP authentication error: {error_msg}")
        print("\nTroubleshooting:")
        print("1. Check if email and app password are correct")
        print("2. Make sure 2-Step Verification is enabled in Google Account")
        print("3. Create a new App Password: https://myaccount.google.com/apppasswords")
        print("4. Make sure IMAP is enabled in Gmail settings")
        print("5. App password should be 16 characters without spaces")
        raise
    except Exception as e:
        print(f"Error connecting to Gmail: {e}")
        raise

def search_verification_emails(mail, search_patterns=None):
    """Tìm email xác minh từ MegaLLM"""
    if search_patterns is None:
        search_patterns = [
            '(UNSEEN FROM "megallm.io")',
            '(UNSEEN FROM "megallm")',
            '(UNSEEN FROM "noreply@megallm.io")',
            '(FROM "megallm.io" SUBJECT "verification")',
            '(FROM "megallm.io" SUBJECT "code")',
            '(FROM "megallm.io")',
            '(FROM "megallm")',
        ]
    
    mail.select("inbox")
    email_ids = None
    
    for pattern in search_patterns:
        try:
            status, messages = mail.search(None, pattern)
            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                if email_ids:
                    print(f"Found {len(email_ids)} email(s) with pattern: {pattern}")
                    return email_ids
        except Exception as e:
            print(f"Error with search pattern {pattern}: {e}")
            continue
    
    # If no emails found with specific patterns, search for recent unread emails
    if not email_ids:
        try:
            status, messages = mail.search(None, 'UNSEEN')
            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                print(f"Found {len(email_ids)} unread email(s)")
                return email_ids
        except Exception as e:
            print(f"Error searching for unread emails: {e}")
    
    return []

def extract_verification_code(email_message):
    """Trích xuất mã xác minh 6 chữ số từ email"""
    # Decode subject
    subject = ""
    try:
        subject_header = decode_header(email_message["Subject"])
        if subject_header and len(subject_header) > 0:
            if subject_header[0][1]:
                subject = subject_header[0][0].decode(subject_header[0][1])
            else:
                subject = subject_header[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode('utf-8', errors='ignore')
    except:
        try:
            subject = str(email_message["Subject"])
        except:
            pass
    
    # Get email content
    body = ""
    body_html = ""
    
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    if content_type == "text/plain":
                        body = payload.decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        body_html = payload.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Error decoding part: {e}")
                try:
                    # Try different encodings
                    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                        try:
                            if content_type == "text/plain":
                                body = payload.decode(encoding)
                            elif content_type == "text/html":
                                body_html = payload.decode(encoding)
                            break
                        except:
                            continue
                except:
                    pass
    else:
        try:
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        except:
            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    try:
                        body = payload.decode(encoding)
                        break
                    except:
                        continue
            except:
                pass
    
    # Use HTML body if plain text is empty
    if not body and body_html:
        body = re.sub(r'<[^>]+>', ' ', body_html)
    
    # Combine subject and body for code extraction
    full_text = f"{subject} {body}"
    
    # Search in HTML directly for codes in specific tags
    if body_html:
        html_text = re.sub(r'<[^>]+>', ' ', body_html)
        full_text = f"{full_text} {html_text}"
        
        # Look for codes in HTML tags
        html_code_patterns = [
            r'<[^>]*>(\d{6})<[^>]*>',
            r'<strong[^>]*>(\d{6})</strong>',
            r'<b[^>]*>(\d{6})</b>',
            r'<span[^>]*>(\d{6})</span>',
            r'font-size[^>]*>(\d{6})<',
        ]
        for pattern in html_code_patterns:
            matches = re.findall(pattern, body_html, re.IGNORECASE)
            if matches:
                code = re.sub(r'[\s\-]', '', str(matches[0]))
                if len(code) == 6 and code.isdigit():
                    return code
    
    # Extract 6-digit verification code from text
    code_patterns = [
        r'code[:\s\-]*(\d{6})',
        r'verification[:\s\-]*(\d{6})',
        r'verify[:\s\-]*(\d{6})',
        r'OTP[:\s\-]*(\d{6})',
        r'pin[:\s\-]*(\d{6})',
        r'(\d{3}[\s\-]?\d{3})',
        r'\b(\d{6})\b',
    ]
    
    found_codes = []
    for pattern in code_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            for match in matches:
                clean_code = re.sub(r'[\s\-]', '', str(match))
                if len(clean_code) == 6 and clean_code.isdigit():
                    found_codes.append(clean_code)
    
    if found_codes:
        return found_codes[0]
    
    return None

def get_verification_code_from_gmail(email_addr=None, app_password=None, max_emails=50, target_email=None, after_time=None, used_email_ids=None, used_email_lock=None):
    """
    Kết nối đến Gmail và lấy mã xác minh mới nhất
    
    Args:
        email_addr: Email Gmail (mặc định dùng GMAIL_EMAIL)
        app_password: App password (mặc định dùng GMAIL_APP_PASSWORD)
        max_emails: Số lượng email tối đa để kiểm tra (mặc định 50)
        target_email: Email đích để lọc (nếu None thì lấy email mới nhất)
        after_time: datetime object - chỉ tìm email sau thời điểm này (None = không filter)
        used_email_ids: set - Set các email ID đã được sử dụng (thread-safe)
        used_email_lock: threading.Lock - Lock cho used_email_ids
    
    Returns:
        Mã xác minh 6 chữ số hoặc None nếu không tìm thấy
    """
    mail = None
    try:
        # Connect to Gmail
        mail = connect_gmail(email_addr, app_password)
        mail.select("inbox")
        
        # Search for verification emails
        email_ids = search_verification_emails(mail)
        
        if not email_ids:
            print("No emails found")
            return None
        
        # Sort email IDs (newest first)
        email_ids_sorted = list(reversed(email_ids))[:max_emails]
        
        print(f"Processing {len(email_ids_sorted)} email(s), checking from newest to oldest...")
        
        # Process emails from newest to oldest
        for email_id in email_ids_sorted:
            try:
                # Check if email already used (thread-safe)
                if used_email_ids is not None and used_email_lock is not None:
                    email_id_str = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
                    with used_email_lock:
                        if email_id_str in used_email_ids:
                            print(f"Skipping email {email_id_str} - already used by another thread")
                            continue
                
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                # Parse email
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Decode subject, sender, and recipient
                subject = ""
                sender = ""
                recipient = ""
                try:
                    subject_header = decode_header(email_message["Subject"])
                    if subject_header and len(subject_header) > 0:
                        if subject_header[0][1]:
                            subject = subject_header[0][0].decode(subject_header[0][1])
                        else:
                            subject = subject_header[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode('utf-8', errors='ignore')
                except:
                    try:
                        subject = str(email_message["Subject"])
                    except:
                        pass
                
                try:
                    sender_header = decode_header(email_message["From"])
                    if sender_header and len(sender_header) > 0:
                        if sender_header[0][1]:
                            sender = sender_header[0][0].decode(sender_header[0][1])
                        else:
                            sender = sender_header[0][0]
                        if isinstance(sender, bytes):
                            sender = sender.decode('utf-8', errors='ignore')
                except:
                    try:
                        sender = str(email_message["From"])
                    except:
                        pass
                
                # Extract recipient email (To field)
                try:
                    recipient_header = decode_header(email_message["To"])
                    if recipient_header and len(recipient_header) > 0:
                        if recipient_header[0][1]:
                            recipient = recipient_header[0][0].decode(recipient_header[0][1])
                        else:
                            recipient = recipient_header[0][0]
                        if isinstance(recipient, bytes):
                            recipient = recipient.decode('utf-8', errors='ignore')
                except:
                    try:
                        recipient = str(email_message["To"])
                    except:
                        pass
                
                # Extract email address from recipient field (may contain name <email>)
                recipient_email = ""
                if recipient:
                    # Try to extract email from format like "Name <email@domain.com>" or just "email@domain.com"
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', recipient.lower())
                    if email_match:
                        recipient_email = email_match.group(0)
                
                # Check if email is from MegaLLM
                is_megallm = False
                if sender:
                    sender_lower = sender.lower()
                    if 'megallm' in sender_lower or 'megallm.io' in sender_lower:
                        is_megallm = True
                
                # Filter by time if provided (only get emails after submit_time)
                if after_time:
                    try:
                        email_date_str = email_message["Date"]
                        if email_date_str:
                            email_date = parsedate_to_datetime(email_date_str)
                            if email_date < after_time:
                                print(f"Skipping email - too old (email date: {email_date}, after_time: {after_time})")
                                continue
                    except Exception as e:
                        print(f"Warning: Could not parse email date: {e}, continuing anyway")
                        # Continue anyway if can't parse date
                
                print(f"Checking email - From: {sender[:50] if sender else 'Unknown'}, To: {recipient_email[:50] if recipient_email else 'Unknown'}, Subject: {subject[:50] if subject else 'Unknown'}")
                
                # Skip if not from MegaLLM (unless we couldn't determine sender)
                if sender and not is_megallm:
                    print(f"Skipping email - not from MegaLLM")
                    continue
                
                # If target_email is specified, check if this email matches
                if target_email:
                    target_email_lower = target_email.lower().strip()
                    if recipient_email and recipient_email != target_email_lower:
                        print(f"Skipping email - recipient {recipient_email} does not match target {target_email_lower}")
                        continue
                    elif not recipient_email:
                        print(f"Warning: Could not extract recipient email, skipping for safety")
                        continue
                
                # Extract verification code
                code = extract_verification_code(email_message)
                
                if code:
                    # Mark email as used (thread-safe)
                    if used_email_ids is not None and used_email_lock is not None:
                        email_id_str = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
                        with used_email_lock:
                            used_email_ids.add(email_id_str)
                    
                    print(f"Found verification code: {code} for email: {recipient_email if recipient_email else 'Unknown'}")
                    # Mark email as read (optional)
                    try:
                        mail.store(email_id, '+FLAGS', '\\Seen')
                    except:
                        pass
                    return code
                else:
                    print(f"No verification code found in this email")
                
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")
                continue
        
        print("No verification code found in emails")
        return None
            
    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}")
        return None
    except Exception as e:
        print(f"Error retrieving email: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if mail:
            try:
                mail.close()
                mail.logout()
                print("Disconnected from Gmail")
            except:
                pass

def test_gmail_connection():
    """Test kết nối Gmail"""
    print("=" * 60)
    print("Testing Gmail Connection")
    print("=" * 60)
    
    try:
        mail = connect_gmail()
        mail.select("inbox")
        
        # Get mailbox status
        status, messages = mail.search(None, 'ALL')
        if status == "OK":
            email_ids = messages[0].split()
            print(f"Total emails in inbox: {len(email_ids)}")
        
        # Count unread emails
        status, messages = mail.search(None, 'UNSEEN')
        if status == "OK" and messages[0]:
            unread_ids = messages[0].split()
            print(f"Unread emails: {len(unread_ids)}")
        else:
            print("Unread emails: 0")
        
        mail.close()
        mail.logout()
        print("\nConnection test successful!")
        return True
        
    except Exception as e:
        print(f"\nConnection test failed: {e}")
        return False

def test_verification_code_retrieval():
    """Test lấy mã xác minh"""
    print("=" * 60)
    print("Testing Verification Code Retrieval")
    print("=" * 60)
    
    code = get_verification_code_from_gmail()
    
    if code:
        print(f"\n✓ Success! Verification code: {code}")
        return code
    else:
        print("\n✗ No verification code found")
        return None

if __name__ == "__main__":
    """Chạy test khi chạy file trực tiếp"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test" or command == "connection":
            # Test kết nối
            test_gmail_connection()
        elif command == "code" or command == "get":
            # Test lấy mã
            test_verification_code_retrieval()
        else:
            print("Usage:")
            print("  python gmail_reader.py test    - Test Gmail connection")
            print("  python gmail_reader.py code    - Get verification code")
    else:
        # Chạy cả hai test
        print("Running all tests...\n")
        test_gmail_connection()
        print("\n")
        test_verification_code_retrieval()


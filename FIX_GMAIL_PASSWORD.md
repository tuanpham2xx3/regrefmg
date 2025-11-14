# Fix Gmail App Password Issue

## Problem
App password chỉ có **15 ký tự**, nhưng Gmail App Password phải có đúng **16 ký tự**.

Current password: `elxkvsccnufclkf` (15 characters) ❌

## Solution

### Bước 1: Tạo App Password mới

1. Truy cập: https://myaccount.google.com/apppasswords
2. Đăng nhập bằng tài khoản Google của bạn
3. Nếu chưa bật 2-Step Verification, bạn cần bật trước:
   - Vào: https://myaccount.google.com/security
   - Bật "2-Step Verification"
4. Tạo App Password mới:
   - Chọn "Mail" làm app
   - Chọn "Other (Custom name)" nếu không có tùy chọn Mail
   - Đặt tên: "Gmail Reader" hoặc bất kỳ tên nào
   - Click "Generate"
5. **Copy password 16 ký tự** (không có khoảng trắng)
   - Password sẽ hiển thị dạng: `xxxx xxxx xxxx xxxx`
   - Copy và **bỏ hết khoảng trắng**: `xxxxxxxxxxxxxxxx`

### Bước 2: Cập nhật password trong code

Cập nhật password trong 2 files:

1. **gmail_reader.py** (dòng 27):
   ```python
   GMAIL_APP_PASSWORD = "your-16-character-password-here"
   ```

2. **test_gmail.py** (dòng 16):
   ```python
   GMAIL_APP_PASSWORD = "your-16-character-password-here"
   ```

### Bước 3: Test lại

```powershell
# Test connection
python test_gmail.py

# Test Gmail reader
python gmail_reader.py test

# Test get verification code
python gmail_reader.py code
```

## Lưu ý

- App Password phải đúng **16 ký tự** (không có khoảng trắng)
- App Password chỉ hiển thị 1 lần khi tạo, nên copy ngay
- Nếu quên, phải tạo App Password mới
- App Password không phải là mật khẩu Gmail thông thường

## Troubleshooting

### Lỗi: "Invalid credentials"
- Kiểm tra lại App Password có đúng 16 ký tự không
- Đảm bảo đã bật 2-Step Verification
- Tạo App Password mới và thử lại

### Lỗi: "IMAP is not enabled"
- Vào Gmail Settings > Forwarding and POP/IMAP
- Bật "Enable IMAP"
- Lưu changes

### Lỗi: "Less secure app access"
- Google không còn hỗ trợ "Less secure app access"
- Phải dùng App Password thay vì mật khẩu thông thường


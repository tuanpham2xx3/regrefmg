"""
Script test proxy đơn giản
Kiểm tra xem proxy có hoạt động không
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Proxy test - HTTP proxy không có authentication
# HTTP format: http://host:port (không có auth)
# SOCKS5 format: socks5://username:password@host:port
PROXY_HTTP = "http://172.30.16.1:10000"  # HTTP proxy không có auth
PROXY_SOCKS5 = "socks5://tuan12345:tuan12345@166.0.152.10:17773"  # SOCKS5 proxy cũ
PROXY = PROXY_HTTP  # Dùng HTTP proxy không có auth
TEST_URL = "https://httpbin.org/ip"  # Website để kiểm tra IP

def test_proxy():
    """Test proxy connection"""
    print("=" * 60)
    print("Testing Proxy Connection")
    print("=" * 60)
    print(f"Proxy: {PROXY.split('@')[-1] if '@' in PROXY else PROXY}")
    print(f"Test URL: {TEST_URL}")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--proxy-server={PROXY}")
    
    # Thêm options để hỗ trợ proxy tốt hơn
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Options đặc biệt cho SOCKS5
    if PROXY.startswith("socks5://"):
        print("   Using SOCKS5 proxy configuration")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    else:
        print("   Using HTTP proxy configuration")
    
    driver = None
    try:
        print("\n1. Initializing Chrome with proxy...")
        driver = webdriver.Chrome(options=chrome_options)
        print("   ✓ Chrome initialized")
        
        print("\n2. Navigating to test URL...")
        driver.get(TEST_URL)
        print("   ✓ Page loaded")
        
        # Wait a bit for page to load
        time.sleep(3)
        
        print("\n3. Checking IP address...")
        # Try to get IP from page
        try:
            wait = WebDriverWait(driver, 10)
            # httpbin.org/ip returns JSON with "origin" field
            body = driver.find_element(By.TAG_NAME, "body")
            page_text = body.text
            print(f"   Page content: {page_text[:200]}")
            
            # Extract IP if possible
            if "origin" in page_text.lower() or "ip" in page_text.lower():
                print("   ✓ IP check page loaded successfully")
        except Exception as e:
            print(f"   ⚠ Could not read IP from page: {e}")
        
        print("\n4. Testing navigation to registration page...")
        driver.get("https://megallm.io/ref/REF-3DXXZJS8")
        time.sleep(5)
        print(f"   ✓ Registration page loaded: {driver.current_url}")
        
        print("\n" + "=" * 60)
        print("✓ Proxy test completed successfully!")
        print("=" * 60)
        print("\nProxy appears to be working. You can now use it in main.py")
        
        # Keep browser open for a few seconds to verify
        print("\nKeeping browser open for 10 seconds for manual verification...")
        time.sleep(10)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Proxy test failed!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nPossible issues với SOCKS5 proxy:")
        print("1. Proxy server is down or unreachable")
        print("2. Proxy credentials are incorrect (tuan12345:tuan12345)")
        print("3. Network/firewall blocking SOCKS5 connection")
        print("4. Chrome version không hỗ trợ SOCKS5 authentication tốt")
        print("5. Proxy server không hỗ trợ SOCKS5 authentication")
        print("\nThử các giải pháp:")
        print("- Kiểm tra proxy server có hoạt động: telnet 166.0.152.10 17773")
        print("- Kiểm tra username/password có đúng không")
        print("- Thử test proxy bằng tool khác (như curl) để xác nhận proxy hoạt động")
        print("- Kiểm tra firewall/antivirus có chặn không")
        
    finally:
        if driver:
            try:
                print("\nClosing browser...")
                driver.quit()
                print("Browser closed")
            except:
                pass

if __name__ == "__main__":
    test_proxy()


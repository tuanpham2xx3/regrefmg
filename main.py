import time
import random
import string
import os
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from gmail_reader import get_verification_code_from_gmail, GMAIL_EMAIL, GMAIL_APP_PASSWORD

# Configuration
REGISTRATION_URL = "https://megallm.io/ref/REF-3DXXZJS8"
# GMAIL_EMAIL and GMAIL_APP_PASSWORD are imported from gmail_reader.py
PASSWORD = "Tuan@2003"
REFERRAL_CODE = "REF-JXKY9D8W"
NUM_THREADS = 5  # Số luồng chạy đồng thời (có thể chỉnh sửa) - Khuyến nghị bằng số proxy

# Proxy configuration
# Format hỗ trợ:
#   - HTTP: "http://host:port" (không có auth)
#   - HTTP với auth: "http://username:password@host:port" 
#   - SOCKS5: "socks5://username:password@host:port" hoặc "socks5://host:port"
# Để trống nếu không dùng proxy: PROXY_LIST = []
PROXY_LIST = [
    "http://172.30.16.1:10000",  # Proxy 1
    "http://172.30.16.1:10001",  # Proxy 2
    "http://172.30.16.1:10002",  # Proxy 3
    "http://172.30.16.1:10003",  # Proxy 4
    "http://172.30.16.1:10004",  # Proxy 5
]
USE_PROXY = len(PROXY_LIST) > 0  # Tự động bật nếu có proxy trong list

# Thread-safe proxy manager - mỗi thread có proxy riêng cố định
thread_proxy_map = {}  # Map thread name -> proxy
proxy_map_lock = threading.Lock()

def get_proxy_for_thread(thread_name=None):
    """
    Lấy proxy cố định cho thread - mỗi thread chỉ dùng 1 proxy
    Args:
        thread_name: Tên thread (nếu None thì dùng current thread name)
    Returns:
        Proxy string hoặc None
    """
    if not USE_PROXY or not PROXY_LIST:
        return None
    
    if thread_name is None:
        thread_name = threading.current_thread().name
    
    # Kiểm tra xem thread đã có proxy chưa
    with proxy_map_lock:
        if thread_name in thread_proxy_map:
            # Thread đã có proxy, trả về proxy đó
            return thread_proxy_map[thread_name]
        
        # Gán proxy mới cho thread dựa trên số lượng thread đã có proxy
        proxy_index = len(thread_proxy_map) % len(PROXY_LIST)
        proxy = PROXY_LIST[proxy_index]
        thread_proxy_map[thread_name] = proxy
        print(f"[Proxy Manager] Gán proxy cho thread '{thread_name}': {proxy}")
        return proxy

def generate_random_name(length=8):
    """Generate a random name with letters"""
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_email():
    """Generate random 10-character email prefix"""
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{random_chars}@iceteadev.site"

def slow_type(element, text, min_delay=0.05, max_delay=0.3):
    """Type text slowly, character by character, with random delays"""
    element.clear()
    time.sleep(random.uniform(0.1, 0.3))  # Wait before starting to type
    
    for char in text:
        element.send_keys(char)
        # Random delay between characters (simulate human typing)
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    # Small delay after finishing typing
    time.sleep(random.uniform(0.1, 0.2))

def get_random_user_agent():
    """Get a random Chrome user agent"""
    chrome_versions = [
        "120.0.0.0", "121.0.0.0", "122.0.0.0", "123.0.0.0", "124.0.0.0",
        "125.0.0.0", "126.0.0.0", "127.0.0.0", "128.0.0.0", "129.0.0.0",
        "130.0.0.0", "131.0.0.0", "132.0.0.0", "133.0.0.0", "134.0.0.0",
    ]
    
    chrome_version = random.choice(chrome_versions)
    webkit_version = "537.36"
    
    os_types = [
        ("Windows NT 10.0; Win64; x64", "Windows"),
        ("Windows NT 11.0; Win64; x64", "Windows"),
        ("X11; Linux x86_64", "Linux"),
        ("Macintosh; Intel Mac OS X 10_15_7", "MacOS"),
    ]
    
    os_string, os_name = random.choice(os_types)
    
    user_agent = f"Mozilla/5.0 ({os_string}) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"
    return user_agent

def get_random_viewport_size():
    """Get a random viewport size"""
    viewports = [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1280, 720),
        (1600, 900), (1024, 768), (1280, 1024), (2560, 1440), (1920, 1200),
    ]
    return random.choice(viewports)

def setup_fake_chrome_fingerprint(driver):
    """Setup fake Chrome fingerprint to avoid detection"""
    try:
        # Get random viewport size
        width, height = get_random_viewport_size()
        
        # Set viewport size
        driver.set_window_size(width, height)
        print(f"Viewport size: {width}x{height}")
        
        # Generate random values for fingerprint
        platform = random.choice(["Win32", "Linux x86_64", "MacIntel"])
        hardware_concurrency = random.choice([4, 8, 12, 16])
        device_memory = random.choice([4, 8, 16])
        effective_type = random.choice(["4g", "3g"])
        rtt = random.randint(50, 200)
        downlink = round(random.uniform(1.5, 10.0), 2)
        webgl_vendor = random.choice(["Intel Inc.", "Google Inc.", "ANGLE"])
        webgl_renderers = [
            "Intel Iris OpenGL Engine",
            "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Google, Vulkan 1.3.0, SwiftShader Device (Subzero) (0x0000C0DE), SwiftShader driver)"
        ]
        webgl_renderer = random.choice(webgl_renderers)
        # Escape quotes for JavaScript
        webgl_renderer_escaped = webgl_renderer.replace("'", "\\'").replace('"', '\\"')
        webgl_vendor_escaped = webgl_vendor.replace("'", "\\'").replace('"', '\\"')
        timezone_offset = random.choice([-420, -480, -540, -600, -660])
        
        # Execute JavaScript to override navigator properties
        script = f"""
        // Override navigator properties
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined
        }});
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [1, 2, 3, 4, 5]
        }});
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['en-US', 'en', 'vi-VN', 'vi']
        }});
        
        // Override platform
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{platform}'
        }});
        
        // Override hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {hardware_concurrency}
        }});
        
        // Override deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {device_memory}
        }});
        
        // Override connection
        Object.defineProperty(navigator, 'connection', {{
            get: () => ({{
                effectiveType: '{effective_type}',
                rtt: {rtt},
                downlink: {downlink}
            }})
        }});
        
        // Override Chrome object
        window.chrome = {{
            runtime: {{}}
        }};
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // Override WebGL
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{webgl_vendor_escaped}';
            }}
            if (parameter === 37446) {{
                return '{webgl_renderer_escaped}';
            }}
            return getParameter.call(this, parameter);
        }};
        
        // Override Canvas fingerprinting
        const toBlob = HTMLCanvasElement.prototype.toBlob;
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        
        // Add noise to canvas
        const noise = () => {{
            return Math.random() * 0.0001;
        }};
        
        HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {{
            const context = this.getContext('2d');
            if (context) {{
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] += noise();
                }}
                context.putImageData(imageData, 0, 0);
            }}
            return toBlob.call(this, callback, type, quality);
        }};
        
        HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
            const context = this.getContext('2d');
            if (context) {{
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] += noise();
                }}
                context.putImageData(imageData, 0, 0);
            }}
            return toDataURL.call(this, type, quality);
        }};
        
        // Override timezone
        Date.prototype.getTimezoneOffset = function() {{
            return {timezone_offset};
        }};
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script})
        print("Chrome fingerprint faked successfully")
        
    except Exception as e:
        print(f"Warning: Could not setup fake fingerprint: {e}")
        # Continue anyway

def setup_driver(proxy=None):
    """
    Setup Chrome driver with options and fake fingerprint
    
    Args:
        proxy: Proxy string in format "http://user:pass@host:port", "socks5://user:pass@host:port", or "http://host:port"
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment if you want headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-automation")
    chrome_options.add_argument("--disable-infobars")
    
    # Add proxy if provided
    if proxy:
        # SOCKS5 format: socks5://username:password@host:port
        # HTTP format: http://username:password@host:port
        chrome_options.add_argument(f"--proxy-server={proxy}")
        
        # Thêm các options để hỗ trợ proxy tốt hơn
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Options đặc biệt cho SOCKS5
        if proxy.startswith("socks5://"):
            # SOCKS5 có thể cần thêm options này
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
        proxy_type = "SOCKS5" if proxy.startswith("socks5://") else "HTTP"
        print(f"Using {proxy_type} proxy: {proxy_display}")  # Hide credentials in log
    
    # Random user agent
    user_agent = get_random_user_agent()
    chrome_options.add_argument(f"--user-agent={user_agent}")
    print(f"User Agent: {user_agent[:80]}...")
    
    # Random language
    languages = ["en-US,en", "vi-VN,vi", "en-GB,en", "en-CA,en"]
    chrome_options.add_argument(f"--lang={random.choice(languages)}")
    
    # Random window position
    chrome_options.add_argument(f"--window-position={random.randint(0, 500)},{random.randint(0, 500)}")
    
    # Experimental options
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("detach", True)
    
    # Preferences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "intl.accept_languages": random.choice(["en-US,en", "vi-VN,vi", "en-GB,en"]),
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Try Selenium's built-in driver management first (recommended for Selenium 4.6+)
    try:
        print("Attempting to use Selenium's built-in driver management...")
        driver = webdriver.Chrome(options=chrome_options)
        print("ChromeDriver initialized successfully using Selenium Manager")
        
        # Setup fake fingerprint
        setup_fake_chrome_fingerprint(driver)
        
        return driver
    except Exception as e1:
        print(f"Selenium built-in driver management failed: {e1}")
        print("Attempting to use ChromeDriverManager...")
        
        try:
            # Fallback to ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            print(f"ChromeDriver path: {driver_path}")
            
            # Verify the file exists
            if not os.path.exists(driver_path):
                raise Exception(f"ChromeDriver not found at: {driver_path}")
            
            # On Windows, handle .exe extension
            if os.name == 'nt':
                # If path doesn't end with .exe, check if it's a directory
                if os.path.isdir(driver_path):
                    exe_path = os.path.join(driver_path, "chromedriver.exe")
                    if os.path.exists(exe_path):
                        driver_path = exe_path
                    else:
                        # Try to find chromedriver.exe in the directory
                        for file in os.listdir(driver_path):
                            if file == "chromedriver.exe":
                                driver_path = os.path.join(driver_path, file)
                                break
                        else:
                            raise Exception(f"ChromeDriver executable not found in directory: {driver_path}")
                elif not driver_path.endswith('.exe'):
                    # If it's a file but not .exe, it might be wrong
                    # Try adding .exe extension
                    exe_path = driver_path + '.exe'
                    if os.path.exists(exe_path):
                        driver_path = exe_path
            
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("ChromeDriver initialized successfully using ChromeDriverManager")
            
            # Setup fake fingerprint
            setup_fake_chrome_fingerprint(driver)
            
            return driver
        except Exception as e2:
            print(f"ChromeDriverManager failed: {e2}")
            print("Attempting to use ChromeDriver from system PATH...")
            
            try:
                # Last resort: try without Service (let Selenium find it automatically)
                # This should work if ChromeDriver is in PATH
                driver = webdriver.Chrome(options=chrome_options)
                print("ChromeDriver initialized from system PATH")
                
                # Setup fake fingerprint
                setup_fake_chrome_fingerprint(driver)
                
                return driver
            except Exception as e3:
                # Collect all error messages safely
                errors = []
                try:
                    errors.append(f"1. Selenium Manager: {str(e1)}")
                except:
                    errors.append(f"1. Selenium Manager: Unknown error")
                try:
                    errors.append(f"2. ChromeDriverManager: {str(e2)}")
                except:
                    errors.append(f"2. ChromeDriverManager: Unknown error")
                try:
                    errors.append(f"3. System PATH: {str(e3)}")
                except:
                    errors.append(f"3. System PATH: Unknown error")
                
                error_msg = (
                    f"Failed to setup ChromeDriver. Tried all methods:\n"
                    f"\n".join(errors) + "\n\n"
                    f"Please ensure:\n"
                    f"- Chrome browser is installed\n"
                    f"- Chrome is up to date\n"
                    f"- You have internet connection (for driver download)\n"
                    f"- Your system architecture is supported (64-bit recommended)\n"
                    f"- Try installing ChromeDriver manually and add it to PATH"
                )
                raise Exception(error_msg)

def wait_for_verify_page(driver, timeout=30):
    """Wait for URL to change to verification page"""
    wait = WebDriverWait(driver, timeout)
    try:
        # Wait for URL to contain /auth/verify
        wait.until(lambda d: '/auth/verify' in d.current_url or 'auth/verify' in d.current_url)
        print(f"URL changed to verification page: {driver.current_url}")
        return True
    except Exception as e:
        print(f"Timeout waiting for verify page. Current URL: {driver.current_url}")
        return False

def fill_registration_form(driver, name, email, password, confirm_password, referral_code):
    """Fill the registration form"""
    wait = WebDriverWait(driver, 30)
    
    # Navigate to registration page
    print("Navigating to registration page...")
    try:
        driver.get(REGISTRATION_URL)
        # Wait for page to load completely
        time.sleep(3)
        
        # Wait for page to be ready (check if document.readyState is complete)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page loaded successfully")
        
        # Additional wait for any dynamic content
        time.sleep(2)
    except Exception as e:
        print(f"Error loading page: {e}")
        raise
    
    # Handle Cookie Settings modal if it appears
    print("Checking for cookie consent modal...")
    try:
        # Wait a bit for modal to appear
        time.sleep(1)
        cookie_wait = WebDriverWait(driver, 5)
        
        # Try multiple ways to find and click "Accept All" button
        accept_all_clicked = False
        
        # Method 1: Try to find "Accept All" button by text
        try:
            accept_buttons = driver.find_elements(By.XPATH, '//button[contains(., "Accept All") or contains(., "Accept")]')
            for btn in accept_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        print("Found Accept All button, clicking...")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", btn)
                        accept_all_clicked = True
                        print("Clicked Accept All button via JavaScript")
                        break
                except:
                    continue
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Try to find button by class or role
        if not accept_all_clicked:
            try:
                buttons = driver.find_elements(By.XPATH, '//button[contains(@class, "Accept") or contains(@class, "accept")]')
                for btn in buttons:
                    try:
                        btn_text = btn.text.lower()
                        if "accept" in btn_text and btn.is_displayed():
                            print("Found Accept button by class, clicking...")
                            driver.execute_script("arguments[0].click();", btn)
                            accept_all_clicked = True
                            print("Clicked Accept button")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Method 2 failed: {e}")
        
        # Method 3: Try to find close button if Accept All not found
        if not accept_all_clicked:
            try:
                # Look for close button (X)
                close_buttons = driver.find_elements(By.XPATH, 
                    '//button[@aria-label="Close" or @aria-label="close" or contains(@class, "close")] | '
                    '//*[@role="button" and (contains(@aria-label, "close") or contains(@class, "close"))] | '
                    '//button[contains(., "×") or contains(., "✕")]'
                )
                for btn in close_buttons:
                    try:
                        if btn.is_displayed():
                            print("Found close button, clicking...")
                            driver.execute_script("arguments[0].click();", btn)
                            accept_all_clicked = True
                            print("Closed cookie modal")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Method 3 failed: {e}")
        
        # Wait for modal to disappear
        if accept_all_clicked:
            time.sleep(1)
            # Wait for cookie modal/overlay to be invisible
            try:
                # Try to find and wait for modal to disappear
                modal_selectors = [
                    (By.XPATH, '//div[contains(@class, "fixed") and contains(@class, "inset-0")]'),
                    (By.XPATH, '//div[contains(@role, "dialog")]'),
                    (By.CSS_SELECTOR, '[role="dialog"]'),
                ]
                
                for selector_type, selector in modal_selectors:
                    try:
                        # Wait for element to become invisible
                        WebDriverWait(driver, 3).until(
                            EC.invisibility_of_element_located((selector_type, selector))
                        )
                        print("Cookie modal disappeared")
                        break
                    except:
                        continue
            except:
                pass
            
            # Additional wait after closing modal
            time.sleep(1)
        else:
            print("No cookie modal found or already handled")
            
    except Exception as e:
        print(f"Cookie modal handling error (continuing anyway): {e}")
        # Continue anyway - modal might not exist
    
    # Fill Name - type slowly
    print("Filling name field...")
    name_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="name"]')))
    name_input.click()
    time.sleep(random.uniform(0.2, 0.5))
    slow_type(name_input, name, min_delay=0.08, max_delay=0.25)
    time.sleep(random.uniform(0.3, 0.6))
    
    # Fill Email - type slowly
    print("Filling email field...")
    email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
    email_input.click()
    time.sleep(random.uniform(0.2, 0.5))
    slow_type(email_input, email, min_delay=0.08, max_delay=0.25)
    time.sleep(random.uniform(0.3, 0.6))
    
    # Fill Password - type slowly
    print("Filling password field...")
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
    password_input.click()
    time.sleep(random.uniform(0.2, 0.5))
    slow_type(password_input, password, min_delay=0.1, max_delay=0.3)
    time.sleep(random.uniform(0.3, 0.6))
    
    # Fill Confirm Password - type slowly
    print("Filling confirm password field...")
    confirm_password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="confirmPassword"]')))
    confirm_password_input.click()
    time.sleep(random.uniform(0.2, 0.5))
    slow_type(confirm_password_input, confirm_password, min_delay=0.1, max_delay=0.3)
    time.sleep(random.uniform(0.3, 0.6))
    
    # Fill Referral Code - type slowly
    print("Filling referral code field...")
    referral_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="referralCode"]')))
    referral_input.click()
    time.sleep(random.uniform(0.2, 0.5))
    slow_type(referral_input, referral_code, min_delay=0.08, max_delay=0.25)
    time.sleep(random.uniform(0.3, 0.6))
    
    # Wait for any overlay/modal to disappear
    try:
        # Try multiple selectors for overlay
        overlay_selectors = [
            (By.CSS_SELECTOR, 'div.fixed.inset-0.bg-black\\/40'),
            (By.CSS_SELECTOR, 'div[class*="fixed"][class*="inset-0"]'),
            (By.XPATH, '//div[contains(@class, "fixed") and contains(@class, "inset-0")]'),
        ]
        
        overlay_found = False
        for selector_type, selector in overlay_selectors:
            try:
                overlay = driver.find_element(selector_type, selector)
                if overlay.is_displayed():
                    overlay_found = True
                    print(f"Overlay found with selector: {selector}")
                    # Wait for overlay to disappear (max 5 seconds)
                    wait_short = WebDriverWait(driver, 5)
                    wait_short.until(EC.invisibility_of_element_located((selector_type, selector)))
                    print("Overlay disappeared")
                    break
            except:
                continue
        
        if not overlay_found:
            print("No overlay found or already gone")
    except Exception as e:
        # Overlay might not exist or already gone, continue anyway
        print(f"Overlay check completed: {e}")
        pass
    
    # Wait a bit for any animations to complete
    time.sleep(1)
    
    # Get current URL before clicking
    current_url_before = driver.current_url
    print(f"Current URL before clicking signup: {current_url_before}")
    
    # Click Sign Up button with retry mechanism (max 5 attempts)
    print("Clicking Sign Up button...")
    max_click_attempts = 10
    url_changed = False
    
    for attempt in range(1, max_click_attempts + 1):
        try:
            # Find button
            signup_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div/div/div[2]/form/button')))
            
            # Scroll button into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", signup_button)
            time.sleep(random.uniform(0.3, 0.6))
            
            # Try to click the button with multiple methods
            clicked = False
            
            # Method 1: Normal click
            try:
                signup_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[2]/form/button')))
                signup_button.click()
                print(f"Attempt {attempt}: Button clicked successfully (normal click)")
                clicked = True
            except Exception as e1:
                print(f"Attempt {attempt}: Normal click failed: {e1}")
                
                # Method 2: JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", signup_button)
                    print(f"Attempt {attempt}: Button clicked successfully (JavaScript click)")
                    clicked = True
                except Exception as e2:
                    print(f"Attempt {attempt}: JavaScript click failed: {e2}")
                    
                    # Method 3: Form submit
                    try:
                        form = driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div/div[2]/form')
                        driver.execute_script("arguments[0].submit();", form)
                        print(f"Attempt {attempt}: Form submitted via JavaScript")
                        clicked = True
                    except Exception as e3:
                        print(f"Attempt {attempt}: Form submit failed: {e3}")
            
            if clicked:
                # Wait a bit after clicking
                time.sleep(random.uniform(1, 2))
                
                # Check if URL changed
                current_url_after = driver.current_url
                print(f"Current URL after click: {current_url_after}")
                
                if '/auth/verify' in current_url_after or 'auth/verify' in current_url_after:
                    print(f"URL changed to verify page after attempt {attempt}!")
                    url_changed = True
                    break
                else:
                    print(f"URL not changed yet after attempt {attempt}, waiting...")
                    # Wait a bit more and check again
                    time.sleep(random.uniform(1, 2))
                    current_url_check = driver.current_url
                    if '/auth/verify' in current_url_check or 'auth/verify' in current_url_check:
                        print(f"URL changed to verify page on recheck after attempt {attempt}!")
                        url_changed = True
                        break
                    else:
                        print(f"URL still not changed: {current_url_check}")
            
            # If not successful, wait before retry
            if attempt < max_click_attempts:
                wait_time = random.uniform(1, 2)
                print(f"Waiting {wait_time:.1f} seconds before retry...")
                time.sleep(wait_time)
        
        except Exception as e:
            print(f"Attempt {attempt} error: {e}")
            if attempt < max_click_attempts:
                time.sleep(random.uniform(1, 2))
    
    # If URL didn't change after all attempts, wait for it with timeout
    if not url_changed:
        print("URL not changed after all click attempts, waiting for URL change...")
        url_changed = wait_for_verify_page(driver, timeout=30)
    
    # Final check
    if not url_changed:
        current_url_final = driver.current_url
        print(f"ERROR: URL did not change to verify page after {max_click_attempts} attempts and 30 seconds timeout")
        print(f"Final URL: {current_url_final}")
        print(f"Expected URL to contain: /auth/verify")
        raise Exception(f"Failed to navigate to verify page. Current URL: {current_url_final}")
    
    # Wait for page to be fully loaded
    print("Waiting for verification page to fully load...")
    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)  # Additional wait for dynamic content
        print("Verification page loaded successfully")
    except:
        print("Page load check skipped, continuing...")

def submit_verification_code(driver, code):
    """Submit the verification code"""
    wait = WebDriverWait(driver, 20)
    
    # Wait for verification page to load
    time.sleep(2)
    
    # Get all 6 input fields
    # Try using the container div first
    try:
        inputs = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[@class="flex gap-2 justify-center mb-4"]/input')
        ))
    except:
        # Fallback: try getting inputs by aria-label
        inputs = []
        for i in range(1, 7):
            try:
                input_field = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f'//input[@aria-label="OTP digit {i}"]')
                ))
                inputs.append(input_field)
            except:
                pass
    
    if len(inputs) != 6:
        raise Exception(f"Expected 6 input fields, found {len(inputs)}")
    
    # Fill each input with corresponding digit - type slowly
    print(f"Filling verification code: {code}")
    for i, input_field in enumerate(inputs):
        if i < len(code):
            try:
                input_field.click()
                time.sleep(random.uniform(0.1, 0.3))
                input_field.clear()
                time.sleep(random.uniform(0.05, 0.15))
                # Type digit slowly
                input_field.send_keys(code[i])
                print(f"Filled digit {i+1}: {code[i]}")
                time.sleep(random.uniform(0.15, 0.35))  # Random delay between digits
            except Exception as e:
                print(f"Error filling input {i+1}: {e}")
                # Try JavaScript as fallback
                try:
                    driver.execute_script(f"arguments[0].value = '{code[i]}';", input_field)
                    driver.execute_script(f"arguments[0].dispatchEvent(new Event('input'));", input_field)
                except:
                    pass
    
    time.sleep(1)
    
    # Click Verify Email button
    verify_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="main"]/div/div/div/div[2]/div[1]/button')
    ))
    verify_button.click()
    time.sleep(3)

def create_account(driver):
    """Create a single account"""
    # Generate random data
    name = generate_random_name()
    email_addr = generate_random_email()
    
    print(f"Creating account: {name} - {email_addr}")
    
    # Fill registration form
    fill_registration_form(driver, name, email_addr, PASSWORD, PASSWORD, REFERRAL_CODE)
    
    # Wait for email to be sent (increased to 15 seconds)
    print("Waiting for verification email (15 seconds)...")
    time.sleep(15)
    
    # Get verification code from Gmail (filter by target email)
    verification_code = None
    max_retries = 10
    for attempt in range(max_retries):
        verification_code = get_verification_code_from_gmail(target_email=email_addr)
        if verification_code:
            print(f"Verification code found: {verification_code} for {email_addr}")
            break
        print(f"Attempt {attempt + 1}/{max_retries}: Code not found for {email_addr}, retrying...")
        time.sleep(3)
    
    if not verification_code:
        raise Exception("Could not retrieve verification code from email")
    
    # Submit verification code
    submit_verification_code(driver, verification_code)
    print(f"Account created successfully: {email_addr}")
    time.sleep(2)

def create_account_worker(account_id, stats_lock, stats):
    """Worker function for creating a single account in a thread"""
    driver = None
    proxy = None
    thread_name = threading.current_thread().name
    
    try:
        # Get proxy cố định cho thread này (mỗi thread chỉ có 1 proxy)
        if USE_PROXY:
            proxy = get_proxy_for_thread(thread_name)
        
        # Setup driver for this account
        print(f"\n{'='*70}")
        print(f"[Thread: {thread_name}] {'='*70}")
        print(f"[Thread: {thread_name}] Account ID: #{account_id}")
        if proxy:
            proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
            print(f"[Thread: {thread_name}] 🌐 PROXY: {proxy_display}")
        else:
            print(f"[Thread: {thread_name}] 🌐 PROXY: None (không dùng proxy)")
        print(f"[Thread: {thread_name}] {'='*70}")
        driver = setup_driver(proxy=proxy)
        
        with stats_lock:
            stats['account_count'] += 1
            current_stats = stats.copy()
        
        print(f"\n[Thread: {thread_name}] {'='*70}")
        print(f"[Thread: {thread_name}] 📝 Bắt đầu tạo account #{account_id}")
        if proxy:
            proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
            print(f"[Thread: {thread_name}] 🌐 Đang dùng PROXY: {proxy_display}")
        print(f"[Thread: {thread_name}] 📊 Stats: Success={current_stats['success_count']}, Errors={current_stats['error_count']}")
        print(f"[Thread: {thread_name}] {'='*70}")
        
        try:
            # Create account
            create_account(driver)
            
            with stats_lock:
                stats['success_count'] += 1
                current_stats = stats.copy()
            
            print(f"\n[Thread: {thread_name}] {'='*70}")
            print(f"[Thread: {thread_name}] ✅ Account #{account_id} tạo thành công!")
            if proxy:
                proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
                print(f"[Thread: {thread_name}] 🌐 PROXY đã dùng: {proxy_display}")
            print(f"[Thread: {thread_name}] 📊 Stats: Success={current_stats['success_count']}, Errors={current_stats['error_count']}")
            print(f"[Thread: {thread_name}] {'='*70}")
        except Exception as e:
            with stats_lock:
                stats['error_count'] += 1
                current_stats = stats.copy()
            
            print(f"\n[Thread: {thread_name}] {'='*70}")
            print(f"[Thread: {thread_name}] ❌ Lỗi khi tạo account #{account_id}: {e}")
            if proxy:
                proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
                print(f"[Thread: {thread_name}] 🌐 PROXY đã dùng: {proxy_display}")
            print(f"[Thread: {thread_name}] 📊 Stats: Success={current_stats['success_count']}, Errors={current_stats['error_count']}")
            print(f"[Thread: {thread_name}] {'='*70}")
            import traceback
            print(f"\n[Thread: {thread_name}] Traceback:")
            traceback.print_exc()
        finally:
            # Close browser after each account (success or failure)
            if driver:
                try:
                    print(f"[Thread: {thread_name}] 🔒 Đóng browser...")
                    driver.quit()
                    print(f"[Thread: {thread_name}] ✅ Browser đã đóng")
                except Exception as e:
                    print(f"[Thread: {thread_name}] ⚠️ Lỗi khi đóng browser: {e}")
                    # Try to kill browser process if quit fails
                    try:
                        if os.name == 'nt':  # Windows
                            os.system("taskkill /F /IM chrome.exe /T")
                        else:  # Linux/Mac
                            os.system("pkill -f chrome")
                    except:
                        pass
    except Exception as e:
        # Fatal error (e.g., setup_driver failed)
        print(f"\n[Thread: {thread_name}] {'='*70}")
        print(f"[Thread: {thread_name}] ❌ Fatal error: {e}")
        if proxy:
            proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
            print(f"[Thread: {thread_name}] 🌐 PROXY đã dùng: {proxy_display}")
        print(f"[Thread: {thread_name}] {'='*70}")
        import traceback
        print(f"\n[Thread: {thread_name}] Traceback:")
        traceback.print_exc()
        
        # Close browser if still open
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """Main function to create accounts continuously with multi-threading"""
    # Thread-safe statistics
    stats_lock = threading.Lock()
    stats = {
        'account_count': 0,
        'success_count': 0,
        'error_count': 0
    }
    
    print(f"\n{'='*60}")
    print("Starting account creation bot (multi-threaded)")
    print(f"Number of threads: {NUM_THREADS}")
    if USE_PROXY:
        print(f"🌐 Proxy mode: ENABLED ({len(PROXY_LIST)} proxy/proxies configured)")
        print(f"📊 Số luồng: {NUM_THREADS}")
        if len(PROXY_LIST) > 0:
            print("\n📋 Danh sách Proxy:")
            for i, proxy in enumerate(PROXY_LIST, 1):
                proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
                print(f"  [{i}] {proxy_display}")
            print(f"\n💡 Mỗi luồng sẽ được gán 1 proxy cố định (không chia sẻ)")
    else:
        print("🌐 Proxy mode: DISABLED")
    print("Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    account_id = 0
    
    try:
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = set()
            
            while True:
                # Submit new tasks up to NUM_THREADS
                while len(futures) < NUM_THREADS:
                    account_id += 1
                    future = executor.submit(create_account_worker, account_id, stats_lock, stats)
                    futures.add(future)
                    time.sleep(1)  # Small delay between starting threads
                
                # Wait for at least one task to complete
                done_futures = []
                try:
                    for future in as_completed(futures, timeout=1):
                        try:
                            future.result()  # Get result (or exception)
                        except Exception as e:
                            pass  # Already handled in worker
                        done_futures.append(future)
                except Exception:
                    # Timeout or other error - no futures completed yet, continue
                    pass
                
                # Remove completed futures
                for future in done_futures:
                    futures.discard(future)
                
                # Print periodic stats
                with stats_lock:
                    current_stats = stats.copy()
                print(f"\n[Main] Current Stats - Total: {current_stats['account_count']}, Success: {current_stats['success_count']}, Errors: {current_stats['error_count']}")
                
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print("Stopped by user (Ctrl+C)")
        print(f"{'='*60}")
        
        with stats_lock:
            final_stats = stats.copy()
        
        print(f"\nFinal Stats:")
        print(f"  Total accounts attempted: {final_stats['account_count']}")
        print(f"  Success: {final_stats['success_count']}")
        print(f"  Errors: {final_stats['error_count']}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()


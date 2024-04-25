from flask import abort
from flasks.credentials import AUTH_CREDENTIALS
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def check_authentication(sitename, username, password):
    if sitename not in AUTH_CREDENTIALS:
        return False

    valid_username = AUTH_CREDENTIALS[sitename]['username']
    valid_password = AUTH_CREDENTIALS[sitename]['password']
    if not username and not password:
        return False
    elif (
        username == valid_username
        and password == valid_password
    ):
        return True
    else:
        abort(404, 'Username and/or password is invalid')


def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--remote-debugging-port=9230")
    user_agent = 'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    browser = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=chrome_options
    )

    return browser

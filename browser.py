# browser.py - Tarayıcı yönetim fonksiyonları
"""
Selenium tarayıcı yönetimi için fonksiyonlar
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import config


def initialize_browser():
    """Tarayıcıyı yapılandır ve başlat"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    # User Agent bilgisini değiştir
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": config.USER_AGENT
    })

    return driver


def login(driver):
    """LinkedIn'e giriş yap"""
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    driver.find_element(By.ID, "username").send_keys(config.EMAIL)
    driver.find_element(By.ID, "password").send_keys(config.PASSWORD + Keys.RETURN)

    # CAPTCHA çöz ve ENTER'a bas
    input("CAPTCHA varsa çöz ve ENTER'a bas: ")

    # Giriş başarılı mı kontrol et
    if "feed" in driver.current_url or "voyager" in driver.current_url:
        print("✅ LinkedIn'e giriş başarılı!")
        return True
    else:
        print("❌ LinkedIn'e giriş başarısız!")
        return False


def check_login_status(driver, profile_url):
    """Giriş durumunu kontrol et ve gerekirse yeniden giriş yap"""
    if "LinkedIn Giriş" in driver.title or "LinkedIn Login" in driver.title:
        print("Oturum süresi dolmuş, yeniden giriş yapılıyor...")
        driver.find_element(By.ID, "username").send_keys(config.EMAIL)
        driver.find_element(By.ID, "password").send_keys(config.PASSWORD + Keys.RETURN)
        time.sleep(5)

        # CAPTCHA kontrolü
        if "güvenlik doğrulaması" in driver.page_source.lower() or "security verification" in driver.page_source.lower():
            input("CAPTCHA tespit edildi. Çözün ve ENTER'a basın: ")

        # Profil sayfasına tekrar git
        driver.get(profile_url)
        time.sleep(config.PAGE_LOAD_WAIT)
        return True

    return False
# config.py - Yapılandırma ayarları
"""
LinkedIn scraper için yapılandırma ayarları
"""
# Giriş bilgileri
EMAIL = input("Mailinizi Girin : ")
PASSWORD = input("Şifreyi Girin : ")

# Veri dosyaları
EXCEL_FILE = "Linkedinlist/Lnklst.xlsx"
DB_FILE = "linkedin_data.db"
PHOTOS_DIR = "linkedin_profile_photos"

# Zaman ayarları
PAGE_LOAD_WAIT = 5
SCROLL_WAIT = 2
MIN_WAIT_BETWEEN_PROFILES = 5
MAX_WAIT_BETWEEN_PROFILES = 15

# HTTP İstekleri için User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# HTTP İstekleri için Headers
REQUEST_HEADERS = {
    'User-Agent': USER_AGENT,
    'Referer': 'https://www.linkedin.com/',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}
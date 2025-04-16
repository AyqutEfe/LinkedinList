# profile_parser.py - Profil verileri ayrıştırma
"""
LinkedIn profil verilerini ayrıştırma işlemleri
"""
from selenium.webdriver.common.by import By
import time
import config
from photo_downloader import download_profile_photo


def scroll_page(driver):
    """Sayfanın sonuna kadar kaydır"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(config.SCROLL_WAIT)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_profile_info(driver):
    """Profil ismini ve fotoğrafını çek"""
    profile_photo_path = ""
    profile_name = ""

    try:
        # İsmi almaya çalış - farklı seçicileri dene
        name_selectors = [
            "h1.text-heading-xlarge",
            "h1.inline.t-24.t-black.t-normal",
            "div.pv-text-details__left-panel h1",
            "div.pv-text-details__title",
            "h1.ember-view",
            "h1.break-words",
            # Daha güncel seçiciler
            "h1.basic-info-member-name",
            "h1.inline"
        ]

        for selector in name_selectors:
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, selector)
                profile_name = name_element.text.strip()
                if profile_name:
                    print(f"İsim bulundu: {profile_name}")
                    break
            except:
                continue

        # Profil fotoğrafını almaya çalış - güncellenmiş seçiciler
        photo_selectors = [
            "img.pv-top-card-profile-picture__image",
            "div.pv-top-card-profile-picture img",
            "div.profile-picture img",
            "div.presence-entity__image img",
            "div.pv-top-card__photo img",
            "img.ember-view.profile-photo-edit__preview",
            "img.profile-picture-view",
            # Daha güncel seçiciler
            "img.profile-photo-edit__preview",
            "div.presence-entity__image img",
            ".profile-photo img",
            "img.photo",
            "img.pv-top-card__photo",
            ".profile-picture-view img",
            ".artdeco-entity-lockup__image img"
        ]

        # Birden fazla seçicide başarısız olursa, doğrudan JavaScript ile görüntüyü almayı dene
        for selector in photo_selectors:
            try:
                profile_photo = driver.find_element(By.CSS_SELECTOR, selector)
                photo_url = profile_photo.get_attribute("src")

                if photo_url and not photo_url.startswith("data:"):
                    print(f"Profil fotoğrafı URL'si bulundu: {photo_url}")
                    profile_photo_path = download_profile_photo(photo_url, driver.current_url)
                    if profile_photo_path:
                        break
            except Exception as e:
                continue

        # Seçicilerle başarısız olursa, tüm img etiketlerini kontrol et
        if not profile_photo_path:
            try:
                print("Standart seçiciler başarısız oldu, tüm resimler taranıyor...")
                all_images = driver.find_elements(By.TAG_NAME, "img")
                for img in all_images:
                    try:
                        alt_text = img.get_attribute("alt") or ""
                        src = img.get_attribute("src") or ""

                        # Profil fotoğrafı olabilecek görüntüleri filtrele
                        if ((profile_name and profile_name.lower() in alt_text.lower()) or
                            "profil" in alt_text.lower() or
                            "profile" in alt_text.lower() or
                            "avatar" in alt_text.lower() or
                            "photo" in alt_text.lower()) and \
                                src and not src.startswith("data:") and \
                                ("linkedin.com" in src or "licdn.com" in src):

                            print(f"Alternatif profil fotoğrafı bulundu: {src}")
                            profile_photo_path = download_profile_photo(src, driver.current_url)
                            if profile_photo_path:
                                break
                    except:
                        continue
            except Exception as e:
                print(f"Alternatif fotoğraf arama hatası: {e}")

        # Son çare olarak JavaScript ile doğrudan fotoğrafı almayı dene
        if not profile_photo_path:
            try:
                print("JavaScript ile fotoğraf URL'si aranıyor...")
                # LinkedIn'in fotoğraf URL'lerini genellikle sakladığı yerlerde ara
                js_photo_urls = driver.execute_script("""
                    var urls = [];
                    var images = document.querySelectorAll('img');
                    for (var i = 0; i < images.length; i++) {
                        if (images[i].src && images[i].src.includes('profile-displayphoto')) {
                            urls.push(images[i].src);
                        }
                    }
                    return urls;
                """)

                if js_photo_urls and len(js_photo_urls) > 0:
                    for url in js_photo_urls:
                        print(f"JavaScript ile bulunan fotoğraf URL'si: {url}")
                        profile_photo_path = download_profile_photo(url, driver.current_url)
                        if profile_photo_path:
                            break
            except Exception as e:
                print(f"JavaScript ile fotoğraf arama hatası: {e}")

    except Exception as e:
        print(f"❌ Profil bilgisi çekme hatası: {e}")

    return profile_name, profile_photo_path


def parse_experience_section(section, profile_id, conn, db):
    """Deneyim bölümünü ayrıştır ve veritabanına kaydet"""
    print("📋 Deneyim bilgileri toplanıyor...")
    items = section.find_elements(By.TAG_NAME, "li")
    for item in items:
        text = item.text.strip()
        if text and len(text.split("\n")) >= 2:
            # Tekrar eden satırları temizle
            lines = text.split("\n")
            cleaned_lines = []
            seen = set()

            for line in lines:
                # Temizlenmiş satır (boşluklar ve noktalama temizleniyor)
                cleaned = ' '.join(line.lower().split())
                if cleaned not in seen and cleaned:
                    seen.add(cleaned)
                    cleaned_lines.append(line)

            # İş pozisyonu, şirket ve tarih bilgisini ayrıştır
            position = ""
            company = ""
            date_range = ""
            location = ""
            description = ""

            try:
                parts = cleaned_lines.copy()

                # İlk satır genelde pozisyon
                if parts:
                    position = parts.pop(0)

                # İkinci satır genelde şirket
                if parts:
                    company = parts.pop(0)

                # Sonraki satır genelde süre
                if parts:
                    date_range = parts.pop(0)

                # Kalan satırlar konum veya açıklama
                if parts:
                    location = parts.pop(0) if parts else ""
                    description = "\n".join(parts) if parts else ""

                # Deneyimi veritabanına ekle
                db.save_experience(conn, profile_id, position, company, date_range, location, description)

            except Exception as e:
                print(f"⚠️ İş deneyimi ayrıştırma hatası: {e}")
                # Ham veriyi description alanına ekle
                db.save_experience(conn, profile_id, "", "", "", "", "\n".join(cleaned_lines))

    print("✅ İş deneyimleri veritabanına kaydedildi.")


def parse_education_section(section, profile_id, conn, db):
    """Eğitim bölümünü ayrıştır ve veritabanına kaydet"""
    print("📚 Eğitim bilgileri toplanıyor...")
    items = section.find_elements(By.TAG_NAME, "li")
    for item in items:
        text = item.text.strip()
        if text and len(text.split("\n")) >= 2:
            # Tekrar eden satırları temizle
            lines = text.split("\n")
            cleaned_lines = []
            seen = set()

            for line in lines:
                cleaned = ' '.join(line.lower().split())
                if cleaned not in seen and cleaned:
                    seen.add(cleaned)
                    cleaned_lines.append(line)

            # Eğitim bilgilerini ayrıştır
            school = ""
            degree = ""
            date_range = ""
            description = ""

            try:
                parts = cleaned_lines.copy()

                # İlk satır genelde okul
                if parts:
                    school = parts.pop(0)

                # İkinci satır genelde derece/bölüm
                if parts:
                    degree = parts.pop(0)

                # Sonraki satır genelde tarih
                if parts:
                    date_range = parts.pop(0)

                # Kalan satırlar açıklama
                description = "\n".join(parts) if parts else ""

                # Eğitimi veritabanına ekle
                db.save_education(conn, profile_id, school, degree, date_range, description)

            except Exception as e:
                print(f"⚠️ Eğitim bilgisi ayrıştırma hatası: {e}")
                # Ham veriyi description alanına ekle
                db.save_education(conn, profile_id, "", "", "", "\n".join(cleaned_lines))

    print("✅ Eğitim bilgileri veritabanına kaydedildi.")
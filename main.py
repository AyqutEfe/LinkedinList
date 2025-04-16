# main.py - Ana program
"""
LinkedIn profil scraper ana programı
"""
import os
import time
import pandas as pd
import random
from selenium.webdriver.common.by import By

# Kendi modüllerimizi içe aktar
import config
import database as db
import browser
import profile_parser as parser


def main():
    """Ana program fonksiyonu"""
    print("LinkedIn Profile Scraper başlatılıyor...")

    # Profil fotoğrafları için klasör oluştur
    os.makedirs(config.PHOTOS_DIR, exist_ok=True)

    # Veritabanı bağlantısını başlat
    conn = db.init_database()

    # Excel dosyasından LinkedIn linklerini oku
    try:
        df = pd.read_excel(config.EXCEL_FILE)
        linkedin_links = df["linkedin"].dropna().tolist()
        print(f"Excel dosyasından {len(linkedin_links)} LinkedIn profil linki alındı.")
    except Exception as e:
        print(f"Excel dosyası okuma hatası: {e}")
        conn.close()
        return

    # Zaten işlenmiş linkleri al
    processed_links = db.get_processed_links(conn)
    print(f"Daha önce işlenmiş {len(processed_links)} profil atlanacak.")

    # Tarayıcıyı başlat ve LinkedIn'e giriş yap
    driver = browser.initialize_browser()
    login_success = browser.login(driver)

    if not login_success:
        print("Giriş yapılamadığı için program sonlandırılıyor.")
        driver.quit()
        conn.close()
        return

    # Her profil için işlem yap
    for index, link in enumerate(linkedin_links):
        # Zaten işlenmiş linkleri atla
        if link in processed_links:
            print(f"Bu profil zaten işlenmiş: {link}")
            continue

        print(f"\n🔍 Profil inceleniyor ({index + 1}/{len(linkedin_links)}): {link}")

        try:
            driver.get(link)
            # Sayfanın yüklenmesi için bekle
            time.sleep(config.PAGE_LOAD_WAIT)

            # Giriş durumunu kontrol et
            browser.check_login_status(driver, link)

            # Sayfayı kaydır
            parser.scroll_page(driver)

            # Profil ismi ve fotoğrafını al
            profile_name, profile_photo_path = parser.extract_profile_info(driver)

            if not profile_name:
                print("⚠️ Profil ismi alınamadı!")
                profile_name = f"Bilinmeyen_{int(time.time())}"

            # Profili veritabanına ekle
            profile_id = db.save_profile(conn, link, profile_name, profile_photo_path)
            print(f"✅ Profil veritabanına eklendi: {profile_name}")

            # Deneyim ve Eğitim bölümlerini bul
            sections = driver.find_elements(By.TAG_NAME, "section")

            for sec in sections:
                # Deneyim (Kariyer) bilgilerini al
                if "Deneyim" in sec.text or "Experience" in sec.text:
                    parser.parse_experience_section(sec, profile_id, conn, db)

                # Eğitim bilgilerini al
                if "Eğitim" in sec.text or "Education" in sec.text:
                    parser.parse_education_section(sec, profile_id, conn, db)

        except Exception as e:
            print(f"❌ Genel hata: {e}")

        # Rate limiting'i aşmamak için rastgele bekleme
        sleep_time = config.MIN_WAIT_BETWEEN_PROFILES + random.random() * (
                config.MAX_WAIT_BETWEEN_PROFILES - config.MIN_WAIT_BETWEEN_PROFILES
        )
        print(f"⏱️ Bir sonraki profile geçmeden önce {sleep_time:.1f} saniye bekleniyor...")
        time.sleep(sleep_time)

    # Tarayıcıyı kapat
    driver.quit()

    # İlişkisel veritabanını görüntüle
    print("\n\n📊 Veritabanındaki kayıtlar:")
    rows = db.get_summary(conn)
    for row in rows:
        photo_status = "✅ Foto var" if row[2] else "❌ Foto yok"
        print(f"Profil: {row[0]}")
        print(f"İsim: {row[1]}")
        print(f"Fotoğraf: {photo_status} {row[2]}")
        print(f"Deneyim: {row[3]}, Eğitim: {row[4]}")
        print("-" * 50)

    conn.close()
    print("\n✅ Veritabanı bağlantısı kapatıldı.")
    print("Program tamamlandı.")


if __name__ == "__main__":
    main()
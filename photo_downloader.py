# photo_downloader.py - Profil fotoğrafı indirme
"""
LinkedIn profil fotoğraflarını indirme işlemleri
"""
import os
import time
import urllib.parse
import requests
import config


def download_profile_photo(image_url, profile_link):
    """LinkedIn profil fotoğrafını indir ve dosya yolunu döndür"""
    try:
        # Profil fotoğrafı kontrolleri
        if not image_url or "data:image" in image_url:
            print("❌ Profil fotoğrafı bulunamadı.")
            return ""

        # LinkedIn'in varsayılan/boş profil fotoğraflarını kontrol et
        # URL'de bulunan belirli terimler ve desenler
        default_photo_indicators = [
            "ghost-person",
            "blank-profile-picture",
            "default-avatar",
            "no-profile",
            "iprofile_",
            "anonymous-user",
            "person-placeholder"
        ]

        # Varsayılan profil fotoğrafı ve boyutları kontrol et
        if any(indicator in image_url.lower() for indicator in
               default_photo_indicators) or "shrink_100_100" in image_url:
            print("❌ Profil fotoğrafı bulunamadı (varsayılan fotoğraf tespit edildi).")
            return ""

        # Profil fotoğrafı indiriliyor mesajı
        print("🔄 Profil fotoğrafı indiriliyor...")

        # URL'den geçersiz karakterleri temizle
        clean_url = urllib.parse.unquote(profile_link)
        try:
            profile_name = clean_url.split("/in/")[1].split("/")[0]
            # URL'de ek parametreler varsa temizle
            if "?" in profile_name:
                profile_name = profile_name.split("?")[0]
        except IndexError:
            # URL formatı beklenmedik ise yedek çözüm
            profile_name = f"profile_{int(time.time())}"

        # Dosya adındaki geçersiz karakterleri temizle
        profile_name = "".join(c for c in profile_name if c.isalnum() or c in '-_')

        file_name = f"{profile_name}.jpg"  # LinkedIn fotoğrafları genellikle JPG formatındadır
        file_path = os.path.join(config.PHOTOS_DIR, file_name)

        # Fotoğrafı indir
        try:
            response = requests.get(
                image_url,
                headers=config.REQUEST_HEADERS,
                stream=True,
                timeout=15,
                allow_redirects=True
            )

            # HTTP durum kodunu kontrol et
            if response.status_code == 200:
                # İçerik türünü kontrol et
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    print("❌ Profil fotoğrafı bulunamadı (geçersiz içerik türü).")
                    return ""

                # Resmin içeriğini alıp analiz et
                image_data = response.content

                # Dosya boyutu kontrolü - çok küçük dosyalar genellikle default ikonlar olabilir
                if len(image_data) < 5000:  # 5KB'dan küçük
                    print("❌ Profil fotoğrafı bulunamadı (dosya boyutu çok küçük).")
                    return ""

                with open(file_path, 'wb') as f:
                    f.write(image_data)

                # Dosya boyutunu kontrol et
                file_size = os.path.getsize(file_path)
                if file_size > 100:  # 100 byte'dan büyük dosyalar geçerli kabul edilir
                    print(f"✅ Profil fotoğrafı başarıyla indirildi.")
                    return file_path
                else:
                    print("❌ Profil fotoğrafı bulunamadı (geçersiz dosya).")
                    os.remove(file_path)  # Geçersiz dosyayı sil
                    return ""
            else:
                print("❌ Profil fotoğrafı indirilemedi.")
                return ""

        except requests.exceptions.RequestException as e:
            print("❌ Profil fotoğrafı indirilemedi (bağlantı hatası).")
            return ""

    except Exception as e:
        print("❌ Profil fotoğrafı işlenirken hata oluştu.")
        return ""
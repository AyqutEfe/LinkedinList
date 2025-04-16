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
            print(f"Geçersiz resim URL'si veya data URI: {image_url}")
            return ""

        # LinkedIn'in varsayılan/boş profil fotoğraflarını kontrol et
        # Örnek: varsayılan profil fotoğraflarının URL'lerinde genellikle belirli desenler olur
        default_photo_indicators = [
            "ghost-person",
            "blank-profile-picture",
            "default-avatar",
            "no-profile",
            "iprofile_",
            "anonymous-user"
        ]

        if any(indicator in image_url.lower() for indicator in default_photo_indicators):
            print(f"Varsayılan profil fotoğrafı tespit edildi, indirme işlemi yapılmıyor: {image_url}")
            return ""

        # Debug için URL'yi yazdır
        print(f"İndirilmeye çalışılıyor: {image_url}")

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

        print(f"Kaydedilecek konum: {file_path}")

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
                    print(f"❌ İndirilen içerik bir resim değil: {content_type}")
                    return ""

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                # Dosya boyutunu kontrol et
                file_size = os.path.getsize(file_path)
                if file_size > 100:  # 100 byte'dan büyük dosyalar geçerli kabul edilir
                    # Varsayılan profil fotoğrafları genellikle belirli bir boyut aralığındadır
                    if 100 < file_size < 5000:  # Bu değerleri LinkedIn'in varsayılan fotoğraf boyutlarına göre ayarlayın
                        # Ekstra bir kontrol olarak basit bir imza kontrolü yapabilirsiniz
                        # Bu değerler LinkedIn'in varsayılan fotoğraflarına göre ayarlanmalıdır
                        with open(file_path, 'rb') as f:
                            file_signature = f.read(50)  # İlk 50 byte'ı oku
                            # Varsayılan profil fotoğraflarının imzasını karşılaştır
                            # Bu örnek, gerçek duruma göre değiştirilmelidir
                            # Gerçek bir uygulama için hash değerleri veya daha detaylı imza kontrolü düşünülebilir

                    print(f"✅ Fotoğraf başarıyla kaydedildi ({file_size} bytes): {file_path}")
                    return file_path
                else:
                    print(f"❌ İndirilen dosya çok küçük ({file_size} bytes), geçersiz olabilir")
                    os.remove(file_path)  # Geçersiz dosyayı sil
                    return ""
            else:
                print(f"❌ İndirme başarısız: HTTP {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            print(f"❌ İndirme isteği hatası: {e}")
            return ""

    except Exception as e:
        print(f"❌ Profil fotoğrafı indirme hatası: {e}")
        return ""
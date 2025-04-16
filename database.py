# database.py - Veritabanı işlemleri
"""
LinkedIn scraper için veritabanı işlemleri
"""
import sqlite3
import config

def init_database():
    """Veritabanını oluştur ve gerekli tabloları hazırla"""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()

    # Profiller tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linkedin_url TEXT UNIQUE,
        name TEXT,
        profile_photo TEXT
    )
    ''')

    # Deneyimler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS experiences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER,
        position TEXT,
        company TEXT,
        date_range TEXT,
        location TEXT,
        description TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles (id)
    )
    ''')

    # Eğitim tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER,
        school TEXT,
        degree TEXT,
        date_range TEXT,
        description TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles (id)
    )
    ''')

    conn.commit()
    return conn

def get_processed_links(conn):
    """İşlenmiş profil linklerini veritabanından al"""
    cursor = conn.cursor()
    cursor.execute("SELECT linkedin_url FROM profiles")
    return [row[0] for row in cursor.fetchall()]

def save_profile(conn, linkedin_url, name, profile_photo):
    """Profil bilgisini veritabanına kaydet ve ID'sini döndür"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO profiles (linkedin_url, name, profile_photo) VALUES (?, ?, ?)",
        (linkedin_url, name, profile_photo)
    )
    conn.commit()
    return cursor.lastrowid

def save_experience(conn, profile_id, position, company, date_range, location, description):
    """Deneyim bilgisini veritabanına kaydet"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO experiences (profile_id, position, company, date_range, location, description) VALUES (?, ?, ?, ?, ?, ?)",
        (profile_id, position, company, date_range, location, description)
    )
    conn.commit()

def save_education(conn, profile_id, school, degree, date_range, description):
    """Eğitim bilgisini veritabanına kaydet"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO education (profile_id, school, degree, date_range, description) VALUES (?, ?, ?, ?, ?)",
        (profile_id, school, degree, date_range, description)
    )
    conn.commit()

def get_summary(conn):
    """Veritabanından özet bilgileri al"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            p.linkedin_url, 
            p.name,
            p.profile_photo,
            COUNT(DISTINCT e.id) as experience_count, 
            COUNT(DISTINCT ed.id) as education_count
        FROM profiles p
        LEFT JOIN experiences e ON p.id = e.profile_id
        LEFT JOIN education ed ON p.id = ed.profile_id
        GROUP BY p.id
    ''')
    return cursor.fetchall()
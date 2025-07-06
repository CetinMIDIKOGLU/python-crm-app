import sqlite3
from logger import Logger

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_table()
        self.logger = Logger()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS musteriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefon TEXT NOT NULL,
                kayit_tarihi TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def musteri_ekle(self, ad, soyad, email, telefon):
        try:
           
            telefon = self._format_telefon(telefon)
            
            kayit_tarihi = self._get_current_datetime()
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO musteriler (ad, soyad, email, telefon, kayit_tarihi) VALUES (?, ?, ?, ?, ?)",
                (ad, soyad, email, telefon, kayit_tarihi)
            )
            self.conn.commit()
            self.logger.log_kaydet(f"Yeni müşteri eklendi: {ad} {soyad}")
            return True
        except sqlite3.IntegrityError:
            self.logger.log_kaydet(f"E-posta zaten kayıtlı: {email}")
            return False

    def _format_telefon(self, telefon):
       
        rakamlar = ''.join(filter(str.isdigit, telefon))
        
        if len(rakamlar) == 10:
           
            return f"+90 {rakamlar[:3]} {rakamlar[3:6]} {rakamlar[6:]}"
        elif len(rakamlar) == 11 and rakamlar.startswith('0'):
           
            return f"+90 {rakamlar[1:4]} {rakamlar[4:7]} {rakamlar[7:]}"
        else:
            
            return telefon

    def musteri_listele(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, ad, soyad, email, telefon, kayit_tarihi FROM musteriler ORDER BY ad, soyad")
            return cursor.fetchall()
        except Exception as e:
            self.logger.log_kaydet(f"Listeleme hatası: {str(e)}")
            return []

    def _get_current_datetime(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __del__(self):
        self.conn.close()
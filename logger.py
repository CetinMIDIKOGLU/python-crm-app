import datetime

class Logger:
    @staticmethod
    def log_kaydet(mesaj, dosya_adi="musteri_log.txt"):
        with open(dosya_adi, "a", encoding="utf-8") as f:
            tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{tarih}] {mesaj}\n")
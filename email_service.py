import smtplib
from email.mime.text import MIMEText
from logger import Logger

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "ornek@gmail.com"  # Kendi bilgilerinizle güncelleyin
        self.sender_password = " Uygulama şifresi"  # Uygulama şifresi
        self.logger = Logger()

    def email_gonder(self, alici_email, konu, icerik):
        try:
            msg = MIMEText(icerik)
            msg['Subject'] = konu
            msg['From'] = self.sender_email
            msg['To'] = alici_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, [alici_email], msg.as_string())
            
            self.logger.log_kaydet(f"{alici_email} adresine e-posta gönderildi")
            return True
        except Exception as e:
            self.logger.log_kaydet(f"E-posta gönderme hatası: {str(e)}")
            return False
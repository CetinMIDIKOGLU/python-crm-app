from ui import ApplicationUI
from database import Database
from email_service import EmailService
import tkinter as tk

def main():
    root = tk.Tk()
    db = Database("musteriler.db")
    email_service = EmailService()
    app = ApplicationUI(root, db, email_service)
    root.mainloop()

if __name__ == "__main__":
    main()
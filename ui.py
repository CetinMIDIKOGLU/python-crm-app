import tkinter as tk
from tkinter import ttk, messagebox
from validations import Validations

class ApplicationUI:
    def __init__(self, root, db, email_service):
        self.root = root
        self.db = db
        self.email_service = email_service
        self.validations = Validations()
        
        self.root.geometry("1100x700")
        self.root.minsize(1000, 600)
        
        self.center_window()
        
        self.setup_ui()

    def center_window(self):
        """Pencereyi ekranın ortasına yerleştirir"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        self.root.title("Müşteri Yönetim Sistemi")
        
        self.left_frame = tk.Frame(self.root, padx=15, pady=15, bd=2, relief=tk.RIDGE)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        self.right_frame = tk.Frame(self.root, padx=15, pady=15)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_form_fields()

        self.create_customer_table()
        
        self.create_buttons()
        
        self.refresh_customer_list()

    def create_form_fields(self):
        form_frame = tk.LabelFrame(self.left_frame, text="Müşteri Bilgileri", padx=5, pady=5)
        form_frame.pack(fill=tk.X)

        labels = ["Ad:", "Soyad:", "E-posta:", "Telefon:"]
        self.entries = {}
        self.validation_labels = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if label == "Telefon:":
                phone_frame = tk.Frame(form_frame)
                phone_frame.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
                
                tk.Label(phone_frame, text="+90", font=('Arial', 10)).pack(side=tk.LEFT)
                
                phone_entry = tk.Entry(
                    phone_frame, 
                    width=15,
                    validate="key",
                    validatecommand=(form_frame.register(self.validate_phone_input), '%P')
                )
                phone_entry.pack(side=tk.LEFT)
                phone_entry.bind("<KeyRelease>", self.format_phone_input)
                phone_entry.bind("<FocusOut>", self.validate_phone)
                
                self.entries["telefon"] = phone_entry
            else:
                entry = tk.Entry(form_frame, width=25)
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.entries[label[:-1].lower()] = entry
            
            validation_lbl = tk.Label(form_frame, text="", fg="red")
            validation_lbl.grid(row=i, column=2, padx=5)
            self.validation_labels[label[:-1].lower()] = validation_lbl
            
            if label == "E-posta:":
                entry.bind("<FocusOut>", lambda e: self.validate_email())

    def create_customer_table(self):
        list_frame = tk.LabelFrame(self.right_frame, text="Müşteri Listesi", padx=5, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Ad", "Soyad", "E-posta", "Telefon", "Kayıt Tarihi")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='extended')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "E-posta" else 150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.load_selected_customer)

        # Üst buton grubu
        top_button_frame = tk.Frame(list_frame)
        top_button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            top_button_frame,
            text="Sil",
            command=self.delete_customer,
            width=10,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            top_button_frame, 
            text="E-posta Gönder", 
            command=self.open_email_dialog,
            width=15
        ).pack(side=tk.RIGHT, padx=5)

    def create_buttons(self):
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, pady=10)

        tk.Button(button_frame, text="Kaydet", command=self.save_customer, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Temizle", command=self.clear_form, width=12).pack(side=tk.LEFT, padx=2)

    def delete_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Lütfen silmek için bir müşteri seçin!")
            return
        
        if messagebox.askyesno("Onay", "Seçili müşteriyi silmek istediğinize emin misiniz?"):
            for item_id in selected:
                customer_id = self.tree.item(item_id)['values'][0]
                cursor = self.db.conn.cursor()
                cursor.execute("DELETE FROM musteriler WHERE id=?", (customer_id,))
                self.db.conn.commit()
            
            messagebox.showinfo("Başarılı", "Müşteri başarıyla silindi!")
            self.refresh_customer_list()

    def open_email_dialog(self):
        selected = self.tree.selection()
        if not selected:
            if not messagebox.askyesno("Uyarı", "Hiç müşteri seçilmedi. Tüm müşterilere e-posta gönderilsin mi?"):
                return
        
        email_dialog = tk.Toplevel(self.root)
        email_dialog.title("E-posta Gönder")
        email_dialog.geometry("500x300")
        
        tk.Label(email_dialog, text="Konu:").pack(pady=(10, 0))
        subject_entry = tk.Entry(email_dialog, width=50)
        subject_entry.pack()
        subject_entry.insert(0, "Hoş Geldiniz")
        
        tk.Label(email_dialog, text="Mesaj:").pack(pady=(10, 0))
        message_text = tk.Text(email_dialog, width=50, height=10)
        message_text.pack()
        message_text.insert("1.0", "Sayın Müşterimiz,\n\nBizi tercih ettiğiniz için teşekkür ederiz.\n\nSaygılarımızla,\nFirma Adı")
        
        def send_selected_emails():
            konu = subject_entry.get()
            icerik = message_text.get("1.0", tk.END)
            
            if not selected:
                customers = self.db.musteri_listele()
                for customer in customers:
                    email = customer[3]
                    ad_soyad = f"{customer[1]} {customer[2]}"
                    personalized_content = icerik.replace("Müşterimiz", ad_soyad)
                    self.email_service.email_gonder(email, konu, personalized_content)
            else:
                for item_id in selected:
                    item = self.tree.item(item_id)
                    email = item['values'][3]
                    ad_soyad = f"{item['values'][1]} {item['values'][2]}"
                    personalized_content = icerik.replace("Müşterimiz", ad_soyad)
                    self.email_service.email_gonder(email, konu, personalized_content)
            
            messagebox.showinfo("Başarılı", "E-postalar gönderildi!")
            email_dialog.destroy()
        
        tk.Button(email_dialog, text="Gönder", command=send_selected_emails).pack(pady=10)

    def validate_phone_input(self, new_text):
        return (new_text.isdigit() or new_text == "") and len(new_text) <= 10

    def format_phone_input(self, event):
        widget = event.widget
        current_text = widget.get()
        cleaned = ''.join(filter(str.isdigit, current_text))[:10]
        widget.delete(0, tk.END)
        widget.insert(0, cleaned)
        self.validate_phone()

    def validate_email(self, event=None):
        email = self.entries["e-posta"].get()
        lbl = self.validation_labels["e-posta"]
        
        if not email:
            lbl.config(text="")
            return True
        
        if self.validations.email_format_dogrula(email):
            lbl.config(text="✓", fg="green")
            return True
        else:
            lbl.config(text="Geçersiz format!", fg="red")
            return False

    def validate_phone(self, event=None):
        phone = self.entries["telefon"].get()
        lbl = self.validation_labels["telefon"]
        
        if not phone:
            lbl.config(text="")
            return False
        
        if len(phone) == 10 and phone.isdigit():
            lbl.config(text="✓", fg="green")
            return True
        else:
            lbl.config(text="10 rakam giriniz!", fg="red")
            return False

    def save_customer(self):
        phone = self.entries["telefon"].get()
        if len(phone) == 10:
            telefon = f"+90{phone}"
        else:
            messagebox.showerror("Hata", "Telefon numarası 10 rakam olmalıdır!")
            return
        
        ad = self.entries["ad"].get().strip()
        soyad = self.entries["soyad"].get().strip()
        email = self.entries["e-posta"].get().strip()
        
        if not all([ad, soyad, email]) or not self.validate_phone():
            messagebox.showerror("Hata", "Tüm alanları doğru doldurunuz!")
            return
        
        if self.db.musteri_ekle(ad, soyad, email, telefon):
            konu = "Hoş Geldiniz"
            icerik = f"Sayın {ad} {soyad},\n\nBizi tercih ettiğiniz için teşekkür ederiz."
            self.email_service.email_gonder(email, konu, icerik)
            
            messagebox.showinfo("Başarılı", "Müşteri başarıyla kaydedildi ve hoşgeldin e-postası gönderildi!")
            self.clear_form()
            self.refresh_customer_list()
        else:
            messagebox.showerror("Hata", "Bu e-posta zaten kayıtlı!")

    def clear_form(self):
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
        
        for lbl in self.validation_labels.values():
            lbl.config(text="")

    def load_selected_customer(self, event):
        selected = self.tree.selection()
        if selected:
            self.clear_form()
            item = self.tree.item(selected[0])
            values = item['values']
            
            self.entries["ad"].insert(0, values[1])
            self.entries["soyad"].insert(0, values[2])
            self.entries["e-posta"].insert(0, values[3])
            self.entries["telefon"].insert(0, values[4].replace("+90", ""))

    def refresh_customer_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for musteri in self.db.musteri_listele():
            self.tree.insert("", tk.END, values=musteri)
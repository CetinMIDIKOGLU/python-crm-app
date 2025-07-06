import re

class Validations:
    @staticmethod
    def email_format_dogrula(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def telefon_format_dogrula(telefon):
        
        telefon = telefon.strip()
        
        if telefon.startswith("+90"):
            telefon = telefon.replace(" ", "")
            if len(telefon) == 12:  
                return True
        
        rakamlar = ''.join(filter(str.isdigit, telefon))
        
        return len(rakamlar) == 10 or (len(rakamlar) == 11 and rakamlar.startswith('0'))
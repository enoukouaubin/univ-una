from datetime import datetime
import random
import string

def generate_reservation_number():
    date_str = datetime.now().strftime('%Y%m%d')  # 8 caractères (ex. 20250609)
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))  # 2 caractères
    return f"RES-{date_str}-{random_str}"  # RES-YYYYMMDD-XX (4+8+1+2=15)

def generate_ticket_number():
    date_str = datetime.now().strftime('%Y%m%d')  # 8 caractères
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))  # 5 caractères
    return f"TIC-{date_str}-{random_str}"  # TIC-YYYYMMDD-XXXXX
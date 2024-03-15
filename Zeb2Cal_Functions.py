import pdfplumber
import re
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from cryptography.fernet import Fernet
from dotenv import load_dotenv
_ = load_dotenv()


allowed_shifts = {}


# parser with pdfplumber
def parse_pdf(f):
    try:
        with pdfplumber.open(f) as pdf:
            name = "Unbekannt"
            page = pdf.pages[0]
            table_raw = page.extract_table({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
            for index, item in enumerate(table_raw[0]):
                if item:
                    firstshift = index
                    break
            table_s = table_raw[1][firstshift:]
            table_p = table_raw[2][firstshift:]
            for index, item in enumerate(table_p):
                if item:
                    table_s[index] = item
            text = page.extract_text_simple(x_tolerance=3, y_tolerance=3)
            names = re.findall(r"^(.+),", text, re.MULTILINE)
            name = names[0]
            months = re.findall(r"\d{2}.(\d{2}).\d{4} - \d{2}.\d{2}.\d{4}", text)
            month = months[0]
            years = re.findall(r"\d{2}.\d{2}.(\d{4}) - \d{2}.\d{2}.\d{4}", text)
            year = years[0]
            return table_s, month, year, name
    except:
        return None, None, None, None


# create calender from shifts with ics
def ics_exporter(shifts, month, year):
    c = Calendar(creator="Zeb2Cal")
    i = 0
    local = pytz.timezone("Europe/Berlin")
    now = datetime.now()
    start_day = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
    for shift in shifts:
        if shift == "--":
            i += 1
        else:
            e = Event()
            e.name = shift
            curr_day = start_day + timedelta(days=i)
            if shift in allowed_shifts and allowed_shifts[shift] != []:
                start = datetime.strptime(f"{curr_day.date()} {allowed_shifts[shift][0]}", "%Y-%m-%d %H:%M")
                start_de = local.localize(start, is_dst=None)
                start_utc = start_de.astimezone(pytz.utc)
                end_utc = start_utc + timedelta(hours=float(allowed_shifts[shift][1]))
                e.created = now
                e.begin = f"{start_utc}"
                e.end = f"{end_utc}"
            else:
                e.begin = curr_day
                e.created = now
                e.make_all_day()
            c.events.add(e)
            i += 1
    return c


# send email to user
def send_mail(file_path, name, month, year, email):
    # Email Configuration
    sender_email_encrypt = os.environ.get("EMAIL_ADDRESS")
    server_password_encrypt = os.environ.get("EMAIL_PASSWORD")
    receiver_email = email
    subject = f"Dienstplan {name}"
    body = f"Im Anhang finden sie den Dienstplan von {name} für {month}.{year}."

    # decryption key
    key = os.environ.get("KEY")

    # prepare variables for encoding
    while len(key) % 4 !=0:
        key += "="
    while len(sender_email_encrypt) % 4 !=0:
        sender_email_encrypt += "="
    while len(server_password_encrypt) % 4 !=0:
        server_password_encrypt += "="

    # decrypt
    fernet = Fernet(key.encode())
    sender_email = fernet.decrypt(sender_email_encrypt).decode()
    server_password = fernet.decrypt(server_password_encrypt).decode()

    # Email Setup
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach body
    message.attach(MIMEText(body, "plain"))

    # Attach file
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(file_path)}")
        message.attach(part)

    # Sending Email
    with smtplib.SMTP_SSL("smtp.strato.com", 465) as server:
        server.login(sender_email, server_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


# check if user email is valid 
def check_mail(email):
    # Regular expression pattern for validating email addresses
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Match the pattern with the email address
    return bool(re.match(pattern, email))

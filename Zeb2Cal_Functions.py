import pdfplumber
import re
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz


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
            table=[]
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
     

def extract_schedule(shifts):
    i = -1
    bad_shifts = []
    for shift in shifts:
        i += 1
        if not shift:
            shift = "?"
        if shift not in allowed_shifts:
            while True:
                if shift[0:2] in allowed_shifts:
                    shifts[i] = shift[0:2]
                    break
                elif shift[0:1] in allowed_shifts:
                    shifts[i] = shift[0:1]
                    break
                elif shift.upper() in allowed_shifts:
                    shifts[i] = shift.upper()
                    break
                else:
                    bad_shifts[(i + 1)] = shift
                    break
    return shifts, bad_shifts


def ics_exporter(shifts, month, year):
    c = Calendar(creator="shiftparse")
    i = 0
    local = pytz.timezone("Europe/Berlin")
    now = datetime.now()
    start_day = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
    for shift in shifts:
        if shift == "--":
            i += 1
            continue
        else:
            e = Event()
            e.name = shift
            curr_day = start_day + timedelta(days=i)
            if shift in allowed_shifts and allowed_shifts[shift] != []:
                start = datetime.strptime(f"{curr_day.date()} {allowed_shifts[shift][0]}", "%Y-%m-%d %H:%M")
                start_de = local.localize(start, is_dst=None)
                start_utc = start_de.astimezone(pytz.utc)
                end_utc = start_utc + timedelta(hours=float(allowed_shifts[shift][1]))
                e.created = (now)
                e.begin = f"{start_utc}"
                e.end = f"{end_utc}"
            else:
                e.begin = curr_day
                e.created = (now)
                e.make_all_day()
            c.events.add(e)
            i += 1
    return c
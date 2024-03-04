import pdfplumber
import tabula
import re
from fpdf import FPDF
from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz


allowed_shifts = {'*9': [],
                  '*C': [],
                  'AK': ["07:00", "9"],
                  'BH': ["07:30", "12.75"],
                  'BN': ["19:30", "12.5"],
                  'BO': ["07:30", "8.5"],
                  'BT': ["07:30", "12.5"],
                  'DP': ["07:30", "12.5"],
                  'EZ': [],
                  'F3': ["09:00", "3.5"],
                  'IH': ["07:30", "12.75"],
                  'IN': ["19:00", "12.75"],
                  'IO': ["07:00", "9"],
                  'IS': ["07:00", "8.5"],
                  'IT': ["07:00", "12.75"],
                  'IW': [],
                  'KA': ["08:00", "8"],
                  'KS': ["09:00", "8.5"],
                  'N1': ["19:30", "12.25"],
                  'N2': ["19:30", "12.25"],
                  'NN': ["19:30", "12.25"],
                  'NO': ["07:30", "8.5"],
                  'NR': ["07:45", "8.5"],
                  'NS': ["11:30", "8.5"],
                  'NT': ["07:30", "12.25"],
                  'NÄ': ["07:30", "8.5"],
                  'T1': ["07:30", "12.5"],
                  'T2': ["07:30", "12.5"],
                  'TB': ["07:00", "8.5"],
                  'U': [],
                  'x': []

}
months_de = {
    "Januar": "01",
    "Februar": "02",
    "März": "03",
    "April": "04",
    "Mai": "05",
    "Juni": "06",
    "Juli": "07",
    "August": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Dezember": "12"

}


# parser with pdfplumber
def parse_pdf(f):
    try:
        with pdfplumber.open(f) as pdf:
            firstshift = 0
            lastshift = 0
            page = pdf.pages[0]
            table_raw = page.extract_table({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
            print(table_raw)
            table=[]
            for line in table_raw:
                if line[0]:
                    table.append(line)
            for line in table_raw:
                if "1." and "2." and "3." in line:
                    firstshift = line.index("1.")
                    for pos in line[firstshift:]:
                        if pos and "." in pos:
                            lastshift = line.index(pos)
            text = page.extract_text_simple(x_tolerance=3, y_tolerance=3)
            matches = re.search(r"Dienstplan (\w.+) (\d{4})", text)
            names = []
            for line in table:
                if line[0]:
                    name = line[0]
                    name = name.casefold()[0:7]
                    if name[0:3] != "von":
                        name = name.split()[0]
                    names.append(name)
            month, year = matches.groups()
            return table, month, year, names, firstshift, lastshift
    except:
        return None, None, None, None


def check_name(name, names):
    table_name = name.strip().casefold()[0:7]
    if table_name in names and names.count(table_name) == 1:
        return names.index(table_name)
    else:
        return None
     

def extract_schedule(table, index, firstshift, lastshift):
    shifts = table[index][firstshift:(lastshift + 1)]
    corr_shifts, bad_shifts = check_data(shifts)
    return corr_shifts, bad_shifts
    

def check_data(shifts):
    length = len(shifts)
    i = -1
    bad_shifts = {}
    for shift in shifts:
        i += 1
        if shift and " " in shift:
            c = i
            com_shifts = shift.split()
            for s in com_shifts:
                if c < length:
                    shifts[c] = s
                    c += 1
    i = -1
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


def ics_exporter(shifts, name, month, year):
    c = Calendar(creator="shiftparse")
    i = 0
    local = pytz.timezone("Europe/Berlin")
    now = datetime.now()
    start_day = datetime.strptime(f"{year}-{months_de[month]}-01", "%Y-%m-%d")
    for shift in shifts:
        if shift == "x":
            i += 1
            continue
        else:
            e = Event()
            e.name = shift
            curr_day = start_day + timedelta(days=i)
            if allowed_shifts[shift] != []:
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


def pdf_exporter(schedule, dates, name, month, year):
    pdf = FPDF(orientation="L")
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 22)
    pdf.set_y(20)
    pdf.cell(txt=f"Schedule for {name}, {month} {year}", center=True)
    pdf.set_y(70)
    pdf.set_font('helvetica', '', 12)
    data = [dates, schedule]
    with pdf.table(text_align="CENTER", borders_layout="INTERNAL") as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    pdf.set_y(120)
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(txt=f"Legend", center=True)
    pdf.set_y(140)
    pdf.set_font('helvetica', '', 12)
    shifts = list(set(schedule))
    shifts.sort()
    shifts = [i for i in shifts if i not in ["U", "x", "EZ", "IW", "*9", "*C"]]
    width = len(shifts)
    times = []
    for shift in shifts:
        t = allowed_shifts[shift]
        times.append(f"{t[0]} - {t[1]}")
    data = [shifts, times]
    with pdf.table(width=(width * 30), text_align="CENTER", borders_layout="INTERNAL") as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    pdf.output(f"Schedule_{name}_{month}_{year}.pdf")
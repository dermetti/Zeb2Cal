import csv
import datetime
from datetime import datetime, date, timedelta



allowed_shifts = {'*9': [],
                  '*C': [],
                  'AK': ["07:00", "16:00"],
                  'BH': ["07:30", "20:15"],
                  'BN': ["19:30", "08:00"],
                  'BO': ["07:30", "16:00"],
                  'BT': ["07:30", "20:00"],
                  'DP': ["07:30", "20:00"],
                  'EZ': [],
                  'F3': ["09:00", "12:30"],
                  'IH': ["07:30", "20:15"],
                  'IN': ["19:00", "07:45"],
                  'IO': ["07:00", "16:00"],
                  'IS': ["07:00", "15:30"],
                  'IT': ["07:00", "19:45"],
                  'IW': [],
                  'KA': ["08:00", "16:00"],
                  'KS': ["09:00", "17:30"],
                  'N1': ["19:30", "07:45"],
                  'N2': ["19:30", "07:45"],
                  'NN': ["19:30", "07:45"],
                  'NO': ["07:30", "16:00"],
                  'NR': ["07:45", "16:15"],
                  'NS': ["11:30", "20:00"],
                  'NT': ["07:30", "19:45"],
                  'NÄ': ["07:30", "16:00"],
                  'T1': ["07:30", "20:00"],
                  'T2': ["07:30", "20:00"],
                  'TB': ["07:00", "15:30"],
                  'U': [],
                  'x': []
}

#time = "08:30"
#duration="24.5"
#start_day = datetime.strptime(f"2023-10-01", "%Y-%m-%d")
#start_day = start_day + timedelta(days=1)
#start_day2 = datetime.strptime(f"{start_day.date()} {time}", "%Y-%m-%d %H:%M")
#print(start_day2)
#end_day = start_day2 + timedelta(hours=float(duration))
#print(end_day)

for shift in allowed_shifts:
    if allowed_shifts[shift] != []:
        start = datetime.strptime(f"{allowed_shifts[shift][0]}", "%H:%M")
        end = datetime.strptime(f"{allowed_shifts[shift][1]}", "%H:%M")
        delta = end - start
        print(shift, delta)

    else:
        continue

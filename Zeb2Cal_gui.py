import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
from Zeb2Cal_Functions import *


class Schedule:
    def __init__(self, name=None, pdf_file=None, table=None, month=None, year=None, names=None, firstshift=None, lastschift=None, index=None, shifts=None, bad_shifts=None):
        self.name = name
        self.pdf_file = pdf_file
        self.table = table
        self.month = month
        self.year = year
        self.names = names
        self.firstshift = firstshift
        self.lastshift = lastschift
        self.index = index
        self.shifts = shifts
        self.bad_shifts = bad_shifts

schedule = Schedule()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AIRCal")
        self.geometry("600x400")
        #self.iconbitmap(r'.\AIRCal_icon.ico')
        self.resizable(False, False)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label = tk.Label(self, text="AIRCal ICS Kalender Export", font=("Century Gothic", 24, "bold"), fg="dark blue")
        label.grid(row=0, column=0, pady=10)

        self.input_frame = Input_Frame(self)
        self.raise_frame(self.input_frame)

        self.name_frame = Name_Frame(self)
        self.export_frame = Export_Frame(self)
        self.shifts_frame = Shifts_Frame(self)
        
    def raise_frame(self, frame):
        frame.configure(highlightbackground="grey", highlightthickness=1)
        frame.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        frame.tkraise()

    def reconfigure(self):
        self.geometry("800x400")


class Input_Frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # widgets
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        label1 = tk.Label(self, text="Dienstplan einlesen", font=("Century Gothic", 16, "bold"), fg="dark blue")
        label1.grid(column=0, row=0, pady=10, columnspan=2)

        #label2 = tk.Label(self, text="Ihr Name wie am Dienstplan", font=("Helvetica", 9))
        #label2.grid(column=0, row=1, pady=10, padx=10, sticky=tk.E)

        #entry1 = tk.Entry(self)
        #entry1.grid(column=1, row=1, pady=10, padx=10, sticky=tk.W)

        button1 = ttk.Button(self, text="Dienstplan öffnen", command=lambda: self.open_file())
        button1.grid(column=0, row=2, columnspan=2, pady=10)

        file_path = tk.Label(self, text=f"Datei: nicht angegeben", font=("Helvetica", 9), bg="white")
        file_path.grid(column=0, row=3, columnspan=2, pady=10)

        analyze_btn = ttk.Button(self, text="Scannen", command=lambda: self.analyze(), state="disabled")
        analyze_btn.grid(column=0, row=4, columnspan=2, pady=10)

        error_message = tk.Label(self, text="", font=("Helvetica", 9), fg="red")
        error_message.grid(column=0, row=5, columnspan=2, pady=10)

        # Instance variables
        self.file_path = file_path
        self.analyze_btn = analyze_btn
        self.error_message = error_message
        self.parent = parent

    def open_file(self):
        schedule.pdf_file = fd.askopenfilename(title="Dienstplan öffnen", initialdir="/", filetypes=[("PDF Datei", "*.pdf")])
        self.file_path["text"] = f"Datei: {schedule.pdf_file}"
        if schedule.pdf_file[-4:] == ".pdf":
            self.analyze_btn["state"] = "normal"

    def analyze(self):
        self.error_message["text"] = ""
        schedule.shifts, schedule.month, schedule.year, schedule.name = parse_pdf(schedule.pdf_file)
        if not schedule.shifts or not schedule.month or not schedule.year:
            self.error_message["text"] = "Fehler: PDF kann nicht gelesen werden"
        else:
            self.parent.raise_frame(self.parent.export_frame)
#            schedule.shifts, schedule.bad_shifts = extract_schedule(schedule.table)
#            if schedule.bad_shifts:
#                self.parent.raise_frame(self.parent.shifts_frame)
#            else:
#                self.parent.raise_frame(self.parent.export_frame)


class Name_Frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)

        label1 = tk.Label(self, text="Name konnte nicht gefunden werden, bitte aus Liste auswählen", font=("Helvetica", 11, "bold"), fg="red")
        label1.grid(column=0, row=0, pady=10)

        self.namebox = ttk.Combobox(self, textvariable=None, postcommand=self.update)
        self.namebox['state'] = 'readonly'
        self.namebox.grid(column=0, row=1, pady=10)

        button = ttk.Button(self, text="Bestätigen", command=self.ex_check_name)
        button.grid(column=0, row=2, pady=10)

        self.error_message = tk.Label(self, text="", font=("Helvetica", 9), fg="red")
        self.error_message.grid(column=0, row=3, pady=10)

        # variables
        self.parent = parent

    def ex_check_name(self):
        if self.namebox.get():
            schedule.name = self.namebox.get()
            schedule.index = check_name(schedule.name, schedule.names)
            schedule.shifts, schedule.bad_shifts = extract_schedule(schedule.table, schedule.index)
            if schedule.bad_shifts:
                self.parent.raise_frame(self.parent.shifts_frame)
            else:
                self.parent.raise_frame(self.parent.export_frame)
        else:
            self.error_message["text"]="Bitte Name auswählen"

    def update(self):
        title_names = [i.title() for i in schedule.names]
        sorted_names = sorted(title_names)
        self.namebox["values"]=sorted_names


class Export_Frame(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            self.grid_columnconfigure(0, weight=1)

            self.bind("<Expose>", self.table)

            label1 = tk.Label(self, text="Bitte Daten vor Export kontrollieren", font=("Helvetica", 11, "bold"))
            label1.grid(column=0, row=0, pady=10)

            self.label2 = tk.Label(self, text="", font=("Helvetica", 11, "bold"))
            self.label2.grid(column=0, row=1, pady=10)

            self.frame = tk.Frame(master=self)
            self.frame.grid(column=0, row=2, pady=10)

            button = ttk.Button(self, text="Als ICS exportieren", command=self.export)
            button.grid(column=0, row=3, pady=10)

            # variables
            self.parent = parent

        def table(self, *args):
            self.parent.reconfigure()
            self.label2["text"]=f"Dienstplan für {schedule.month}.{schedule.year}"
            for i in range(2):
                for j in range(len(schedule.shifts)):
                    if i == 0:
                        l = tk.Label(master=self.frame, text=f"{(j + 1):02d}.", relief="ridge")
                        l.grid(row=i, column=j, sticky="nsew")
                    else:
                        l = tk.Label(master=self.frame, text=f"{schedule.shifts[j]}", relief="ridge")
                        l.grid(row=i, column=j, sticky="nsew")

        def export(self):
            c = ics_exporter(schedule.shifts, schedule.month, schedule.year)
            file_path = fd.asksaveasfilename(title="Dienstplan speichern", initialdir="/", initialfile=f"Dienstplan_{schedule.name}_{schedule.month}_{schedule.year}", filetypes=[("ICS Datei", "*.ics")], defaultextension=".ics")
            cal = c.serialize().split()      
            if file_path:          
                with open(file_path, "w", encoding="utf-8") as file:
                    for line in cal:
                        file.write(line)
                        file.write("\n")
            self.parent.destroy()


class Shifts_Frame(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            self.bind("<Expose>", self.corr)

            # variables
            self.parent = parent
            corr_shifts = [i for i in allowed_shifts]
            self.sort_corr_shifts = sorted(corr_shifts)

            label1 = tk.Label(self, text="Es konnten nicht alle Schichten ausgelesen werden, bitte korrigieren", font=("Helvetica", 11, "bold"), fg="red")
            label1.grid(column=0, row=0, pady=10, columnspan=2)

            self.label2 = tk.Label(self, text="", font=("Helvetica", 9))
            self.label2.grid(column=0, row=1, pady=10, columnspan=2)

            self.combobox = ttk.Combobox(self, values=self.sort_corr_shifts)
            self.combobox['state'] = 'readonly'
            self.combobox.grid(column=0, row=2, pady=10, padx=5, sticky="e")  

            button1 = ttk.Button(self, text="Bestätigen", command=lambda: self.confirm(self.combobox))
            button1.grid(column=1, row=2, pady=10, padx= 5, sticky="w")          

            self.error_message = tk.Label(self, text="", font=("Helvetica", 9), fg="red")
            self.error_message.grid(column=0, row=3, pady=10, columnspan=2)


        def corr(self, *args):
            self.error_message["text"] = ""
            try:
                s = int(list(schedule.bad_shifts.keys())[0])
                self.label2["text"]=f"Schicht | {schedule.bad_shifts[s]} | am {s}. {schedule.month} wurde nicht erkannt, bitte korrekte Schicht eingeben:"
            except:
                pass

                
        def confirm(self, combobox):
            shift = combobox.get()
            if not shift:
                self.error_message["text"] = "Keine Schicht ausgewählt"
            else:
                s = int(list(schedule.bad_shifts.keys())[0])
                index = s - 1
                schedule.shifts[index] = shift
                del schedule.bad_shifts[s]
                if not schedule.bad_shifts:
                    self.parent.raise_frame(self.parent.export_frame)
                else:
                    self.combobox.set("")
                    self.corr()


if __name__ == "__main__":
    app = App()
    app.mainloop()
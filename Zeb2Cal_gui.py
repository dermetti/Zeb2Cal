import tkinter as tk
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from Zeb2Cal_Functions import *
import webbrowser


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


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename = "journal")
        self.title("Zeb2Cal")
        self.geometry("600x400")
        self.resizable(False, False)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label = ttk.Label(self, text="Zeb2Cal ICS Kalender Export", font=("default", 24, "bold"), bootstyle="primary")
        label.grid(row=0, column=0, pady=10)

        self.input_frame = Input_Frame(self)
        self.raise_frame(self.input_frame)

        self.export_frame = Export_Frame(self)
        
    def raise_frame(self, frame):
        frame.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        frame.tkraise()

    def reconfigure(self):
        self.geometry("800x400")


class Input_Frame(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text = "einlesen")

        # widgets
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        rowcount = 0
        label1 = ttk.Label(self, text="Dienstplan einlesen", font=("default", 16, "bold"), bootstyle="dark")
        label1.grid(column=0, row=rowcount, pady=10, columnspan=2)

        rowcount+=1
        button1 = ttk.Button(self, text="Dienstplan suchen", command=lambda: self.open_file())
        button1.grid(column=0, row=rowcount, columnspan=2, pady=10)

        rowcount+=1
        file_path = ttk.Label(self, text=f"Datei: nicht angegeben", font=("default", 9), bootstyle="info")
        file_path.grid(column=0, row=rowcount, columnspan=2, pady=10)

        rowcount+=1
        analyze_btn = ttk.Button(self, text="Scannen", command=lambda: self.analyze(), state="disabled")
        analyze_btn.grid(column=0, row=rowcount, columnspan=2, pady=10)

        rowcount+=1
        link1 = ttk.Label(self, text="Anleitung", cursor="hand2", bootstyle="info-inverse", padding=5)
        link1.grid(column=0, row=rowcount, columnspan=2, pady=10)
        link1.bind("<Button-1>", lambda _: self.callback("https://github.com/dermetti/Zeb2Cal?tab=readme-ov-file#readme"))

        rowcount+=1
        error_message = ttk.Label(self, text="", font=("default", 9), bootstyle="danger")
        error_message.grid(column=0, row=rowcount, columnspan=2, pady=10)

        # Instance variables
        self.file_path = file_path
        self.analyze_btn = analyze_btn
        self.error_message = error_message
        self.parent = parent

    def callback(_, url):
        webbrowser.open_new(url)

    def open_file(self):
        schedule.pdf_file = fd.askopenfilename(title="Dienstplan öffnen", initialdir="/", filetypes=[("PDF Datei", "*.pdf")])
        self.file_path["text"] = f"Datei: {schedule.pdf_file}"
        if schedule.pdf_file[-4:] == ".pdf":
            self.analyze_btn["state"] = "normal"

    def analyze(self, f=None):
        if f:
            schedule.pdf_file=f
        self.error_message["text"] = ""
        schedule.shifts, schedule.month, schedule.year, schedule.name = parse_pdf(schedule.pdf_file)
        if not schedule.shifts or not schedule.month or not schedule.year:
            self.error_message["text"] = "Fehler: PDF kann nicht gelesen werden"
        else:
            self.parent.raise_frame(self.parent.export_frame)



class Export_Frame(ttk.Labelframe):
        def __init__(self, parent):
            super().__init__(parent, text = "exportieren" )
            self.grid_columnconfigure(0, weight=1)

            self.bind("<Expose>", self.table)

            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            label1 = ttk.Label(self, text="Bitte Daten vor Export kontrollieren", font=("default", 11, "bold"), bootstyle="dark")
            label1.grid(column=0, row=0, pady=10, columnspan=2)

            self.label2 = ttk.Label(self, text="", font=("default", 11, "bold"), bootstyle="dark")
            self.label2.grid(column=0, row=1, pady=10, columnspan=2)

            self.frame = ttk.Frame(master=self)
            self.frame.grid(column=0, row=2, pady=10, columnspan=2)

            button = ttk.Button(self, text="Als ICS exportieren", command=self.export)
            button.grid(column=0, row=3, pady=10, columnspan=2)

            button2 = ttk.Button(self, text="Als Email senden an:", command=self.mail)
            button2.grid(column=0, row=4, pady=10, padx=10, sticky="e")

            entry = ttk.Entry(self, bootstyle="primary", width=40)
            entry.grid(column=1, row=4, pady=10, sticky="w")

            self.label3 = ttk.Label(self, text="", font=("default", 9), bootstyle="danger")
            self.label3.grid(column=0, row=5, pady=10, columnspan=2)

            # variables
            self.parent = parent
            self.entry = entry

        def table(self, *args):
            self.parent.reconfigure()
            self.label2["text"]=f"Dienstplan für {schedule.month}.{schedule.year}"
            for i in range(2):
                for j in range(len(schedule.shifts)):
                    if i == 0:
                        l = ttk.Label(master=self.frame, text=f"{(j + 1):02d}.", relief="ridge", bootstyle="dark", padding=2)
                        l.grid(row=i, column=j, sticky="nsew")
                    else:
                        l = ttk.Label(master=self.frame, text=f"{schedule.shifts[j]}", relief="ridge", bootstyle="dark", padding=2)
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
            

        def mail(self):
            email = self.entry.get()
            if check_mail(email) == False:
                self.label3.config(bootstyle="danger")
                self.label3["text"] = "Email Adresse ungültig"
            else:
                c = ics_exporter(schedule.shifts, schedule.month, schedule.year)
                cal = c.serialize().split() 
                file_path = f"Dienstplan_{schedule.name}_{schedule.month}_{schedule.year}.ics"
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                            for line in cal:
                                file.write(line)
                                file.write("\n")
                    send_mail(file_path, schedule.name, schedule.month, schedule.year, email)
                    self.label3.config(bootstyle="success")
                    self.label3["text"] = "Email gesendet"
                    os.remove(file_path)
                except Exception as e:
                    self.label3.config(bootstyle="danger")
                    self.label3["text"] = f"Fehler: {e}"
                    os.remove(file_path)



if __name__ == "__main__":
    app = App()
    app.mainloop()
"""Project Work:
Version 1.0
Peter Briggs 12 May 2025
For Python 3 which should be installed with tkinter to manage windows.
#______________________________________________________________________________
#inputs: CSV files. Distance is a number of distance pairs. These are only
#starter distances, as the panel displayed can be edited before and after.
#Only set distances once per session unless the trackers move.
#Select & Load. Flyer file must have least "Index", "Cname", "Sname", "Rocket", "Recov",
#fields, or indexing will be out of bounds. Simple text, comma delimited.
#Manual entry fields Alt and Azimuth have zero checking which takes max of azm and 0.1 rad.
#Results can be viewed as CSV or in a spreadsheet.
#_______________________________________________________________________________
"""
import tkinter as tk
from tkinter import ttk
import csv
import datetime
import math
import os

MAX_ROWS = 60  
DATA_FILE = "LaunchData.csv"  
DISTANCE_FILE = "Distances.csv"  
RESULTS_FILE = "Results.csv"
BANNER = "DDARA Toowoomba"

DEFAULT_DIST = 1

class FileHandler:
    """Handles CSV file operations: loading and // no writing //saving data."""

    def __init__(self, file_name):
        self.file_name = file_name
        self.data = []  

    def is_number(self, value):
        """Checks if a value can be converted to a number (first line headings)."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def load_csv(self):
        """Loads CSV file and stores data, skipping headers if needed."""
        self.data = []  
        try:
            with open(self.file_name, newline="") as file:
                reader = csv.reader(file)
                data = list(reader)

                if data and not self.is_number(data[0][0]):  
                    data = data[1:]  

                for row in data:
                    if not row or all(cell.strip() == "" for cell in row):  
                        break
                    if len(self.data) < MAX_ROWS:
                        self.data.append(row)

        except FileNotFoundError:
            print(f"Error: {self.file_name} not found.")


class Flyer_Panel(tk.Toplevel):
    """A window for selecting and editing CSV data (n fields)."""
    """Also overridden to be a distance editor, so __Init__ is common to both. """
    def __init__(self, parent, file_handler, callback):
        super().__init__(parent)
        self.title("Select/Edit")
        self.file_handler = file_handler
        self.callback = callback  

        self.file_handler.load_csv()  

        self.selected_row = tk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.selected_row, state="normal", width=26)
        
        self.combobox.set("Choose")
        """ Need to check whether this init is being asked for distance or flyer"""
        """ Load self.file_handler.data into a list variable."""
        filedata =  self.file_handler.data
        for record in filedata:
            flyer = distance = record
            if len(flyer) > 2:
                self.combobox["values"] = [f"{flyer[0]} - {flyer[1]} {flyer[2]}-{flyer[3]}" for flyer in filedata]
            if len(flyer) < 3:
                self.combobox["values"] = [f"{distance[0]} - {distance[1]}" for distance in filedata]
        self.combobox.grid(row=0, column=1, columnspan=2, pady=10)
        self.combobox.bind("<<ComboboxSelected>>", self.populate_fields)

        self.entries = []  
        self.create_entry_fields()

        save_button = tk.Button(self, text="Select & Load", command=self.send_data)
        save_button.grid(row=MAX_ROWS + 2, column=0, columnspan=4, pady=10)

    def create_entry_fields(self):
        """Creates entry fields for editing the selected row."""
        labels = ["Index", "First name", "Surname", "Rkt", "Recov", "Mtr"] 
        for i, label in enumerate(labels):
            tk.Label(self, text=label).grid(row=1, column=i, padx=5, pady=2)
        for i in range(6):
            entry = tk.Entry(self, width=12)
            entry.grid(row=2, column=i, padx=5, pady=2)
            self.entries.append(entry)

    def populate_fields(self, event=None):
        """Fills entry fields with data from the selected row."""
        selection = self.combobox.current()
        if selection >= 0:  
            row_data = self.file_handler.data[selection]
            for i, entry in enumerate(self.entries):
                #entry.config(font=("Courier",12),state="normal")
                entry.config(state="normal") 
                entry.delete(0, tk.END)
                entry.insert(0, row_data[i] if i < len(row_data) else "")
                if i == 0:  
                    entry.config(state="readonly")

    def send_data(self):
        """Sends the selected data back to the main application."""
        selection = self.combobox.current()
        if selection >= 0:
            row_data = [self.entries[i].get() for i in range(6)]
            """sending entry data back to main window"""
            """as a list""" 
            self.callback(row_data) 
            self.destroy()  

class DistanceEditor(Flyer_Panel):
    """A override of Flyer Panel to get Distance to 2 trackers."""
    """ Create the two distance entry boxes  """
    def create_entry_fields(self):
        """Creates labels for distance entry fields in Column 1."""
        labels = ["Dist1", "Dist2"]
        for i, label in enumerate(labels):
            tk.Label(self, text=label).grid(row=(i+1), column=1, padx=5, pady=5)
        """ get default pair of distances from file """
        row_data = self.file_handler.data[DEFAULT_DIST]
        """ Assemble the entry fields on the page as column 2. """
        for i in range(2):
            entry = tk.Entry(self, width=18)
            entry.grid(row=(i+1), column=2, padx=15, pady=15)
            self.entries.append(entry)
            entry.insert(0, row_data[i] if i < len(row_data) else "")

    """ At this stage default values (DEFAULT_DIST) are loaded into the distance entry boxes."""
    def populate_fields(self, event=None):
        """Fills entry fields with data from the selected row."""
        selection = self.combobox.current()
        #selection['state'] = 'readonly'
        if selection >= 0:  
            row_data = self.file_handler.data[selection]
            for i, entry in enumerate(self.entries):
                #entry.config(font=("Courier",12),state="normal")
                entry.config(state="normal") 
                entry.delete(0, tk.END)
                entry.insert(0, row_data[i] if i < len(row_data) else "")
                if i == 0:
                    entry.config(state="normal")

    def send_data(self):
        """Sends the selected tracker distance data back to the main application."""
        """Take distances from the entry fields whether selected from list or filled in """
        row_data = [self.entries[i].get() for i in range(2)]
        """as a list"""
        self.callback(row_data)  
        self.destroy()  

class CalculationHandler:
    """Handles mathematical operations on extra fields and updates the results."""

    def __init__(self, callback):
        self.callback = callback  

    def perform_calculations(self, values):
        """Converts string inputs to float and performs calculations."""
        try:
            span = float(0.0)
            Elev1_degrees = float(values[2])
            Azim1_degrees = float(values[3])
            Elev2_degrees = float(values[4])
            Azim2_degrees = float(values[5])
            span = span + float(values[0]) + float(values[1])
            el1 = math.radians(Elev1_degrees)
            az1 = max(math.radians(Azim1_degrees), math.radians(0.1))# Azimuth = max(az1, 0.1)
            el2 = math.radians(Elev2_degrees)
            az2 = max(math.radians(Azim2_degrees), math.radians(0.1))
            gamma = 0.0
            closure_verdict = True
            """ Calculate distance from trackers to base of altitude measurement using Sine Rule. !all in Radians. """
            """ central interior angle"""            
            gamma = math.pi - az1 - az2
            """ Lateral distances """
            Os1 = span * (math.sin(az2) / math.sin(gamma))
            Os2 = span * (math.sin(az1) / math.sin(gamma))
            #print(gamma, Os1, Os2)
            """ heights """
            hA = (Os1 * math.tan(el1)if el1 else None)
            hB = (Os2 * math.tan(el2)if el2 else None)
            heights = [h for h in [hA, hB] if h is not None]
            if not heights:
                result_text = "Enter at least one elevation and distance."
                return None, None, None, None, None
            if not hA:
                pass #Work on using hB
            if not hB: 
                pass #Work on using hA   
            """ Find altitude using FAI method, 2 observers. """
            min_apogee = min(heights)
            max_apogee = max(heights)
            mean_apogee = (min_apogee + max_apogee)/2
            #print(heights, min_apogee, max_apogee)
            closure_percent = ((max_apogee - min_apogee)/(max_apogee + min_apogee))*100
            """ Closure is defined as less than 10 percent variation from mean. """
            if(closure_percent > 10):
                closure_verdict = False
            delta = max_apogee - min_apogee if len(heights) == 2 else 0
            avg_apogee_m = mean_apogee
            """ Convert to feet ICAO Standard """
            avg_apogee_ft = avg_apogee_m * 3.28084
            result_text = f"Alt:{avg_apogee_m:.0f}m, {avg_apogee_ft:.0f}ft \n Min:{min_apogee:.0f}m, Max:{max_apogee:.0f}m, Diff:{delta:.0f}m, Closure:{closure_verdict}"        
            """result_text as a string"""
           
            """ Test for divide by zero """
            #result1 = Alt1 / Alt2 if Alt2 != 0 else "Error (Div/0)"
            #result2 = Azim1 / Azim2 if Azim2 != 0 else "Error (Div/0)"
        except ValueError:
            result_text = "Error: Non-numeric input"
        self.callback(result_text)

class MainApp:
    """Main application window with results saving functionality."""

    """ for layout of labels and entries, odd column and evens column """

    def __init__(self, root):
        self.root = root
        self.root.title(BANNER)
        self.saved = ""
        self.file_handler = FileHandler(DATA_FILE)
        self.distance_handler = FileHandler(DISTANCE_FILE)
        self.calculator = CalculationHandler(self.update_results)

        menubar = tk.Menu(root)
        root.config(menu=menubar)

        load_menu = tk.Menu(menubar, tearoff=0)
        dist_menu = tk.Menu(menubar, tearoff=0)
        help_menu = tk.Menu(menubar, tearoff=0)
        exit_menu = tk.Menu(menubar, tearoff=0)
        
        load_menu.add_command(label="Load Flyer", command=self.open_flyer_panel)
        dist_menu.add_command(label="Load Distances", command=self.open_distance_editor)
        exit_menu.add_command(label="Exit", command=self.exit_program)

        """ Order of appearance in menubar """
        menubar.add_cascade(label="Load", menu=load_menu)
        menubar.add_cascade(label="Trackers", menu=dist_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        menubar.add_cascade(label="Exit", menu=exit_menu)
        
        
        
        labels = [
            "Index", "Cname", "Sname", "Rocket", "Recov",
            "Dist.T1", "Dist.T2", "Elev1", "Azim1", "Elev2", "Azim2"
        ]
        """ Work on getting 4 columns """
        self.entries = []
        for i, label in enumerate(labels): #11 labels
            """ Check for index zero for first field """
            if i == 0:
                tk.Label(root, text=label).grid(row=i, column=0, columnspan=1, padx=5, pady=5)
                entry = tk.Entry(root, width=5)
                entry.grid(row=i, column=1, columnspan = 1, padx=5, pady=5)
                self.entries.append(entry)
            else:
                """ Odd numbered labels to left, followed by entry boxes """
                if i & 1 != 0:
                    """ Odd based on modulo 1 test """
                    tk.Label(root, text=label,font=("Arial", 14)).grid(row=i, column=0, padx=5, pady=5)
                    entry = tk.Entry(root, width=15)
                    if i <= 5: entry.insert(0, label)
                    entry.grid(row=i, column=1, padx=5, pady=5)
                    self.entries.append(entry)
 
                if i & 1 == 0:
                    """ Even based on modulo 1 test Place back in line with previous indexed row i-1 """
                    tk.Label(root, text=label,font=("Arial", 14)).grid(row=i-1, column=2, padx=5, pady=5)
                    entry = tk.Entry(root, width=15)
                    if i <= 6: entry.insert(0, label)
                    entry.grid(row=i-1, column=3, padx=5, pady=5)
                    self.entries.append(entry)

        self.calculate_button = tk.Button(root, text="Calculate", command=self.run_calculations)
        self.calculate_button.grid(row=len(labels), column=0, columnspan=1, pady=5)

        self.result_label = tk.Label(root, text="Result: ", font=("Arial", 14))
        self.result_label.grid(row=len(labels) + 1, column=0, columnspan=4, pady=10)

        self.save_button = tk.Button(root, text="Save Results", command=self.save_results)
        self.save_button.grid(row=len(labels), column=2, columnspan=1, pady=5)
        
        self.saved_label = tk.Label(root, text=f"Saved?:{self.saved}", fg="green", font=("Arial", 12))
        self.saved_label.grid(row=len(labels), column=3, columnspan=2, pady=10)



    def open_flyer_panel(self):
        """Opens CSV editor for main data file."""
        Flyer_Panel(self.root, self.file_handler, self.receive_data)

    def open_distance_editor(self):
        """Opens Distance editor (inherit from CSV Editor) for distance data file."""
        DistanceEditor(self.root, self.distance_handler, self.receive_distance_data)

    def receive_data(self, data):
        """Receives and populates selected person - rocket - data in the main window."""
        for i in range(5):
            self.entries[i].delete(0, tk.END)
            self.entries[i].insert(0, data[i])
        self.saved = "No"
        self.saved_label.config(text = f"Saved?:{self.saved}")

    def receive_distance_data(self, data):
        """Receives and populates selected distance list in the main window."""
        for i in range(2):
            self.entries[i + 5].delete(0, tk.END)
            self.entries[i + 5].insert(0, data[i])
            #,font=("Calibri",12),justify="center")
            

    def run_calculations(self):
        """Fetches extra field values and runs calculations."""
        values = [self.entries[i+5].get() for i in range(6)] #########
        """values to come back as string"""
        #print(values)
        self.calculator.perform_calculations(values)

    def update_results(self, result_text):
        """Updates the results label with calculated values."""
        self.result_label.config(text=f"{result_text}")
        """result_text comes back as string"""
    
    def save_results(self):
        """Saves the results label text to an external CSV file with a timestamp."""
        result_text = self.result_label.cget("text").replace("Results: ", "").strip()
        person_rocket = [self.entries[i].get() for i in range(11)]
        s1 = ','.join(person_rocket)
        """person_rocket cast to string"""
        #print("S1:",s1)
        s2 = result_text.replace("\n", ",")
        #print("S2:",s2)
        sdatetime = (datetime.datetime.now().strftime("%Y:%m:%d,%H%M%S"))
        #print("Sdatetime:",sdatetime)
        """Convert string to list for writerow() """
        output_to_file = sdatetime.split(',') + s1.split(',') + s2.split(',')
        """concatenating strings"""
        """reinstating list from string"""
        #print(output_to_file) 
        if output_to_file:
            with open(RESULTS_FILE, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(output_to_file)
                #print((output_to_file), RESULTS_FILE)
                self.saved = "Yes"
                self.saved_label.config(text = f"Saved?:{self.saved}")
                """Clear the tracker values that have been saved to file"""
                for i in range(4):
                    #print(self.entries[i+7].get()) #Prints correct entries.
                    self.entries[i+7].delete(0,tk.END)

    def exit_program(self):
        self.root.destroy()


root = tk.Tk()
app = MainApp(root)
root.mainloop()

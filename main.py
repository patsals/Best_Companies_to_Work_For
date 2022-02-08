#Written by:
# GUI - Patrick Salsbury
# Plotting - Patrick Salsbury, Katerina Bosko

import tkinter as tk
import tkinter.messagebox as tkmb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sqlite3
import numpy as np
from textwrap import wrap
from collections.abc import Iterable


COLOR_SCHEME = {'back': '#0D19A3', 'button': '#15DB95', 'button_text': '#0D19A3', 'font': 'white',
                'button_pressed': 'springgreen4'}
FONT = "Cambria"


class MainWindow(tk.Tk):
    """
    Definition of the MainWindow class that acts as the primary menu selection screen
    """
    def __init__(self):
        """
        Default Constructor for MainWindow class
        """
        super().__init__()
        self.minsize(800, 600)
        self.resizable(False, False)
        self.title("")
        self.configure(bg=COLOR_SCHEME["back"])

        # connect to the database
        self._connection = sqlite3.connect("companies.db")
        self._cur = self._connection.cursor()

        tk.Label(self, text="© Katerina Bosko, Patrick Salsbury. Data by Forbes", bg=COLOR_SCHEME["back"], font=(FONT, 10)).grid(
            sticky="nw")
        frame = tk.Frame(self, bg=COLOR_SCHEME["back"])
        tk.Label(frame, text="500 Best Companies to Work For", fg=COLOR_SCHEME["font"], bg=COLOR_SCHEME["back"],
                 font=(FONT, 30, "bold")).grid(row=0, pady=40)
        tk.Button(frame, text="Display Top Employers by Rank", width=40, height=2, fg=COLOR_SCHEME["button_text"],
                  bg=COLOR_SCHEME["button"], activebackground=COLOR_SCHEME["button_pressed"],
                  activeforeground=COLOR_SCHEME["font"], font=(FONT, 15, "bold"),
                  command=lambda: self.subWindow(NumDisplayWindow, "Display Top Employers by Rank",
                                                 self.getEmployers())).grid(row=2, pady=5)
        tk.Button(frame, text="Display by Industry", fg=COLOR_SCHEME["button_text"], width=40, height=2,
                  bg=COLOR_SCHEME["button"], activebackground=COLOR_SCHEME["button_pressed"],
                  activeforeground=COLOR_SCHEME["font"], font=(FONT, 15, "bold"),
                  command=lambda: self.subWindow(DisplayListButtonWindow, "Display by Industry",
                                                 self.getIndustries())).grid(row=3, pady=5)
        tk.Button(frame, text="Display by Location", fg=COLOR_SCHEME["button_text"], width=40, height=2,
                  bg=COLOR_SCHEME["button"], activebackground=COLOR_SCHEME["button_pressed"],
                  activeforeground=COLOR_SCHEME["font"], font=(FONT, 15, "bold"),
                  command=lambda: self.subWindow(DisplayListButtonWindow, "Display by Location",
                                                 self.getLocations())).grid(row=4, pady=5)
        tk.Button(frame, text="Display by Trends", fg=COLOR_SCHEME["button_text"], width=40, height=2,
                  bg=COLOR_SCHEME["button"], activebackground=COLOR_SCHEME["button_pressed"],
                  activeforeground=COLOR_SCHEME["font"], font=(FONT, 15, "bold"), command=self.byTrend).grid(row=5,
                                                                                                             pady=5)
        frame.grid(padx=200)
        self.protocol("WM_DELETE_WINDOW",self.windowClosing)

    def windowClosing(self):
        """
        Protocol for when the MainWindow is closed
        :return: nothing
        """
        self._connection.close()
        self.destroy()

    def subWindow(self, windowClass, title, displayList):
        """
        Handles the functionality when one of the MainWindow buttons have been pressed by creating a
        DisplayListButtonWindow object
        :param windowClass: which class object to create
        :param title: title of window class object to create
        :param displayList: what to display in window class object
        :return: nothing
        """
        window = windowClass(self, title, displayList)
        self.wait_window(window)
        if window.isConfirmed():
            if type(window) == NumDisplayWindow:
                self._cur.execute("""
                    SELECT c.name, c.rank, ind.industry, st.state, c.year_founded, c.employees, c.desc
                    FROM Companies AS c
                    INNER JOIN States AS st
                    ON c.state_id = st.id
                    INNER JOIN Industries AS ind
                    ON c.industry_id = ind.id
                    WHERE rank = ?""",
                    (window.getSelection()[0],))

            elif type(window) == DisplayListButtonWindow:  # could be by location or industry
                windowType = title.split()[-1].strip()
                if windowType == "Industry":
                    self._cur.execute("""
                        SELECT c.name, c.rank, ind.industry, st.state, c.year_founded, c.employees, c.desc
                        FROM Companies AS c
                        INNER JOIN States AS st
                        ON c.state_id = st.id
                        INNER JOIN Industries AS ind
                        ON c.industry_id = ind.id
                        WHERE industry = ?""",
                        (window.getSelection(),))

                elif windowType == "Location":
                    self._cur.execute("""
                        SELECT c.name, c.rank, ind.industry, st.state, c.year_founded, c.employees, c.desc
                        FROM Companies AS c
                        INNER JOIN States AS st
                        ON c.state_id = st.id
                        INNER JOIN Industries AS ind
                        ON c.industry_id = ind.id
                        WHERE state = ?""",
                        (window.getSelection(),))

            data = self._cur.fetchall()
            displayTitle, dataList = self.getDataForSubWin(data, window, title)

            DisplayListWindow(self, displayTitle, dataList)


    def getDataForSubWin(self, data, window, title):
        """
        Get the appropriate formated data depending on which sub window is created and display using
        another DisplayListWindow object
        :param data: the data needed to format
        :param window: the subclass window created
        :param title: title of window to create
        :return: nothing
        """
        # changing format to a list of lists
        # bc tuple is immutable (self._cur.fetchall() output is list of tuples)
        dataList = [[*elem, "\n"] for elem in data]

        # window depth 3: title based on type of industry or location
        displayTitle = "Companies in "
        if type(window) == NumDisplayWindow:
            displayTitle = dataList[0][0]
        elif type(window) == DisplayListButtonWindow:  # could be by location or industry
            windowType = title.split()[-1].strip()
            if windowType == "Industry":
                # making the long titles fit better on the screen
                title_splitted = dataList[0][2].split(",")
                if len(title_splitted) > 2:
                    title_splitted = ", ".join(title_splitted[:2]) + ",\n" + ", ".join(title_splitted[2:])
                elif len(title_splitted) == 2:
                    title_splitted = ", ".join(title_splitted[:1]) + ",\n" + ", ".join(title_splitted[1:])
                else:
                    title_splitted = dataList[0][2]
                displayTitle += title_splitted
            elif windowType == "Location":
                displayTitle += dataList[0][3]

        # adding information to a company (a list)
        for company in dataList:
            company[0] = "Company: " + company[0]
            company[1] = "Rank: " + str(company[1])
            company[2] = "Industry: " + company[2]
            company[3] = "Location: " + company[3]
            company[4] = "Year Founded: " + str(company[4])
            company[5] = "Employees: " +str(company[5])
            if company[6] != "-1":
                company[6] = "Description: " + company[6]
            else:
                company[6] = "Description: None Provided"

            #split long description into lines of ~50 char (by whole words),
            # produces a list
            company[6] = wrap(company[6], 53)

        # flatten the list of lists for correct display
        dataList = [elem for tuple in dataList for elem in tuple]

        # flatten again bc dataList is a list of irregular lists like ["abc", "def", "efg", ["hij", "klm"]]
        flatten_dataList = []
        for elem in dataList:
            if isinstance(elem, Iterable) and not isinstance(elem, str):
                for el in elem:
                    flatten_dataList.append(el)
            else:
                flatten_dataList.append(elem)
        return (displayTitle, flatten_dataList)

    # Plotting
    def byTrend(self):
        """
        Handles the functionality of when the display by trend button is pressed by creating a RadioButtonWindow
        object which will decide from user input which type of PlotWindow object to create
        :return: nothing
        """
        displayList = ["Distribution by Employees", "Distribution by Year Founded", "Number of Companies by Industry","Number of Companies by Location"]
        trendWin = RadioButtonWindow(self, displayList)
        self.wait_window(trendWin)
        if trendWin.isConfirmed():
            choice = trendWin.getSelection()
            if choice == 1:
                self._cur.execute("""
                                    SELECT employees
                                    FROM Companies""")

            elif choice == 2:
                self._cur.execute("""SELECT year_founded
                                    FROM Companies""")
            elif choice == 3:
                self._cur.execute("""SELECT ind.industry, COUNT(c.industry_id)
                                    FROM Companies AS c
                                    INNER JOIN Industries AS ind
                                    ON c.industry_id = ind.id
                                    GROUP BY ind.industry
                                    ORDER BY COUNT(c.industry_id) ASC
                                    """)

            elif choice == 4:
                self._cur.execute("""SELECT state, COUNT(state)
                                     FROM Companies
                                     INNER JOIN States
                                     ON Companies.state_id = States.id
                                     GROUP BY state
                                     ORDER BY COUNT(state) ASC""")
            data = self._cur.fetchall()
            PlotWindow(self,data,choice)



    def getLocations(self):
        """
        Get all locations from database
        :return: list of employer locations
        """
        self._cur.execute("""
                        SELECT state
                        FROM States
                        ORDER BY state ASC""")
        return [state for tuple in self._cur.fetchall() for state in tuple]

    def getIndustries(self):
        """
        Get all industries from database
        :return: list of employer industries
        """
        self._cur.execute("""
                        SELECT industry
                        FROM Industries
                        ORDER BY industry ASC""")
        return [industry for tuple in self._cur.fetchall() for industry in tuple]

    def getEmployers(self):
        """
        Get all Employers from database
        :return: list of Employers
        """
        self._cur.execute("""SELECT rank, name
                            FROM Companies
                            ORDER BY rank ASC""")
        return self._cur.fetchall()


class DisplayListWindow(tk.Toplevel):
    """
    Defintion of DisplayListWindow that has a title and listbox, also inherited from other classes
    """
    def __init__(self, masterwin, title, displayList):
        """
        Default constructor
        :param masterwin: master window object
        :param title: title to display
        :param displayList: list to display in listbox
        """
        super().__init__(masterwin)
        self.minsize(400, 480)
        self.resizable(False, False)
        self.configure(bg=COLOR_SCHEME["back"])
        tk.Label(self, text=title, fg=COLOR_SCHEME["font"], bg=COLOR_SCHEME["back"],
                 font=(FONT, 25, "bold")).grid(pady=30, padx=100)
        self.frame = tk.Frame(self, bg=COLOR_SCHEME["back"])
        scrollBar = tk.Scrollbar(self.frame, orient="vertical")
        self.listBox = tk.Listbox(self.frame, width=40, height=15, font=(FONT, 15),
                                  listvariable=tk.StringVar(value=displayList), yscrollcommand=scrollBar.set)
        self.listBox.grid(row=1, column=0)
        scrollBar.config(command=self.listBox.yview)
        scrollBar.grid(row=1, column=1, sticky="ns")
        self.frame.grid(padx=100)

    def getListboxSelection(self):
        return self.listBox.curselection()


class DisplayListButtonWindow(DisplayListWindow):
    """
    Defintion of DisplayListButtonWindow that inherits everything from DisplayListWindow but adds the
    extra functionality of a button to confirm selection within the listbox
    """
    def __init__(self, masterwin, title, displayList):
        """
        Default constructor
        :param masterwin: master window object
        :param title: title to display
        :param displayList: list to display in listbox
        """
        super().__init__(masterwin, title, displayList)
        self.confirmed = False
        tk.Button(self, text="Confirm Selection", fg=COLOR_SCHEME["button_text"], bg=COLOR_SCHEME["button"],
                  activebackground=COLOR_SCHEME["button_pressed"], activeforeground=COLOR_SCHEME["font"],
                  font=(FONT, 16, "bold"), command=self.confirmSelectionPressed).grid(pady=20)

    def confirmSelectionPressed(self):
        """
        Handles the functionality of when the confirm selection button is pressed
        :return: nothing
        """
        if len(super().getListboxSelection()) != 0:
            self.selection = self.listBox.get(super().getListboxSelection()[0])
            self.confirmed = True
            self.destroy()

    def getSelection(self):
        return self.selection

    def isConfirmed(self):
        return self.confirmed


class NumDisplayWindow(DisplayListButtonWindow):
    """
    Definiton of NumDisplayWindow which inherits all the functionality of DisplayListButtonWindow but also
    adds a couple of descriptive lines, a text entry, and a confirm button so the user can select which range
    to display from the DisplayList
    """
    def __init__(self, masterwin, windowTitle, displayList):
        """
        Default Constructor
        :param masterwin: main window object
        :param windowTitle: title to display
        :param displayList: list to display in listbox
        """
        super().__init__(masterwin, windowTitle, None)
        frame1 = tk.Frame(self.frame, bg=COLOR_SCHEME["back"])
        tk.Label(frame1, text="Enter number for amount to display", fg=COLOR_SCHEME["font"], bg=COLOR_SCHEME["back"],
                 font=(FONT, 15, "bold")).grid()
        tk.Label(frame1, text="*use START-END format for a range*", fg=COLOR_SCHEME["font"], bg=COLOR_SCHEME["back"],
                 font=(FONT, 15, "bold")).grid(pady=5)
        self.entry = tk.Entry(frame1, width=10, font=(FONT, 20))
        self.entry.grid()
        self.displayList = displayList
        self.displayRange = [0, 1]
        tk.Button(frame1, text="Confirm", fg=COLOR_SCHEME["button_text"], bg=COLOR_SCHEME["button"],
                  activebackground=COLOR_SCHEME["button_pressed"], activeforeground=COLOR_SCHEME["font"],
                  font=(FONT, 15, "bold"), command=self.confirmPressed).grid(pady=5)
        frame1.grid(padx=20, row=1, column=2)

    def confirmPressed(self):
        """
        Handles the functionality of when the user inputs into the entry widget and clicks confirm
        :return: nothing
        """
        if len(self.entry.get()) != 0:
            try:
                if "-" in self.entry.get():
                    if len(self.entry.get().split("-")) == 2:
                        self.displayRange = int(self.entry.get().split("-")[0].strip())-1, int(self.entry.get().split("-")[1].strip())
                        if self.displayRange[0] > self.displayRange[1]:
                            raise Exception("START value must be less than END value")
                    else:
                        raise Exception("Incorrect format")
                else:
                    self.displayRange[1] = int(self.entry.get())
                if self.displayRange[0] < 0 or self.displayRange[1] < 1 or self.displayRange[1] > len(self.displayList) or self.displayRange[0] > len(self.displayList):
                    raise Exception("Values are out of bounds")

                self.listBox.delete(0, tk.END)
                self.listBox.configure(listvariable=tk.StringVar(
                    value=[(str(elem[0]) + ". " + elem[1]) for elem in self.displayList][
                          self.displayRange[0]:self.displayRange[1]]))
            except ValueError:
                tkmb.showinfo("Error", "Incorrect format", parent=self)
            except Exception as e:
                tkmb.showinfo("Error", e, parent=self)

    def confirmSelectionPressed(self):
        """
        Handles the functionality of when the confirm selection button is pressed
        :return: nothing
        """
        if len(super().getListboxSelection()) != 0:
            self.selection = self.displayList[self.displayRange[0]:self.displayRange[1]][
                super().getListboxSelection()[0]]
            self.confirmed = True
            self.destroy()


class RadioButtonWindow(tk.Toplevel):
    """
    Definition for the RadioButtonWindow class for when the user clicks display by trend
    """
    def __init__(self, masterwin, displayList):
        """
        Default constructor
        :param masterwin: master window object
        :param displayList: list of what to display in an array of radiobuttons
        """
        super().__init__(masterwin)
        self.minsize(500, 400)
        self.resizable(False, False)
        self.configure(bg=COLOR_SCHEME["back"])
        self.choice = tk.IntVar()
        self.confirmed = False
        frame = tk.Frame(self, bg=COLOR_SCHEME["back"])
        tk.Label(self, text="Display by trends", fg=COLOR_SCHEME["font"], bg=COLOR_SCHEME["back"],
                 font=(FONT, 25, "bold ")).grid(pady=30)
        for i,elem in enumerate(displayList):
            tk.Radiobutton(frame, text=elem, fg=COLOR_SCHEME["font"], bg=COLOR_SCHEME["back"],
                           activebackground=COLOR_SCHEME["back"],
                           activeforeground=COLOR_SCHEME["font"], selectcolor=COLOR_SCHEME["back"],
                           font=(FONT, 16, "bold"), variable=self.choice, value=i+1).grid(pady=6, sticky="w")
        frame.grid(padx=150)
        tk.Button(self, text="Confirm Selection", fg=COLOR_SCHEME["button_text"], bg=COLOR_SCHEME["button"],
                  activebackground=COLOR_SCHEME["button_pressed"], activeforeground=COLOR_SCHEME["font"],
                  font=(FONT, 16, "bold"), command=self.confirmSelectionPressed).grid(pady=30)

    def confirmSelectionPressed(self):
        """
        Handles functionality of when the confirm selection button is pressed
        :return:
        """
        self.confirmed = True
        self.destroy()

    def getSelection(self):
        return self.choice.get()

    def isConfirmed(self):
        return self.confirmed


class PlotWindow(tk.Toplevel):
    """
    Definiton of PlotWindow class which will be used to plot multiple different trends
    """
    def __init__(self, masterwin,data,choice):
        """
        Default constructor
        :param masterwin: master window object
        :param data: list of tuples that will be used to display
        :param choice: which type of plot to use
        """
        super().__init__(masterwin)
        self.resizable(False,False)
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid()
        self.makePlot(data, choice)
        self.canvas.draw()


    def makePlot(self, data, choice):
        """
        Configure the plot before displaying it
        :param data: list of tuples that will be used to display
        :param choice: which type of plot to use
        :return: nothing
        """
        if choice == 1:
            numEmployees = [int(str(elem[0]).replace(',', '')) for elem in data]
            numEmployees_np = np.array(numEmployees)

            # removing outliers, > 2 deviations from the mean
            distance_from_mean = abs(numEmployees_np - numEmployees_np.mean())
            not_outlier = distance_from_mean < 2 * numEmployees_np.std()
            no_outliers = numEmployees_np[not_outlier]
            ax = self.fig.add_subplot()
            bins = [0, 25000, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000]
            plt.hist(no_outliers, bins=bins, density=False, edgecolor="black", color="lightskyblue")
            plt.title("Distribution by Number of Employees", fontsize=16, fontweight="bold")
            plt.xlabel("Number of Employees")
            plt.ylabel("Number of Companies")
            # print values for each bin
            for rect in ax.patches:
                height = rect.get_height()
                ax.annotate(f'{int(height)}', xy=(rect.get_x()+rect.get_width()/2, height),
                            xytext=(0, 2), textcoords='offset points', ha='center', va='bottom')
            plt.text(0.63,0.95, f"Note: Data without outliers.", transform=ax.transAxes, color='grey', fontsize=8)
            plt.text(0.63,0.92, f"{len(no_outliers)} out of 500 companies shown.", transform=ax.transAxes, color='grey', fontsize=8)
            plt.tight_layout()

        elif choice == 2:
            years = [int(elem[0]) for elem in data]
            years_np = np.array(years)

            # removing outliers, > 2 deviations from the mean
            distance_from_mean = abs(years_np - years_np.mean())
            not_outlier = distance_from_mean < 2 * years_np.std()

            no_outliers = years_np[not_outlier]
            ax = self.fig.add_subplot()
            bins = [1800, 1825, 1850, 1875, 1900, 1925, 1950, 1975, 2000, 2020]
            ax.hist(no_outliers, bins=bins, density=False, edgecolor="black", color="lightskyblue")
            plt.title("Distribution by Year Founded", fontsize=16, fontweight="bold")
            plt.xlabel("Years Founded")
            plt.ylabel("Number of Companies")
            # print values for each bin
            for rect in ax.patches:
                height = rect.get_height()
                ax.annotate(f'{int(height)}', xy=(rect.get_x()+rect.get_width()/2, height),
                            xytext=(0, 2), textcoords='offset points', ha='center', va='bottom')

            plt.text(0.03,0.95, f"Note: Data without outliers.", transform=ax.transAxes, color='grey', fontsize=8)
            plt.text(0.03,0.92, f"{len(no_outliers)} out of 500 companies shown.", transform=ax.transAxes, color='grey', fontsize=8)

        elif choice == 3:
            industry_names = [elem[0] for elem in data]
            industry_num = [elem[1] for elem in data]
            industry_names_short = []
            for industry in industry_names:
                if len(industry.split(", ")) > 2:
                    industry = ", ".join(industry.split(", ")[0:2]) + "\n" + ", ".join(industry.split(", ")[2:4])
                industry_names_short.append(industry)

            ax = self.fig.add_subplot()
            ax.barh(industry_names_short, industry_num, edgecolor="black", color="lightskyblue")
            # print values for each bar
            for i, v in enumerate(industry_num):
                ax.text(v + .25, i - 0.2, str(v), fontsize=6)
            plt.title("Companies by Industry", fontsize=16, fontweight="bold")
            plt.xlabel("Number of Companies")
            plt.yticks(fontsize=6)
            plt.tight_layout()

        elif choice == 4:

            state = [elem[0] for elem in data]
            numPerState = [elem[1] for elem in data]
            ax = self.fig.add_subplot()
            ax.barh(state, numPerState, edgecolor="black", color="lightskyblue")
            # print values for each bar
            for i, v in enumerate(numPerState):
                ax.text(v + .25, i - 0.2, str(v), fontsize=6)

            plt.title("Companies by Location", fontsize=16, fontweight="bold")
            plt.ylabel("Location")
            plt.xlabel("Number of Companies")
            plt.tight_layout()


#main
if __name__ == "__main__":
    run = MainWindow()
    run.mainloop()
    run.quit()

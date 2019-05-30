import time

# For operations with csv files
import csv

# Import modules for GUI
import tkinter as tk
from tkinter import Frame
from tkinter import Text
from tkinter import Label
import tkinter.messagebox as mb
import tkinter.filedialog as fd
from PIL import Image, ImageTk

# Importing modules used for builing figures
import matplotlib.pyplot as plt
import numpy as np

import os

# Importing libraries for ADS1115 connction
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class GUI(Frame):

    # The very beginning of class
    def __init__(self, master=None):
        self.master = master
        self.remember_val = tk.IntVar()
        self.save_fig = tk.IntVar()
        self.init_ads1x15()
        self.init_window()

    # Function for saving figure as pdf/png image
    def save(self, name='', fmt='png'):
        try:
            pwd = os.getcwd()
            iPath = './pictures/{}'.format(fmt)
            if not os.path.exists(iPath):
                os.makedirs(iPath)
            os.chdir(iPath)
            plt.savefig('{}.{}'.format(name, fmt), fmt='png')
            os.chdir(pwd)
            self.text_box.insert(tk.END, "Figure saved!\n")
        except Exception as e:
            # Case if error occure while saving a figure
            print(str(e))
            mb.showerror("Save Figure", "Failed to save figure!\n")
            return

    # Function that helps with opening figures and csv data
    def open_file(self):
        try:
            # Call the window which helps to find a file to open
            filename = fd.askopenfilename(filetypes = (("CSV Files", ".csv"), ("PNG Files", ".png"), ("PDF Files", '.pdf'), ("All files", "*.*")))

            # Case if opening file is .csv
            if '.csv' in filename:
                # Open and read data of this file
                f = open(filename)
                file_read = f.read()

                # Removing previous data from text_box
                self.text_box.delete(1.0, "end-1c")

                # Output data into text box of program
                self.text_box.insert(tk.END, file_read)

                # Close file
                f.close()

            # Case if opening file is .png or .pdf
            elif '.png' in filename or '.pdf' in filename:
                # Open image
                img = Image.open(filename)

                # Removing previous data from text_box
                self.text_box.delete(1.0, "end-1c")

                # Make resizing of image and saving it
                basewidth = 400
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), Image.ANTIALIAS)
                os.remove(filename)
                img.save(filename)

                # Open and put new image to program window
                new_img = Image.open(filename)
                render = ImageTk.PhotoImage(new_img)
                self.img_lbl = tk.Button(self.master, image=render,command=self.imgpress)
                self.img_lbl.image = render
                self.img_lbl.place(x=0, y=0)
        except Exception as e:
            # Case if error occured while opening file
            print(str(e))
            mb.showerror("Open File", "Failed to open a file!\n")
            return

    # Image press handler, removes image while clicking on it
    def imgpress(self):
        self.img_lbl.destroy()
        self.text_box.insert(tk.END, "Image has been removed!\n")
        return


    # Function that manages data processing
    def process_data(self, event=None):
        # Check for invalid values
        tmp1 = self.e1.get()
        tmp2 = self.e2.get()
        tmp3 = self.e3.get()
        tmp4 = self.e4.get()
        if tmp1.lstrip('-').isdigit() == False or tmp2.lstrip('-').isdigit() == False or tmp3.replace(".", "", 1).lstrip('-').isdigit() == False or tmp4.replace(".", "", 1).lstrip('-').isdigit() == False:
            mb.showwarning("Error", 'Fields must be digits and not empty!')
            return

        # Assigning values from user input
        self.delay = int(self.e1.get())
        self.delay_ms = self.delay / 1000
        self.measure_nb = int(self.e2.get())
        self.ymin = float(self.e3.get())
        self.ymax = float(self.e4.get())

        # Check for invalid values
        if self.delay <= 0 or self.measure_nb <= 0:
            mb.showwarning("Error", 'Delay and number of measurements cannot be less or equal zero!')
            return
        if self.ymin >= self.ymax:
            mb.showwarning("Error", 'ymin cannot be greater or equal ymax!')
            return

        # Removing initial text from text box
        self.text_box.delete(1.0, "end-1c")


        # Assigning values to x and y
        x = np.arange(self.measure_nb)
        y = []

        # Assigning title and labels to axis
        plt.title("V = f(n)")
        plt.xlabel('Number of measurements, n')
        plt.ylabel('Voltage, V')

        # Check for invalid limits of y axis
        if float(self.chan.voltage) < self.ymin:
            mb.showwarning("Error", 'ymin cannot be greater than measured voltage: {}'.format(round(self.chan.voltage, 3)))
            return

        # Printing title of table with voltage values
        with open('data.csv', mode='w') as csv_file:
            csv_write = csv.writer(csv_file, delimiter=',')
            csv_write.writerow(['#', ' raw', '    v'])

        # Printing resulting values to file
        with open('data.csv', mode='a') as csv_write:
            for i in range(0, int(self.measure_nb)):
                csv_writer = csv.writer(csv_write, delimiter=',')
                csv_writer.writerow([(i + 1), self.chan.value, round(self.chan.voltage, 5)])
                y.append(self.chan.voltage)
                time.sleep(self.delay_ms)

        # Printing about successfull write to file
        self.text_box.insert(tk.END, "Data was successfully written to file data.csv!\n")

        # Building plot
        plt.plot(x, y)
        plt.grid(True)

        # Setting limits of y axis
        plt.ylim(float(self.ymin), float(self.ymax))

        # If check button is False, then remove values from fields
        if int(self.remember_val.get()) == 0:
            self.e1.delete(0, tk.END)
            self.e2.delete(0, tk.END)
            self.e3.delete(0, tk.END)
            self.e4.delete(0, tk.END)

        # Showing plot on a screeen
        plt.show(block=False)

        if int(self.save_fig.get()) == 1:
            self.save('1')

    # Function that handles quit button
    def callback(self):
        # Prompts a window if user wants to quit
        if mb.askyesno('Verify', 'Really quit?'):
            exit()
        else:
            mb.showinfo('No', 'Quit has been cancelled')

    # Create save connection to ADC via I2C bus
    def init_ads1x15(self):
        # Create the I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Create the ADC object using the I2C bus
        self.ads = ADS.ADS1115(self.i2c)

        # Create single-ended input on channel 0
        self.chan = AnalogIn(self.ads, ADS.P0)

    # Main function, that makes GUI
    def init_window(self):
        # Assigning title to our window
        self.master.title("Measuring voltage")

        # Create name of entry fields
        tk.Label(self.master, padx=30, text="Delay (in ms):").grid(row=0)
        tk.Label(self.master, padx=30, text="Number of measurements:").grid(row=1)
        tk.Label(self.master, padx=30, text="Minimum of y axis:").grid(row=2)
        tk.Label(self.master, padx=30, text="Maximum of y axis:").grid(row=3)

        # Create a box, which will behave like console window
        self.text_box = tk.Text(self.master, width=50, height=15)
        self.text_box.grid(row=8, column=0, columnspan=10)
        self.text_box.insert("end-1c", "Enter values\n")

        # Add scrollbar to the Text widget
        self.scroll = tk.Scrollbar(self.master)
        self.scroll.config(command=self.text_box.yview)
        self.text_box.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=8, column=2, columnspan=10, sticky='NS')

        # Create check button
        tk.Checkbutton(self.master, text="Remember values", variable=self.remember_val).grid(row=1, column=2, sticky=tk.NS, padx=35)
        tk.Checkbutton(self.master, text="Save figure after", variable=self.save_fig).grid(row=2, column=2, sticky=tk.NS, padx=35)

        # Create entry fields
        self.e1 = tk.Entry(self.master)
        self.e2 = tk.Entry(self.master)
        self.e3 = tk.Entry(self.master)
        self.e4 = tk.Entry(self.master)

        # Assigning to fields basic values
        self.e1.insert(10, "100")
        self.e2.insert(10, "20")
        self.e3.insert(10, "1")
        self.e4.insert(10, "5")

        # Make a grid of entry fields
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)

        # Binding Enter button as if user could press Apply button
        self.e1.bind("<Return>", self.process_data) 
        self.e2.bind("<Return>", self.process_data) 
        self.e3.bind("<Return>", self.process_data)
        self.e4.bind("<Return>", self.process_data)

        # Create two buttons which will call funcs if user press them
        tk.Button(self.master, text='Quit', command=self.callback).grid(row=5, column=0, sticky=tk.W, pady=10, padx=60)
        tk.Button(self.master, text='Apply', command=self.process_data).grid(row=5, column=1, sticky=tk.W, pady=2, padx=60)
        tk.Button(self.master, text='Browse files', command=self.open_file).grid(row=5, column=2, sticky=tk.W, pady=2, padx=60)

# Create a Tkinter object
root = tk.Tk()

# Creating an object of program
program = GUI(root)

# Show window
root.mainloop()

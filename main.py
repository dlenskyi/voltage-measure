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

# System imports
import os
import shutil
import time

# For exceptions
import traceback

# Importing libraries for ADS1115 connection
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class GUI(Frame):

    # The very beginning of class
    def __init__(self, master=None):
        self.master = master
        self.name_for_save_fig = '1'
        self.remember_val = tk.IntVar()
        self.save_fig = tk.IntVar()
        self.two_chan = tk.IntVar()
        self.three_chan = tk.IntVar()
        self.csv_file1 = 'chan1.csv'
        self.csv_file2 = 'chan2.csv'
        self.csv_file3 = 'chan3.csv'
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
            self.text_box.insert(tk.END, "Figure saved\n")
        except Exception as e:
            # Case if error occure while saving a figure
            print(traceback.format_exc())
            mb.showerror("Save Figure", "Failed to save figure:\n" + str(e))
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

            # If selected file nor csv neither pdf or png
            else:
                mb.showwarning("Open File", "Type of file is not satisfied by a program\n")
        except Exception as e:
            # Case if error occured while opening file
            print(traceback.format_exc())
            mb.showerror("Open File", "Failed to open a file:\n" + str(e))
            return

    # Function that sends selected file to shared directory
    def send_file(self):
        try:
            # Call the window which helps to find a file to open
            filename = fd.askopenfilename(filetypes = (("CSV Files", ".csv"), ("PNG Files", ".png"), ("PDF Files", '.pdf'), ("All files", "*.*")))

            source_file = filename
            destination_folder = '/home/pi/share/'
            # Case if selected file is .csv
            if '.csv' in filename:

                # If file exists remove it
                path_to_csv = destination_folder + self.csv_file1
                if os.path.exists(path_to_csv):
                    os.remove(path_to_csv)

                # Moves selected csv file to destination folder
                shutil.move(source_file, destination_folder)

            # Case if selected file is .png or .pdf
            elif '.png' in filename or '.pdf' in filename:

                # If file exists remove it
                path_to_png = destination_folder + self.name_for_save_fig + '.png'
                path_to_pdf = destination_folder + self.name_for_save_fig + '.pdf'
                if os.path.exists(path_to_png) and '.png' in filename:
                    os.remove(path_to_png)
                elif os.path.exists(path_to_pdf) and '.pdf' in filename:
                    os.remove(path_to_pdf)

                # Moves selected file to destination folder
                shutil.move(source_file, destination_folder)

            # Removing previous data from text_box
            self.text_box.delete(1.0, "end-1c")

            # Printing about successfull operation
            self.text_box.insert(tk.END, "File has been moved to {}!\n".format(destination_folder))

        except Exception as e:
            # Case if error occured while opening file
            print(traceback.format_exc())
            mb.showerror("Open File", "Failed to open a file:\n" + str(e))
            return

    # Image press handler, removes image while clicking on it
    def imgpress(self):
        self.img_lbl.destroy()
        self.text_box.insert(tk.END, "Image has been removed\n")
        return


    # Function that manages data processing
    def process_data(self, event=None):
        try:
            # Check for correct checks of buttons
            if int(self.two_chan.get()) == 1 and int(self.three_chan.get()) == 1:
                mb.showwarning("Error", 'So do you want to use 2 or 3 channels of ADS1115? :D')
                return

            # Create connection to ADS1115 via I2C
            self.init_ads1x15()

            # Check for invalid values
            tmp1 = self.e1.get()
            tmp2 = self.e2.get()
            tmp3 = self.e3.get()
            tmp4 = self.e4.get()
            if tmp1.lstrip('-').isdigit() == False or tmp2.lstrip('-').isdigit() == False or tmp3.replace(".", "", 1).lstrip('-').isdigit() == False or tmp4.replace(".", "", 1).lstrip('-').isdigit() == False:
                mb.showwarning("Error", 'Fields must be digits and not empty')
                return

            # Assigning values from user input
            self.delay = int(self.e1.get())
            self.delay_ms = self.delay / 1000
            self.measure_nb = int(self.e2.get())
            self.ymin = float(self.e3.get())
            self.ymax = float(self.e4.get())

            # Check for invalid values
            if self.delay <= 0 or self.measure_nb <= 0:
                mb.showwarning("Error", 'Delay and number of measurements cannot be less or equal zero')
                return
            if self.ymin >= self.ymax:
                mb.showwarning("Error", 'ymin cannot be greater or equal ymax')
                return

            # Removing initial text from text box
            self.text_box.delete(1.0, "end-1c")


            # Assigning values to x and y
            x = np.arange(self.measure_nb)
            y1 = []
            y2 = []
            y3 = []

            # Assigning title and labels to axis
            plt.title("V = f(n)")
            plt.xlabel('Number of measurements, n')
            plt.ylabel('Voltage, V')

            # Check for invalid limits of y axis
            for i in range(0, int(self.measure_nb)):
                if float(self.chan1.voltage) < self.ymin:
                    mb.showwarning("Error", 'ymin cannot be greater than measured voltage: {}'.format(round(self.chan1.voltage, 3)))
                    return

            # Printing title of table with voltage values
            with open(self.csv_file1, mode='w') as csv_file1:
                csv_write1 = csv.writer(csv_file1, delimiter=',')
                csv_write1.writerow(['#', ' raw', '    V'])

            # Case if user uses 2 channels, creates another file
            if int(self.two_chan.get()) == 1:
                with open(self.csv_file2, mode='w') as csv_file2:
                    csv_write2 = csv.writer(csv_file2, delimiter=',')
                    csv_write2.writerow(['#', ' raw', '    I'])

            # Same if user uses 3 channels, creates two another files with data
            elif int(self.three_chan.get()) == 1:
                with open(self.csv_file2, mode='w') as csv_file2:
                    csv_write2 = csv.writer(csv_file2, delimiter=',')
                    csv_write2.writerow(['#', ' raw', '    I'])
                with open(self.csv_file3, mode='w') as csv_file3:
                    csv_write3 = csv.writer(csv_file3, delimiter=',')
                    csv_write3.writerow(['#', ' raw', '    v'])

            # Printing resulting values to file
            with open(self.csv_file1, mode='a') as csv_write1:
                for i in range(0, int(self.measure_nb)):
                    csv_writer1 = csv.writer(csv_write1, delimiter=',')
                    csv_writer1.writerow([(i + 1), self.chan1.value, round(self.chan1.voltage, 5)])
                    y1.append(self.chan1.voltage)
                    time.sleep(self.delay_ms)

            # Case if user wants to use 2 channels, also writing resulting values to another file
            if int(self.two_chan.get()) == 1:
                with open(self.csv_file2, mode='a') as csv_write2:
                    for i in range(0, int(self.measure_nb)):
                        csv_writer2 = csv.writer(csv_write2, delimiter=',')
                        csv_writer2.writerow([(i + 1), (self.chan2.value / 0.22), (round(self.chan2.voltage, 5) / 0.22)])
                        y2.append(self.chan2.voltage)
                        time.sleep(self.delay_ms)

            # Same if user uses 3 channels, write data to 2 another files
            elif int(self.three_chan.get()) == 1:
                with open(self.csv_file2, mode='a') as csv_write2:
                    for i in range(0, int(self.measure_nb)):
                        csv_writer2 = csv.writer(csv_write2, delimiter=',')
                        csv_writer2.writerow([(i + 1), (self.chan2.value / 0.22), (round(self.chan2.voltage, 5) / 0.22)])
                        y2.append(self.chan2.voltage)
                        time.sleep(self.delay_ms)
                with open(self.csv_file3, mode='a') as csv_write3:
                    for i in range(0, int(self.measure_nb)):
                        csv_writer3 = csv.writer(csv_write3, delimiter=',')
                        csv_writer3.writerow([(i + 1), self.chan3.value, round(self.chan3.voltage, 5)])
                        y3.append(self.chan3.voltage)
                        time.sleep(self.delay_ms)

            # Printing about successfull write to file
            self.text_box.insert(tk.END, "Data was successfully written to file {}\n".format(self.csv_file1))

            if int(self.two_chan.get()) == 1:
                self.text_box.insert(tk.END, "Data was successfully written to file {}\n".format(self.csv_file2))

            elif int(self.three_chan.get()) == 1:
                self.text_box.insert(tk.END, "Data was successfully written to file {}\n".format(self.csv_file2))

            # Building a plot
            if int(self.two_chan.get()) == 0 and int(self.three_chan.get()) == 0:
                plt.plot(x, y1)
                plt.grid(True)
                plt.ylim(float(self.ymin), float(self.ymax))

            elif int(self.two_chan.get()) == 1:
                ax1 = plt.subplot(211)
                plt.plot(x, y1)
                plt.ylim(float(self.ymin), float(self.ymax))
                plt.setp(ax1.get_xticklabels(), fontsize=6)

                ax2 = plt.subplot(212, sharex=ax1)
                plt.plot(x, y2)
                plt.ylim(float(self.ymin), float(self.ymax))
                plt.setp(ax2.get_xticklabels(), fontsize=6)

            elif int(self.three_chan.get()) == 1:
                ax1 = plt.subplot(311)
                plt.plot(x, y1)
                plt.ylim(float(self.ymin), float(self.ymax))
                plt.setp(ax1.get_xticklabels(), fontsize=6)

                ax2 = plt.subplot(312, sharex=ax1)
                plt.plot(x, y2)
                plt.ylim(float(self.ymin), float(self.ymax))
                plt.setp(ax2.get_xticklabels(), fontsize=6)

                ax3 = plt.subplot(313, sharex=ax1)
                plt.plot(x, y3)
                plt.ylim(float(self.ymin), float(self.ymax))
                plt.setp(ax2.get_xticklabels(), fontsize=6)

            # If check button is False, then remove values from fields
            if int(self.remember_val.get()) == 0:
                self.e1.delete(0, tk.END)
                self.e2.delete(0, tk.END)
                self.e3.delete(0, tk.END)
                self.e4.delete(0, tk.END)

            # Showing plot on a screeen
            plt.show(block=False)

            if int(self.save_fig.get()) == 1:
                self.save(self.name_for_save_fig)
        except Exception as e:
            # Case if error occured while proccesing data
            print(traceback.format_exc())
            mb.showerror("Process Data", "Failed to process data:\n" + str(e))
            return

    # Function that handles quit button
    def callback(self):
        # Prompts a window if user wants to quit
        if mb.askyesno('Verify', 'Really quit?'):
            exit()
        else:
            mb.showinfo('No', 'Quit has been cancelled')

    # Create save connection to ADC via I2C bus
    def init_ads1x15(self):
        try:
            # Create the I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Create the ADC object using the I2C bus
            self.ads = ADS.ADS1115(self.i2c)    

            # Create single-ended input on channel 0
            self.chan1 = AnalogIn(self.ads, ADS.P0)

            # Case if user wants to use 2 channels, also create singe-ended input on channel 1
            if int(self.two_chan.get()) == 1:
                self.chan2 = AnalogIn(self.ads, ADS.P1)

            # Same if user wants 3 channels, also create input on channel 1 and 2
            elif int(self.three_chan.get()) == 1:
                self.chan2 = AnalogIn(self.ads, ADS.P1)
                self.chan3 = AnalogIn(self.ads, ADS.P2)

        except Exception as e:
            # Case if error occured while connecting ADS1115 to Raspberry
            print(traceback.format_exc())
            mb.showerror("ADS1115 Connection", "Failed to connect ADS1115 with Raspberry Pi:\n" + str(e))

            # Destroy Tkinter object
            # self.master.destroy()
            return

    # Main function, that makes GUI
    def init_window(self):
        try:
            # Assigning title to our window
            self.master.title("Measuring voltage")

            # Create name of entry fields
            tk.Label(self.master, padx=30, text="Delay (in ms):").grid(row=0)
            tk.Label(self.master, padx=30, text="Number of measurements:").grid(row=1)
            tk.Label(self.master, padx=30, text="Minimum of y axis:").grid(row=2)
            tk.Label(self.master, padx=30, text="Maximum of y axis:").grid(row=3)

            # Create a box, which will behave like console window
            self.text_box = tk.Text(self.master, width=50, height=15)
            self.text_box.grid(row=7, column=0, columnspan=15, sticky='W', padx=65)
            self.text_box.insert("end-1c", "Enter values\n")    

            # Add scrollbar to the Text widget
            self.scroll = tk.Scrollbar(self.master)
            self.scroll.config(command=self.text_box.yview)
            self.text_box.config(yscrollcommand=self.scroll.set)
            self.scroll.grid(row=7, column=1, columnspan=15, sticky='NS')

            # Create check buttons
            tk.Checkbutton(self.master, text="Remember values", variable=self.remember_val).grid(row=0, column=2, sticky=tk.NS, padx=35)
            tk.Checkbutton(self.master, text="Save figure after", variable=self.save_fig).grid(row=1, column=2, sticky=tk.NS, padx=35)
            tk.Checkbutton(self.master, text="Use 2 channels", variable=self.two_chan).grid(row=2, column=2, sticky=tk.NS, padx=30)
            tk.Checkbutton(self.master, text="Use 3 channels", variable=self.three_chan).grid(row=3, column=2, sticky=tk.NS, padx=30)

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
            tk.Button(self.master, text='Apply!', command=self.process_data).grid(row=5, column=1, sticky=tk.W, pady=2, padx=60)
            tk.Button(self.master, text='Open file', command=self.open_file).grid(row=5, column=2, sticky=tk.W, pady=2, padx=60)
            tk.Button(self.master, text='Send file!', command=self.send_file).grid(row=7, column=2, columnspan=10, sticky=tk.W, pady=0, padx=60)
        except Exception as e:
            # Case if error occured while connecting ADS1115 to Raspberry
            print(traceback.format_exc())
            mb.showerror("Window creation", "Failed to create a GUI window:\n" + str(e))

            # Destroy Tkinter object
            self.master.destroy()
            exit()

# Create a Tkinter object
root = tk.Tk()

# Creating an object of program
program = GUI(root)

# Show window
root.mainloop()

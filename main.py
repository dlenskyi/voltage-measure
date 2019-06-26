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
# import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class GUI(Frame):

    # The very beginning of class
    def __init__(self, master=None):
        self.master = master
        self.name_for_save_fig = '1'
        self.remember_val = tk.IntVar()
        self.ymin2 = 0
        self.ymax2 = 0
        self.ymin3 = 0
        self.ymax3 = 0
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

        # Case if error occure while saving a figure
        except Exception as e:
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
            elif '.' in filename:
                mb.showwarning("Open File", "Type of file is not satisfied by a program\n")

        # Case if error occured while opening file
        except Exception as e:
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

        # Case if error occured while opening file
        except Exception as e:
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

            # Get values from user input
            tmp1 = self.e1.get()
            tmp2 = self.e2.get()
            tmp3 = self.e3.get()
            tmp4 = self.e4.get()
            tmp5 = 0
            tmp6 = 0
            tmp7 = 0
            tmp8 = 0

            if int(self.two_chan.get()) == 1:
                tmp5 = self.e5.get()
                tmp6 = self.e6.get()

            if int(self.three_chan.get()) == 1:
                tmp5 = self.e5.get()
                tmp6 = self.e6.get()
                tmp7 = self.e7.get()
                tmp8 = self.e8.get()

            # Check for invalid values
            if tmp1.lstrip('-').isdigit() == False or tmp2.lstrip('-').isdigit() == False or tmp3.replace(".", "", 1).lstrip('-').isdigit() == False or tmp4.replace(".", "", 1).lstrip('-').isdigit() == False:
                mb.showwarning("Error", 'Fields must be digits and not empty')
                return
            if int(self.two_chan.get()) == 0 and int(self.three_chan.get()) == 0 and (tmp5 or tmp6 or tmp7 or tmp8):
                mb.showwarning("Error", 'Fill \'Use 2/3 channels\' before entering y limits for this channels')
                return
            if int(self.two_chan.get()) == 1 and (tmp5.replace(".", "", 1).lstrip('-').isdigit() == False or tmp6.replace(".", "", 1).lstrip('-').isdigit() == False):
                mb.showwarning("Error", 'Fields must be digits and not empty')
                return
            if int(self.three_chan.get()) == 1 and (tmp5.replace(".", "", 1).lstrip('-').isdigit() == False or tmp6.replace(".", "", 1).lstrip('-').isdigit() == False or
            tmp7.replace(".", "", 1).lstrip('-').isdigit() == False or tmp8.replace(".", "", 1).lstrip('-').isdigit() == False):
                mb.showwarning("Error", 'Fields must be digits and not empty')
                return

            # Assigning values from user input
            self.delay = int(self.e1.get())
            self.delay_ms = self.delay / 1000
            self.measure_nb = int(self.e2.get())
            self.ymin1 = float(self.e3.get())
            self.ymax1 = float(self.e4.get())

            # Check if values from input fields are not empty and have only digits
            if self.e5.get() != '' and self.e5.get().replace(".", "", 1).lstrip('-').isdigit() == True:
                self.ymin2 = float(self.e5.get())
            if self.e6.get() != '' and self.e6.get().replace(".", "", 1).lstrip('-').isdigit() == True:
                self.ymax2 = float(self.e6.get())
            if self.e7.get() != '' and self.e7.get().replace(".", "", 1).lstrip('-').isdigit() == True:
                self.ymin3 = float(self.e7.get())
            if self.e8.get() != '' and self.e8.get().replace(".", "", 1).lstrip('-').isdigit() == True:
                self.ymax3 = float(self.e8.get())

            # Check for invalid values
            if self.delay <= 0 or self.measure_nb <= 0:
                mb.showwarning("Error", 'Delay and number of measurements cannot be less or equal zero')
                return
            if self.ymin1 >= self.ymax1:
                mb.showwarning("Error", 'ymin1 cannot be greater or equal ymax1')
                return
            if self.ymin2 >= self.ymax2 and int(self.two_chan.get()) == 1:
                mb.showwarning("Error", 'ymin2 cannot be greater or equal ymax2')
                return
            if (self.ymin3 >= self.ymax3 or self.ymin2 >= self.ymax2) and int(self.three_chan.get()) == 1:
                mb.showwarning("Error", 'ymin2/ymin3 cannot be greater or equal ymax2/ymax3')
                return

            # Removing initial text from text box
            self.text_box.delete(1.0, "end-1c")


            # Assigning values to x and y
            x = np.arange(self.measure_nb)
            y1 = []
            y2 = []
            y3 = []

            # Check for invalid limits of y axis
            for i in range(0, int(self.measure_nb)):
                if float(self.chan1.voltage) < self.ymin1:
                    mb.showwarning("Error", 'ymin1 cannot be greater than measured voltage: {}'.format(round(self.chan1.voltage, 3)))
                    return
                if float(self.chan1.voltage) > self.ymax1:
                    mb.showwarning("Error", 'ymax1 must be greater than measured voltage: {}'.format(round(self.chan1.voltage, 3)))
                    return

            if int(self.two_chan.get()) == 1:
                for i in range(0, int(self.measure_nb)):
                    if float(round((self.chan2.voltage * 0.22), 3)) < self.ymin2:
                        mb.showwarning("Error", 'ymin2 cannot be greater than measured current: {}'.format(round((self.chan2.voltage * 0.22), 3)))
                        return
                    if float(round((self.chan2.voltage * 0.22), 3)) > self.ymax2:
                        mb.showwarning("Error", 'ymax2 must be greater than measured current: {}'.format(round((self.chan2.voltage * 0.22), 3)))
                        return

            elif int(self.three_chan.get()) == 1:
                for i in range(0, int(self.measure_nb)):
                    if float(round((self.chan2.voltage * 0.22), 3)) < self.ymin2:
                        mb.showwarning("Error", 'ymin2 cannot be greater than measured current: {}'.format(round((self.chan2.voltage * 0.22), 3)))
                        return
                    if float(round((self.chan2.voltage * 0.22), 3)) > self.ymax2:
                        mb.showwarning("Error", 'ymax2 must be greater than measured current: {}'.format(round((self.chan2.voltage * 0.22), 3)))
                        return
                for i in range(0, int(self.measure_nb)):
                    if float(self.chan3.voltage) < self.ymin3:
                        mb.showwarning("Error", 'ymin3 cannot be greater than measured voltage: {}'.format(round(self.chan3.voltage, 3)))
                        return
                    if float(self.chan3.voltage) > self.ymax3:
                        mb.showwarning("Error", 'ymax3 must be greater than measured voltage: {}'.format(round(self.chan3.voltage, 3)))
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
                    csv_write3.writerow(['#', ' raw', '    V'])

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
                        csv_writer2.writerow([(i + 1), int(self.chan2.value * 0.22), round((self.chan2.voltage * 0.22), 5)])
                        y2.append(self.chan2.voltage * 0.22)
                        time.sleep(self.delay_ms)

            # Same if user uses 3 channels, write data to 2 another files
            elif int(self.three_chan.get()) == 1:
                with open(self.csv_file2, mode='a') as csv_write2:
                    for i in range(0, int(self.measure_nb)):
                        csv_writer2 = csv.writer(csv_write2, delimiter=',')
                        csv_writer2.writerow([(i + 1), int(self.chan2.value * 0.22), round((self.chan2.voltage * 0.22), 5)])
                        y2.append(self.chan2.voltage * 0.22)
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
                self.text_box.insert(tk.END, "Data was successfully written to file {}\n".format(self.csv_file3))

            # Building a plot
            if int(self.two_chan.get()) == 0 and int(self.three_chan.get()) == 0:
                # Assigning title and labels to axis
                plt.title("V = f(n)")
                plt.xlabel('Number of measurements, n')
                plt.ylabel('Voltage, V')

                # Build plot with grid and set y axis limits
                plt.plot(x, y1)
                plt.grid(True)
                plt.ylim(float(self.ymin1), float(self.ymax1))

            elif int(self.two_chan.get()) == 1:
                # Build subplot for each channel data on figure object
                fig = plt.figure(figsize=(10,5))

                # Set the title of subplots and legends, set grid, limits and build plots
                ax1 = fig.add_subplot(211)
                ax1.title.set_text("V = f(n)")
                plt.plot(x, y1)
                plt.xlabel('Number of measurements, n')
                plt.ylabel('Voltage, V')
                plt.grid(True)
                plt.ylim(float(self.ymin1), float(self.ymax1))

                ax2 = fig.add_subplot(212, sharex=ax1)
                ax2.title.set_text("I = f(n)")
                plt.plot(x, y2)
                plt.xlabel('Number of measurements, n')
                plt.ylabel('Current, I')
                plt.grid(True)
                plt.ylim(float(self.ymin2), float(self.ymax2))

                # Correct layout of subplots
                plt.tight_layout()

            # Same case with 3 channel input
            elif int(self.three_chan.get()) == 1:
                fig = plt.figure(figsize=(12,7))
                ax1 = fig.add_subplot(311)
                ax1.title.set_text("V = f(n)")
                plt.plot(x, y1)
                plt.grid(True)
                plt.xlabel('Number of measurements, n')
                plt.ylabel('Voltage, V')
                plt.ylim(float(self.ymin1), float(self.ymax1))

                ax2 = fig.add_subplot(312, sharex=ax1)
                ax2.title.set_text("I = f(n)")
                plt.plot(x, y2)
                plt.grid(True)
                plt.xlabel('Number of measurements, n')
                plt.ylabel('Current, I')
                plt.ylim(float(self.ymin2), float(self.ymax3))

                ax3 = fig.add_subplot(313, sharex=ax1)
                ax3.title.set_text("V = f(n)")
                plt.plot(x, y3)
                plt.grid(True)
                plt.xlabel('Number of measurements, n')
                plt.ylabel('Voltage, V')
                plt.ylim(float(self.ymin3), float(self.ymax3))
                fig.tight_layout()

            # If check button 'Remember values' is False, then remove values from fields
            if int(self.remember_val.get()) == 0:
                self.e1.delete(0, tk.END)
                self.e2.delete(0, tk.END)
                self.e3.delete(0, tk.END)
                self.e4.delete(0, tk.END)

            if int(self.remember_val.get()) == 0 and int(self.two_chan.get()) == 1:
                self.e5.delete(0, tk.END)
                self.e6.delete(0, tk.END)

            elif int(self.remember_val.get()) == 0 and int(self.three_chan.get()) == 1:
                self.e5.delete(0, tk.END)
                self.e6.delete(0, tk.END)
                self.e7.delete(0, tk.END)
                self.e8.delete(0, tk.END)

            # Showing plot on a screeen
            plt.show(block=False)

            # If check button 'Save figure' is True, then save the figure
            if int(self.save_fig.get()) == 1:
                self.save(self.name_for_save_fig)

        # Case if error occured while proccesing data
        except Exception as e:
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

        # Case if error occured while connecting ADS1115 to Raspberry Pi
        except Exception as e:
            print(traceback.format_exc())
            mb.showerror("ADS1115 Connection", "Failed to connect ADS1115 with Raspberry Pi:\n" + str(e))
            return

    # Main function, that makes GUI
    def init_window(self):

        try:
            # Assigning title to our window
            self.master.title("Measuring voltage")

            # Create name of entry fields
            tk.Label(self.master, padx=30, text="Delay (in ms):").grid(row=0)
            tk.Label(self.master, padx=30, text="Number of measurements:").grid(row=1)
            tk.Label(self.master, padx=30, text="Minimum of y axis channel 1:").grid(row=2)
            tk.Label(self.master, padx=30, text="Maximum of y axis channel 1:").grid(row=3)
            tk.Label(self.master, padx=30, text="Minimum of y axis channel 2:").grid(row=4)
            tk.Label(self.master, padx=30, text="Maximum of y axis channel 2:").grid(row=5)
            tk.Label(self.master, padx=30, text="Minimum of y axis channel 3:").grid(row=6)
            tk.Label(self.master, padx=30, text="Maximum of y axis channel 3:").grid(row=7)

            # Create a box, which will behave like console window
            self.text_box = tk.Text(self.master, width=50, height=15)
            self.text_box.grid(row=10, column=0, columnspan=15, sticky='W', padx=65)
            self.text_box.insert("end-1c", "Enter values\n")    

            # Add scrollbar to the Text widget
            self.scroll = tk.Scrollbar(self.master)
            self.scroll.config(command=self.text_box.yview)
            self.text_box.config(yscrollcommand=self.scroll.set)
            self.scroll.grid(row=10, column=1, columnspan=15, sticky='NS')

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
            self.e5 = tk.Entry(self.master)
            self.e6 = tk.Entry(self.master)
            self.e7 = tk.Entry(self.master)
            self.e8 = tk.Entry(self.master)

            # Assigning to fields basic values
            self.e1.insert(10, "100")
            self.e2.insert(10, "20")
            self.e3.insert(10, "1")
            self.e4.insert(10, "5")
            self.e5.insert(10, "0")
            self.e6.insert(10, "0")
            self.e7.insert(10, "0")
            self.e8.insert(10, "0")

            # Make a grid of entry fields
            self.e1.grid(row=0, column=1)
            self.e2.grid(row=1, column=1)
            self.e3.grid(row=2, column=1)
            self.e4.grid(row=3, column=1)
            self.e5.grid(row=4, column=1)
            self.e6.grid(row=5, column=1)
            self.e7.grid(row=6, column=1)
            self.e8.grid(row=7, column=1)

            # Binding Enter button as if user could press Apply button
            self.e1.bind("<Return>", self.process_data)
            self.e2.bind("<Return>", self.process_data)
            self.e3.bind("<Return>", self.process_data)
            self.e4.bind("<Return>", self.process_data)
            self.e5.bind("<Return>", self.process_data)
            self.e6.bind("<Return>", self.process_data)
            self.e7.bind("<Return>", self.process_data)
            self.e8.bind("<Return>", self.process_data)

            # Create two buttons which will call funcs if user press them
            tk.Button(self.master, text='Quit', command=self.callback).grid(row=8, column=0, sticky=tk.W, pady=10, padx=60)
            tk.Button(self.master, text='Apply!', command=self.process_data).grid(row=8, column=1, sticky=tk.W, pady=2, padx=60)
            tk.Button(self.master, text='Open file', command=self.open_file).grid(row=8, column=2, sticky=tk.W, pady=2, padx=60)
            tk.Button(self.master, text='Send file!', command=self.send_file).grid(row=10, column=2, columnspan=10, sticky=tk.W, pady=0, padx=60)

        # Case if error occured while creating a GUI window
        except Exception as e:
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

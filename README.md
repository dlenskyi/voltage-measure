# voltage-measure
Program developed for Raspberry Pi, for the purpose of measuring voltage, converted by ADS1115, and further processing data
### GUI
* Program has GUI, built using Tkinter
* For images, program uses PIL library
### Data processing
User enters in entry fields of program:
* Number of voltage measurements
* Delay in ms - interval between each measurement
* Limits of y axis (using for building figure by matplotlib)
After that, measured data(number of measurement, raw voltage values, converted voltage) will be written to csv file and a matplotlib will build a V = f(n) dependency
### Features
* User can check the box if he wants program to remember values user entered
* User can check the box if he wants to save the figure
* User can open csv file, data from file will be displayed in text box of program
* User can open saved (in png or pdf) figure. It will be opened in program window, and can be closed by pressing on image
* Exit from program using button Quit

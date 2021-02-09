# SendPlot Server
## Requirements

### Python

* Version >= 3.8.0

#### Install

* After installation add Python & Python\\scripts folders to SYSTEM PATH

----

### SendPlot

#### install

* Run Command Prompt(or Power Shell)
* cd {project folder}
* git clone https://github.com/teknoprep/sendplot.git
* cd sendplot
* python -m venv env
* env/Scripts/activate (Windows)
* pip install -r requirements.txt
* Environment settings in .env files

----

### IrfanView

* Version 4.37

#### Install

* Install to C:\\Program Files (x86)\\IrfanView\\
* Install IrfanView plugin: Postscript.dll to .\\plugins 
* Install IrfanView plugin: BabCAD4Image.dll to .\\plugins
* IrfanView > Option > Properties/Settings > Plugins > Postscript Options > select **Retrieve GS location from System Registry**

----

### GhostScript

* Version: 9.15

#### Install

* Install to C:\\usr\\local\\gs\\gs9.15
* Add C:\\usr\\local\\gs\\gs9.15\\bin to SYSTEM PATH
* Import registry key: **ghostscript.reg**

----

### novaPDF

  novaPDF is installed on client computers rather than the server.

  novaPDF is used to embed fonts within the CAD drawing PDF's.  

  Without embedded fonts Acrobat Readers substitute fonts not present on the viewing computer.  The results are not ideal.

#### Install

* Install novaPDF on computer that will produce PDF's from CAD files
* Use installation and setup instructions from the wiki -- http://odcl5/wiki/index.php/NovaPdfSettings

----


## Queue Setup & Add Printer

* The queue folders follow a similar layout to PlotManager queues.
* QUEUE-ROOT: The root folder of the PDF queues.  When SendPlot Print Server starts it makes a list of queues from the subfolders and monitors those folders for PDF files.  When a PDF file is copied into a QUEUE SendPlot Print Server prints it to the configured printer and removes the PDF file from the QUEUE.  If queue folders are added or removed restart SendPlot Server.
* QUEUE: Each available printer and page size has a separate queue.  An IrfanView INI file resides in each queue.  The INI file contains configuration options for the Printer name, page size, orientation handling and output fit to page.
* Open a PDF drawing in IrfanView
* File menu > Print
* Check **Auto Rotate**
* Select Print Size > **Best fit to page (aspect ratio)**
* Position > check **Centered**
* Printer setup button > choose printer and page size
* Test the print settings and change settings if needed
* Locate the INI file with the new settings at %APPDATA%\\IrfanView\\i_view32.ini.  (Open Windows Explorer and in the address bar type **%APPDATA%\\IrfanView\\**)
* Create a new queue folder below the QUEUE-ROOT
* Copy the new IrfanView INI file to the new queue folder and add printer to printer.json.  
    Example: "CSize": "Plotter C size",
* Do not make any other changes in IrfanView until after the INI file is copied.

----

## Environment Setup (.env)
* SCAN_DIRECTORIES: the array of directories you want to scan
  * parameters: 
    * the path of directory, 
    * the type of file you store in the directory, 
    * the URL used by the webserver
* PRINTERS: the dictionary of printers
   * key: printer's directory name
  * value: printer name to be displayed
* RESCAN_DELAY: directory scan delay time
* IN_QUEUE: Masterbills input directory
* OUT_QUEUE: Masterbills temporary output directory (for working)
* ARCHIVE: Masterbills output directory (for storage)
* MASTERBILLS_SCAN_DELAY: Masterbills scan delay time
* MASTERBILLS_LOG_DIR: Masterbills Log directory
* PRINT_QUEUE_ROOT: the root folder of the PDF queue for printing
* PRINT_LOG_FILE: Path to log file of Print Server
* I_VIEW32: Path to i_view32.exe
* PRINT_SCAN_DELAY: print scan delay time
* ADMIN_NAME: administrator's name
* ADMIN_PASSWORD: administrator's password
* TRASH_BIN: Directory where "deleted" files are stored

----
## Run

### Web Server

* run_Sendplot.cmd

----

### pyMasterbills

* run_pyMasterBills.cmd

----

### Print Server

* run_print_server.cmd




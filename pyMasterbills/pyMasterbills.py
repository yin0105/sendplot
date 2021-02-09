import os
import glob
import signal
import sys
import logging
import shutil
import time
import datetime
import json

import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4, LEGAL, elevenSeventeen,landscape

from os.path import join, dirname
from dotenv import load_dotenv
import dotenv
from pathlib import Path



start_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# last_time_path = sys.path[0]
# print(last_time_path)
# last_time_path = last_time_path[:last_time_path.rfind("\\")] + "\\WebServer\\last_time.txt"
# print(last_time_path)
    # last_date = os.environ.get('LAST_DATE')
# print(os.path.isfile(last_time_path))
file1 = open(join(dirname(__file__), '..\\WebServer\\static\\last_time.txt'),"r")  
  
last_date = file1.read() 
print("last_date = " + last_date)
file1.close()

# dotenv.set_key(dotenv_path, "LAST_DATE", start_time)
file1 = open(join(dirname(__file__), '..\\WebServer\\static\\last_time.txt'),"w")  
file1.write(start_time)
file1.close()

in_queue    = os.environ.get('IN_QUEUE') + "\\"
out_queue   = os.environ.get('OUT_QUEUE') + "\\"
archive     = os.environ.get('ARCHIVE') + "\\"
log_dir     = os.environ.get('MASTERBILLS_LOG_DIR') + "\\"
scan_delay  = float(os.environ.get('MASTERBILLS_SCAN_DELAY'))


class Logger(logging.Logger):
  def __init__(self):
    logging.Logger.__init__(self, 'masterbill_processor')

    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
    #     Set level for the events to be logged
    self.root.setLevel(logging.NOTSET)
    #     Create handler for logging to console
    console = logging.StreamHandler()
    console.setLevel(0)
    console.setFormatter(formatter)
    self.addHandler(console)
    #     Create handler for logging to log file
    sLogFile = log_dir + 'masterbill_processor.log'
    fileHandler = logging.FileHandler(sLogFile)
    fileHandler.setFormatter(formatter)
    self.addHandler(fileHandler)

def signal_handler(signal, frame):
    print ('Shutting down Masterbill Processor!')
    logger.info('\tshutting down...')
    logger.info('========================= Masterbill Processor shutdown ========================')
    writeLogToHtml()
    sys.exit(0)

def checkMasterbillComplete(mb_file):
  #     check that 80 files are in the masterbill folder
  os.chdir(in_queue + mb_file)

  if len(glob.glob('??')) == 80:
    return True
  elif len(glob.glob('??')) == 79:
    return True
  elif len(glob.glob('??')) == 70:
    return True
  elif len(glob.glob('??')) == 59:
    return True
  elif len(glob.glob('??')) == 56:
    return True
  elif len(glob.glob('??')) == 55:
    return True
  elif len(glob.glob('??')) == 46:
    return True
  else:
    return False

  if len(os.listdir('.')) < 80:
    #     return false if all of the files/lines are not complete
    return False

  #     return true if all of the files/lines are complete
  return True

def combineMasterbill(mb_file):
  os.chdir(in_queue + mb_file)

  #     Prefix single digit files with a zero to sort correctly
  for file in os.listdir('.'):              
      if len(file) == 1:                         
          os.rename(file, '0' + file)

  files              = os.listdir('.')
  # files.sort()
  files = sorted(files)

  in_file  = ''
  out_file = open(mb_file + '.txt', 'w')

  iCnt     = 0

  for file in files:
    in_line         = open(file, 'r')
    in_file         = in_file + in_line.readline()
    in_line.close()

    iCnt            = iCnt + 1

  time_stamp         = 'Masterbill converted to PDF ' + datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%y %H:%M:')
  in_file            = in_file + time_stamp.rjust(196)

  logger.info('master bill lines: ' + str(iCnt))

  #if iCnt == 55:
  search_for   = '--------------------------------------------------------------------------------'
  logger.info('find search_for: ' + str(in_file.find(search_for)))
  if in_file.find(search_for) > 0:
    logger.info('change part sheet')
    replace_with = '--------------------------------------------------------------------------------\n'
    in_file      = in_file.replace(search_for, replace_with)

  out_file.write(in_file)
  out_file.close()
  os.chdir('..')
  
  return out_file

def processFile(fIn, fOut, fname):
    f             = open(fIn,'r')
    lines         = f.readlines()
    f.close()
    c             = canvas.Canvas(fOut, pagesize = landscape(elevenSeventeen))
    file_type     = fname[0].upper()

    if file_type  == 'A':
      left_margin = .1
      left_start  = 0
    else:
      left_margin = .15
      left_start  = 0


    textobject    = c.beginText()
    textobject.setFont("Courier", 10, leading=9)
    
    textobject.setTextOrigin(left_margin*inch, 10.6*inch)
    
    iCnt     = 0
    lenLines = len(lines)
    for line in lines:
        textobject.textLine(line[left_start:-1])
        iCnt = iCnt + 1
        if iCnt > 85 or iCnt == lenLines:
            c.drawText(textobject)
            c.showPage()
            textobject = c.beginText()
            textobject.setFont("Courier", 8)
            textobject.setTextOrigin(left_margin*inch, 10.6*inch)
            iCnt = 0
    try:
      c.save()
      logger.info('saved file: ' + fOut)
    except:
      logger.info('cannot save file: ' + fOut)

def time_stamp(): 
  return datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%y %H:%M:%S')

def check_older_out_queue():
  #       check masterbill out queue for and delete older files
  now = time.time()
  if not os.path.exists(out_queue):
    logger.info('cannot access ' + out_queue)
  else:
    for file in os.listdir(out_queue):
      if os.path.isfile(os.path.join(out_queue, file)):
        try:
          if os.stat(out_queue + file).st_mtime < now - 86400:
            ts = time_stamp()
            logger.info('deleting older file: ' + file)
            os.remove(out_queue + file)
        except Exception as e:
          logger.info('failed to delete older pdf file')
          logger.info(e)

    for file in os.listdir(out_queue + 'text'):
      if os.path.isfile(file):
        try:
          if os.stat(out_queue + 'text/' + file).st_mtime < now - 86400:
            ts = time_stamp()
            logger.info('deleting older text file: ' + file)
            os.remove(out_queue + 'text/' + file)
        except Exception as e:
          logger.info('failed to delete older file')
          logger.info(e)


def check_existing_pdf(pdf):
  #       check if pdf exists
  #       try to delete pdf
  #       if delete fails log event and skip to next file in queue
  #       NOTE: if someone has the PDF open the processor cannot replace it
  if os.path.exists(pdf):
    try:
      #     log remove existing pdf
      logger.info('removing existing file - ' + pdf)
      os.remove(pdf)
      return True
    except Exception as e:
      #     log failed delete
      logger.info('failed to remove existing file - ' + pdf)
      logger.info(e)
      return False
  else:
    return True


def writeLogToHtml():  
  sLogFile = log_dir + 'masterbill_processor.log'
  sHtmlFile = log_dir + 'masterbill-log.html'  #'//ntsvr4/www_eng$/masterbill-log.html'
  sMblogFile = log_dir + 'mblog.json'  #'//ntsvr4/www_eng$/mblog.json'
  sMbqueueFile = log_dir + 'mbqueue.json'  #'//ntsvr4/www_eng$/mbqueue.json'

  if os.path.getsize(sLogFile) > 100 * 1024:
    filehandle = open(sLogFile, 'w')
    filehandle.write('Clearing Large File\n')
    filehandle.close()
    print("Clearing Large File")
      
  if not os.path.exists(sHtmlFile):
    logger.info('cannot access ' + sHtmlFile)
  else:
    fLog_file = open(sLogFile, 'r')
    lines = fLog_file.readlines()
    fLog_file.close()
    num_of_lines = len(lines)
    lines_reversed = lines[::-1]
    out = lines_reversed[:15]
    mblog_json = []
    mbqueue_json = []
    html_out = '<html><head><title>Masterbill Processor Logs</title>'
    html_out = html_out + '<meta http-equiv="refresh" content="10"></head><body>'
    html_out = html_out + '<span style="font-size: 18pt; font-family: arial;">Masterbill Processor Log</span>'
    html_out = html_out + '<span style="font-size: 18pt; font-family: arial; float: right;">' + time_stamp() + '&nbsp;'
    html_out = html_out + '<img src="/images/ajax-loader.gif" width="25" height="25">&nbsp;</span><br><br><hr>'

    html_out = html_out + '<div style="font-size: 14pt; font-family: arial;">Masterbill Output [F:\Operations\Masterbills]<br><ul>'
    output_masterbills = filter(os.path.isfile, glob.glob(out_queue + '*.pdf'))
    # output_masterbills.sort(key=lambda x: os.path.getmtime(x))
    output_masterbills = sorted(output_masterbills, key=lambda x: os.path.getmtime(x))
    output_masterbills_r = output_masterbills[::-1]

    for mb in output_masterbills_r:                                                                                              
      mb_out = mb[mb.rfind('\\'):]                                                                                       
      mbqueue_json.append(mb_out[1:]) 
      html_out = html_out + '<li><a target="_blank" href="http://ntsvr4/masterbills/' + mb_out[1:] + '">' 
      html_out = html_out + '<img src="/images/acrobat.jpg" width="25" height="25"> &nbsp; ' + mb_out[1:].upper() + '</a> &nbsp; '
      html_out = html_out + '<a target="_blank" href="http://ntsvr4/masterbills/text/' + mb_out[:-3] + 'txt" title="  Text version of the Masterbill -- right-click Save Link as  ">'
      html_out = html_out + '<img src="/images/notepad01.gif" width="12" height="12"></a></li>'
      
    html_out = html_out + '</ul>Newest files at the top | Masterbills cleared from output queue after 24 hours.<hr>'
    html_out = html_out + '</div><div style="font-size: 8pt; font-family: arial; color: #090; background: #eee; padding: 4px;"><pre>'

    for line in out:
      html_out = html_out + line
      mblog_json.append(line[:-1])

    html_out = html_out + '</pre></div><hr></body></html>'

    fHtml = open(sHtmlFile, 'w')
    fHtml.write(html_out)
    fHtml.close()

    fMblog = open(sMblogFile, 'w')
    fMblog.write(json.dumps(mblog_json))
    fMblog.close()

    fMbqueue = open(sMbqueueFile, 'w')
    fMbqueue.write(json.dumps(mbqueue_json))
    fMbqueue.close()


# Initialize application
logger = Logger()

logger.info('Masterbill processor ||||||||||||||||||||||||||||||||||')

logger.info('Initializing...')

ts = time_stamp()
logger.info('starting...')

signal.signal(signal.SIGINT, signal_handler)
logger.info('\t\t\t ===[ Press Ctrl+C to shutdown Masterbill Processor ]===')

while 1:
  if not os.path.exists(in_queue):
    logger.info('cannot access ' + in_queue)
    #     TODO call function to net use omega_p640\smbshare
  else:
    inqueue = os.listdir(in_queue)
    for mb_file in inqueue:
      is_file = os.path.isfile(mb_file)
      is_dir  = os.path.isdir(mb_file)
      exists  = os.path.exists(mb_file)
      logger.info(mb_file + '\tisfile: ' + str(is_file) + '\t isdir: ' + str(is_dir) + '\t exists: ' + str(exists))
#       if os.path.isdir(mb_file):
      if checkMasterbillComplete(mb_file):
        # compare timestamp
        mtime = os.path.getctime(in_queue + mb_file)
        if mtime < os.path.getmtime(in_queue + mb_file):
          mtime = os.path.getmtime(in_queue + mb_file)
        created_date = datetime.fromtimestamp(mtime)
        if created_date <= datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S'): continue
        fname = combineMasterbill(mb_file).name

        txt   = in_queue + mb_file + '\\' + fname
        pdf   = out_queue + mb_file + ".pdf"
        ts    = time_stamp()
        logger.info('processing ' + mb_file)

        # don't remove existing pdf files (updated part)

        # if not check_existing_pdf(pdf):
        #   #    check for existing pdf
        #   #    if older pdf cannot be removed skip until next cycle
        #   break

        processFile(txt, pdf, fname)

        ts       = datetime.datetime.fromtimestamp(time.time()).strftime('%y-%m-%d')
        new_name = ts + '_' + mb_file

        #     copy a text version of the mb file
        shutil.copy(txt, out_queue + 'text\\')

        os.rename(in_queue + mb_file, new_name)
        if os.path.exists(archive + new_name):
          #     remove existing archive folder to allow archiving the new masterbill folder
          shutil.rmtree(archive + new_name)

        shutil.move(in_queue + new_name, archive)

        try:
          shutil.copy(pdf, archive)
        except Exception as e:
          logger.info('copy pdf to archive failed')
          logger.info(e)

        logger.info('finished ' + mb_file)
      else:
        ts = time_stamp()
        logger.info('partial ' + mb_file)
#     else:
#       logger.warning('WARNING: file in root of IN_QUEUE \t' + mb_file)

  

  check_older_out_queue()

  writeLogToHtml()

  time.sleep(scan_delay)




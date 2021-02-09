import glob
import json
import timeit
import os
from os.path import join, dirname
from dotenv import load_dotenv
import threading

# aDirs = [['h:\\plot\\scanned_tif', 'tif'], ['h:\\plot\\masterbills', 'tif'],
#          ['h:\\plot\\apdf', 'pdf'], [
#              'h:\\plot\\bpdf', 'pdf'], ['h:\\plot\\pdf', 'pdf'],
#          ['h:\\plot\\cpdf', 'pdf'], [
#              'h:\\plot\\dpdf', 'pdf'], ['h:\\plot\\dxf', 'dxf'],
#          ['h:\\plot\\aprf', 'prf'], ['h:\\plot\\bprf', 'prf'], [
#              'h:\\plot\\cprf', 'prf'],
#          ['h:\\plot\\dprf', 'prf'],
#          ['l:\\PDFDrawings', 'pdf'], ['l:\\Drawings', 'dwg'], [
#              'l:\\SWDRAW~1', 'slddrw'],
#          ['l:\\SWMODE~1', 'sld*'], ['f:\\ISNETW~1\\mrp\\masterbill_archive', 'pdf'],
#          ['g:\\MB-ss\\SCANNE~1\\imported', 'pdf'], ['I:\\research\\R51541\\Finished', 'sld*']]


def get_dir_dict(fDir, fType, fLink):
    aDir = glob.glob(fDir + '/*.' + fType)
    tmp_dict = {}
    for item in aDir:
        basename = item[item.rfind('\\') + 1:item.rfind('.')].upper()
        # basename = basename.upper()
        # print fLink, item
        tmp_dict[basename] = item
    return tmp_dict


def get_dir_combined(dDrawingList):
    for item in dDrawingList:        
        if item in dCombined:
            dCombined[item].append(dDrawingList[item])
        else:
            dCombined[item] = [dDrawingList[item]]

def scan_all_directories():
    global dCombined, rescan_delay
    dCombined = {}
    print("Scanning directories ...")
    for drawing_directory in aDirs:
        dDirectory = get_dir_dict(drawing_directory[0], drawing_directory[
                                  1], drawing_directory[2])
        get_dir_combined(dDirectory)
    fJSON = open('combined_directories.json', 'w')
    fJSON.write(json.dumps(dCombined, sort_keys=True,
                           indent=2, separators=(',', ': ')))
    fJSON.close()
    threading.Timer(rescan_delay * 60, scan_all_directories).start()


def read_json():
    global dCombined
    with open('combined_directories.json') as json_file:
        dCombined = json.load(json_file)


def search_for_drawing():
    for key, value in dCombined.items():
        if sSearch == '*':
            dReturned[key] = value
        elif key.startswith(sSearch):
            dReturned[key] = value


def save_directories():
    fJSON = open('scanned_directories.json', 'w')
    fJSON.write(json.dumps(aDirs, sort_keys=True,
                           indent=2, separators=(',', ': ')))
    fJSON.close()


def read_directories():
    # with open('scanned_directories.json') as json_file:
    #     dDirectories = json.load(json_file)
    dotenv_path = join(dirname(__file__), '../.env')
    load_dotenv(dotenv_path)
    scan_directories_env = os.environ.get('SCAN_DIRECTORIES')
    dDirectories = []
    for line in scan_directories_env.splitlines():
        if line.strip() == "": continue
        line_tmp = []
        for word in line.split(","):
            word = word.strip()
            line_tmp.append(word[1:-1])
        dDirectories.append(line_tmp)
    # print(dDirectories)
    return dDirectories


#############################################################################

dCombined = {}
dReturned = {}

sScanned = 0
sSearch = ''
sSearched = 0
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
rescan_delay = float(os.environ.get('RESCAN_DELAY'))
print("#" + str(rescan_delay) + "#")

aDirs = read_directories()

# if len(sys.argv) >= 2:
#   sSearch = sys.argv[1].upper()
# else:
#   sSearch = '*'

sScanned = str(timeit.timeit(stmt=scan_all_directories, number=1))
# sScanned           = str(timeit.timeit(stmt=read_json, number=1))
# sSearched          = str(timeit.timeit(stmt=search_for_drawing, number=1))

dReturned['stats'] = {'search_string': sSearch + '...',
                      'total_searched': str(len(dCombined)),
                      'scan_time': sScanned,
                      'drawings_found': str(len(dReturned)),
                      'search_time': sSearched}



# save_directories()

# print json.dumps(dReturned, sort_keys=True, indent=2, separators=(',', ': '))

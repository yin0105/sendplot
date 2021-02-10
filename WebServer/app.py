from flask import Flask, abort, render_template, send_from_directory, request, make_response

from cachelib.simple import SimpleCache
from flask_debugtoolbar import DebugToolbarExtension

import os
import json
import time
import logging
import re
import urllib3, shutil
from shutil import copyfile
from livereload import Server
from os.path import join, dirname, exists
from dotenv import load_dotenv
import fetch_drawings

path_url = {}
url_path = {}

app = Flask(__name__)
app.secret_key = 'l1wovKLN7xsMT5bieGN3vVnyhzQwNJmdmzzr5NMjC7AbaxJyRx34n5qXHuDBHBXUix2BLlBeoDZNh3XcNqUZLHC6oZzVioCq'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


#                Set app.debug = True to enable Debug Toolbar
app.debug = False
toolbar = DebugToolbarExtension(app)

cache = SimpleCache()
CACHE_TIMEOUT = 30

SEARCH_LIMIT = 1000

PRF_PLOT = 'h:\\PLOT\\'
# QUEUES = 'G:\\queues\\'
# QUEUES_PDF = 'G:\\queues\\pdfOut\\'
QUEUES          = os.environ.get('PRINT_QUEUE_ROOT')
QUEUES_PDF      = os.environ.get('PRINT_QUEUE_ROOT')
USER            = os.environ.get('USER')
PASSWORD        = os.environ.get('PASSWORD')

DRAWING_CHARACTERS = "ABCDEX012345"
X_PART_CHARACTERS = "12345"
rx = re.compile('[a-zA-z]')


class Logger(logging.Logger):

    def __init__(self):
        logging.Logger.__init__(self, 'sendplot_flask')

        formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
        #     Set level for the events to be logged
        self.root.setLevel(logging.NOTSET)
        #     Create handler for logging to console
        console = logging.StreamHandler()
        console.setLevel(0)
        console.setFormatter(formatter)
        self.addHandler(console)
        #     Create handler for logging to log file
        sLogFile = 'C:/var/hg/sendplot.flask/log/sendplot.log'
        fileHandler = logging.FileHandler(sLogFile)
        fileHandler.setFormatter(formatter)
        self.addHandler(fileHandler)


@app.route('/')
def default():
    logger.info(request.method + ' - ' + request.path +
                ' - ' + request.remote_addr + ' - index')
    resp = make_response(render_template('index.html', user=''))
    return resp
    # return render_template('index.html')


@app.route('/login', methods = ['POST', 'GET'])
def login():
    logger.info(request.method + ' - ' + request.path +
                    ' - ' + request.remote_addr + ' - login')
    resp = make_response(render_template('login.html', data = "ok"))
    if request.method == 'POST':
        if os.environ.get('ADMIN_NAME') == request.form['user'] and os.environ.get('ADMIN_PASSWORD') == request.form['password']:
            resp = make_response(render_template('index.html', user='admin'))
        else:
            resp = make_response(render_template('login.html'))
    else:
        print("GET::::::::::::::::::::::::::::")
        
    return resp


@app.route('/file_del/<string:data_id>', methods = ['POST', 'GET'])
def file_del(data_id):
    dReturned = {}
    dCombined = read_json()
    trash_bin = os.environ.get('TRASH_BIN')
    for key, value in dCombined.items():
        key = key.upper()
        new_value = []
        if key == data_id:
            for v in value:
                ext = v[-3:]
                if ext.upper() != "PDF": 
                    new_value.append(v)
                    continue
                if exists(v):
                    try:
                        shutil.move(v, trash_bin)
                        print(v + " is removed.")
                    except:
                        return ""
                else:
                    return ""
            if len(new_value) > 0: dReturned[key] = new_value
                
        else:
            dReturned[key] = value
    fJSON = open('combined_directories.json', 'w')
    fJSON.write(json.dumps(dReturned))
    fJSON.close()

    return "ok"

@app.route('/q/<q>')
def index(q):
    return render_template('index.html', q=q)

# *********************************************************************************************
# *          Private functions
# *********************************************************************************************


def read_json():
    dCombined = cache.get('dCombined')
    if dCombined is None:
        logger.info('Cache miss -')
        dCombined = {}
        with open('combined_directories.json') as json_file:
            dCombined = json.load(json_file)
        cache.set('dCombined', dCombined, timeout=CACHE_TIMEOUT)
    else:
        logger.info('Cache hit ++')
    return dCombined


def get_web_links(links):
    global path_url
    web_links = []
    for link in links:
        last_slash = link[0].rfind('\\')
        tmp_arr = []
        # next_slash = url[0:last_slash].rfind('\\') + 1
        # web_links.append(
        #     '/download' + get_url(url[next_slash:last_slash]) + url[url.rfind('\\') + 1:])
        tmp_arr.append('/download/' + path_url[link[0][:last_slash]] + "/" + link[0][link[0].rfind('\\') + 1:])
        tmp_arr.append(link[1])
        web_links.append(tmp_arr)
    return web_links


def search_for_drawing(q, dCombined):
    # logger.info(request.method + ' - ' + request.path + ' - ' + ' - search_for_drawing')
    iLimit = 0
    dReturned = {}
    q = q.upper()
    for key, value in dCombined.items():
        if iLimit > SEARCH_LIMIT:
            return dReturned
        key = key.upper()
        if q == '*':
            dReturned[key] = get_web_links(value)
            iLimit += 1
        elif key.startswith(q):
            dReturned[key] = get_web_links(value)
            iLimit += 1
    return dReturned


# def read_mb_notes_json():
#     dMbNotes = {}
#     with open('mb_notes.json') as json_file:
#         dMbNotes = json.load(json_file)
#     return dMbNotes


def search_for_mb_notes(q, dMbNotes):
    dReturned = {}
    for key, value in dMbNotes.items():
        if key == q:
            dReturned[key] = value
    return dReturned


# def get_path(file_url):
#     return {
#         'drawings': 'l:\\Drawings',
#         'pdf_out': 'l:\\pdf_out',
#         'tiff_pdf': 'l:\\tiff_pdf',
#         'swcommercial': 'l:\\SWCOMM~1',
#         'swdrawings': 'l:\\SWDRAW~1',
#         'swmodels': 'l:\\SWMODE~1',
#         'swreference': 'l:\\SWREFE~1',
#         'pdfdrawings': 'l:\\PDFDrawings',
#         'scanned_asize' : 'l:\\scanned_asize',
#         'mb-archive': 'f:\\ISNETW~1\\mrp\\masterbill_archive',
#         'masterbills': 'h:\\plot\\masterbills',
#         'apdf': 'h:\\plot\\apdf',
#         'bpdf': 'h:\\plot\\bpdf',
#         'cpdf': 'h:\\plot\\cpdf',
#         'dpdf': 'h:\\plot\\dpdf',
#         'pdf': 'h:\\plot\\pdf',
#         'aprf': 'h:\\plot\\aprf',
#         'bprf': 'h:\\plot\\bprf',
#         'cprf': 'h:\\plot\\cprf',
#         'dprf': 'h:\\plot\\dprf',
#         'dxf': 'h:\\plot\\dxf',
#         'scanned-tif': 'h:\\plot\\scanned_tif',
#         'imported': 'g:\\MB-ss\\SCANNE~1\\imported',
#         'finished': 'i:\\research\\R51541\\Finished'
#     }[file_url]


# def get_url(web_url):
    # print("web_url = " + web_url)
    # return {
    #     'Drawings': '/drawings/',
    #     'pdf_out': '/pdf_out/',
    #     'pdfout': '/pdfout/',
    #     'tiff_pdf': '/tiff_pdf/',
    #     'SWCOMM~1': '/swcommercial/',
    #     'SWDRAW~1': '/swdrawings/',
    #     'SWMODE~1': '/swmodels/',
    #     'SWREFE~1': '/swreference/',
    #     'PDFDrawings': '/pdfdrawings/',
    #     'scanned_asize': '/scanned_asize/',
    #     'masterbill_archive': '/mb-archive/',
    #     'masterbills': '/masterbills/',
    #     'apdf': '/apdf/',
    #     'bpdf': '/bpdf/',
    #     'cpdf': '/cpdf/',
    #     'dpdf': '/dpdf/',
    #     'pdf': '/pdf/',
    #     'aprf': '/aprf/',
    #     'bprf': '/bprf/',
    #     'cprf': '/cprf/',
    #     'dprf': '/dprf/',
    #     'dxf': '/dxf/',
    #     'scanned_tif': '/scanned-tif/',
    #     'imported': '/imported/',
    #     'finished': '/finished/'
    # }[web_url]

# Routed folders
    # '/drawings/'            | '/Drawings/'           | 'l:\\Drawings'                           'dwg'
    # '/pdf_out/'             | '/pdf_out/'            | 'l:\\pdf_out'                            'pdf'
# '/tiff_pdf/'            | '/tiff_pdf/'           | 'l:\\tiff_pdf'                           'pdf'
    # '/swcommercial/'        | '/SWCOMM~1/'           : 'l:\\SWCOMM~1'
    # '/swdrawings/'          | '/SWDRAW~1/'           | 'l:\\SWDRAW~1'                           'slddrw'
    # '/swmodels/'            | '/SWMODE~1/'           | 'l:\\SWMODE~1'                           'sld*'
    # '/swreference/'        | '/SWREFE~1/'           : 'l:\\SWREFE~1'
    # '/pdfdrawings/'         | '/PDFDrawings/'        | 'l:\\PDFDrawings'                        'pdf'
    # '/mb-archive/'          | '/masterbill_archive/' | 'f:\\ISNETW~1\\mrp\\masterbill_archive'  'pdf'
    # '/masterbills/'         | '/masterbills/'        | 'h:\\plot\\masterbills'                  'tif'
    # '/apdf/'                | '/apdf/'               | 'h:\\plot\\apdf'                         'pdf'
    # '/bpdf/'                | '/bpdf/'               | 'h:\\plot\\bpdf'                         'pdf'
    # '/cpdf/'                | '/cpdf/'               | 'h:\\plot\\cpdf'                         'pdf'
    # '/dpdf/'                | '/dpdf/'               | 'h:\\plot\\dpdf'                         'pdf'
    # '/dxf/'                 | '/dxf/'                | 'h:\\plot\\dxf'                          'dxf'
    # '/pdf/'                 | '/pdf/'                | 'h:\\plot\\pdf'                          'pdf'
    # '/scanned-tif/'         | '/scanned_tif/'        | 'h:\\plot\\scanned_tif'                  'tif'
    # '/imported/'            | '/imported/'           | 'g:\\MB-ss\\SCANNE~1\\imported'          'pdf'

# *********************************************************************************************
# *          Private functions
# *********************************************************************************************

# *********************************************************************************************
# *          Downloads
# *********************************************************************************************


@app.route('/download/<path:filepath>/<path:filename>')
def download(filepath, filename):
    logger.info(request.method + ' - ' + request.path + ' - ' +
                request.remote_addr + ' - download file - ' + filename)
    if '..' in filename or filename.startswith('/'):
        abort(404)
    directory = url_path[filepath]
    logger.info('file path: ' + directory)
    if os.path.isfile(directory + '\\' + filename):
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        sReturn = {}
        sReturn['results'] = 'File not found on server.'
        return(json.dumps(sReturn))

# *********************************************************************************************
# *          Downloads
# *********************************************************************************************

# *********************************************************************************************
# *           Print
# *********************************************************************************************


@app.route('/print/<path:printer>/<path:folder>/<path:filename>')
def print_file(printer, folder, filename):
    # remote_address = socket.gethostbyaddr(request.remote_addr)
    # logger.info(request.method + ' - ' + request.path + ' - ' + remote_address[0] + ' - download file - ' + filename)
    logger.info('printer ******************')
    logger.info(printer)
    logger.info(folder)
    logger.info(filename)
    returnJSON = {}
    returnJSON['printer'] = printer
    returnJSON['file'] = filename
    returnJSON['result'] = 'success'
    returnJSON['description'] = filename[filename.rfind('.'):].upper()

    logger.info('File exists? ' +
                str(os.path.isfile(url_path[folder] + '\\' + filename)))

    if os.path.isfile(url_path[folder] + '\\' + filename):
        if filename[filename.rfind('.'):].upper() == '.PDF':
            returnJSON['action'] = 'Print PDF (Acrobat)'
            returnJSON['result'] = 'success'
            # returnJSON['folder'] = get_path(folder)
            copyfile(url_path[folder] + '\\' + filename,
                     QUEUES_PDF + '\\' + printer + '\\' + filename)
        elif filename[filename.rfind('.'):].upper() == '.PRF':
            returnJSON['action'] = 'Print PRF (PlotManager)'
            returnJSON['result'] = 'success'
            copyfile(PRF_PLOT + folder + '\\' + filename,
                     QUEUES + printer + '\\' + filename)

        logger.info('Print success: ' + filename)
        return json.dumps(returnJSON), 200

    else:
        returnJSON['action'] = 'Missing file: ' + filename
        returnJSON['result'] = 'failed'
        logger.info('Print failed (file not found): ' + filename)
        return json.dumps(returnJSON), 400

# *********************************************************************************************
# *           Print
# *********************************************************************************************

# *********************************************************************************************
# *           API calls
# *********************************************************************************************


@app.route('/api/search/')
@app.route('/api/search/<q>')
def search(q='None'):
    # logger.info(request.method + ' - ' + request.path + ' - ' + request.remote_addr + ' - search query: "' + q + '"')
    dReturned = {}
    dCombined = read_json()
    dReturned = search_for_drawing(q, dCombined)
    if len(dReturned) == 0:
        dReturned['results'] = 'no files found'

    return json.dumps(dReturned)


@app.route('/api/set_printer/<default_printer>')
def set_printer(default_printer):
    # print '\t default_printer'
    # print default_printer
    # print '******************************************'
    response = make_response()
    response.set_cookie('default_printer', default_printer)
    return response


@app.route('/api/get_printer/')
def get_printer():
    logger.info('get default printer')
    if 'default_printer' in request.cookies:
        default_printer = request.cookies.get('default_printer')
    else:
        default_printer = 'no cookie'
    dPrinter = {}
    dPrinter['default_printer'] = default_printer
    return default_printer


@app.route('/api/get_printers/')
def get_printers():
    dotenv_path = join(dirname(__file__), '../.env')
    load_dotenv(dotenv_path)
    dPrinters = json.loads(str(os.environ.get('PRINTERS')))
    return json.dumps(dPrinters)


@app.route('/api/get_file_meta/<path:filepath>/<path:filename>')
def get_file_meta(filepath, filename):
    # logger.info('meta file path: ')
    # logger.info(filepath)
    # logger.info(filename)
    file_meta = {}
    file_meta['link'] = '/download/' + filepath + '/' + filename
    # ********* Do not return path to web
    file_meta['path'] = url_path[filepath]
    file_meta['name'] = filename
    # ********* Check if files exists
    if os.path.isfile(file_meta['path'] + '\\' + file_meta['name']):
        file_meta['modified'] = time.ctime(os.path.getmtime(
            file_meta['path'] + '\\' + file_meta['name']))
        file_meta['created'] = time.ctime(os.path.getctime(
            file_meta['path'] + '\\' + file_meta['name']))
        file_meta['size'] = float(os.path.getsize(
            file_meta['path'] + '\\' + file_meta['name'])) / 1024 / 1024
    else:
        file_meta['modified'] = 'N/A'
        file_meta['created'] = 'N/A'
        file_meta['size'] = 'N/A'
    file_meta.pop('path', None)
    return json.dumps(file_meta)


# @app.route('/api/get_mb_drawings/<q>')
# def get_mb_drawings(q):
#     print ('\t\t\t ' + q)
#     dMbDrawings = {}
#     with open('mb_drawings.json') as json_file:
#         dMbDrawings = json.load(json_file)

#     dReturned = {}
#     for key, value in dMbDrawings.items():
#         if key == q:
#             # logger.info( 'key, value')
#             # logger.info(  key )
#             # for item in value:
#             #   logger.info( item )
#             # logger.info( value )
#             dReturned[key] = value
#     return json.dumps(dReturned)


# @app.route('/api/get_media/<q>')
# def get_media(q):
#     print ('\t\t\t ' + q)
#     dMedia = {}
#     with open('picture_directories.json') as json_file:
#         dMedia = json.load(json_file)

#     dReturned = {}
#     for key, value in dMedia.items():
#         if key == q:
#             # logger.info( 'key, value')
#             # logger.info(  key )
#             # for item in value:
#             #   logger.info( item )
#             # logger.info( value )
#             dReturned[key] = value
#     return json.dumps(dReturned)


@app.route('/api/get_media_folder/<q>')
def get_media_folder(q):
    dMedia = {}
    lMedia = []
    safe_files = ['.JPG', '.MP4', '.AVI', '.MOV', '.PNG', '.TIF']
    q = urllib3.unquote(q)
    q = q.replace('\\\\', '/')
    for file in os.listdir(q):
        if file[-4:].upper() in safe_files:
            lMedia.append(file)

    dMedia[q] = lMedia

    return json.dumps(dMedia)


# @app.route('/api/get_misplaced_files')
# def get_misplaced_files():

#     with open('misplaced_files.json') as json_file:
#         dMisplacedFiles = json.load(json_file)

#     return json.dumps(dMisplacedFiles)


@app.route('/api/get_image/<q>/<r>')
def get_image(q, r):
    q = q.replace('\\\\', '/')
    q = urllib3.unquote(q)
    r = urllib3.unquote(r)
    filename = r
    directory = q
    logger.info(filename)
    logger.info(directory)
    if os.path.isfile(q + '\\' + r):
        return send_from_directory(directory, filename, as_attachment=False)
    else:
        sReturn = {}
        sReturn['results'] = 'File not found on server.'
        return(json.dumps(sReturn))


# @app.route('/api/get_mb_notes/<q>')
# def get_mb_notes(q):
#     # logger.info(request.method + ' - ' + request.path + ' - ' + request.remote_addr + ' - search query: "' + q + '"')
#     dMbNotes = read_mb_notes_json()
#     dReturned = search_for_mb_notes(q, dMbNotes)
#     return json.dumps(dReturned)

@app.route('/api/rescan')
def rescan():  
    fetch_drawings.scan_all_directories()
    return ""


@app.route('/api/json_del')
def json_del():  
    json_arr = ["combined_directories", "mb_drawings", "mb_notes", "misplaced_files", "picture_directories"]
    try:
        for json_file in json_arr:
            fJSON = open(json_file + '.json', 'w')
            fJSON.write("")
            fJSON.close()
    except:
        return ""
    return "ok"


def read_directories():
    global path_url, url_path
    dotenv_path = join(dirname(__file__), '../.env')
    load_dotenv(dotenv_path)
    scan_directories_env = os.environ.get('SCAN_DIRECTORIES')
    for line in scan_directories_env.splitlines():
        if line.strip() == "": continue
        try :
            line_tmp = [word.strip()[1:-1] for word in line.split(",")]

            # Append path_url dictionary
            if line_tmp[0] in path_url.keys():
                if line_tmp[2] != path_url[line_tmp[0]] :
                    return (1, line_tmp[0])
            else:
                path_url[line_tmp[0]] = line_tmp[2]

            # Append url_path dictionary
            if line_tmp[2] in url_path.keys():
                if line_tmp[0] != url_path[line_tmp[2]] :
                    return (2, line_tmp[2])
            else:
                url_path[line_tmp[2]] = line_tmp[0]
        except :
            return (0, "")
    
    return (3, "")

# *********************************************************************************************
# *           API calls
# *********************************************************************************************


logger = Logger()

logger.info('SendPlot.flask ||||||||||||||||||||||||||||||||||')

logger.info('Initializing...')

logger.info('starting...')




if __name__ == '__main__':
    server = Server(app.wsgi_app)

    server.watch('*.py')
    server.watch('*.cmd')
    server.watch('templates/*.html')
    server.watch('static/docs/*.html')
    server.watch('static/css/*.css')
    server.watch('static/js/*.js')
    server.watch('static/js/app.coffee', 'make_coffee.cmd', delay=1)
    server.watch('static/docs/*.md', 'make_docs.cmd', delay=1)

    result, path = read_directories()
    if result < 3:
        print("""
        
            ######################################################################
            #                                                                    #
            #       Check the SCAN_DIRECTORIES variable in the .env file.        #""")
        if result == 1:
            print("            #       There are duplicate directory path.  (See below.)            #")
        elif result == 2:
            print("            #       There are duplicate URLs.  (See below.)                      #")
        
        print("""            #                                                                    #
            ######################################################################
            """)

        if result == 1:
            print("")
            print("            duplicate URL: " + path)        
        elif result == 2:
            print("")
            print("            duplicate path: " + path)

        print("")
    else:
        # server.serve(port=80)
        app.run()

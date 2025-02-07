import threading
import sqlite3
import subprocess
import sys
import os
import time
import random
import pickle
import gzip
import shutil
from enum import Enum
import tempfile
import string
import inspect
import builtins
import io

from instances import *
# from gui import *
# import gui

class PrintLock:
    _ = threading.Lock()

def print(*args, **kwargs):
    # print arguments
    buffer_args = io.StringIO()
    builtins.print(*args, **kwargs, file=buffer_args)

    # include thread info per line
    thread = threading.current_thread().name
    pid, process = 0, ''
    if not Instances.is_main_process:
        pid = os.getpid()
        process = str(os.getpid()) + '/'

    # send to GUI
    Instances.gui_out.event.emit(pid, thread, buffer_args.getvalue())

    for line in buffer_args.getvalue().splitlines():
        with PrintLock._:
            builtins.print('[', process, thread, '] ', line, sep='')

class Utils:
    def initialize(app_name):
        assert(threading.current_thread() is threading.main_thread())
        # threading.main_thread().name = NO this breaks checks for main thread in 3rd party libs
        random.seed(time.time())
        OScompat.initialize()

        k_data_dir = "data"
        data_path = get_data_path(app_name) + "/" + k_data_dir
        if not os.path.isdir(data_path):
            os.mkdir(data_path)
        os.chdir(data_path)

class OScompat:
    class ID(Enum):
        Undetected = 0
        Windows = 1
        WSL = 2
    id = ID.Undetected
    id_str = ''
    def initialize():
        if 'WSL_DISTRO_NAME' in os.environ:
            OScompat.id = OScompat.ID.WSL
        else:
            OScompat.id = OScompat.ID.Windows
        OScompat.id_str = str(OScompat.id).split('.')[1]
        # print('OS:', OScompat.id_str)

def get_windows_env_var(var_name):
    return subprocess.run(["cmd.exe", "/c", "echo", "%" + var_name + "%"], capture_output=True).stdout.strip().decode("utf-8")

def convert_path(path):
    if len(path) < 2:
        return path

    path = path.replace('\\', '/')

    match OScompat.id:
        case OScompat.ID.WSL:
            # 'C:' -> '/c'
            first_char, second_char = path[0], path[1]
            if first_char.isalpha() and second_char == ':':
                path = '/' + first_char.lower() + path[2:]

    return path

def get_firefox_dir():
    if OScompat.id in [ OScompat.ID.Windows, OScompat.ID.WSL ]:
        path = get_windows_env_var("APPDATA")
        path = convert_path(path)
        path = path + "/Mozilla/Firefox/Profiles/"
        return remove_trailing_slash(path)
    raise

def remove_trailing_slash(path):
    return path[:-1] if path.endswith("/") else path

# directory for read-write data: create if needed, return path
def get_data_path(app_name):
    local_app_data = get_windows_env_var("LOCALAPPDATA")

    local_app_data = convert_path(local_app_data)
    local_app_data = remove_trailing_slash(local_app_data)

    path = local_app_data + "/" + app_name

    if os.path.isdir(path):
        # os.path.iswritable fails on linux: 'posixpath' has no attribute 'iswritable'
        if not os.access(path, os.W_OK):
            print("DataPath", path, "exists but is not writable")
            path = ""
    else:
        os.mkdir(path)
    return path

class ProgressBar:
    # needs a tty
    # not compatible with multithreaded prints
    def __init__(self, count, prefix='', size=60):
        self.count = count
        self.prefix = prefix + ' '
        self.size = size
        self.start = time.time()
        self.tick(0)
    def tick(self, index):
        if self.count <= 0:
            return
        j = min(self.count, index + 1)
        x = int(self.size*j/self.count)
        current = time.time()
        if j <= 0:
            remaining = 0
        else:
            remaining = ((current - self.start) / j) * (self.count - j)
        mins, sec = divmod(remaining, 60)
        time_str = f"{int(mins):02}m:{int(sec):02}s"
        print(f"{self.prefix}[{u'#'*x}{('.'*(self.size-x))}] {index}/{self.count} ETA {time_str}", end='\r', flush=True)
        if j == self.count:
            print('')

def pickle_compress_suffix(compress):
    return ".gz" if compress else ""

def pickle_save(data, path, compress=True):
    suffix = pickle_compress_suffix(compress)
    path = path + suffix
    try:
        backup = "." + path + ".backup"
        shutil.copy(path, backup)
    except:
        pass
    pickle.dump(data, gzip.open(path, "wb") if compress else open(path, 'wb'))

def pickle_load(path):
    for compress in [ True, False ]:
        try:
            p = path + pickle_compress_suffix(compress)
            return pickle.load(gzip.open(p, 'rb') if compress else open(p, 'rb'))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)
            pass
    raise

def temp_file_path():
    # tempfile.[Named]TemporaryFile() fails to be compatible with wsl and mingw
    return tempfile.gettempdir() + "/" + ''.join(random.choices(string.ascii_uppercase, k=8))

class sqlite_copy_db():
    def __init__(self, path):
        self.tmppath = temp_file_path()
        # print(path, '->', self.tmppath)
        shutil.copy(path, self.tmppath)
        self.con = sqlite3.connect(self.tmppath)
    def __del__(self):
        # print('deleting temporary copy', self.tmppath)
        self.con.close()
        os.remove(self.tmppath)

def describe_function():
    caller = inspect.currentframe().f_back
    if caller is None:
        return
    builtins.print('function:', caller.f_code.co_name, 'line:', caller.f_lineno)
    args = inspect.getargvalues(caller).locals
    for i in args:
        builtins.print(' [local]', i, '=', args[i])

def clamp(value, min, max):
    return sorted(min, value, max)[1]

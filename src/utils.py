import subprocess
import sys
import os
import time
import random
import pickle
import gzip
import shutil

class Utils:
    def initialize(app_name):
        random.seed(time.time())

        k_data_dir = "data"
        data_path = get_data_path(app_name) + "/" + k_data_dir
        if not os.path.isdir(data_path):
            os.mkdir(data_path)
        os.chdir(data_path)

def get_windows_env_var(var_name):
    return subprocess.run(["cmd.exe", "/c", "echo", "%" + var_name + "%"], capture_output=True).stdout.strip().decode("utf-8")

def convert_path_to_wsl(path):
    if len(path) < 2:
        return path

    path = path.replace('\\', '/')

    # 'C:' -> '/c'
    first_char, second_char = path[0], path[1]
    if first_char.isalpha() and second_char == ':':
        path = '/' + first_char.lower() + path[2:]

    return path

def remove_trailing_slash(path):
    return path[:-1] if path.endswith("/") else path

# directory for read-write data: create if needed, return path
def get_data_path(app_name):
    local_app_data = get_windows_env_var("LOCALAPPDATA")

    local_app_data = convert_path_to_wsl(local_app_data)
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
    def __init__(self, count, prefix='', size=60, out=sys.stdout):
        self.count = count
        self.prefix = prefix + ' '
        self.size = size
        self.out = out
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
        print(f"{self.prefix}[{u'#'*x}{('.'*(self.size-x))}] {index}/{self.count} ETA {time_str}", end='\r', file=self.out, flush=True)
        if j == self.count:
            print('')

def pickle_compress_suffix(compress):
    return ".gz" if compress else ""

def pickle_save(data, path, compress=True):
    suffix = pickle_compress_suffix(compress)
    backup = path + ".backup" + suffix
    path = path + suffix
    try:
        # TODO hide backup
        shutil.copy(path, backup)
    except:
        pass
    pickle.dump(data, gzip.open(path, "wb") if compress else open(path, 'wb'))

def pickle_load(path):
    for compress in [ True, False ]:
        try:
            p = path + pickle_compress_suffix(compress)
            return pickle.load(gzip.open(p, 'rb') if compress else open(p, 'rb'))
        except:
            pass
    raise

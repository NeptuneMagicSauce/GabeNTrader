#!/usr/bin/env python3

import subprocess
import sys
import os
import time
import random

k_data_dir = "data"

def init(app_name):
    random.seed(time.time())

    data_path = GetDataPath(app_name) + "/" + k_data_dir
    if not os.path.isdir(data_path):
        os.mkdir(data_path)
    os.chdir(data_path)

def GetWindowsEnvVar(var_name):
    return subprocess.run(["cmd.exe", "/c", "echo", "%" + var_name + "%"], capture_output=True).stdout.strip().decode("utf-8")

def ConvertPathToWSL(path):
    if len(path) < 2:
        return path

    path = path.replace('\\', '/')

    # 'C:' -> '/c'
    first_char, second_char = path[0], path[1]
    if first_char.isalpha() and second_char == ':':
        path = '/' + first_char.lower() + path[2:]

    return path

def RemoveTrailingSlash(path):
    return path[:-1] if path.endswith("/") else path

# directory for read-write data: create if needed, return path
def GetDataPath(app_name):
    local_app_data = GetWindowsEnvVar("LOCALAPPDATA")

    local_app_data = ConvertPathToWSL(local_app_data)
    local_app_data = RemoveTrailingSlash(local_app_data)

    path = local_app_data + "/" + app_name

    if os.path.isdir(path):
        # os.path.iswritable fails on linux: 'posixpath' has no attribute 'iswritable'
        if not os.access(path, os.W_OK):
            print("DataPath", path, "exists but is not writable", file=sys.stderr)
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

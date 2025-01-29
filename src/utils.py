#!/usr/bin/env python3

import subprocess
import sys
import os

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

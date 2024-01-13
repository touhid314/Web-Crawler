import requests, pyperclip, sys
from requests.exceptions import ConnectionError
from selenium import webdriver
from time import sleep, perf_counter
import general

import shlex
import winreg

def get_default_windows_app(suffix):
    class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, suffix)
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
        command = winreg.QueryValueEx(key, '')[0]
        return shlex.split(command)[0]

print(get_default_windows_app('.mp3'))
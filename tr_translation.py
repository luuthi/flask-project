#!flask/bin/python
import os
import sys
if sys.platform == 'win32':
    pybabel = 'c:\Python27\Scripts\pybabel.exe'
else:
    pybabel = 'pybabel'
os.system(pybabel + ' compile -d app/translations')
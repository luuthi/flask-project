#!flask/bin/python
import os
import sys
if sys.platform == 'win32':
    pybabel = 'c:\Python27\Scripts\pybabel.exe'
else:
    pybabel = 'pybabel'
os.system(pybabel)
os.system(pybabel + ' extract -F babel.cfg -k lazy_gettext -o messages.po app')
os.system(pybabel + ' update -i messages.po -d app/translations')
os.unlink('messages.po')
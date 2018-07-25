#!flask/bin/python
import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'pybabel'
if len(sys.argv) != 2:
    print "usage: tr_init <language-code>"
    sys.exit(1)
os.system(pybabel +
          ' extract -F babel.cfg -k lazy_gettext -o messages.po app')
os.system(pybabel +
          ' init -i messages.po -d app/translations -l ' + sys.argv[1])
os.unlink('messages.po')
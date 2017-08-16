activate_this = '/var/www/dietwatr.com/default/websites/files/virtenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys

sys.path.insert(0, '/var/www/dietwatr.com/default/websites/files')

from dwcfiles import app as application

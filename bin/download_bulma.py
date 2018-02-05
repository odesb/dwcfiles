#!/usr/bin/env python
import os
import re
import urllib.request

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
BULMA_LOCATION = os.path.join(CURRENT_DIR, '..', 'dwcfiles', 'static', 'css', 'bulma.css')

def download_bulma():
    """Download the latest Bulma CSS framework from GitHub"""
    resp = urllib.request.urlopen('https://raw.githubusercontent.com/jgthms/bulma/master/css/bulma.css')
    css = resp.read().decode('utf-8')
    # Get Bulma version from file
    pattern = r'bulma.io\sv(?P<version>[\d\.]*)\s'
    prog = re.compile(pattern)
    # Get new version
    res = prog.search(css)
    new_version = res.group('version')
    # Get old version
    try:
        with open(BULMA_LOCATION) as f:
            res = prog.search(f.read())
            old_version = res.group('version')
    except FileNotFoundError:
        # No Bulma version on disk
        install_bulma(css)
        print(f'Installed new Bulma version: {new_version}')
        return
    if old_version != new_version:
        while True:
            overwrite = input(f'New Bulma version available ({new_version})! Overwrite existing file ({old_version})? [y/n] ')
            if overwrite.lower() == 'y':
                install_bulma(css)
                print(f'Installed new Bulma version: {old_version} -> {new_version}')
                return
            elif overwrite.lower() == 'n':
                print('Aborted!')
                return
    else:
        print(f'Bulma latest version already installed: {new_version}')

def install_bulma(css):
    with open(BULMA_LOCATION, 'w') as g:
        g.write(css)

if __name__ == '__main__':
    download_bulma()

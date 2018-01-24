import os
import urllib.request
from distutils.command.install import install
from setuptools import setup

class DownloadCss(install):
    def run(self):
        resp = urllib.request.urlopen('https://raw.githubusercontent.com/jgthms/bulma/master/css/bulma.css')
        css = resp.read()
        with open(os.path.join('dwcfiles', 'static', 'css', 'bulma.css'), 'w+b') as f:
            f.write(css)
        super().run()

setup(
        name='dwcfiles',
        packages=['dwcfiles'],
        version='0.1.0',
        include_package_data=True,
        install_requires=[
            'flask',
            'flask-pymongo',
            'flask-wtf',
            'gunicorn',
            'hamlish-jinja',
            'pillow',
            'python-magic',
            ],
        cmdclass={
            'install': DownloadCss,
            },
        )

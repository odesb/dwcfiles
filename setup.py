from setuptools import setup

setup(
        name='dwcfiles',
        packages=['dwcfiles'],
        include_package_data=True,
        install_requires=[
            'flask',
            'flask-pymongo',
            'flask-wtf',
            'hamlish-jinja',
            'pillow',
            'python-magic',
            ],
        )

from setuptools import setup

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
        )

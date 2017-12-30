# Requirements
- Python 3.x (tested with Python 3.6)
- Flask (tested with Flask 0.12.2)
- MongoDB
- Hamlish-jinja
- Flask-PyMongo
- Flask-WTF
- Python-magic
- FFmpeg (tested with FFmpeg 3.3.2)
- Pillow

# Installing the website

Create the `instance` directory where the config files are stored:
```bash
mkdir instance
```

Generate a secret key for sessions and add it to a new `instance/secret_key` file:
```bash
python -c "import os;print(os.urandom(24))" > instance/secret_key
```

**Optionally:** If MongoDB is not running on localhost/127.0.0.1, create a new `instance/settings.cfg` file and add `MONGO_HOST`:
```bash
echo "MONGO_HOST = '<remote_computer>'" > instance/settings.cfg
```

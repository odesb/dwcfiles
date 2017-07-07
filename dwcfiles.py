import os
import io
import uuid
import base64
import re
import shutil
from flask import Flask, render_template, redirect, send_from_directory
from hamlish_jinja import HamlishExtension
from flask_pymongo import PyMongo, ASCENDING, DESCENDING
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

# User uploaded files location
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Secret key (used for CSRF protection and sessions)
# To generate, execute this in a python shell:
# import os
# os.urandom(24)
app.secret_key = 'dev'

# Hamlish-jinja setup
app.jinja_env.add_extension(HamlishExtension)
app.jinja_env.hamlish_enable_div_shortcut = True

# Connect to the MongoDB database
mongo = PyMongo(app)


class FileUploadForm(FlaskForm):
    title = StringField('Title')
    filename_title = BooleanField('')
    actualfile = FileField(validators=[FileRequired()])


def create_url_id():
    """Create a URL safe unique ID
    """
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').replace('=', '')


def filesize(stream):
    """Retrieve size in bytes on a open stream
    """
    stream.seek(0, io.SEEK_END)
    filesize = stream.tell()
    stream.seek(0, io.SEEK_SET)
    return filesize
    

def human_readable(num_bytes):
    """Convert a number of bytes to a human readable format
    """
    suffixes = ['B', 'KB', 'MB', 'GB']
    suffixIndex = 0
    while num_bytes > 1024 and suffixIndex < 3:
        suffixIndex += 1
        num_bytes = num_bytes/1024
    return f'{num_bytes:.2f} {suffixes[suffixIndex]}'


@app.route('/', methods=['GET', 'POST'])
def home():
    form = FileUploadForm()
    if form.validate_on_submit():
        # validate_on_submit verifies if it is a POST request and if valid
        f = form.actualfile.data
        # Create unique id and filename based on existing extension
        unique_id = create_url_id()
        ext = os.path.splitext(secure_filename(f.filename))[1]
        filename = unique_id + ext
        # Save to database
        mongo.db.userfiles.insert_one({
            'unique_id': unique_id, 
            'filename': filename,
            'title': form.title.data, 
            'mime_type': f.mimetype,
            'filesize': human_readable(filesize(f)),
            })
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/')
    fs_info = shutil.disk_usage(app.config['UPLOAD_FOLDER'])
    context = {
            'form': form,
            'last_multimedia': mongo.db.userfiles.find({'mime_type': re.compile('^(image|video|audio)')}).sort('_id', DESCENDING),
            'last_files': mongo.db.userfiles.find({'mime_type': re.compile('^(?!image|video|audio)')}).sort('_id', DESCENDING),
            'used_space': human_readable(fs_info[1]),
            'total_space': human_readable(fs_info[0]),
            'percent_space': fs_info[1]/fs_info[0]*100,
            }
    return render_template('home.haml', **context)


@app.route('/<userfile_id>')
def get_userfile(userfile_id):
    userfile = mongo.db.userfiles.find_one_or_404({'unique_id': userfile_id})
    return render_template('userfile.haml', userfile=userfile)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

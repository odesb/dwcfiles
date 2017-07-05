import os
import io
import uuid
import base64
import re
from datetime import datetime
from flask import Flask, render_template, redirect, send_from_directory
from hamlish_jinja import HamlishExtension
from flask_pymongo import PyMongo, ASCENDING, DESCENDING
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField
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
    title = StringField('Title', validators=[DataRequired()])
    actualfile = FileField(validators=[FileRequired()])


def create_url_id():
    """Create a URL safe unique ID
    """
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').replace('=', '')

def retrieve_filesize(stream):
    """Retrieve file size in bytes on a open stream and outputs it in human
    readable format
    """
    stream.seek(0, io.SEEK_END)
    filesize = stream.tell()
    stream.seek(0, io.SEEK_SET)
    suffixes = ['B', 'KB', 'MB', 'GB']
    suffixIndex = 0
    while filesize > 1024 and suffixIndex < 3:
        suffixIndex += 1
        filesize = filesize/1024
    return f'{filesize:.2f} {suffixes[suffixIndex]}'

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
            '_id': unique_id, 
            'filename': filename,
            'title': form.title.data, 
            'mime_type': f.mimetype,
            'filesize': retrieve_filesize(f),
            'pub_date': datetime.now(),
            })
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/')
    context = {
            'form': form,
            'last_multimedia': mongo.db.userfiles.find({'mime_type': re.compile('^(image|video|audio)')}).sort('pub_date', DESCENDING),
            'last_files': mongo.db.userfiles.find({'mime_type': re.compile('^(?!image|video|audio)')}).sort('pub_date', DESCENDING),
            }
    return render_template('home.haml', **context)


@app.route('/<userfile_id>')
def get_userfile(userfile_id):
    userfile = mongo.db.userfiles.find_one_or_404({'_id': userfile_id})
    return render_template('userfile.haml', userfile=userfile)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

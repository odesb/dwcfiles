import os
import uuid
import base64
import re
import shutil
import io
import subprocess as sp
from magic import from_buffer
from PIL import Image
from flask import Flask, render_template, redirect, send_from_directory, url_for, flash, request
from hamlish_jinja import HamlishExtension
from flask_pymongo import PyMongo, ASCENDING, DESCENDING
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, ValidationError

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


@app.context_processor
def meme_saying():
    meme_sayings = [
            'Keeping your memes safe since 2017',
            'No ads, yet',
            'With the power of the Cloud&trade;',
            'Do it for the children',
            '😂💯👌m👌MMMMᎷМ💯💯😂💯👌ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ😂💯💯👌'
            ]
    return dict(meme_sayings=meme_sayings)


class FileUploadForm(FlaskForm):
    title = StringField('Title')
    filename_title = BooleanField('Use filename as title')
    actualfile = FileField(validators=[FileRequired()])


def create_url_id():
    """Create a URL safe unique ID
    """
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').replace('=', '')


def filesize(stream):
    """Retrieve size in bytes on a open stream
    """
    stream.seek(0, 2)   # Change stream position to the end
    filesize = stream.tell()
    stream.seek(0, 0)   # Change stream position to the beginning
    return filesize


def human_readable(num_bytes):
    """Convert a number of bytes to a human readable format
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while num_bytes > 1024 and suffixIndex < 4:
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
        # Define the file title
        title = form.title.data if form.title.data != '' else f.filename
        # Find the mime type and if it is a video, generate a thumbnail
        mime_type = from_buffer(f.read(), mime=True)
        f.seek(0, 0)
        if 'video' in mime_type:
            ss_filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_id + '.png')
            completed = sp.run(['ffmpeg', '-i', '-', '-ss', '00:00:01', '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], input=f.read(), stdout=sp.PIPE)
            # Generate the thumbnail
            size = 226, 160
            im = Image.open(io.BytesIO(completed.stdout))
            im.thumbnail(size)
            im.save(ss_filename)
        # Save to database and filesystem
        mongo.db.userfiles.insert_one({
            'unique_id': unique_id,
            'filename': filename,
            'title': title,
            'mime_type': mime_type,
            'filesize': human_readable(filesize(f)),
            })
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Send successful message and redirect
        flash('File successfully uploaded!')
        return redirect(url_for('get_userfile', userfile_id=unique_id))
    fs_info = shutil.disk_usage(app.config['UPLOAD_FOLDER'])
    context = {
            'form': form,
            'last_multimedia': mongo.db.userfiles.find({'mime_type': re.compile('^(image|video|audio)')}, limit=5, sort=[('_id', DESCENDING)]),
            'last_files': mongo.db.userfiles.find({'mime_type': re.compile('^(?!image|video|audio)')}, limit=5, sort=[('_id', DESCENDING)]),
            'used_space': human_readable(fs_info[1]),
            'total_space': human_readable(fs_info[0]),
            'percent_space': fs_info[1]/fs_info[0]*100,
            }
    return render_template('home.haml', **context)


@app.route('/_ajax_multimedia')
def load_multimedia():
    n = int(request.args.get('next'))
    context = {
            'more_media': mongo.db.userfiles.find({'mime_type': re.compile('^(image|video|audio)')}, skip=5*n, limit=5, sort=[('_id', DESCENDING)])
            }
    return render_template('more.haml', **context)

@app.route('/_ajax_other')
def load_other():
    n = int(request.args.get('next'))
    context = {
            'more_other': mongo.db.userfiles.find({'mime_type': re.compile('^(?!image|video|audio)')}, skip=5*n, limit=5, sort=[('_id', DESCENDING)])
            }
    return render_template('more.haml', **context)

@app.route('/<userfile_id>')
def get_userfile(userfile_id):
    userfile = mongo.db.userfiles.find_one_or_404({'unique_id': userfile_id})
    return render_template('userfile.haml', userfile=userfile)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

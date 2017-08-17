import os
import string
import secrets
import shutil
import io
import subprocess as sp
from magic import from_buffer
from PIL import Image
from flask import Flask, render_template, redirect, url_for, flash, request
from hamlish_jinja import HamlishExtension
from flask_pymongo import PyMongo, DESCENDING
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired


HTML5_FORMATS = [
        'audio/mp4',
        'audio/mpeg',
        'audio/webm',
        'audio/ogg',
        'audio/wav',
        'audio/x-wav',
        'audio/x-pn-wav',
        'audio/flac',
        'audio/x-flac',
        'image/jpeg',
        'image/gif',
        'image/png',
        'image/svg',
        'image/bmp',
        'video/webm',
        'video/ogg',
        'video/mp4'
        ]


UNCOMMON_EXTENSIONS = [
        '.tar'
        ]


MEME_SAYINGS = [
            'Keeping your memes safe since 2017',
            'No ads, yet',
            'With the power of the Cloud&trade;',
            'Do it for the children',
            '😂💯👌m👌MMMMᎷМ💯💯😂💯👌ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ😂💯💯👌'
            ]


app = Flask(__name__)

# Secret key (used for CSRF protection and sessions)
# To generate, execute this in a python shell:
# import os
# os.urandom(24)
# And save it in 'secret_key' file
app.secret_key = open(os.path.join(app.instance_path, 'secret_key'), 'rb').read()

# Hamlish-jinja setup
app.jinja_env.add_extension(HamlishExtension)
app.jinja_env.hamlish_enable_div_shortcut = True

# Connect to the MongoDB database
mongo = PyMongo(app)


@app.context_processor
def meme_saying():
    return dict(meme_sayings=MEME_SAYINGS)


class FileUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    actualfile = FileField(validators=[FileRequired()])


def create_url_id():
    """Create a "unique" id of length = 4
    """
    return ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(4))


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
    while num_bytes > 1024 and suffixIndex < 5:
        suffixIndex += 1
        num_bytes = num_bytes/1024
    final_suffix = suffixes[suffixIndex]
    return f'{num_bytes:.2f} {suffixes[suffixIndex]}'


def retrieve_extension(filename):
    for ext in UNCOMMON_EXTENSIONS:
        if ext in filename:
            index = filename.find(ext)
            return filename[index:]
    return os.path.splitext(filename)[1]

def generate_thumbnail(f, unique_id, video=False):
    thumb_filename = unique_id + '_thumb.png'
    if video:
        completed = sp.run(['ffmpeg', '-i', '-', '-ss', '00:00:01', '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], input=f.read(), stdout=sp.PIPE)
        f = completed.stdout
    elif not video:
        f = f.read()
    # Generate the thumbnail
    size = 226, 160
    im = Image.open(io.BytesIO(f))
    im.thumbnail(size)
    raw_im = io.BytesIO()
    im.save(raw_im, 'png')
    raw_im.seek(0, 0)
    mongo.save_file(thumb_filename, raw_im)


@app.route('/', methods=['GET', 'POST'])
def home():
    form = FileUploadForm()
    if form.validate_on_submit():
        # validate_on_submit verifies if it is a POST request and if form is valid
        f = form.actualfile.data
        # Create unique id and filename based on existing extension
        unique_id = create_url_id()
        ext = retrieve_extension(secure_filename(f.filename))
        filename = unique_id + ext
        # Define the file title
        title = form.title.data
        # Find the mime type and if it is a video, generate a thumbnail
        mime_type = from_buffer(f.read(), mime=True)
        f.seek(0, 0)
        html5 = False
        if mime_type in HTML5_FORMATS:
            html5 = True
            if 'image' in mime_type:
                generate_thumbnail(f, unique_id)
            elif 'video' in mime_type:
                generate_thumbnail(f, unique_id, video=True)
        # Save to database and filesystem
        mongo.db.userfiles.insert_one({
            'unique_id': unique_id,
            'filename': filename,
            'title': title,
            'mime_type': mime_type,
            'filesize': human_readable(filesize(f)),
            'html5': html5,
            'pinned': False,
            })
        mongo.save_file(filename, f)
        # Send successful message and redirect
        flash('File successfully uploaded!')
        return redirect(url_for('get_userfile', userfile_id=unique_id))
    fs_info = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__)))
    context = {
            'form': form,
            'last_multimedia': mongo.db.userfiles.find({'html5': True}, limit=5, sort=[('_id', DESCENDING)]),
            'last_files': mongo.db.userfiles.find({'html5': False}, limit=5, sort=[('_id', DESCENDING)]),
            'used_space': human_readable(fs_info[1]),
            'total_space': human_readable(fs_info[0]),
            'percent_space': fs_info[1]/fs_info[0]*100,
            }
    return render_template('home.haml', **context)


@app.route('/_ajax_more')
def load_more():
    n = int(request.args.get('next'))
    html5 = bool(request.args.get('html5'))
    context = {
            'more': mongo.db.userfiles.find({'html5': html5}, skip=5*n, limit=5, sort=[('_id', DESCENDING)])
            }
    return render_template('more.haml', **context)

#For paging in the gallery
@app.route('/next_page')
def next_page():
    return


@app.route('/<userfile_id>')
def get_userfile(userfile_id):
    userfile = mongo.db.userfiles.find_one_or_404({'unique_id': userfile_id})
    return render_template('userfile.haml', userfile=userfile)


@app.route('/u/<filename>')
def uploaded_file(filename):
    return mongo.send_file(filename)

@app.route('/gallery')
def gallery():

    context={
        'images': mongo.db.userfiles.find({'mime_type': {'$regex': '.*image.*'}}, limit=10, sort=[('_id', DESCENDING)])
    }

    return render_template('gallery.haml', **context)

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")

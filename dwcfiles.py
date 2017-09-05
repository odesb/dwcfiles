import base64
import os
import string
import secrets
import shutil
import io
import subprocess as sp
from functools import wraps
from magic import from_buffer
from PIL import Image
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from hamlish_jinja import HamlishExtension
from flask_pymongo import PyMongo, DESCENDING
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired, Length


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


def human_readable(func):
    """Convert a number of bytes to a human readable format
    """
    @wraps(func)
    def wrapper(self):
        num_bytes = func(self)
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffixIndex = 0
        while num_bytes > 1024 and suffixIndex < 5:
            suffixIndex += 1
            num_bytes = num_bytes/1024
        final_suffix = suffixes[suffixIndex]
        return f'{num_bytes:.2f} {suffixes[suffixIndex]}'
    return wrapper


def retrieve_extension(filename):
    for ext in UNCOMMON_EXTENSIONS:
        if ext in filename:
            index = filename.find(ext)
            return filename[index:]
    return os.path.splitext(filename)[1]


class FileUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    actualfile = FileField(validators=[FileRequired()])


class UserFile:
    def __init__(self, *args, **kwargs):
        self.title = kwargs['title']
        self.actualfile = kwargs['actualfile']
        self.unique_id = ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(4))
        try:
            self.filename = self.unique_id + retrieve_extension(secure_filename(self.actualfile.filename))
        except AttributeError:
            self.filename = self.unique_id + retrieve_extension(secure_filename(kwargs['filename']))
        self.mime_type = self.get_mime_type()
        self.filesize = self.get_filesize()
        self.html5 = False
        self.pinned = False

    def __iter__(self):
        for key in vars(self):
            if key != 'actualfile':
                yield (key, getattr(self, key))

    def get_mime_type(self):
        """Retrieve mime type of the actual file
        """
        m = from_buffer(self.actualfile.read(), mime=True)
        self.actualfile.seek(0, 0)
        return m

    @human_readable
    def get_filesize(self):
        """Retrieve file size of the actual file
        """
        self.actualfile.seek(0, 2)   # Change stream position to the end
        filesize = self.actualfile.tell()
        self.actualfile.seek(0, 0)   # Change stream position to the beginning
        return filesize

    def save_thumbnail(self, video=False):
        thumb_filename = self.unique_id + '_thumb.png'
        if video:
            completed = sp.run(['ffmpeg', '-i', '-', '-ss', '00:00:01', '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], input=f.read(), stdout=sp.PIPE)
            f = completed.stdout
        elif not video:
            f = self.actualfile.read()
            self.actualfile.seek(0, 0)
        im = Image.open(io.BytesIO(f))
        im.thumbnail((226, 160))
        thumb = io.BytesIO()
        im.save(thumb, 'png')
        thumb.seek(0, 0)
        mongo.save_file(thumb_filename, thumb)

    def save_to_db(self):
        # Generate and save thumbnail if file is html5 video or image
        if self.mime_type in HTML5_FORMATS:
            self.html5 = True
            if 'image' in self.mime_type:
                self.save_thumbnail()
            elif 'video' in self.mime_type:
                self.save_thumbnail(video=True)
        # Insert metadata in userfiles database
        mongo.db.userfiles.insert_one(dict(self))
        # Save actual file to GridFS
        mongo.save_file(self.filename, self.actualfile)

@human_readable
def space(fs_info):
    return fs_info

@app.route('/', methods=['GET', 'POST'])
def home():
    form = FileUploadForm()
    if form.validate_on_submit():
        # validate_on_submit verifies if it is a POST request and if form is valid
        userfile = UserFile(title=form.title.data, actualfile=form.actualfile.data)
        userfile.save_to_db()
        flash('File successfully uploaded!')
        return redirect(url_for('get_userfile', userfile_id=userfile.unique_id))
    else:
        fs_info = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__)))
        context = {
                'form': form,
                'last_multimedia': mongo.db.userfiles.find({'html5': True}, limit=5, sort=[('_id', DESCENDING)]),
                'last_files': mongo.db.userfiles.find({'html5': False}, limit=5, sort=[('_id', DESCENDING)]),
                'used_space': space(fs_info[1]),
                'total_space': space(fs_info[0]),
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


@app.route('/ul/<filename>')
def uploaded_file(filename):
    return mongo.send_file(filename)


@app.route('/gallery')
def gallery():
    context = {
        'images': mongo.db.userfiles.find({'mime_type': {'$regex': '.*image.*'}}, limit=10, sort=[('_id', DESCENDING)])
    }
    return render_template('gallery.haml', **context)


@app.route('/api/files', methods=['GET', 'POST'])
def api():
    if not request.is_json:
        abort(400)
    elif request.method == 'GET':
        documents = mongo.db.userfiles.find({})
        response = {}
        for x, doc in enumerate(documents):
            del doc['_id']
            response[x] = doc
        return jsonify(response)
    elif request.method == 'POST':

        json = request.get_json()
        d = {
                'title': json['title'],
                'filename': json['filename'],
                'actualfile': io.BytesIO(base64.b64decode(json['file'].encode())),
                }
        userfile = UserFile(**d)
        userfile.save_to_db()
        response = {
                'url': 'http://files.dietwatr.com{}'.format(url_for('get_userfile', userfile_id=userfile.unique_id)),
                'direct_url': 'http://files.dietwatr.com{}'.format(url_for('uploaded_file', filename=userfile.filename)),
                }
        return jsonify(response), 201


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")


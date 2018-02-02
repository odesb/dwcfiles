import base64
import os
import shutil
import io
from dwcfiles import app
from dwcfiles.models import UserFile
from dwcfiles.utils import human_readable
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from hamlish_jinja import HamlishExtension
from flask_pymongo import PyMongo, DESCENDING
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length


MEME_SAYINGS = [
            'Keeping your memes safe since 2017',
            'No ads, yet',
            'With the power of the Cloud&trade;',
            'Do it for the children',
            '😂💯👌m👌MMMMᎷМ💯💯😂💯👌ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ😂💯💯👌'
            ]

class DefaultSettings:
    MONGO_HOST = 'localhost'
    DB_LOCATION = os.path.dirname(os.path.abspath(__file__))


app.config.from_object('dwcfiles.views.DefaultSettings')       # Development settings
app.config.from_envvar('DWCFILES_SETTINGS', silent=True) # Production settings

# Hamlish-jinja setup
app.jinja_env.add_extension(HamlishExtension)
app.jinja_env.hamlish_enable_div_shortcut = True

# Secret key (used for CSRF protection and sessions)
# To generate, execute this in a Python 3.6+ shell:
# import secrets
# secrets.token_bytes(24)
# And save it in 'secret_key' file in instance folder
with app.open_instance_resource('secret_key') as f:
    app.secret_key = f.read()

# Connect to the MongoDB database
mongo = PyMongo(app)


@app.context_processor
def meme_saying():
    return dict(meme_sayings=MEME_SAYINGS)


class FileUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    actualfile = FileField(validators=[FileRequired()])
    frontpage = BooleanField('Show on the front page?', default='checked')


@human_readable
def space(fs_info):
    return fs_info

@app.route('/', methods=['GET', 'POST'])
def home():
    form = FileUploadForm()
    if form.validate_on_submit():
        # validate_on_submit verifies if it is a POST request and if form is valid
        userfile = UserFile(title=form.title.data,
                            actualfile=form.actualfile.data,
                            frontpage=form.frontpage.data,
                            )
        userfile.save_to_db(mongo)
        flash('File successfully uploaded!', 'success')
        if not userfile.frontpage:
            flash("Write down the url because this file won't show up on the front page.", 'warning')
        return redirect(url_for('get_userfile', userfile_id=userfile.unique_id))
    else:
        fs_info = shutil.disk_usage(app.config['DB_LOCATION'])
        context = {
                'form': form,
                'last_multimedia': mongo.db.userfiles.find({'frontpage': True}, limit=15, sort=[('_id', DESCENDING)]),
                'last_files': mongo.db.userfiles.find({'html5': False, 'frontpage': True}, limit=5, sort=[('_id', DESCENDING)]),
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
            'more': list(mongo.db.userfiles.find({'html5': html5, 'frontpage': True}, skip=15-3+n, limit=3, sort=[('_id', DESCENDING)]))
            }
    return render_template('more.haml', **context)


#For paging in the gallery
@app.route('/next_page')
def next_page():
    return


@app.route('/<userfile_id>')
def get_userfile(userfile_id):
    context = {
        'form': FileUploadForm(),
        'userfile': mongo.db.userfiles.find_one_or_404({'unique_id': userfile_id})
        }
    return render_template('userfile.haml', **context)


@app.route('/ul/<filename>')
def uploaded_file(filename):
    return mongo.send_file(filename)


@app.route('/gallery')
def gallery():
    context = {
        'images': mongo.db.userfiles.find({'mime_type': {'$regex': '.*image.*'}}, limit=10, sort=[('_id', DESCENDING)])
    }
    return render_template('gallery.haml', **context)

### API ###

@app.route('/api')
def api():
    form = FileUploadForm()
    return render_template('api.haml', form=form)


@app.route('/api/files', methods=['GET', 'POST'])
def api_collection():
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
                'actualfile': io.BytesIO(base64.b64decode(json['file'])),
                'frontpage': json['public'],
                }
        userfile = UserFile(**d)
        userfile.save_to_db(mongo)
        response = {
                'url': '{0}{1}'.format(request.host, url_for('get_userfile', userfile_id=userfile.unique_id)),
                'direct_url': '{0}{1}'.format(request.host, url_for('uploaded_file', filename=userfile.filename)),
                }
        return jsonify(response), 201

@app.route('/api/files/<unique_id>')
def api_file(unique_id):
    if not request.is_json:
        abort(400)
    userfile = mongo.db.userfiles.find_one({'unique_id': unique_id})
    del userfile['_id']
    return jsonify(userfile)


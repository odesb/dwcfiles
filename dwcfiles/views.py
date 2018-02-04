import base64
import binascii
import os
import shutil
import io
from dwcfiles import app, mongo
from dwcfiles.forms import FileUploadForm
from dwcfiles.models import UserFile
from dwcfiles.utils import human_readable
from flask import render_template, redirect, url_for, flash, request, abort, jsonify


MEME_SAYINGS = [
            'Keeping your memes safe since 2017',
            'No ads, yet',
            'With the power of the Cloud&trade;',
            'Do it for the children',
            '😂💯👌m👌MMMMᎷМ💯💯😂💯👌ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ😂💯💯👌'
            ]


@app.context_processor
def global_context():
    """Global context used in all views"""
    return dict(meme_sayings=MEME_SAYINGS, form=FileUploadForm())


@human_readable
def transform(num_bytes):
    """Transform number of bytes into human readable format"""
    return num_bytes


@app.route('/', methods=['GET', 'POST'])
def home():
    """Home page view"""
    form = FileUploadForm() # Need to access the global form
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
        fs_info = shutil.disk_usage(app.config['DB_LOCATION']) # Retrieve filesystem info
                                                               # For home page bar
        context = {
                'latest_files': mongo.db.userfiles.find({'frontpage': True}, limit=15, sort=[('_id', -1)]), # Descending by _id
                'used_space': transform(fs_info[1]),
                'total_space': transform(fs_info[0]),
                'percent_space': fs_info[1]/fs_info[0]*100,
                }
        return render_template('home.haml', **context)


@app.route('/_ajax_more')
def load_more():
    """View used to load more files on home page"""
    n = int(request.args.get('next'))
    context = {
            'more': list(mongo.db.userfiles.find({'frontpage': True}, skip=15-3+n, limit=3, sort=[('_id', -1)])) # Descending by _id
            }
    return render_template('more.haml', **context)


@app.route('/<userfile_id>')
def get_userfile(userfile_id):
    """Detailed page for a single user uploaded file"""
    context = {
        'userfile': mongo.db.userfiles.find_one_or_404({'unique_id': userfile_id})
        }
    return render_template('userfile.haml', **context)


@app.route('/ul/<filename>')
def uploaded_file(filename):
    """Direct link to the user uploaded file in GridFS"""
    return mongo.send_file(filename)


### API ###

@app.route('/api')
def api():
    """API documentation view"""
    return render_template('api.haml')


@app.route('/api/files', methods=['GET', 'POST'])
def api_collection():
    """API binding to interact with the public files collection"""
    if not request.is_json:
        abort(400)
    elif request.method == 'GET':
        # Get a response dict with each key (int) associated to a value (public file)
        documents = mongo.db.userfiles.find({'frontpage': True})
        response = {}
        for x, doc in enumerate(documents):
            del doc['_id']  # We don't want clients to access this
            response[x] = doc
        return jsonify(response)
    elif request.method == 'POST':
        # Create and save a new user uploaded file
        json = request.get_json()
        try:
            actualfile = io.BytesIO(base64.b64decode(json['file']))
        except binascii.Error:
            abort(400) # Should maybe send an error message
        d = {
                'title': json['title'],
                'filename': json['filename'],
                'actualfile': actualfile,
                'frontpage': json['public'],
                }
        userfile = UserFile(**d)
        userfile.save_to_db(mongo)
        response = {
                # request.host_url[:-1] is to remove the trailing '/' (e.g. '.com//ul/')
                'url': '{0}{1}'.format(request.host_url[:-1], url_for('get_userfile', userfile_id=userfile.unique_id)),
                'direct_url': '{0}{1}'.format(request.host_url[:-1], url_for('uploaded_file', filename=userfile.filename)),
                }
        return jsonify(response), 201


@app.route('/api/files/<unique_id>')
def api_file(unique_id):
    """API binding to interact with a single uploaded file"""
    if not request.is_json:
        abort(400)
    userfile = mongo.db.userfiles.find_one({'unique_id': unique_id})
    del userfile['_id'] # We don't want clients to access this
    return jsonify(userfile)


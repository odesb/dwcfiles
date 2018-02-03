from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length

class FileUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    actualfile = FileField(validators=[FileRequired()])
    frontpage = BooleanField('Show on the front page?', default='checked')


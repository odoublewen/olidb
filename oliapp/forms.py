from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, length

class ExperimentForm(Form):
    saveas = SelectField('Save As')
    name = StringField('Name', validators=[DataRequired(), length(max=64)])
    description = StringField('Description', validators=[DataRequired(), length(max=255)])
    is_public = BooleanField('Make Public', default=False)

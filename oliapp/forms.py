from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, length

class ExperimentForm(Form):
    saveas = SelectField('Save As')
    name = StringField('Name', validators=[DataRequired(), length(max=128)])
    description = StringField('Description', validators=[DataRequired(), length(max=256)])
    is_public = BooleanField('Make Public', default=False)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL

class Item(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    img = StringField("Img", validators=[URL()])
    url = StringField("Url", validators=[URL()])
    type = SelectField("Type", choices=[('filter-web', 'Web'), ('filter-app', 'App'), ('filter-bot', 'Bot')], validators=[DataRequired()] )  
    submit = SubmitField('Submit Item') 
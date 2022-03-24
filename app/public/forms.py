from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,TextAreaField, BooleanField,DateField,IntegerField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileRequired

class ParticipanteForm(FlaskForm):
    id = IntegerField('id')
    concurso_id = IntegerField('concurso')
    path_audio = FileField('Voz', validators=[FileRequired()], render_kw={'placeholder': 'Cargar Voz'})
    nombres = StringField('nombres', validators=[Length(max=128)])
    apellidos = StringField('apellidos', validators=[Length(max=128)])
    mail = EmailField('mail', validators=[DataRequired(), Email(), Length(max=128)])
    observaciones = TextAreaField('observaciones', validators=[Length(max=128)])
    convertido = StringField('convertido', validators=[Length(max=128)])
    submit = SubmitField('Enviar')

    def __init__(self,concurso):
        super().__init__()
        self.concurso_id=concurso

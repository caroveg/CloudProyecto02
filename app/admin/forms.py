from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,TextAreaField, BooleanField,DateField,IntegerField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileRequired

class ConcursoForm(FlaskForm):
    id = IntegerField('id')
    nombre = StringField('Nombre', validators=[Length(max=128)])
    imagen = FileField('Imagen o Banner', render_kw={'placeholder': 'Imagen o Banner'})
    url = StringField('Url', validators=[Length(max=128)])
    valor = StringField('Valor', validators=[Length(max=128)])
    fechaInicio = DateField('Fecha Inicio')
    fechaFin = DateField('Fecha Finalizacióm')
    guion = TextAreaField('Guion', validators=[Length(max=128)])
    recomendaciones = TextAreaField('recomendaciones', validators=[Length(max=128)])
    submit = SubmitField('Enviar')


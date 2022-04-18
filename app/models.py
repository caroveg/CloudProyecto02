from flask import url_for
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from app import db
from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError
import boto3  
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id='ASIATGWEY6Q5LVXJNPHS',
    aws_secret_access_key='dS+V8PEt5BShtfqjroI9//utf/cR3utbOwae93Lw',
	aws_session_token='IQoJb3JpZ2luX2VjECAaCXVzLWVhc3QtMSJHMEUCIQDUswKxqvvFIZi2pkiWx+13UYSyCrCYJSySib6hK1Av1wIgNCQHBhelv/dV9wXPcmklprJ9t+slNW9M4WoBrtbO1VoqgwQIyf//////////ARAAGgwyMjA1Mjk3NTEwOTgiDKxlR0WXSB2vPHpR9irXA7Q7EIoydA8Yio49iBC2YR91gaRUBQyV7c0873XmDuziPJKsyLUONKZuyqlVy2Te4MzFgdeOEp1l56qAK033jl58UYWXWeihNg40NpfV4v9rdCHHkIQQCsE+bZHQB7Q7WbDFliR+18Yn3dJ3ftu/dq6um04VW0RTGgRuh3xV67sh+G/nMrqnQuxUNVwNU8d2lsic1zM0kYkuRA8QUvgsQjSqJCK22SYuk0iG0fafOZ4mocVZr/2lV+QtILGxnYS6oE5Q6Pim+LNIR2HnFaXBLG2+bFXGLTh0pC+zZeRAoTYxZhLpCeOeUd+zOg7iPArjdu7Gqd3nOil9py6fA5zT53Z6fwFDYegFlIPw/ZAur+PdqQD9KIzo20ipvh05FpxhMzSfJ9OZsyi9USRoFnHirO58vj3GwHFKs0+YISiAnKh8E+PRWZ/b1EMyMfxsrWX7U4XCI3wwisv4gMI1UMHo6eNeSUzM1q9AfwJ3OaHYbCoFSEY5kPYJa6kImziTBdkXttcDO+VWxnCye4LzlBxi1Zp0oxgLWa2NJwtFtY9bacWYxha0IwWYLINRzeNKe4oRDDnx/rjCr9JnrHWL8dEtlaTcVSJLM//4nbMJCd+BHCSSYMUzTrH+hzCcyfKSBjqlASbIUz1SipBQsNO3c/5EM8KuCUz/r0TgkR/+7MUNuKkykYE6xZxA9mINf4r6WIhxlqW8DR3oZ5DjqZO82YhXSLDYeVIPD8OnJtXznHkQ4Vz4N1bS3nMMAXwmeKIteMWE6TH3EXV4X438Uwg3p2yLcnSQ4W9zz7HGHleLwe41aCQ5haj/xJHUPelAiI8JEGhPwNfPp5ZNGQ3ixzEhNKSSOjfanWsKxA==',
	region_name='us-east-1'
    )

class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nombre = db.Column( db.String(250) )
    imagen = db.Column( db.String(250) )
    url = db.Column( db.String(250) )
    fechaInicio = db.Column( db.DateTime )
    fechaFin = db.Column( db.DateTime )
    valor = db.Column( db.String(250) )
    guion = db.Column( db.String(250) )
    recomendaciones = db.Column( db.String(250) )
    fechaCreacion = db.Column( db.DateTime )
    def __repr__(self):
        return f'<Concurso {self.url}>'
    def save(self):
        if not self.id:
            db.session.add(self)
        if not self.url:
            self.url = slugify(self.url)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def public_url(self):
        return url_for('public.show_concurso', url=self.url)
    def concurso_delete(self):
        return url_for('admin.concurso_delete',concurso_id=self.id)
    def concurso_update(self):
         return url_for('admin.concurso_update',concurso_id=self.id)
    @staticmethod
    def get_by_id(concurso_id):
        return Concurso.query.filter_by(id=concurso_id).first()
    @staticmethod
    def get_by_url(url):
        return Concurso.query.filter_by(url=url).first()
    @staticmethod
    def get_all():
        concurso = []
        response = dynamodb.Table('concurso').scan()
        concurso = reponse.get('Items')
        return concurso
    def get_by_user(user_id):
        concurso = Concurso.query.filter_by(user_id=user_id).order_by(desc(Concurso.fechaCreacion)).all()
        return concurso


class ConcursoRDS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nombre = db.Column( db.String(250) )
    imagen = db.Column( db.String(250) )
    url = db.Column( db.String(250) )
    fechaInicio = db.Column( db.DateTime )
    fechaFin = db.Column( db.DateTime )
    valor = db.Column( db.String(250) )
    guion = db.Column( db.String(250) )
    recomendaciones = db.Column( db.String(250) )
    fechaCreacion = db.Column( db.DateTime )
    def __repr__(self):
        return f'<Concurso {self.url}>'
    def save(self):
        if not self.id:
            db.session.add(self)
        if not self.url:
            self.url = slugify(self.url)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def public_url(self):
        return url_for('public.show_concurso', url=self.url)
    def concurso_delete(self):
        return url_for('admin.concurso_delete',concurso_id=self.id)
    def concurso_update(self):
         return url_for('admin.concurso_update',concurso_id=self.id)
    @staticmethod
    def get_by_id(concurso_id):
        return Concurso.query.filter_by(id=concurso_id).first()
    @staticmethod
    def get_by_url(url):
        return Concurso.query.filter_by(url=url).first()
    @staticmethod
    def get_all():
        return Concurso.query.all()
    def get_by_user(user_id):
        concurso = Concurso.query.filter_by(user_id=user_id).order_by(desc(Concurso.fechaCreacion)).all()
        return concurso



class Participante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concurso_id = db.Column(db.Integer, db.ForeignKey('concurso.id', ondelete='CASCADE'), nullable=False)
    path_audio = db.Column( db.String(250), nullable=False )
    path_audio_origin = db.Column(db.String(250), nullable=False)
    nombres = db.Column( db.String(250), nullable=False )
    apellidos = db.Column( db.String(250) , nullable=False)
    mail = db.Column( db.String(250), nullable=False )
    observaciones = db.Column( db.String(250) )
    convertido = db.Column(db.Boolean())
    fechaCreacion = db.Column( db.DateTime )
    def __repr__(self):
        return f'<Participante {self.mail}>'
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def public_url(self):
        return url_for('public.show_participante',  participante_id=self.id)
    def participante_delete(self):
        return url_for('admin.participante_delete',participante_id=self.id)
    @staticmethod
    def get_by_id(participante_id):
        return Participante.query.filter_by(id=participante_id).first()
    @staticmethod
    def get_by_Concurso_id(concurso_id):
        return Participante.query.filter_by(concurso_id=concurso_id).order_by(Participante.fechaCreacion.desc()).slice(0, 20).all()
    @staticmethod
    def get_paths_Concurso_id(concurso_id):
        return Participante.query.filter_by(concurso_id=concurso_id).all()
    @staticmethod
    def get_all():
        return Participante.query.all()
    @staticmethod
    def get_no_procesados():
        return Participante.query.filter_by(convertido=False).all()
    def get_by_user(user_id):
        participante = participante.query.filter_by(user_id=user_id).order_by(desc(Participante.fechaCreacion)).all()
        return participante
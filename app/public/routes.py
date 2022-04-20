from flask import render_template, redirect, url_for, request, flash
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models import Concurso, Participante
from . import public_bp
from .forms import ParticipanteForm
import boto3  
import os
from .. import dynamodb
from boto3.dynamodb.conditions import Key

import math

tconcurso = dynamodb.Table('concurso')
tparticipante =  dynamodb.Table('participante')

@public_bp.route("/")
def index():
    return render_template("principal.html")

@public_bp.route("/concursos")
def principal():
    concursos = []
    if request.method == 'GET':
        response = tconcurso.scan()
        concursos = response.get('Items')
    return render_template("index.html", concursos=concursos)

@public_bp.route("/concursos/<string:url>/", defaults={"page": 1})
@public_bp.route("/concursos/<string:url>/<int:page>")
def show_concurso(page,url):
    response = tconcurso.get_item(
        Key={'url': url}
        )
    data = response.get('Item')

    concurso = Concurso(id= 0
                        ,nombre=data.get('nombre')
                        ,imagen=data.get('imagen')
                        ,url=data.get('url')
                        ,valor=data.get('valor')
                        ,fechaInicio= datetime.strptime(data.get('fechaInicio'),'%Y-%m-%d') 
                        ,fechaFin=datetime.strptime(data.get('fechaFin'),'%Y-%m-%d') 
                        ,guion=data.get('guion')
                        ,recomendaciones=data.get('recomendaciones'))

    
    #participantes = Participante.query.filter_by(concurso_id='{}'.format(concurso.id)).order_by(Participante.fechaCreacion.desc()).paginate(page=page, per_page=20).items
    number_pages = 1 #Participante.query.filter_by(concurso_id='{}'.format(concurso.id)).count()
    if number_pages<= 20:
        number_pages=1
    else:
        number_pages= int(math.ceil(number_pages/20)+1)
    return render_template("concurso_view.html", concurso=concurso,  pages=number_pages)
    #return render_template("concurso_view.html", concurso=concurso, voz=participantes, pages=number_pages)
   


@public_bp.route("/participantes/<int:participante_id>/")
def show_participante(participante_id):
    participante = Participante.get_by_id(participante_id)
    if participante is None:
        abort(404)
    return render_template("participante_view.html", participante=participante)

@public_bp.route("/public/participante/<string:url>", methods=['GET', 'POST'])
def participante_form(url):
    form = ParticipanteForm(url)
    if form.validate_on_submit():
       
        path_audio = secure_filename(form.path_audio.data.filename)
        form.path_audio.data.save("app/static/AudioFilesOrigin/" + path_audio)

        data = {}
        data['concurso_id'] = uuid.uuid4().hex
        data['url'] = form.url.data
        data['nombres'] = form.nombres.data
        data['path_audio'] = form.path_audio.data
        data['path_audio_origin'] = form.path_audio.data
        data['apellidos'] = form.url.data
        data['mail'] = form.mail.data
        data['observaciones'] = form.observaciones.data
        data['convertido'] = "False"
        data['fechaCreacion'] = datetime.now().isoformat()

        data = dict((k, v) for k, v in data.items() if v)

        response = tparticipante.put_item(Item=data)
        if response:
            flash('Participante creado correctamente')
       
        #Almacenamiento en S3
        s3 = boto3.resource('s3')     
        data = open("app/static/AudioFilesOrigin/" + path_audio, 'rb')
        s3.Bucket("storagedespd").put_object(Key="AudioFilesOrigin/" + path_audio, Body=data)
        os.remove("app/static/AudioFilesOrigin/" + path_audio)

        flash('Hemos recibido tu voz y la estamos procesando para que sea publicada en la \
                            página del concurso y pueda ser posteriormente revisada por nuestro equipo de trabajo. \
                            Tan pronto la voz quede publicada en la página, te notificaremos por email.')
        return  redirect(url_for('public.participante_form',url=url))
    return render_template("participante_form.html", form=form)

#ROUTE ADMIN
from flask import render_template, redirect, url_for, request,send_file, send_from_directory, flash
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.models import Concurso, Participante
from . import admin_bp
from .forms import ConcursoForm
from .. import dynamodb
import uuid

import boto3

tconcurso = dynamodb.Table('concurso')
tparticipante =  dynamodb.Table('participante')

@admin_bp.route("/admin/concurso/", methods=['GET', 'POST'], defaults={'concurso_id': None})
@admin_bp.route("/admin/concurso/<string:concurso_id>/", methods=['GET', 'POST','PUT'])
@login_required
def concurso_form(concurso_id): 
    form = ConcursoForm()  
    if form.validate_on_submit():

        path_imagen = secure_filename(form.imagen.data.filename)
        form.imagen.data.save("app/static/images_concurso/" + path_imagen)

        print(path_imagen)

        s3 = boto3.resource('s3')
        data = open("app/static/images_concurso/" + path_imagen, 'rb')
        s3.Bucket("storagedespd").put_object(Key="images_concurso/" + path_imagen, Body=data)
        os.remove("app/static/images_concurso/" + path_imagen)


        #Dynamo
        data = {}
        data['id'] = uuid.uuid4().hex
        data['user_id'] = current_user.id
        data['nombre'] = form.nombre.data
        data['imagen'] = path_imagen
        data['url'] = form.url.data
        data['valor'] = form.valor.data
        data['fechaInicio'] = form.fechaInicio.data.isoformat()
        data['fechaFin'] = form.fechaFin.data.isoformat()
        data['guion'] = form.guion.data
        data['recomendaciones'] = form.recomendaciones.data
        data['fechaCreacion'] = datetime.now().isoformat()

        data = dict((k, v) for k, v in data.items() if v)

        response = tconcurso.put_item(Item=data)

        return redirect(url_for('public.index'))
    return render_template("concurso_form.html", form=form)

@admin_bp.route("/concursoDelete/<string:url>/", methods=['GET', 'POST'])   
def  concurso_delete(url):
    responseg = tconcurso.get_item(
        Key={'url': url}
        )
    datag = responseg.get('Item')
    pathimg = datag.get('imagen')

    s3 = boto3.resource('s3')
    s3.Object('storagedespd', 'images_concurso/' + pathimg).delete()
    

    response = tconcurso.delete_item(
        Key={'url':url}
        )
    return redirect(url_for('public.index'))

@admin_bp.route("/concursoupdate/<string:url>/", methods=['GET', 'POST'])   
def concurso_update(url):
    response = tconcurso.get_item(
        Key={'url': url}
        )
    data = response.get('Item')

    form = ConcursoForm(nombre=data.get('nombre')
        ,imagen=data.get('imagen')
        ,url=data.get('url')
        ,fechaInicio = datetime.strptime(data.get('fechaInicio'),'%Y-%m-%d') 
        ,fechaFin = datetime.strptime(data.get('fechaFin'),'%Y-%m-%d') 
        ,valor=data.get('valor')
        ,guion=data.get('guion')
        ,recomendaciones=data.get('recomendaciones')
        )
   
     # Check request method and validate form
    if request.method == 'POST' and form.validate():
        data = {}
        #data['id'] = concurso_id
        data['nombre'] = form.nombre.data
        data['imagen'] = form.imagen.data
        data['url'] = form.url.data
        data['fechaInicio'] = form.fechaInicio.data.isoformat()
        data['fechaFin'] = form.fechaFin.data.isoformat()
        data['valor'] = form.valor.data
        data['guion'] = form.guion.data
        data['recomendaciones'] = form.recomendaciones.data
        #data['fechaCreacion'] = form.fechaCreacion.data.isoformat()
        
        data = dict((k, v) for k, v in data.items() if v)

        response = tconcurso.put_item(Item=data)

        if response:
            return redirect(url_for('public.index'))

    return render_template('concurso_form.html', form=form)

@admin_bp.route("/participanteDelete/<string:participante_id>/", methods=['GET', 'POST'])   
def  participante_delete(participante_id):
    responseg = tparticipante.get_item(
        Key={'Participante_id': participante_id}
        )
    datag = responseg.get('Item')
    path_audio = datag.get('path_audio')
    path_audio_origin = datag.get('path_audio_origin')

    s3 = boto3.resource('s3')
    s3.Object('storagedespd', 'AudioFilesOrigin/' + path_audio).delete()
    s3.Object('storagedespd', 'AudioFilesDestiny/' + path_audio_origin).delete()
    
    
    response = tparticipante.delete_item(
        Key={'Participante_id': participante_id}
        )
    #os.remove("app/static/AudioFilesDestiny/{}".format(data.get('path_audio')))
    #os.remove("app/static/AudioFilesOrigin/{}".format(data.get('path_audio_origin')))	
    return redirect(url_for('public.index'))


@admin_bp.route('/participante/uploads/<path:filename>', methods=['GET', 'POST'])
def download_participante(filename):
    path = "http://d25jsbtuwtqsio.cloudfront.net/AudioFilesDestiny/{}".format(filename)
    return send_file(path, as_attachment=True)

@admin_bp.route('/participante/uploads_origin/<path:filename>', methods=['GET', 'POST'])
def participante_origin_download(filename):
    path = "http://d25jsbtuwtqsio.cloudfront.net/AudioFilesOrigin/{}".format(filename)
    print(path)
    return send_from_directory(path, filename, as_attachment=True)

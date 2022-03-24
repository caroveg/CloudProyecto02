from flask import render_template, redirect, url_for, request,send_file
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.models import Concurso, Participante
from . import admin_bp
from .forms import ConcursoForm



@admin_bp.route("/admin/concurso/", methods=['GET', 'POST'], defaults={'concurso_id': None})
@admin_bp.route("/admin/concurso/<int:concurso_id>/", methods=['GET', 'POST','PUT'])
@login_required
def concurso_form(concurso_id): 
    form = ConcursoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        path_imagen = secure_filename(form.imagen.data.filename)
        form.imagen.data.save("app/static/images_concurso/" + path_imagen)
        url = form.url.data
        valor = form.valor.data
        fechaInicio = form.fechaInicio.data
        fechaFin = form.fechaFin.data
        guion = form.guion.data
        recomendaciones = form.recomendaciones.data
        fechaCreacion = datetime.now()
        concurso = Concurso(user_id=current_user.id
                        ,nombre=nombre
                        ,imagen=path_imagen
                        ,url=url
                        ,valor=valor
                        ,fechaInicio=fechaInicio
                        ,fechaFin=fechaFin
                        ,guion=guion
                        ,recomendaciones=recomendaciones
                        ,fechaCreacion=fechaCreacion)
        concurso.save()
        return redirect(url_for('public.index'))
    return render_template("concurso_form.html", form=form)

@admin_bp.route("/concursoDelete/<int:concurso_id>/", methods=['GET', 'POST'])   
def  concurso_delete(concurso_id):
    concurso = Concurso.get_by_id(concurso_id) 
    participantes = Participante.get_paths_Concurso_id(concurso_id)
   	    
    for k in participantes:
        print(k.path_audio)
        os.remove("app/static/AudioFilesDestiny/{}".format(k.path_audio))
        os.remove("app/static/AudioFilesOrigin/{}".format(k.path_audio_origin))

    os.remove("app/static/images_concurso/{}".format(concurso.imagen))
    concurso.delete()
    return redirect(url_for('public.index'))

@admin_bp.route("/concursoupdate/<int:concurso_id>/", methods=['GET', 'POST'])   
def concurso_update(concurso_id):
    concurso = Concurso.get_by_id(concurso_id)
    if concurso:
        form = ConcursoForm(obj=concurso)
        if request.method == 'POST' and form.validate():
            try:
                concurso.nombre = form.nombre.data
                path_imagen = secure_filename(form.imagen.data.filename)
                form.imagen.data.save("app/static/images_concurso/" + path_imagen)
                concurso.imagen = path_imagen
                concurso.url = form.url.data
                concurso.valor = form.valor.data
                concurso.fechaInicio = form.fechaInicio.data
                concurso.fechaFin = form.fechaFin.data
                concurso.guion = form.guion.data
                concurso.recomendaciones = form.recomendaciones.data
                concurso.update()
            except:
                concurso.nombre = form.nombre.data
                concurso.url = form.url.data
                concurso.valor = form.valor.data
                concurso.fechaInicio = form.fechaInicio.data
                concurso.fechaFin = form.fechaFin.data
                concurso.guion = form.guion.data
                concurso.recomendaciones = form.recomendaciones.data
                concurso.update()

            return redirect(url_for('public.index')) 
        return render_template('concurso_form.html', form=form)

@admin_bp.route("/participanteDelete/<int:participante_id>/", methods=['GET', 'POST'])   
def  participante_delete(participante_id):
    participante = Participante.get_by_id(participante_id)
    os.remove("app/static/AudioFilesDestiny/{}".format(participante.path_audio))
    os.remove("app/static/AudioFilesOrigin/{}".format(participante.path_audio_origin))	
    participante.delete()
    return redirect(url_for('public.index'))


@admin_bp.route('/participante/uploads/<path:filename>', methods=['GET', 'POST'])
def download_participante(filename):
    path = "static/AudioFilesDestiny/{}".format(filename)
    return send_file(path, as_attachment=True)

@admin_bp.route('/participante/uploads_origin/<path:filename>', methods=['GET', 'POST'])
def participante_origin_download(filename):
    path = "static/AudioFilesOrigin/{}".format(filename)
    return send_file(path, as_attachment=True)
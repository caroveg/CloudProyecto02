from email.mime import audio
from .models import Participante
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

HEADER_EXITO='Tu audio ya se convirtio!'
HEADER_FALLA='Problemas con tu audio'
MENSAJE_EXITO="Hola, %s \n Es de nuestro gusto informarte que tu archivo de audio se convirtio exitosamente"
MENSAJE_FALLA="Hola, %s \n Actualmente presentamos problemas con tu audio \n por favor comunicate con ayuda"
PATH_AUDIOS_NEW = "static/AudioFilesDestiny/audio_%s.mp3"
PATH_AUDIOS_ORIGIN= "static/AudioFilesOrigin/%s"
MAIN_PATH=os.path.dirname(__file__)

#def generateMailParticipante(nombre,recipient,mensaje,header):
#    cmd=f'sendemail -f proyectoCloud2022@gmail.com -t {recipient} -s smtp.gmail.com:587 -u "{header}" -m "{mensaje % nombre}" -v -xu proyectoCloud2022 -xp Cloud2022 -o tls=yes'
#    os.system(cmd)

# pylint: disable=E1101
def generateMailParticipante(nombre,recipient,mensaje,header):
    message = Mail(
        from_email='caro.castro.v@gmail.com',
        to_emails= recipient ,
        subject= header,
        html_content= mensaje % nombre)
    #try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    #except Exception as e:
        #print(e.message)

def procesarAudio(path,audio_id):
    path=PATH_AUDIOS_ORIGIN % path
    path = os.path.join(MAIN_PATH, path)
    newPath=PATH_AUDIOS_NEW % audio_id
    newPath = os.path.join(MAIN_PATH, newPath)
    cmd=f'ffmpeg -loglevel quiet -y -i {path} {newPath}'
    os.system(cmd)
    return f'audio_{audio_id}.mp3'

def jobAudios():
        print("Job Audios")
        participantes=Participante.get_no_procesados()
        print(f'Participantes sin procesar {len(participantes)}')
        for participante in participantes:
            print(participante)
            audio=participante.path_audio
            mailParticipante=participante.mail
            nombre=participante.nombres
            id=participante.id
            try:
                newPath=procesarAudio(audio,id)
                generateMailParticipante(nombre,mailParticipante,MENSAJE_EXITO,HEADER_EXITO)
                participante.path_audio=newPath
                participante.convertido=True
                participante.update()
            except:
                generateMailParticipante(nombre,mailParticipante,MENSAJE_FALLA,HEADER_FALLA)




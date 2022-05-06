from email.mime import audio
import logging
from .models import Participante
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import boto3
import botocore

from . import dynamodb, s3, sqs, sqsR
import uuid


queue = sqsR.get_queue_by_name(QueueName='sqsdespd')
#client = boto3.client('sqs',region_name='us-east-1')

HEADER_EXITO='Tu audio ya se convirtio!'
HEADER_FALLA='Problemas con tu audio'
MENSAJE_EXITO="Hola, %s \n Es de nuestro gusto informarte que tu archivo de audio se convirtio exitosamente"
MENSAJE_FALLA="Hola, %s \n Actualmente presentamos problemas con tu audio \n por favor comunicate con ayuda"
PATH_AUDIOS_NEW = "static/AudioFilesDestiny/audio_%s.mp3"
PATH_AUDIOS_ORIGIN= "static/AudioFilesOrigin/%s"
MAIN_PATH=os.path.dirname(__file__)
PATH_AUDIOS_NEW_S3 = "AudioFilesDestiny/audio_%s.mp3"
NEW_FILE_NAME = "audio_%s.mp3"
BUCKET_NAME_S3 = "storagedespd"
tparticipante =  dynamodb.Table('participante')


def generateMailParticipante(nombre,recipient,mensaje,header):
    message = Mail(
        from_email='cloud5202010@gmail.com',
        to_emails= recipient ,
        subject= header,
        html_content= mensaje % nombre)
    
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg = SendGridAPIClient('')
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    #except Exception as e:
        #print(e.message)

def procesarAudio(path,audio_id):

    print('Procesando el audio')
    path_S3 = 'AudioFilesOrigin/' + path
    filename = path
    newfilename = NEW_FILE_NAME % audio_id

    path=PATH_AUDIOS_ORIGIN % path
    pathf = os.path.join(MAIN_PATH, path)
    
    newPath=PATH_AUDIOS_NEW % audio_id
    newPath = os.path.join(MAIN_PATH, newPath)

    print('4. Descargar el audio desde S3 y lo pone en AudioFilesOrigin')    
    #s3 = boto3.resource('s3')
    if not os.path.isdir('./app/static/AudioFilesOrigin/'):
        #pathlib.mkdir(upload_path, parents = True, exist_ok= True)
        os.umask(0)
        os.makedirs('./app/static/AudioFilesOrigin/')
        logging.info('Created directory {}'.format(pathf))
    if not os.path.isdir('./app/static/AudioFilesDestiny/'):
        #pathlib.mkdir(upload_path, parents = True, exist_ok= True)
        os.umask(0)
        os.makedirs('./app/static/AudioFilesDestiny/')
        logging.info('Created directory {}'.format(pathf))
    try:
        s3.Bucket('storagedespd').download_file(path_S3, pathf)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    print('6. Convertir el audio')  
    cmd=f'ffmpeg -loglevel quiet -y -i {pathf} {newPath}'
    os.system(cmd)

    print('7. lo sube a S3') 
    newPath_S3 = PATH_AUDIOS_NEW_S3 % audio_id
    data = open(newPath, 'rb') #Path de la máquina en S3
    s3.Bucket(BUCKET_NAME_S3).put_object(Key=newPath_S3, Body=data)

    print('8 lo elimina de EC2') 
    os.remove("app/static/AudioFilesOrigin/" + filename)
    os.remove("app/static/AudioFilesDestiny/" + newfilename)
    
    return f'audio_{audio_id}.mp3'

def procesoparticipante(participante_id):
    print('Entra a proceso')
    print(participante_id)
    response = tparticipante.get_item(
        Key={'Participante_id': participante_id}
        )
    data = response.get('Item')
    print(data)
             
    audio = data.get('path_audio') 
    mailParticipante =  data.get('mail')
    nombre = data.get('nombres') 
    
    try:

        newPath=procesarAudio(audio,participante_id)
        generateMailParticipante(nombre,mailParticipante,MENSAJE_EXITO,HEADER_EXITO)

        response2 = tparticipante.get_item(Key={'Participante_id': participante_id})
        datap = response2.get('Item')

        data2 = {}              
        data2['path_audio_origin'] = datap.get('path_audio_origin')
        data2['path_audio'] = newPath
        data2['Participante_id'] = participante_id
        data2['mail'] = datap.get('mail')
        data2['observaciones'] = datap.get('observaciones')
        data2['convertido'] = 'True'
        data2['id'] = 12
        data2['url'] = datap.get('url')
        data2['fechaCreacion'] = datap.get('fechaCreacion')
        data2['nombres'] = datap.get('nombres')

        print(data2)
        print('insertando data2')
        #data2 = dict((k, v) for k, v in data.items() if v)
        response2 = tparticipante.put_item(Item=data2)
        print(response2)
        print('completado')

    except:
            generateMailParticipante(nombre,mailParticipante,MENSAJE_FALLA,HEADER_FALLA)

def jobAudios():
        messages = sqs.receive_message(QueueUrl=queue.url,MaxNumberOfMessages=10)

        if 'Messages' in messages:
            for message in messages['Messages']:
                id=str(message['Body'])
                procesoparticipante(id)
                sqs.delete_message(QueueUrl=queue.url,ReceiptHandle=message['ReceiptHandle'])
        else:
            print('Queue is now empty')

        




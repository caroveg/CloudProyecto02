from email.mime import audio
from .models import Participante
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import boto3
import botocore

from . import dynamodb
import uuid

sqs = boto3.resource('sqs', region_name='us-east-1')
queue = sqs.get_queue_by_name(QueueName='sqsdespd')
client = boto3.client('sqs',region_name='us-east-1')

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
        from_email='caro.castro.v@gmail.com',
        to_emails= recipient ,
        subject= header,
        html_content= mensaje % nombre)
    #try:
   #sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    
    #response = sg.send(message)
    #print(response.status_code)
    #print(response.body)
    #print(response.headers)
    #except Exception as e:
        #print(e.message)

def procesarAudio(path,audio_id):

    print('Procesando el audio')
    path_S3 = 'AudioFilesOrigin/' + path
    filename = path
    newfilename = NEW_FILE_NAME % audio_id

    path=PATH_AUDIOS_ORIGIN % path
    path = os.path.join(MAIN_PATH, path)
    
    newPath=PATH_AUDIOS_NEW % audio_id
    newPath = os.path.join(MAIN_PATH, newPath)

    print('4. Descargar el audio desde S3 y lo pone en AudioFilesOrigin')    
    s3 = boto3.resource('s3')
    try:
        s3.Bucket('storagedespd').download_file(path_S3, path)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    print('6. Convertir el audio')  
    cmd=f'ffmpeg -loglevel quiet -y -i {path} {newPath}'
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
    response = tparticipante.get_item(
        Key={'Participante_id': participante_id}
        )
    data = response.get('Item')
             
    audio = data.get('path_audio') 
    mailParticipante =  data.get('mail')
    nombre = data.get('nombres') 
    id = data.get('Participante_id') 
    
    try:
        newPath=procesarAudio(audio,id)
        generateMailParticipante(nombre,mailParticipante,MENSAJE_EXITO,HEADER_EXITO)

        response = tparticipante.get_item(Key={'Participante_id': id})
        data = response.get('Item')
                    
        data['path_audio_origin'] = participante.get('path_audio_origin')
        data['path_audio'] = newPath
        data['Participante_id'] = id
        data['mail'] = participante.get('mail')
        data['observaciones'] = participante.get('observaciones')
        data['convertido'] = 'True'
        data['id'] = 12
        data['convertido'] = 'True'
        data['url'] = participante.get('url')
        data['fechaCreacion'] = participante.get('fechaCreacion')
        data['nombres'] = participante.get('nombres')

        data = dict((k, v) for k, v in data.items() if v)
        response = tparticipante.put_item(Item=data)

    except:
            generateMailParticipante(nombre,mailParticipante,MENSAJE_FALLA,HEADER_FALLA)

def jobAudios():
        messages = client.receive_message(QueueUrl=queue.url,MaxNumberOfMessages=10)

        if 'Messages' in messages:
            for message in messages['Messages']:
                id=str(message['Body'])
                procesoparticipante(id)
                client.delete_message(QueueUrl=queue.url,ReceiptHandle=message['ReceiptHandle'])
        else:
            print('Queue is now empty')

        




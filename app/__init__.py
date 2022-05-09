from flask import Flask, jsonify, render_template, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import os
from urllib.parse import urljoin
import boto3
import bmemcached
from flask_session import Session
import pylibmc
import os
from flask import Flask
from hirefire.contrib.flask.blueprint import build_hirefire_blueprint
from celery import Celery
from hirefire.procs.celery import CeleryProc


celery = Celery('myproject', broker='amqp://localhost//')

class WorkerProc(CeleryProc):
    name = 'worker'
    queues = ['celery']
    app = celery


login_manager = LoginManager()
db = SQLAlchemy()
scheduler = APScheduler()

import requests
#r = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/EMR_EC2_DefaultRole")
#response_json = r.json()
v_access_key_id=os.environ.get('aws_access_key_id', '')
v_secret_access_key=os.environ.get('aws_secret_access_key', '')
v_session_token=os.environ.get('aws_session_token', '')

cache_servers = os.environ.get('MEMCACHIER_SERVERS', '').split(',')
cache_user = os.environ.get('MEMCACHIER_USERNAME', '')
cache_pass = os.environ.get('MEMCACHIER_PASSWORD', '')

#mc = bmemcached.Client(cache_servers, username=cache_user, password=cache_pass)

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
	aws_session_token=v_session_token,
    region_name='us-east-1'
)
s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
    aws_session_token=v_session_token
)


sqs = boto3.resource('sqs',
 region_name='us-east-1',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
    aws_session_token=v_session_token)
#dynamodb = boto3.resource('dynamodb',
#    aws_access_key_id='ASIATGWEY6Q5LVXJNPHS',
#    aws_secret_access_key='dS+V8PEt5BShtfqjroI9//utf/cR3utbOwae93Lw',
#	aws_session_token='IQoJb3JpZ2luX2VjECAaCXVzLWVhc3QtMSJHMEUCIQDUswKxqvvFIZi2pkiWx+13UYSyCrCYJSySib6hK1Av1wIgNCQHBhelv/dV9wXPcmklprJ9t+slNW9M4WoBrtbO1VoqgwQIyf//////////ARAAGgwyMjA1Mjk3NTEwOTgiDKxlR0WXSB2vPHpR9irXA7Q7EIoydA8Yio49iBC2YR91gaRUBQyV7c0873XmDuziPJKsyLUONKZuyqlVy2Te4MzFgdeOEp1l56qAK033jl58UYWXWeihNg40NpfV4v9rdCHHkIQQCsE+bZHQB7Q7WbDFliR+18Yn3dJ3ftu/dq6um04VW0RTGgRuh3xV67sh+G/nMrqnQuxUNVwNU8d2lsic1zM0kYkuRA8QUvgsQjSqJCK22SYuk0iG0fafOZ4mocVZr/2lV+QtILGxnYS6oE5Q6Pim+LNIR2HnFaXBLG2+bFXGLTh0pC+zZeRAoTYxZhLpCeOeUd+zOg7iPArjdu7Gqd3nOil9py6fA5zT53Z6fwFDYegFlIPw/ZAur+PdqQD9KIzo20ipvh05FpxhMzSfJ9OZsyi9USRoFnHirO58vj3GwHFKs0+YISiAnKh8E+PRWZ/b1EMyMfxsrWX7U4XCI3wwisv4gMI1UMHo6eNeSUzM1q9AfwJ3OaHYbCoFSEY5kPYJa6kImziTBdkXttcDO+VWxnCye4LzlBxi1Zp0oxgLWa2NJwtFtY9bacWYxha0IwWYLINRzeNKe4oRDDnx/rjCr9JnrHWL8dEtlaTcVSJLM//4nbMJCd+BHCSSYMUzTrH+hzCcyfKSBjqlASbIUz1SipBQsNO3c/5EM8KuCUz/r0TgkR/+7MUNuKkykYE6xZxA9mINf4r6WIhxlqW8DR3oZ5DjqZO82YhXSLDYeVIPD8OnJtXznHkQ4Vz4N1bS3nMMAXwmeKIteMWE6TH3EXV4X438Uwg3p2yLcnSQ4W9zz7HGHleLwe41aCQ5haj/xJHUPelAiI8JEGhPwNfPp5ZNGQ3ixzEhNKSSOjfanWsKxA==',
#	region_name='us-east-1'
#)

def create_app():

    app = Flask(__name__)
 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jirafa159*@db01.crbchgb8swzt.us-east-1.rds.amazonaws.com/DB_DESP_C'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'Jirafa159*'
    app.config['SESSION_TYPE'] = 'memcached'
    app.config['SESSION_MEMCACHED'] = pylibmc.Client(cache_servers, binary=True,
                       username=cache_user, password=cache_pass,
                       behaviors={
                            # Faster IO
                            'tcp_nodelay': True,
                            # Keep connection alive
                            'tcp_keepalive': True,
                            # Timeout for set/get requests
                            'connect_timeout': 2000, # ms
                            'send_timeout': 750 * 1000, # us
                            'receive_timeout': 750 * 1000, # us
                            '_poll_timeout': 2000, # ms
                            # Better failover
                            'ketama': True,
                            'remove_failed': 1,
                            'retry_timeout': 2,
                            'dead_timeout': 30,
                       })

    server_sesssion = Session(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    db.init_app(app)    
    
    #registro hireFire blue print 
    bp = build_hirefire_blueprint(os.environ['HIREFIRE_TOKEN'],
                              ['hirefire.procs.celery.CeleryProc'])
    app.register_blueprint(bp)

    # Registro de los Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    @app.before_first_request
    def createDB():
        db.create_all()

    # if __name__ == '__main__':
    #     app.run(debug=True)

    #if __name__ == '__main__':
        #app.run(host="0.0.0.0", port=8080, debug=False)

    return app
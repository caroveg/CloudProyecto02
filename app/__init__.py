from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import os
from urllib.parse import urljoin
import boto3


login_manager = LoginManager()
db = SQLAlchemy()
scheduler = APScheduler()

import requests
r = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/EMR_EC2_DefaultRole")
response_json = r.json()
v_access_key_id=response_json.get('AccessKeyId')
v_secret_access_key=response_json.get('SecretAccessKey')
v_session_token=response_json.get('Token')

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
	aws_session_token=v_session_token,
    region_name='us-east-1'
)


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

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    db.init_app(app)    

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

    if __name__ == '__main__':
        app.run(debug=True)

    #if __name__ == '__main__':
        #app.run(host="0.0.0.0", port=8080, debug=False)

    return app
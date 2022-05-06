from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import boto3

login_manager = LoginManager()
db = SQLAlchemy()
scheduler = APScheduler()

import requests
# r = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/EMR_EC2_DefaultRole")
# response_json = r.json()
# v_access_key_id=response_json.get('AccessKeyId')
# v_secret_access_key=response_json.get('SecretAccessKey')
# v_session_token=response_json.get('Token')

v_access_key_id='ASIATGWEY6Q5B46WJY5A'
v_secret_access_key='s4BCm4sjN2Jb+N3Xll2xbaKVuJCjWknMyHO3BI6H'
v_session_token='FwoGZXIvYXdzEPX//////////wEaDD2e9UJEL2fYeolITyLKAfuw5xogsLOruf4ls52q1kRU8mjIzME2sq6K2CuuNh3RJ9a3PzqisBH0INsT2VH9ujjACLcrpQjX9YeWNr0R/UoCgoQtwxjODa6JjH3REQkKm2IEHk2knWzIRnSCUCiLjyKc6tCflUTIOklOxpYKn/yvN4/ONrNKzy997/kXwcx0CmJ+zIg8qECbAgeu8Wv4rszWy/OWWefYsO1mnk21B0WDTApv4dTzm8j82Ju8DiIQltDOI7HcqarlsHhfpDK57d19pQYp1c4MUHkokvbVkwYyLajwwKZHmBeGT5JGjiRVoWudZL2h3XW74Iy9EAHdM1Jk3oPO3/JZD4WXx/6FKQ=='

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
	aws_session_token=v_session_token,
    region_name='us-east-1'
)


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




sqs = boto3.client('sqs',
 region_name='us-east-1',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
    aws_session_token=v_session_token)

sqsR = boto3.resource('sqs',region_name='us-east-1',
    aws_access_key_id=v_access_key_id,
    aws_secret_access_key=v_secret_access_key,
    aws_session_token=v_session_token)

def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jirafa159*@db01.crbchgb8swzt.us-east-1.rds.amazonaws.com/DB_DESP_C'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'Jirafa159*'

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    db.init_app(app)
    #El encargado de hacer jobs perodicamente
    scheduler.init_app(app)
    scheduler.start()    

    from .cronJob import jobAudios
    @scheduler.task('interval', id='job_process', seconds=20, misfire_grace_time=120)
    def cronTask():
        with scheduler.app.app_context():
            jobAudios()
            
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
from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_cdn import CDN
import os
from urllib.parse import urljoin


login_manager = LoginManager()
db = SQLAlchemy()
scheduler = APScheduler()
cdn = CDN()

def create_app():

    app = Flask(__name__)
 
    app.config['CDN_DOMAIN'] = 'd25jsbtuwtqsio.cloudfront.net'
    CDN(app)

    #CDN(app)

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
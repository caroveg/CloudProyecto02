
from app import create_app
from flask_cdn import CDN
from flask import Flask


cdn = CDN()


#app = create_app()

if __name__=='__main__':
    from app import create_app
    app = create_app()

    app.config['CDN_DOMAIN'] = 'd25jsbtuwtqsio.cloudfront.net'
    CDN(app)

    app.run(debug=True)

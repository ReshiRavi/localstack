from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    from .views import views
    app.register_blueprint(views, url_prefix='/')
    return app

if(__name__ == '__main__'):
    app = create_app()
    app.run(debug=True)
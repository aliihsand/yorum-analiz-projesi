from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    CORS(app)

    # Blueprint'leri burada import et ve kaydet
    from app.routes.reviews import reviews_bp
    from app.routes.raporlar import raporlar_bp
    from app.routes.oneriler import oneriler_bp

    app.register_blueprint(reviews_bp)
    app.register_blueprint(raporlar_bp)
    app.register_blueprint(oneriler_bp)

    return app
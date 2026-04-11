from flask import Flask
from flask_cors import CORS
from routes import api_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for frontend access
    
    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    return app

# Create the app instance at the module level so Gunicorn can find it
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

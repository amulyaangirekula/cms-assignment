import os
from flask import Flask
from db import db
from routes import api_routes
from auth import auth_routes

app = Flask(__name__)

app.secret_key = "supersecretkey"   # for sessions

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(api_routes)
app.register_blueprint(auth_routes)

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

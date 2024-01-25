from flask_cors import CORS
from loginApi import app, db

from loginApi.api.login import loginBp
from loginApi.model.login import initLogin

# Create CORS instance before registering blueprint
cors = CORS(app)

# Register blueprint
app.register_blueprint(loginBp)

# Flag to ensure initialization only happens once
initialized = False

@app.before_request
def init_db():
    global initialized
    if not initialized:
        with app.app_context():
            db.create_all()
            initLogin()
            initialized = True

if __name__ == "__main__":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./volumes/sqlite.db"
    app.run(debug=True, host="0.0.0.0", port="8199")

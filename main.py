from flask_cors import CORS
from loginApi import app, db

from loginApi.api.login import loginBp

from loginApi.model.login import initLogin

app.register_blueprint(loginBp)

@app.before_first_request
def init_db():
    with app.app_context():
        db.create_all()
        
        initLogin()

if __name__ == "__main__":
    cors = CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./volumes/sqlite.db"
    app.run(debug=True, host="0.0.0.0", port="8199")
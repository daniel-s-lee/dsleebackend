from flask import Flask,Blueprint, Response, app, current_app, request, jsonify
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime

import jwt
import logging

from loginApi.model.user import User
from auth_middleware import token_required

# blueprint, which is registered to app in main.py
user_api = Blueprint('user_api', __name__,
                   url_prefix='/api/users')

# Configure the logging module
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)  # Set the logging level as needed

# API docs https://flask-restful.readthedocs.io/en/latest/api.html#id1
api = Api(user_api)
class UserAPI:        
    class _Create(Resource):
        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            print("%%%%% here1")
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                print("%%%%% name error")
                return {'message': f'Name is missing, or is less than 2 characters'}, 400
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 400
            
            email = body.get('email')
            if email is None or len(uid) < 2:
                return {'message': f'email  is missing, or is less than 2 characters'}, 400
            # look for password and dob
            password = body.get('password')
          
            
            dob = body.get('dob')
            print("%%%%% here12")
            ''' #1: Key code block, setup USER OBJECT '''
            uo = User(name=name, 
                      uid=uid,email=email)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)
                
                           
            # convert to date type
            if dob is not None:
                try:
                    uo.dob = datetime.strptime(dob, '%m-%d-%Y').date()
                except:
                    return {'message': f'Date of birth format error {dob}, must be mm-dd-yyyy'}, 400
            
            ''' #2: Key Code block to add user to database '''
            # create user in database
            user = uo.create()
            # success returns json of user
            if user:
                return jsonify(user.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 400

    
    class _CRUD(Resource):
        def post(self): # Create method
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 400
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 400
            
            email = body.get('email')
            if email is None or len(uid) < 2:
                return {'message': f'email  is missing, or is less than 2 characters'}, 400
            # look for password
            password = body.get('password')

            ''' #1: Key code block, setup USER OBJECT '''
            uo = User(name=name, 
                      uid=uid, email=email)
            
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)
                
            # set server request status    
            uo.server_needed = body.get('server_needed')
            
            ''' #2: Key Code block to add user to database '''
            # create user in database
            user = uo.create()
            # success returns json of user
            if user:
                return jsonify(user.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 400
        

        def get(self): # Read Method
            users = User.query.all()    # read/extract all users from database
            json_ready = [user.read() for user in users]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps
        
        @token_required       
        def put(self, current_user, id):  # Update method
            ''' Read data for json body '''
            body = request.get_json()

            ''' Find user by ID '''
            user = User.query.get(id)
            if user is None:
                return {'message': f'User with ID {id} not found'}, 404

            ''' Update fields '''
            name = body.get('name')
            if name:
                user.name = name
 
            email = body.get('email')
            if email:
                user.email = email
                               
            uid = body.get('uid')
            if uid:  
                user.uid = uid
                
            user.server_needed = body.get('server_needed')

            user.active_classes = body.get('active_classes')
            user.archived_classes = body.get('archived_classes')

            ''' Commit changes to the database '''
            user.update()
            return jsonify(user.read())
        
        def delete(self, id):  # Delete method
            ''' Find user by ID '''
            user = User.query.get(id)
            if user is None:
                return {'message': f'User with ID {id} not found'}, 404

            ''' Delete user '''
            user.delete()
            return {'message': f'User with ID {id} has been deleted'}

    class _Security(Resource):

        def post(self):
            try:
                print('*******security started')
                
                body = request.get_json()
                if not body:
                    return {
                        "message": "Please provide user details",
                        "data": None,
                        "error": "Bad request"
                    }, 400
                ''' Get Data '''
                uid = body.get('uid')
                if uid is None:
                    return {'message': f'User ID is missing'}, 400
                password = body.get('password')
                
                ''' Find user '''
                user = User.query.filter_by(_uid=uid).first()
                print('******* found user')
                if user is None or not user.is_password(password):
                    return {'message': f"Invalid user id or password"}, 400
                if user:
                    try:
                        token = jwt.encode(
                            {"_uid": user._uid},
                            current_app.config["SECRET_KEY"],
                            algorithm="HS256"
                        )
                        resp = Response("Authentication for %s successful" % (user._uid))
                        resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None'  # This is the key part for cross-site requests

                                # domain="frontend.com"
                                )
                        
                        return resp
                    except Exception as e:
                        return {
                            "error": "Something went wrong",
                            "message": str(e)
                        }, 500
                return {
                    "message": "Error fetching auth token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 404
            except Exception as e:
                print(e)
                return {
                        "message": "Something went wrong!",
                        "error": str(e),
                        "data": None
                }, 500
        
    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_CRUD, '/', '/<int:id>')
    api.add_resource(_Security, '/authenticate')
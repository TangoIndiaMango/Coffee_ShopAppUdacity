from operator import methodcaller
import os
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, verify_decode_jwt, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message':'hello-coffee'})
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['GET'])
# @requires_auth('get:drinks')
def get_drinks():
    
    # data = []
    drinks = Drink.query.all()

    return jsonify({
        'success' : True,
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-details', methods=['GET'])
@requires_auth('get:drinks-details')
def get_drinks_details(jwt):
    
    drinks = Drink.query.all()
    
    try:
        return jsonify({
            'success': True,
            'drinks': [d.long() for d in drinks]
        }), 200
    except:
        abort (422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):

    # body = request.get_json()

    # title_drink = body['title']
    # recipe_drink = json.dumps(body['recipe'])

    # if title_drink is None or recipe_drink is None:
    #     abort(422)

    # try:
    #     put_drink = Drink(title=title_drink, recipe=recipe_drink)
    #     put_drink.insert()

    #     return jsonify({
    #         'success': True,
    #         'drinks': [put_drink.long()]
    #     }), 200
    # except:
    #     abort(422)

        body = request.get_json()
        
        try:
            recipe = body['recipe']
            if type(recipe) is dict:
                recipe = [recipe]
            
            title = body['title']
            
            drink = Drink(title=title, recipe=json.dumps(recipe))
            drink.insert()
            

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
            
        except:
            abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt, id):
    body = request.get_json()

    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort (422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):

    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        "success": True,
        "delete": drink.id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def Drink_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Drink not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def Unauthorized_action(error):
    return jsonify({
        "success":False,
        "error": 401,
        "message": "Unauthorized to perform this action"
    }), 401



@app.errorhandler(AuthError)
def handle_AuthError(error):
    response = jsonify(error)
    response.status_code = error.status_code

    return response
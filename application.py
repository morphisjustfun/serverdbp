from flask import Flask,render_template, request, session, Response, redirect
import connector
import entities
from datetime import datetime
import json
import time
import threading
from sqlalchemy import or_, and_


db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)
app.config.from_object('config')
cache = {}
key_users = 'keyuser'
key_pets = 'keypets'
lock = threading.Lock()
locku = threading.Lock()



@app.route('/logout',methods=['GET'])
def logout():
    if 'logged' in session:
        del session['logged']
    if 'idk' in session:
        del session['idk']
    msg = {'msg':'logged out'}
    return Response(json.dumps(msg),status=200)

def assign(key,value):
    session[key] = value

@app.route('/login',methods=["POST"])
def login():
    body = json.loads(request.data)
    username = body["username"]
    password = body["password"]
    key='logged'
    if key in session:
        r_msg = {'msg':'already logged','username':username,'id':session['idk'],'password':password}
        json_msg = json.dumps(r_msg)
        return Response(json_msg,status=200)
    db_session = db.getSession(engine)
    respuesta = db_session.query(entities.User).filter(entities.User.username==username).filter(entities.User.password==password).all()
    users = respuesta[:]
    if len(users) > 0:
        idk = respuesta[0].id
        assign(key,[username,password])
        assign('idk',idk)
        db_session.close()
        r_msg = {'msg':'welcome','username':str(username),'id':int(idk),'password':str(password)}
        json_msg = json.dumps(r_msg)
        return Response(json_msg,status=200)
    db_session.close()
    r_msg = {'msg':'failed'}
    json_msg = json.dumps(r_msg)
    return Response(json_msg,status=401)
"""
@app.route('/authenticate',methods=["POST"])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    key = 'logged'
    if key in session and session[key] == [username,password]:
        return Response("Already logged",status=200)
    db_session = db.getSession(engine)
    respuesta = db_session.query(entities.User).filter(entities.User.username==username).filter(entities.User.password==password)
    users = respuesta[:]
    idk = respuesta[0].id
    if len(users) > 0:
        assign(key,[username,password])
        assign('idk',idk)
        db_session.close()
        return Response("Welcome",status=200)
    db_session.close()
    return Response("Failed",status=200)
"""


@app.route('/current', methods = ['GET'])
def current():
    db_session = db.getSession(engine)
    response = db_session.query(entities.User).filter(entities.User.id==session['idk'])
    users = response[:]
    json_message = json.dumps(users, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status=200 ,mimetype='application/json')



#-------------CRUD USERS --------------#
#GET - with cache
@app.route('/users', methods = ['GET'])
def read_user():
    users = []
    locku.acquire()
    if key_users in cache and (datetime.now()-cache[key_users]['datetime']).total_seconds() < 10:
        users = cache[key_users]['data']
    else:
        db_session = db.getSession(engine)
        response = db_session.query(entities.User).all()
        users = response[:]
        now = datetime.now()
        cache[key_users] = {'data':users,'datetime':now}
        db_session.close()
    json_message = json.dumps(users, cls=connector.AlchemyEncoder)
    locku.release()
    return Response(json_message, status=200 ,mimetype='application/json')
#GET with ID
@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')
    message = { 'status': 404, 'message': 'Not Found'}
    db_session.close()
    return Response(json.dumps(message), status=404, mimetype='application/json')
#CREATE
@app.route('/users', methods = ['POST'])
def create_users():
    body = json.loads(request.data)
    user = entities.User(username = body['username'], name = body['name'], fullname = body['fullname'], password = body['password'],contact=body['contact'])
    db_session =  db.getSession(engine)
    db_session.add(user)
    db_session.commit()
    message = {'msg': 'User created'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status=201, mimetype='application/json')
#DELETE with ID
@app.route('/users/<id>', methods = ['DELETE'])
def delete_user(id):        
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == id).first()
    db_session.delete(user)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'User Deleted'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status = 201, mimetype='application/json')
#UPDATE with ID
@app.route('/users/<id>', methods = ['PUT'])
def update_user(id):
    #busca al usuarui
    db_session =  db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == id).first()
    body = json.loads(request.data)
    #actualiza los datos
    for key in body.keys():
        setattr(user, key, body[key])
    #se guarda la actulizacion
    db_session.add(user)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'User update'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status = 201, mimetype='application/json')


#CRUD PETS

@app.route('/pets', methods = ['GET'])
def read_pet():
    pets = []
    locku.acquire()
    if key_pets in cache and (datetime.now()-cache[key_pets]['datetime']).total_seconds() < 10:
        pets = cache[key_pets]['data']
    else:
        db_session = db.getSession(engine)
        response = db_session.query(entities.Pets).all()
        pets = response[:]
        now = datetime.now()
        cache[key_pets] = {'data':pets,'datetime':now}
        db_session.close()
    json_message = json.dumps(pets, cls=connector.AlchemyEncoder)
    locku.release()
    return Response(json_message, status=200 ,mimetype='application/json')



@app.route('/pets', methods = ['POST'])
def create_pets():
    body = json.loads(request.data)
    pet = entities.Pets(id_user = body['id_user'], type = body['type'], breed = body['breed'], place = body['place'],info =body['info'],age =body['age'],color =body['color'],date =datetime.now())
    db_session =  db.getSession(engine)
    db_session.add(pet)
    db_session.commit()
    message = {'msg': 'Pet created'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status=201, mimetype='application/json')

    
@app.route('/pets/<id>', methods = ['DELETE'])
def delete_pet(id):        
    db_session = db.getSession(engine)
    pet = db_session.query(entities.Pets).filter(entities.Pets.id == id).first()
    db_session.delete(pet)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'Pet Deleted'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status = 201, mimetype='application/json')

@app.route('/pets/<id>', methods = ['PUT'])
def update_pet(id):
    #busca al pet
    db_session =  db.getSession(engine)
    pet = db_session.query(entities.Pets).filter(entities.User.id == id).first()
    body = json.loads(request.data)
    #actualiza los datos
    for key in body.keys():
        setattr(pet, key, body[key])
    #se guarda la actulizacion
    db_session.add(pet)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'Pet update'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status = 201, mimetype='application/json')


@app.route('/pets/<id>', methods = ['GET'])
def get_pet(id):
    db_session = db.getSession(engine)
    pets = db_session.query(entities.Pets).filter(entities.Pets.id == id)
    for pet in pets:
        js = json.dumps(pet, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')
    message = { 'status': 404, 'message': 'Not Found'}
    db_session.close()
    return Response(json.dumps(message), status=404, mimetype='application/json')
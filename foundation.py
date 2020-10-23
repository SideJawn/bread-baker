from flask import Flask, request
import json, requests, string, secrets, hashlib
app = Flask(__name__)

oven_url = 'http://127.0.0.1:8001'

#Middleware for data in project cards feed
@app.route('/project', methods=['GET'])
def get_projects():
    params = request.args
    response = send_to_oven('/project', 'GET', params)
    
    return response

#Creates a hashed salted password for new users
@app.route('/user', methods=['PUT'])
def create_user():
    user = request.get_json()['data']
    user_pass = ''
    alphabet = string.ascii_letters + string.digits

    if user['password'] is not None:
        user_pass = user['password']
        salt = ''.join(secrets.choice(alphabet) for i in range(8))
        salted_pass = user_pass + salt
        hashed_pass = hashlib.sha256(salted_pass.encode()).hexdigest()

        new_creds = {'salt': salt, 'hashed_pass': hashed_pass}
        del user['password']
        user.update(new_creds)

        response = send_to_oven('/user', 'PUT', user)
    else:
        response = { 'status_code': 'Password is missing' }

    return response

#Authenticates the user
@app.route('/creds/<username>', methods=['POST'])
def get_auth(username = None):
    endpoint = '/creds/' + username
    creds = request.get_json()['data']
    entered_pass = creds['password']

    oven_response = send_to_oven(endpoint, 'GET')
    if 'results' in oven_response:
        db_creds = oven_response['results'][0]
        db_pass = db_creds['password']
        salt = db_creds['salt']
        salted_pass = entered_pass + salt
        hashed_pass = hashlib.sha256(salted_pass.encode()).hexdigest()
        if hashed_pass == db_pass:
            response = {'auth_status': 'AUTHORIZED'}
        else:
            response = {'auth_status': 'UNAUTHORIZED'}
    else:
        return oven_response
    
    return response

#Gets user profile data
@app.route('/user/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id = None):
    endpoint = '/user/' + user_id + '/profile'
    response = send_to_oven(endpoint, 'GET')
    
    return response

#Gets data to update the user profile
@app.route('/user/<user_id>/profile', methods=['PUT'])
def update_user_profile(user_id = None):
    endpoint = '/user/' + user_id + '/profile'
    user = request.get_json()['data']
    response = send_to_oven(endpoint, 'PUT', user)
    
    return response

#Change User Status
@app.route('/user/<user_id>/profile/status', methods=['PUT'])
def update_user_status(user_id = None):
    endpoint = '/user/' + user_id + '/profile/status'
    status = request.get_json()['data']
    response = send_to_oven(endpoint, 'PUT', status)
    
    return response

#Communicates with oven API
def send_to_oven(endpoint, request_type, payload = None):
    updated_oven_url = oven_url + endpoint
    r = ''
    try:
        if request_type == 'PUT':
            header = {"Content-Type": "application/json"}
            json_payload = json.dumps(payload)
            r = requests.put(updated_oven_url, headers= header, data=json_payload)
        elif request_type == 'GET':
            r = requests.get(updated_oven_url, params=payload)
        response = r.json()
    except requests.ConnectionError as err:
        print(err)
        response = { 'status_code': 'Connection Error'}
    except requests.exceptions.HTTPError as err:
        print(err)
        response = { 'status_code': 'HTTP Error'}
    except requests.exceptions.Timeout as err:
        print(err)
        response = { 'status_code': 'Timeout Error'}
    except requests.exceptions.RequestException as err:
        print(err)
        response = { 'status_code': 'General error'}

    return response
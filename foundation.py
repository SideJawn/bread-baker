from flask import Flask, request
import json, requests
app = Flask(__name__)

oven_url = 'http://127.0.0.1:8001/project'

@app.route('/project', methods=['GET'])
def get_projects():
    args = request.args

    r = requests.get(oven_url, params=args)
    response = r.text
    
    return response
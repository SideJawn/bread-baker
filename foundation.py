from flask import Flask, request
import json, requests
app = Flask(__name__)

@app.route('/project', methods=['GET'])
def get_projects():
    category = request.args.get('category')
    num_recs = request.args.get('num_recs')
    index = request.args.get('index')

    payload = {'category': category, 'num_recs': num_recs, 'index': index}

    r = requests.get('http://127.0.0.1:8001/project', params=payload)
    response = r.text
    
    return response
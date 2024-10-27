from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests
import time
import logging
import cv2
import numpy as np
from deepface import DeepFace
from flask_socketio import SocketIO, emit
from PIL import Image
import io
app = Flask(__name__)
app.secret_key = 'fb44aa78e91373ff5b7f65b7fc205eca'  # 设置会话的密钥
# 加载预训练的人脸检测模型
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


users = {}
APPID = '180984ea'
API_KEY = 'd751ff970ef3bfd80bb3dec113430a35'

socketio = SocketIO(app)
def getHeader(image_name):
    curTime = str(int(time.time()))
    param = json.dumps({"image_name": image_name})
    paramBase64 = base64.b64encode(param.encode('utf-8')).decode('utf-8')
    checkSum = hashlib.md5((API_KEY + curTime + paramBase64).encode('utf-8')).hexdigest()

    headers = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
    }
    return headers


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message="用户名或密码错误")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form['newUsername']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']

        if new_username in users:
            return render_template('register.html', message="用户名已存在")

        if new_password != confirm_password:
            return render_template('register.html', message="两次输入的密码不一致")

        hashed_password = generate_password_hash(new_password)
        users[new_username] = {'username': new_username, 'password': hashed_password}

        return render_template('register.html', success_message="注册成功，请返回登录")
    return render_template('register.html')


@app.route('/face_compare', methods=['GET', 'POST'])
def face_compare():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            try:
                img1 = request.files['image1'].read()
                img2 = request.files['image2'].read()
                similarity_score = run_face_comparison(img1, img2)
                return jsonify({"ret": 0, "score": similarity_score})
            except Exception as e:
                logging.error("Error in face_compare: %s", e)
                return jsonify({"ret": 1, "error": str(e)})
        return render_template('face_compare.html', username=username)
    return redirect(url_for('login'))


@app.route('/face_detect', methods=['GET', 'POST'])
def face_detect():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            try:
                img = request.files['image'].read()
                detect_results = run_face_detection(img)
                if detect_results.get('ret') != 0:
                    raise ValueError("Face detection failed with error code {}".format(detect_results.get('ret')))
                return jsonify({"ret": 0, "results": detect_results})
            except Exception as e:
                logging.error("Error in face_detect: %s", e)
                return jsonify({"ret": 1, "error": str(e)})
        return render_template('face_detect.html', username=username)
    return redirect(url_for('login'))


@app.route('/face_feature_analysis', methods=['GET', 'POST'])
def face_feature_analysis():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            try:
                img = request.files['image'].read()
                age_results = feature_analysis_age("image.jpg", img)
                sex_results = feature_analysis_sex("image.jpg", img)
                expression_results = feature_analysis_expression("image.jpg", img)
                face_score_results = feature_analysis_face_score("image.jpg", img)

                if age_results.get('code') == 0 and sex_results.get('code') == 0 and expression_results.get('code') == 0 and face_score_results.get('code') == 0:
                    results = {
                        "age": age_results['data']['fileList'][0]['label'],
                        "sex": sex_results['data']['fileList'][0]['label'],
                        "expression": expression_results['data']['fileList'][0]['label'],
                        "face_score": face_score_results['data']['fileList'][0]['label']
                    }
                    return jsonify({"ret": 0, "results": results, "face_count": 1})
                else:
                    error_msg = f"Face feature analysis failed with age_results: {age_results}, sex_results: {sex_results}, expression_results: {expression_results}, face_score_results: {face_score_results}"
                    logging.error(error_msg)
                    return jsonify({"ret": 1, "error": error_msg})

            except Exception as e:
                logging.error("Error in face_feature_analysis: %s", e)
                return jsonify({"ret": 1, "error": str(e)})

        return render_template('face_feature_analysis.html', username=username)
    return redirect(url_for('login'))

@app.route('/time_recognition', methods=['GET', 'POST'])
def time_recognition():
    if 'username' in session:
        username = session['username']
        return render_template('time_recognition.html', username=username)
    return redirect(url_for('login'))
def feature_analysis_age(image_name, image_data):
    url = "http://tupapi.xfyun.cn/v1/age"
    headers = getHeader(image_name)
    response = requests.post(url, headers=headers, data=image_data)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('code') != 0:
        logging.error(f"feature_analysis_age failed: {response_data}")
    return response_data

def feature_analysis_sex(image_name, image_data):
    url = "http://tupapi.xfyun.cn/v1/sex"
    headers = getHeader(image_name)
    response = requests.post(url, headers=headers, data=image_data)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('code') != 0:
        logging.error(f"feature_analysis_sex failed: {response_data}")
    return response_data

def feature_analysis_expression(image_name, image_data):
    url = "http://tupapi.xfyun.cn/v1/expression"
    headers = getHeader(image_name)
    response = requests.post(url, headers=headers, data=image_data)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('code') != 0:
        logging.error(f"feature_analysis_expression failed: {response_data}")
    return response_data

def feature_analysis_face_score(image_name, image_data):
    url = "http://tupapi.xfyun.cn/v1/face_score"
    headers = getHeader(image_name)
    response = requests.post(url, headers=headers, data=image_data)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('code') != 0:
        logging.error(f"feature_analysis_face_score failed: {response_data}")
    return response_data

def gen_body(appid, img1_data, img2_data, server_id):
    body = {
        "header": {
            "app_id": appid,
            "status": 3
        },
        "parameter": {
            server_id: {
                "service_kind": "face_compare",
                "face_compare_result": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "json"
                }
            }
        },
        "payload": {
            "input1": {
                "encoding": "jpg",
                "status": 3,
                "image": str(base64.b64encode(img1_data), 'utf-8')
            },
            "input2": {
                "encoding": "jpg",
                "status": 3,
                "image": str(base64.b64encode(img2_data), 'utf-8')
            }
        }
    }
    return json.dumps(body)


def run_face_comparison(img1, img2):
    appid = '180984ea'
    api_key = 'fb44aa78e91373ff5b7f65b7fc205eca'
    api_secret = 'ZjU2NDAwMTJmYzhmM2M2NTQ4OTY1ZTY1'
    server_id = 's67c9c78c'
    url = 'http://api.xf-yun.com/v1/private/{}'.format(server_id)

    try:
        request_url = assemble_ws_auth_url(url, "POST", api_key, api_secret)
        headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': appid}

        body = gen_body(appid, img1, img2, server_id)

        response = requests.post(request_url, data=body, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        resp_data = json.loads(response.content.decode('utf-8'))

        result_text = base64.b64decode(resp_data['payload']['face_compare_result']['text']).decode()
        result_json = json.loads(result_text)

        similarity = result_json.get('score', None)
        if similarity is None:
            raise ValueError("Response JSON does not contain 'score' field")

        return similarity

    except requests.exceptions.RequestException as e:
        logging.error("Network error in run_face_comparison: %s", e)
        return {"ret": 1, "error": "Network error, please try again later"}
    except Exception as e:
        logging.error("Error in run_face_comparison: %s", e)
        return {"ret": 1, "error": str(e)}


def gen_body_detect(appid, img_data, server_id):
    body = {
        "header": {
            "app_id": appid,
            "status": 3
        },
        "parameter": {
            server_id: {
                "service_kind": "face_detect",
                "detect_points": "1",  # 检测特征点
                "detect_property": "1",  # 检测人脸属性
                "face_detect_result": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "json"
                }
            }
        },
        "payload": {
            "input1": {
                "encoding": "jpg",
                "status": 3,
                "image": str(base64.b64encode(img_data), 'utf-8')
            }
        }
    }
    return json.dumps(body)


def run_face_detection(img):
    appid = '180984ea'
    api_key = 'fb44aa78e91373ff5b7f65b7fc205eca'
    api_secret = 'ZjU2NDAwMTJmYzhmM2M2NTQ4OTY1ZTY1'
    server_id = 's67c9c78c'
    url = 'http://api.xf-yun.com/v1/private/{}'.format(server_id)

    try:
        # Generate request URL
        request_url = assemble_ws_auth_url(url, "POST", api_key, api_secret)
        headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': appid}

        # Generate request body
        body = gen_body_detect(appid, img, server_id)

        # Send POST request to the API
        response = requests.post(request_url, data=body, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the response
        resp_data = json.loads(response.content.decode('utf-8'))

        # Check for successful response
        result_text = base64.b64decode(resp_data['payload']['face_detect_result']['text']).decode()
        result_json = json.loads(result_text)

        if 'ret' in result_json and result_json['ret'] == 0:
            return result_json
        else:
            error_code = result_json.get('ret', 'Unknown')
            error_message = result_json.get('error_message', 'No error message provided')
            raise ValueError(f"Face detection failed with error code {error_code}: {error_message}")

    except requests.exceptions.RequestException as e:
        logging.error("Network error in run_face_detection: %s", e)
        return {"ret": 1, "error": "Network error, please try again later"}
    except Exception as e:
        logging.error("Error in run_face_detection: %s", e)
        return {"ret": 1, "error": str(e)}
#
def assemble_ws_auth_url(request_url, method="GET", api_key="", api_secret=""):
    u = parse_url(request_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
    api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }
    return request_url + "?" + urlencode(values)

def parse_url(request_url):
    stidx = request_url.index("://")
    host = request_url[stidx + 3:]
    schema = request_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise ValueError("invalid request url:" + request_url)
    path = host[edidx:]
    host = host[:edidx]
    return Url(host, path, schema)
class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema


def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


# @socketio.on('frame')
# def handle_frame(data):
#     try:
#         # image_data = data['imageData']
#         sbuf = np.frombuffer(base64.b64decode(data), dtype=np.uint8)
#         img = cv2.imdecode(sbuf, flags=1)
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(150, 150))
#         property = {'data': data,'property': []}
#         for (x, y, w, h) in faces:
#             property['property'].append({'x': int(x), 'y': int(y) , 'w': int(w), 'h': int(h), 'name':"person"})
#         # emit('detection-results', {'image_data': image_data, 'faces': analysis['instances']})
#         emit('response', property)
#     except Exception as e:
#         print(e)
#         logging.error("Error in handle_frame: %s", e)
#         emit('detection-results', {'error': str(e)})

@socketio.on('frame')
def handle_frame(data):
    try:
        sbuf = np.frombuffer(base64.b64decode(data), dtype=np.uint8)
        img = cv2.imdecode(sbuf, flags=1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 使用DeepFace进行人脸分析
        analysis = DeepFace.analyze(gray)

        # 组织返回数据
        faces = []
        for face in analysis:
            region = face['region']
            dominant_emotion = face['dominant_emotion']
            age = face['age']
            gender = face['dominant_gender']
            face_info = {
                'x': region['x'],
                'y': region['y'],
                'w': region['w'],
                'h': region['h'],
                'emotion': dominant_emotion,
                'age': age,
                'gender': gender
            }
            faces.append(face_info)

        property = {'data': data, 'property': faces}

        emit('response', property)
    except Exception as e:
        logging.error("Error in handle_frame: %s", e)
        emit('detection-results', {'error': str(e)})
# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)








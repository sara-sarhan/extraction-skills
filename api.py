import os
import urllib.request
from controller_api import Controller
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import predict
ctrl = Controller()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
# UPLOAD_FOLDER = 'C:/uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    print(filename)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/fileupload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    print('request.files', request.files)
    uploaded_files = request.files.getlist("file")
    print("uploaded_files.....", uploaded_files)
    
    # start istanza servizio , in teoria dovrebbe leggerlo da qualche parte, un file di configurazione
    with open('status_service.txt', 'w') as f:
        f.write('200') # 
    ctrl.set_status_run("200")    
    
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 404
        ctrl.set_status_run("404")
        ctrl.set_status("404")
        with open('status_service.txt', 'w') as f:
            f.write('404')
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        ctrl.set_status_run("404")
        ctrl.set_status("404")
        resp.status_code = 404
        with open('status_service.txt', 'w') as f:
            f.write('404')
        return resp
    if file and allowed_file(file.filename):
        print('file.filename', file.filename)
        ctrl.set_status("202") #opeeration in progress."
        filename = secure_filename(file.filename)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        path = os.getcwd()
        file.save(filename)
        pdfnamepath = os.path.join(path, filename)
        print(pdfnamepath)
        language = "Italian"
        category, skillsner = predict.main(pdfnamepath, language)
        resp = jsonify({'job title': str(category), 'skills': str(skillsner)})
        resp.status_code = "200"
        ctrl.set_status_run("200")
        ctrl.set_status("200")
       
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = "404"
        ctrl.set_status_run("404")
        return resp


@app.route('/services/start', methods=['POST'])
def start():
    status=ctrl.get_status()
    if status == "200":
        resp = jsonify({"summary": "Starts an instance of the service", 'description': ctrl.status_desc[str(status)],"status_code":status})
        resp.status_code = "200"
        return resp
    if status == "202":
        resp = jsonify({"summary": "Starts an instance of the service", 'description': ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "202"
        return resp
    if status == "404":
        resp = jsonify({"summary": "Starts an instance of the service", 'description': ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "404"
        return resp


@app.route('/services/stop', methods=['POST'])
def stop():
    status=ctrl.get_status()
    print('status',status)
    print(ctrl.status_desc[str(status)])
    if status == "200":
        resp = jsonify({"summary": "Stops an instance of the service",
                        'description':ctrl.status_desc[str(status)],
                        "status_code":status})
        resp.status_code = "200"
        return resp
    if status == "202":
        resp = jsonify({"summary": "Stops an instance of the service", 'description':ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "202"
        return resp
    if status == "404":
        resp = jsonify({"summary": "Stops an instance of the service", 'description': ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "404"
        return resp


@app.route('/services/restart', methods=['POST'])
def restart():
    status=ctrl.get_status()
    if status == "200":
        resp = jsonify({"summary": "Restarts an instance of the service", 'description': ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "200"
        return resp
    if status == "202":
        resp = jsonify({"summary": "Restarts an instance of the service", 'description': ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "202"
        return resp
    if status == "404":
        resp = jsonify({"summary": "Restarts an instance of the service", 'description': ctrl.status_desc[str(status)], "status_code":status})
        resp.status_code = "404"
        return resp


@app.route('/services/healtcheck/isalive', methods=['GET'])
def isalive():
    status_run=ctrl.get_status_run()
    # print("status_run",status_run ,type(status_run))
    # print(ctrl.status_desc[str(status_run)])
    if status_run == "200":
        print('in 200')
        resp = jsonify({"summary": "Checks that a service instance is running correctly",
                        'description':"Successful operation.", "status_code":status_run})
        resp.status_code = "200"
        return resp

    if status_run == "404":
        resp = jsonify({"summary": "Checks that a service instance is running correctly",
                        'description':"Service istance not found.","status_code":status_run})
        resp.status_code = "404"
        return resp


if __name__ == "__main__":
    app.run(port=8051)

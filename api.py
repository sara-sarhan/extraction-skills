import os
import urllib.request

from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import predict
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
	print('request.files',request.files)
	uploaded_files = request.files.getlist("file")
	print("uploaded_files.....", uploaded_files)
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		print('file.filename',file.filename)
		filename = secure_filename(file.filename)
		#file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		path = os.getcwd()
		file.save(filename)
		pdfnamepath = os.path.join(path, filename)
		print(pdfnamepath)
		language="Italian"
		category, skillsner = predict.main(pdfnamepath, language)
		resp = jsonify({'job title' :str(category),'skills':str(skillsner)})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp

if __name__ == "__main__":
    app.run(port=8051)

	
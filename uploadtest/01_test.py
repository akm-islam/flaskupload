# chmod 644 01_test.py
from flask import Flask, render_template, request
from werkzeug import secure_filename
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# This is where we set the path
app.config['UPLOAD_PATH']="./upload"
@app.route('/upload')
def upload_file1():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
# request.files conatains (werkzeug.datastructures.FileStorage)  
      for f in request.files.getlist('file'): 
# f.save(arg1 is the path, arg2 is the filename)
         f.save(os.path.join(app.config['UPLOAD_PATH'],  secure_filename(f.filename)))
      return 'file uploaded successfully'
if __name__ == '__main__':
   app.run(debug = True)
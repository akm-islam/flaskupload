# chmod 644 01_test.py
from flask import Flask, render_template, request
from werkzeug import secure_filename
import os
app = Flask(__name__)
app.config['UPLOAD_PATH']="./upload"
@app.route('/upload')
def upload_file1():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      for f in request.files.getlist('file'): 
         f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
      return 'file uploaded successfully'
if __name__ == '__main__':
   app.run(debug = True)
import base64
import json
import os
import requests
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from google.cloud import storage

API_KEY='AIzaSyC7E1Ml0kLAg7A675q9Ib043-iIlyHz3OI'
CAT_BUCKET='19580414-catbucket-2304'
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
  
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
 
 
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'no file'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print 'no filename'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # label the image 
            labels = label_image(filepath, API_KEY)

            # is it a cat?
            for l in labels['labelAnnotations']:
                if l['description'] == 'cat':
                    # put it in the bucket
                    print('Cat!')
                    upload_image(CAT_BUCKET, filepath, file.filename)

            return 'Received: ' + filename + '\n'
                  
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
         <input type=submit value=Upload>
    </form>
    '''
 
def label_image(filepath, apikey):
    with open(filepath, 'rb') as image:
        content = { 'content': base64.b64encode(image.read()).decode('UTF-8') }
    features = []
    features.append({
        'type': 'LABEL_DETECTION',
        'maxResults': 3,
    })
    rqs= []
    rqs.append({
        'features': features,
        'image': content,
    })
    response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=' + apikey, 
            data=json.dumps({ 'requests': rqs }),
            headers={'Content-Type': 'application/json'})
    resp = json.loads(response.text)
    return resp['responses'][0]
    
def upload_image(bucket_name, source_file_name, destination_blob_name):
  """Uploads a file to the bucket."""
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_filename(source_file_name)
  print('File {} uploaded to {}.'.format(
      source_file_name,
      destination_blob_name))
      
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

from typing import TextIO
from flask import Flask, render_template, request, url_for, flash,redirect
from io import TextIOWrapper
from detect_delimiter import detect
from werkzeug.utils import secure_filename
import os, sys
import csv
import numpy as np

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'xyz'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
  """Determines if the file type (extention) is allowed
  """
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Multiple Files
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
      # Fixture
      fixture_file = request.files['file']
      fixture_csv = TextIOWrapper(fixture_file, encoding='utf-8')
      delimiter = detect(fixture_csv.readline())
      fixture_csv.seek(0, 0)
      x = list(csv.reader(fixture_csv, delimiter=delimiter))
      fixture = np.array(x).astype('float')
      print('Name of the Fixture: {}'.format(fixture_file.filename))

      # Plates
      plate_files = request.files.getlist("file[]")
      plates = [] # list of Plate Objects
      for file in plate_files:
        csvFile = TextIOWrapper(file, encoding='utf-8')
        delimiter = detect(csvFile.readline())
        # send fp back to 0
        csvFile.seek(0, 0)
        csv_reader = csv.reader(csvFile, delimiter=delimiter)
        x = list(csv_reader)
        plate = np.array(x).astype('float')
        print('Name of the plate: {}'.format(file.filename))
        plates.append(plate)
    return render_template('index.html')

# end of upload_file()

'''# single files
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # once you get to the file
        if file and allowed_file(file.filename):
          # Getting the filename
          print('Filename: {}'.format(file.filename))
          # Steps for extracting a file from flask and turning into np array
          csvfile = TextIOWrapper(file, encoding='utf-8')
          delimiter = detect(csvfile.readline())
          csvfile.seek(0,0)
          csv_reader = csv.reader(csvfile, delimiter=delimiter)
          x = list(csv_reader)
          fixture = np.array(x).astype("float")
          pass
# end of upload_file()'''

if __name__ == '__main__':
  app.secret_key = 'super secret key'
  app.run(debug = True)
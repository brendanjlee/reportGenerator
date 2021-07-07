from typing import TextIO
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
from io import TextIOWrapper
from detect_delimiter import detect
from werkzeug.utils import secure_filename
import os, sys
import csv
import numpy as np
#
from generator import Generator, read_fixture, read_plates
from pathlib import Path

# Server setup
cwd = os.getcwd()
ALLOWED_EXTENSIONS = {'xyz'}

app = Flask(__name__)

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  # end of allowed_file()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # Process Fixture file into np.array
    fixture_file = request.files['file']
    fixture = read_fixture(fixture_file)

    # Process Plate files into list of np.array
    plate_files = request.files.getlist("file[]")
    plateList = read_plates(plate_files)

    # Create temp directory (cwd/userfiles/..)
    generator_dir = os.path.join(cwd, 'userfiles')
    Path(generator_dir).mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = Generator(fixture=fixture, plateList=plateList, cwd=generator_dir)
    generator.process_plates()

    # Zip files into cwd/reports.zip
    generator.zip_files()

    return redirect('/files/reports.zip')

  return render_template('index.html')
# end of upload_file()

@app.route('/files/<path:path>',methods = ['GET','POST'])
def get_files(path):
  DOWNLOAD_DIRECTORY = os.getcwd()
  """Download a file."""
  try:
      return send_from_directory(DOWNLOAD_DIRECTORY, path, as_attachment=True)
  except FileNotFoundError:
      abort(404)

if __name__ == '__main__':
  app.secret_key = 'super secret key'
  app.run(debug = True)
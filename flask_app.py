from flask import Flask, render_template, request, redirect, send_from_directory, abort
from generator import Generator, read_fixture, read_plates
from pathlib import Path
import os

# Server setup
cwd = os.getcwd()

if os.path.exists('reports.zip'):
  os.remove('reports.zip')
  print('> Deleted Zip File')
else:
  print('> No Zip file to delete')

# Create Flask app
app = Flask(__name__)

def allowed_file(filename):
  """Checks if the filename can be accepted.

  Args:
      filename (string): the filename with extention

  Returns:
      Bool: whether the filetype is supported or not
  """
  ALLOWED_EXTENSIONS = {'xyz'}
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # scanner name
    scanner_name = request.form['username']

    # Process Fixture file into np.array
    fixture_file = request.files['file']
    fixture = read_fixture(fixture_file)

    # Process Plate files into list of np.array
    plate_files = request.files.getlist("file[]")
    plateList = read_plates(plate_files)

    # Create temp directory (cwd/reports/..)
    generator_dir = os.path.join(cwd, 'reports')
    Path(generator_dir).mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = Generator(fixture=fixture, plateList=plateList, cwd=generator_dir, scanner=scanner_name)
    generator.process_plates()

    # Zip files into cwd/reports.zip
    generator.zip_files()

    return redirect('/files/reports.zip')

  return render_template('index.html')

@app.route('/files/<path:path>',methods = ['GET','POST'])
def get_files(path):
  """Returns the processed reports back to the user as a zipped folder.
  """
  DOWNLOAD_DIRECTORY = os.getcwd()
  try:
      return send_from_directory(DOWNLOAD_DIRECTORY, path, as_attachment=True)
  except FileNotFoundError:
      abort(404)

if __name__ == '__main__':
  app.secret_key = 'super secret key'
  app.run(debug = True)
from detect_delimiter import detect
from io import TextIOWrapper
from shutil import rmtree
from pathlib import Path
from plate import Plate
import numpy as np
import zipfile
import csv
import os


class Generator:
  # comes in as np array
  def __init__(self, fixture, plateList, cwd, scanner) -> None:
    """Container that holds methods for calculating the thickness of the plates
    with fixtures.

    Args:
        fixture (np.array): np.array of the fixture XYZ file
        plateList (list of np.array): list of np.arrays of the uploaded plate XYZ files
        cwd (str): current working directory (userfiles)
    """
    self.scanner_name = scanner
    self.fixture = fixture
    self.plateList = plateList # list of Plate objects
    self.cwd = cwd # cwd/userfiles

  def calculate_thickness(self, plate):
    """Calculates and sets the thickness of an individual plate

    Args:
        plate (Plate): Plate object without thickness data

    Returns:
        np.array: 1D array containing thickness measurement at each point
    """
    # Calculate thickness at each point
    thickness = np.subtract(plate.data[:,2], self.fixture[:,2])

    # Set thickness of plate object as well
    plate.thickness_list = thickness
    return thickness

  def set_plate_directory(self, plate):
    """Creates a directory for each plate and adds the path to said directory
    in the invidual plate objects.

    Args:
        plate (Plate): current plate file
    """
    # Sets plate.plate_dir as dir
    # Create a directory: cwd/userfiles/plate_name/ for each plate
    plate_dir = os.path.join(self.cwd, plate.name)
    Path(plate_dir).mkdir(parents=False, exist_ok=True)
    plate.plate_dir = plate_dir
    print('>> Plate Directory Set')

  def process_plates(self):
    """ For every plate that has been uploaded:
          1. Calculate and set thickness
          2. Create and set plate directory
          3. Generate and save csv
          4. Generate and save histogram
          5. Generate and save heatmap
          6. Generate and save report
    """
    print('>> Processing Plates')
    for p in self.plateList:
      # calculate thickness
      self.calculate_thickness(p)

      # set current plate directory
      self.set_plate_directory(p)

      # process figures
      p.generate_csv()
      p.generate_histogram()
      p.generate_heatmap()
      p.generate_report(self.scanner_name)

  def zip_files(self):
    """Zips all of the report files for retur to the user
    """
    print('>> Zipping Files')
    reports_zip = zipfile.ZipFile("reports.zip", "w")
    for dirname, subdirs, files in os.walk(self.cwd):
      for filename in files:
        extention = os.path.splitext(filename)[-1]
        # Save only for pdf reports
        if extention.lower() == '.pdf':
          filePath = os.path.join(dirname, filename)
          reports_zip.write(filePath, os.path.basename(filePath))
    reports_zip.close()

    # delete working directory
    print('current cwd: {}'.format(self.cwd))
    try:
      rmtree(self.cwd)
    except OSError as e:
      print("Error: {}".format(e))

# Global functions
def read_fixture(fixtureFile):
  """Reads in the fixture file and returns it as a 2D matrix

  Returns:
      np.array: The contents of the xyz file as a 2D matrix
  """
  csvFile = TextIOWrapper(fixtureFile, encoding='utf-8')
  delimiter = detect(csvFile.readline())
  csvFile.seek(0, 0)
  x = list(csv.reader(csvFile, delimiter=delimiter))
  fixture = np.array(x).astype('float')
  print('Currently processing: {}'.format(fixtureFile.filename))

  return fixture

def read_plates(plateFilesRequest):
  """Reads in a list of file requests, creates a list of Plate objects for each
  requested file. Each Plate object currently contains (name, 2D matrix of xyz)

  Args:
      plateFilesRequest: List of file requests

  Returns:
      List of Plate: List of plate objects.
  """
  plateList = []
  delimiter = None
  for plateFile in plateFilesRequest:
    plate_csv_file = TextIOWrapper(plateFile, encoding='utf-8')

    # Find delimiter on the first file
    if delimiter is None:
      delimiter = detect(plate_csv_file.readline())
      plate_csv_file.seek(0, 0)

    # Convert file into a list
    x = list(csv.reader(plate_csv_file, delimiter=delimiter))
    plate_data = np.array(x).astype('float')

    # Create Plate object and append to plateList
    curr_plate = Plate(plate_data, os.path.splitext(plateFile.filename)[0])
    plateList.append(curr_plate)

  return plateList

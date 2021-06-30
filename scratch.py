import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from detect_delimiter import detect
from csv import reader

def resource_path(relative_path):
    """Gets the relative path of a file\n
    Args:
        relative_path (str): path to the file
    Returns:
        str: the full path of the file that was passed in
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


f = open(resource_path('example.xyz'))
delimniter = (detect(f.readline()))

plate = np.genfromtxt(resource_path('example.xyz'), delimiter=delimniter)
fixture = np.genfromtxt(resource_path('fixture.xyz'), delimiter=delimniter)

# try processing thickness
thickness = np.subtract(plate, fixture)
# print(thickness[0][2])


# no paths, come in as np array
class Processor:
  def __init__(self, fixture_path, plates_dir) -> None:
      pass

  def get_thickness(self, fixture, plate):
    pass

class Plate:
  def __init__(self, plate_array, name) -> None:
    self.plate_array = plate_array
    self.name = name
    pass
from plate import Plate, resource_path
# test imports
import numpy as np
import os, sys
from detect_delimiter import detect

class Generator:
  # comes in as np array
  def __init__(self, fixture_array) -> None:
    self.fixture = fixture_array[0: , 2]
    self.plates = [] # list of Plate objects

  def set_plates(self, plate_arr):
    for p in plate_arr:
      currPlate = Plate(p)
      self.get_plate_thickness(currPlate)
      self.plates.append(currPlate)


  def process_plates(self):
    # TODO set up some working directory here
    for plate in self.plates:
      # get csv
      plate.generate_csv()
      plate.generate_histogram()
      plate.generate_heatmap()
      print('nice')


  # this one also sets the plate thickness
  def get_plate_thickness(self, plate_arr):
    z = plate_arr.data[0: ,2]
    thickness =  np.subtract(z, self.fixture)
    plate_arr.set_thickness(thickness)
    return thickness

############## Testing Area ##############
f = open(resource_path('example.xyz'))
delimniter = (detect(f.readline()))

plate_arr = np.genfromtxt(resource_path('example.xyz'), delimiter=delimniter)
fixture_arr = np.genfromtxt(resource_path('fixture.xyz'), delimiter=delimniter)

# Get plate
p1 = Plate(plate_arr, 'example')
# Put all plates into a lsit
plate_obs = []
plate_obs.append(p1)
# init generator
generator = Generator(fixture_arr)
# feed generator plates
generator.set_plates(plate_obs)
print(len(generator.plates))
generator.process_plates()
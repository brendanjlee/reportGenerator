import os
import sys
import numpy as np
from math import floor, ceil
import matplotlib.pyplot as plt
from detect_delimiter import detect
from reportlab.pdfbase.pdfdoc import PDFStreamFilterBase85Encode
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
from datetime import date

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

class Plate:
  # plate comes in as np array
  def __init__(self, plate_array, plate_name=None) -> None:
    self.name = 'plate'
    if plate_name is not None:
      self.name = plate_name
    self.data = plate_array
    self.thickness_list = None
    self.csvFile = None
    self.histogram = None
    self.heatmap = None
    self.report = None

  def set_thickness(self, thickness_list):
    self.thickness_list = thickness_list

  def get_stddev(self):
    if self.thickness_list is None:
      print('Calculate thickness first')
      return
    return np.std(self.thickness_list)

  def get_mean(self):
    if self.thickness_list is None:
      print('Calculate thickness first')
      return
    return np.mean(self.thickness_list)

  def generate_csv(self):
    if self.thickness_list is None:
      print('Calculate thickness first')
      return

    cols = 11
    rows = ceil((len(self.thickness_list)) / cols)
    file_content = ''
    loc = 0

    # Write content
    for i in range(rows):
      currline = ''
      for j in range(cols):
        if loc == len(self.thickness_list):
          break
        currline += str('%.3f' % self.thickness_list[loc])
        if j < (cols - 1):
          currline += ','
        elif j == (cols - 1):
          currline += '\n'
        loc += 1
      file_content += currline

    # add newline if CSV was cut short from missing data
    if file_content[-1] != '\n':
      file_content += '\n'

    # Find mean and stddev
    file_content += ('Thickness_Mean, {}\n'.format(self.get_mean()))
    file_content += ('Thickness_StdDev, {}'.format(self.get_stddev()))

    self.csvFile = file_content
    return file_content

  def generate_histogram(self):
    if self.thickness_list is None:
      print('Calculate thickness first')
      return

    count, bins = np.histogram(self.thickness_list)
    fig = plt.hist(bins[:-1], bins, weights=count, ec='black')
    plt.xlabel('mm')
    plt.ylabel('frequency')
    plt.title('Distribition of Thickness')
    plt.show()
    # TODO find a way to return object

  def generate_heatmap(self):
    if self.thickness_list is None:
      print('Calculate thickness first')
      return

    # Set up contraints
    cols = 11
    rows = ceil((len(self.thickness_list)) / cols)

    # TODO determine if Z will be a list or nparr
    # it's actually already a np arr for now
    z = self.thickness_list


    x = list(range(1, cols + 1))
    y = list(range(1, rows + 1))
    Z = z.reshape(-1, cols)
    X, Y = np.meshgrid(x, y)

    # Generate Heatmap
    cont = plt.contourf(X,Y,Z, cmap='jet', vmin=np.min(Z), vmax=np.max(Z))
    plt.colorbar(label='mm')
    plt.scatter(X, Y, marker=".", c='black')
    plt.show()              # uncomment to see the graph instead of saving it
    # TODO figure out a way to return as object and save to self

  def generate_report(self, scanner_name):
    # Paths
    reportPath = resource_path(self.name + '.pdf')
    heatmap_fullpath = ''
    histo_fullpath = ''

    # Create canvas
    can = canvas.Canvas(reportPath, pagesize=letter) # 612, 729
    w, h = letter
    left_margin = inch

    # Page 1
    # Prelim report string write
    can.setFont("Times-Bold", 16)
    can.drawString(left_margin, 680, "Report on {}".format(self.name))

    # Purdue Logo
    im = Image.open(resource_path('purdue_logo.png'))
    can.drawInlineImage(im, 20, 740, width=100.44, height=30)

    # Fermi Logo
    im = Image.open(resource_path('fermi_logo.png'))
    can.drawInlineImage(im, 173, 740, width=100, height=41)

    # CMS Logo
    im = Image.open(resource_path('cms_logo.png'))
    can.drawInlineImage(im, 326, 720, width=70, height=70)

    # CMSC Logo
    im = Image.open(resource_path('cmsc_logo.png'))
    can.drawInlineImage(im, 461, 720, width=90, height=90)

    # Write Date
    today = date.today()
    today = today.strftime("%m/%d/%Y")
    can.setFont('Times-Roman', 12)
    can.drawString(left_margin, 650, today)

    # Write Name
    can.drawString(left_margin, 630, scanner_name)

    # Write layup
    can.drawString(
        left_margin, 600, 'The plate was laid up and cured and post cured as'
                        + 'per the manufacturer recommended procedure.')
    can.drawString(
        left_margin, 590, 'It was then measured on a Hexagon coordinate'
                        + 'measuring machine for the thickness measurements')

    # Write Units
    can.setFont('Times-Bold', 12)
    can.drawString(left_margin, 550, "Units in mm")

    # Enter heatmap
    # TODO figure out what to do with this
    im = Image.open(heatmap_fullpath)
    can.drawInlineImage(im, 40, 300, 280, 210)

    # Enter Histogram
    # TODO figure out graph saving
    im = Image.open(histo_fullpath)
    can.drawInlineImage(im, w/2, 300, 230, 230)

    # Statistics
    can.setFont('Times-Bold', 14)
    can.drawString(left_margin, 260, "Statistics")

    avg_str = '%.3f' % self.get_mean()
    std_str = '%.3f' % self.get_stddev()
    data = [["Average Thickness: ", avg_str], [
        "Thickness Standard Deviation: ", std_str]]
    t = Table(data)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    t.wrapOn(can, 0, 0)
    t.drawOn(can, left_margin, h/4)

    # Page 2
    can.showPage()

    # Print Plate name again
    # TODO Figure filename: self.name was filename
    can.setFont('Times-Bold', 16)
    can.drawCentredString(
        w/2, 730, "11x11 Thickness Measurements for " + self.name)

    # print units
    can.setFont('Times-Bold', 12)
    can.drawCentredString(w/2, 700, "Units in mm")

    # Get table
    # TODO rewrite to get it working or string or file
    '''with open(csv_fullpath, 'r') as read_obj:
        csv_reader = reader(read_obj)
        values = list(csv_reader)
        values = values[:len(values) - 2]
        t = Table(values)
        t.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        t.wrapOn(can, 0, 0)
        t.drawOn(can, 110, h/2)'''

    # TODO save to self
    can.save()


############## Testing Area ##############
f = open(resource_path('example.xyz'))
delimniter = (detect(f.readline()))

plate_arr = np.genfromtxt(resource_path('example.xyz'), delimiter=delimniter)
fixture_arr = np.genfromtxt(resource_path('fixture.xyz'), delimiter=delimniter)

plate_name = os.path.splitext("example.xyz")[0]

p1 = Plate(plate_arr, plate_name)

p1.thickness_list = (plate_arr[0: , 2]) # index by slicing
thic = p1.thickness_list

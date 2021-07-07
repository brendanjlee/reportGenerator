import matplotlib
matplotlib.use('Agg') # run matplotlib on thread
import matplotlib.pyplot as plt
import os, sys
import numpy as np
from math import ceil
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
from datetime import date
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

class Plate:
  def __init__(self, plate_data, plate_name=None) -> None:
    """Creates a plate object that stores the measurements and methods for each
    individual plate.

    Args:
        plate_data (np.array): np.array of the xyz file
        plate_name (string, optional): Name of the plate (no extention).
    """
    self.name = 'plate'
    if plate_name is not None:
      self.name = plate_name  # name without extention

    self.data = plate_data
    self.thickness_list = None
    self.plate_dir = None # current working dir of plate: cwd(root)/userfiles/plate_name/

    # Absolute Paths to saved files
    self.csv_path = None
    self.histogram_path = None
    self.heatmap_path = None
    self.report = None

  def set_thickness(self, thickness_list):
    # Sets the current thickness
    self.thickness_list = thickness_list

  def get_stddev(self):
    if self.thickness_list is None:
      print('Calculate thickness first')
      return
    return np.std(self.thickness_list)

  def get_mean(self):
    if self.thickness_list is None:
      print('>>> Calculate thickness first')
      return
    return np.mean(self.thickness_list)

  def generate_csv(self):
    """Generates a csv file based on the thickness measurement of the current
    plate.

    Returns:
        string: path to the csv file
    """
    if self.thickness_list is None:
      print('>>> Calculate thickness first')
      return

    # Set up constraints
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

    # save to csv file
    csvPath = os.path.join(self.plate_dir, self.name + '_csv.csv')
    f = open(csvPath, 'w')
    f.write(file_content)
    f.close()

    self.csv_path = csvPath
    return file_content

  def generate_histogram(self):
    """Generates a histogram using matplotlib and saves it as a png image

    Returns:
        string: path to the histogram
    """
    if self.thickness_list is None:
      print('>>> Calculate thickness first')
      return

    count, bins = np.histogram(self.thickness_list)
    fig = plt.hist(bins[:-1], bins, weights=count, ec='black')
    plt.xlabel('mm')
    plt.ylabel('frequency')
    plt.title('Distribition of Thickness')

    # TODO find a way to return object
    # save to png file
    histoPath = os.path.join(self.plate_dir, self.name + '_hist.png')
    plt.savefig(histoPath)
    plt.clf()

    print('>>> Histogram Generated')
    self.histogram_path = histoPath
    return histoPath

  def generate_heatmap(self):
    """Generates a heatmap using matplotlib and saves it as a png image

    Returns:
        string: path to the heatmap
    """
    if self.thickness_list is None:
      print('>>> Calculate thickness first')
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
    plt.gca().set_aspect('equal')
    plt.colorbar(label='mm')
    plt.scatter(X, Y, marker=".", c='black')

    # save to png file
    heatPath = os.path.join(self.plate_dir, self.name + '_heat.png')
    plt.savefig(heatPath)
    plt.clf()

    print('>>> Heatmap Generated')
    self.heatmap_path = heatPath
    return heatPath

  # TODO also take in scanner name
  def generate_report(self, scanner_name='Brendan'):
    """Generates a PDF report of the current plate. Uses all generated figures
    to print onto the PDF. Check ReportLabs documentation to modify to the
    format of the file

    Args:
        scanner_name (str): Name of Scanner.
    """
    #reportPath = resource_path(self.name + '.pdf')
    reportPath = os.path.join(self.plate_dir, self.name + '.pdf')
    heatmap_fullpath = self.heatmap_path
    histo_fullpath = self.histogram_path
    csv_fullpath = self.csv_path

    # Create canvas
    can = canvas.Canvas(reportPath, pagesize=letter) # 612, 729
    w, h = letter
    left_margin = inch

    # Page 1
    # Prelim report string write
    can.setFont("Times-Bold", 16)
    can.drawString(left_margin, 680, "Report on {}".format(self.name))

    # Purdue Logo
    im = Image.open(resource_path('logos/purdue_logo.png'))
    can.drawInlineImage(im, 20, 740, width=100.44, height=30)

    # Fermi Logo
    im = Image.open(resource_path('logos/fermi_logo.png'))
    can.drawInlineImage(im, 173, 740, width=100, height=41)

    # CMS Logo
    im = Image.open(resource_path('logos/cms_logo.png'))
    can.drawInlineImage(im, 326, 720, width=70, height=70)

    # CMSC Logo
    im = Image.open(resource_path('logos/cmsc_logo.png'))
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
    with open(csv_fullpath, 'r') as read_obj:
        csv_reader = reader(read_obj)
        values = list(csv_reader)
        values = values[:len(values) - 2]
        t = Table(values)
        t.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        t.wrapOn(can, 0, 0)
        t.drawOn(can, 110, h * 0.25)

    # TODO save to self
    print('>>> Report Generated')
    can.save()
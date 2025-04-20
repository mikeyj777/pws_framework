import os

class Tables:

  def __init__(self):
    self.path = os.path.join(os.path.dirname(__file__), 'csvs/')
    self.cheminfo = self.path + 'cheminfo.csv'
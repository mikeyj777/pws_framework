from modeling.main import Main

class Interface:
  def __init__(self):
    pass
  def set_inputs(self, press_pa = 2*101325, temp_k = 350, hole_size_m = 0.1, elevation_m = 0, release_angle_rad = 0, chem_list = ['ammonia'], composition = [1], composition_is_molar = False, release_quantity_kg = 100):
    self.press_pa = press_pa
    self.temp_k = temp_k
    self.hole_size_m = hole_size_m
    self.elevation_m = elevation_m
    self.release_angle_rad = release_angle_rad
    self.chem_list = chem_list
    self.composition = composition
    self.composition_is_molar = composition_is_molar
    self.release_quantity_kg = release_quantity_kg

  def run():
    pass
from modeling.main import Main

class Interface:
  def __init__(self):
    self.inputs = {}

  def set_inputs(self, press_pa = 2*101325, temp_k = 350, hole_size_m = 0.1, elevation_m = 0, release_angle_rad = 0, chem_list = ['ammonia'], composition = [1], composition_is_molar = False, release_quantity_kg = 100):
    
    self.inputs['press_pa'] = press_pa
    self.inputs['temp_k'] = temp_k
    self.inputs['hole_size_m'] = hole_size_m
    self.inputs['elevation_m'] = elevation_m
    self.inputs['release_angle_rad'] = release_angle_rad
    self.inputs['chem_list'] = chem_list
    self.inputs['composition'] = composition
    self.inputs['composition_is_molar'] = composition_is_molar
    self.inputs['release_quantity_kg'] = release_quantity_kg

  def run():
    
    main = Main()

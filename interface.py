from modeling.main import Main

class Interface:
  def __init__(self):
    self.inputs_dict = {}

  def set_inputs(self, press_pa = 2*101325, temp_k = 350, hole_size_m = 0.1, elevation_m = 0, release_angle_rad = 0, chem_mix = ['50-00-0'], molar_composition = [1], release_mass_kg = 100, release_volume_m3 = None, containment_area_m2 = None, log_handler = print):
    
    self.inputs_dict['press_pa'] = press_pa
    self.inputs_dict['temp_k'] = temp_k
    self.inputs_dict['hole_size_m'] = hole_size_m
    self.inputs_dict['elevation_m'] = elevation_m
    self.inputs_dict['release_angle_rad'] = release_angle_rad
    self.inputs_dict['chem_mix'] = chem_mix
    self.inputs_dict['molar_composition'] = molar_composition
    self.inputs_dict['mass_kg'] = release_mass_kg
    self.inputs_dict['volume_m3'] = release_volume_m3
    self.inputs_dict['containment_area_m2'] = containment_area_m2
    self.inputs_dict['log_handler'] = log_handler


  def run():
    
    main = Main()

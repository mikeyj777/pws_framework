import json

from pypws.enums import ResultCode

from modeling.main import Main
from data.exceptions import Exceptions


class Interface:
  def __init__(self):
    self.inputs_dict = {}
    self.main = None

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


  def run(self):
    
    self.main = Main()
    if self.main.run(app_inputs=self.inputs_dict) != ResultCode.SUCCESS:
      raise Exception(Exceptions.unspecified_error)
    self.data_dict_of_dfs = self.main.data
    self.data_dict_of_list_of_dicts = self.main.dispersion_calc.footprints_conc_elev_z_x_y_list
    self.data = json.dumps(self.data_dict_of_list_of_dicts)
    return ResultCode.SUCCESS
    
def tester():
  interface = Interface()
  # interface.set_inputs(
  #   press_pa=(0.01+14.6959)/14.6959 * 101325,
  #   temp_k=73.15 + 273.15,
  #   chem_mix=['121-44-8', '67-56-1'],
  #   molar_composition=[0.5, 0.5],
  # )

  interface.set_inputs(
    press_pa=(100+14.6959)/14.6959 * 101325,
    temp_k=73.15 + 273.15,
    chem_mix=['7782-50-5'],
    molar_composition=[1],
  )

  res = interface.run()
  if res != ResultCode.SUCCESS or interface.main.data is None:
    raise Exception(Exceptions.dispersion_calc_failed)
  
  data = interface.main.data

  apple = 1

if __name__ == '__main__':
  tester()

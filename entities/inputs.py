from data.exceptions import Exceptions
from entities.prep import material, state, get_flash_result

class Inputs:

  def __init__(self):
    self.flash_result = None
    self.material = None

  def set_values(self, inputs):
    for k, v in inputs.items():
      setattr(self, k, v)
    self.get_properties()

  def get_properties(self):
    self.material = material(self)
    self.state = state(self)
    self.flash_result = get_flash_result(self)
    self.set_release_mass_or_volume()

  def set_release_mass_or_volume(self):
    dens_kg_m3 = self.flash_result.total_fluid_density
    if dens_kg_m3 <= 0 or dens_kg_m3 > 1e10:
      self.log_handler(f'\n\n\n***\n\n\nFlash Calculation did not provide correct density results')
      raise Exception(Exceptions.flash_calc_failed)
    
    mass_kg = 0
    if hasattr(self, "mass_kg"):
      if self.mass_kg is not None:
        if self.mass_kg > 0:
          mass_kg = self.mass_kg
    
    if not hasattr(self, "volume_m3") and mass_kg > 0:
      self.volume_m3 = mass_kg / dens_kg_m3
    
    if hasattr(self, "volume_m3") and mass_kg <= 0:
      self.mass_kg = self.volume_m3 * dens_kg_m3

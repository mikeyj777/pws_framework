import os
import sys
import math

from pypws.calculations import VesselStateCalculation, State
from pypws.entities import Leak, Vessel, VesselShape, VesselConditions
from pypws.enums import ResultCode

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.exceptions import Exceptions

def vessel(inputs):
  material = inputs.material
  state = inputs.state
  vessel_state_calc = VesselStateCalculation(material=material, material_state = state)
  if vessel_state_calc.run() != ResultCode.SUCCESS:
    inputs.log_handler(f'\n\n\n***\n\n\nVessel State Calculation did not complete.  Messages:\n\n\n{vessel_state_calc.messages}')
    raise Exception(Exceptions.vessel_leak_state_model_failure)
  state = vessel_state_calc.output_state
  
  ll = get_liquid_level(results=inputs.flash_result)
  vol = inputs.volume_m3
  l_by_d = 1
  d = math.sqrt(4*vol / math.pi / l_by_d) ^ (1/3)
  l = d * l_by_d

  vessel = Vessel(state=vessel_state_calc.output_state, shape=VesselShape.VERTICAL_CYLINDER, vessel_conditions=vessel_state_calc.vessel_conditions, liquid_fill_fraction_by_volume=ll)

def get_liquid_level(results):
  
  liq_dens_kg_m3 = results.liquid_density
  vap_dens_kg_m3 = results.vapour_density
  liquid_spec_volume = 0
  if liq_dens_kg_m3 > 0 and liq_dens_kg_m3 < 1e10:
    liquid_spec_volume = 1 / liq_dens_kg_m3
  vapor_spec_volume = 0
  if vap_dens_kg_m3 > 0 and vap_dens_kg_m3 < 1e10:
    vapor_spec_volume = 1 / vap_dens_kg_m3
  liq_mass_fract = results.liquid_mass_fraction
  vap_mass_fract = 1 - liq_mass_fract
  liquid_volume_m3 = liquid_spec_volume * liq_mass_fract
  vapor_volume_m3 = vapor_spec_volume * vap_mass_fract
  ll = 0
  if liquid_volume_m3 + vapor_volume_m3 > 0:
    ll = liquid_volume_m3 / (liquid_volume_m3 + vapor_volume_m3)
  return ll


class Inputs:
  def __init__(self):
    pass

def main():
  inputs = Inputs()
  inputs.chem_mix = ['50-00-0']
  inputs.molar_composition = [1]
  inputs.temp_k = 298.15
  inputs.press_pa = 101325
  from entities.prep import material
  inputs.material = material(inputs=inputs)
  inputs.state = State(pressure=inputs.press_pa, temperature= inputs.temp_k, liquid_fraction=None)
  vessel(inputs=inputs)


if __name__ == '__main__':
  main()
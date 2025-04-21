import os
import sys
import math

from pypws.calculations import VesselStateCalculation, State
from pypws.entities import Leak, Vessel, VesselShape, VesselConditions, LocalPosition, Leak
from pypws.enums import ResultCode

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.exceptions import Exceptions
from interface import Interface
from entities.inputs import Inputs

def vessel_and_leak(inputs):
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
  d = (4*vol / math.pi / l_by_d) ** (1/3)
  l = d * l_by_d

  # set leak point slightly below any liquid level.  this will ensure proper phase designation.
  hole_height_fraction = ll * 0.99
  leak_height_above_btm_of_tank = l * hole_height_fraction
  elev_m = inputs.elevation_m
  # set elevation of bottom of tank such that the hole size is at the stated elevation from the inputs
  z = elev_m - leak_height_above_btm_of_tank
  tank_position = LocalPosition(z = z)

  vessel = Vessel(
    state = state,
    material = material, 
    location = tank_position,
    diameter = d,
    height = l,
    shape = VesselShape.VERTICAL_CYLINDER,
    vessel_conditions = vessel_state_calc.vessel_conditions,
    liquid_fill_fraction_by_volume = ll
  )

  leak = Leak(hole_diameter=inputs.hole_size_m, release_angle=inputs.release_angle_rad, hole_height_fraction = hole_height_fraction, release_elevation=elev_m)

  return (vessel, leak)

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


def main():
  interface = Interface()
  interface.set_inputs(temp_k=250.15)
  inputs = Inputs()
  inputs.set_values(inputs_dict=interface.inputs_dict)
  vessel, leak = vessel_and_leak(inputs=inputs)

if __name__ == '__main__':
  main()
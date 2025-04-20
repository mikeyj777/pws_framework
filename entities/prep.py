import math
import pandas as pd

from pypws.entities import Weather, Substrate, Bund, Material, MaterialComponent
from pypws.enums import AtmosphericStabilityClass, WindProfileFlag
from pypws.materials import get_component_by_id

from data.tables import Tables

def material(inputs):
  chems = inputs.chem_mix
  molfs = inputs.molar_composition
  cheminfo = pd.read_csv(Tables().cheminfo)
  mat = Material(name = 'Release Components', components=[])
  for i in range(len(chems)):
    mc:MaterialComponent
    cas_no = chems[i]
    molf = molfs[i]
    row = cheminfo[cheminfo[cas_no] == cas_no]
    id = row['id'].values[0]
    comp = get_component_by_id(id=id)
    comp.mole_fraction = molf
    mat.components.append(comp)
  mat.component_count = len(mat.components)

  return material

def weather():
  wx = Weather()
  wx.stability_class = AtmosphericStabilityClass.STABILITY_F
  wx.wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE
  wx.wind_speed = 1.5
  wx.solar_radiation = 0

  return wx

def substrate(inputs):
  containment_area = inputs.containment_area_m2
  v = inputs.volume_m3
  elev = inputs.elevation_m

  bund = Bund()
  if containment_area is not None:
    if isinstance(containment_area, (int, float, complex)) and not isinstance(containment_area, bool):
      if containment_area > 0:
        bund.specify_bund = True
        d = math.sqrt(4*containment_area/math.pi)
        h = v / d
        h = max(h, elev + 10)
        bund.bund_diameter = d
        bund.bund_height = h
  
  substrate = Substrate(bund=bund)

  return substrate


class Inputs:
  def __init__(self):
    pass

def main():
  inputs = Inputs()
  inputs.chem_mix = ['50-00-0']
  inputs.molar_composition = [1]
  mat = material(inputs=inputs)
  apple = 1

if '__name__' == '__main__':
  main()
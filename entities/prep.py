import math

from pypws.entities import Weather, Substrate, Bund
from pypws.enums import AtmosphericStabilityClass, WindProfileFlag
from pypws.materials import get_component_by_id

def material(inputs):
  chems = inputs.chem_mix



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



from pypws.entities import MaterialComponent, Material

def get_vapor_phase_composition(discharge):
  vlc = discharge.vlc
  fin_state = vlc.discharge_records[0].final_state

  lf = fin_state.liquid_fraction
  if lf == 0:
    return discharge.inputs.molar_composition
  temp_k = fin_state.temperature
  vps = get_vapor_pressures(inputs=discharge.inputs, temp_k=temp_k)
  
def get_vapor_pressures(inputs, temp_k):
  material:Material = inputs.material
  mc:MaterialComponent
  vps = []
  for mc in material.components:
    for di in mc.data_item:
      if di.description == "vapourPressure":
        vps.append({
          "cas_id": mc.cas_id,
          "vp_consts": di.equation_coefficients,
          "calculation_limits": di.calculation_limits,
          "equation_number": di.equation_number,
          "equation_string": di.equation_string
        })

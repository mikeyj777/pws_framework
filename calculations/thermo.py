import numpy as np

from pypws.entities import MaterialComponent, Material

from calculations.dippr_eqns import dippr_eqn_101

def get_vapor_phase_composition(discharge):
  vlc = discharge.vlc
  fin_state = vlc.discharge_records[0].final_state

  lf = fin_state.liquid_fraction
  if lf == 0:
    return discharge.inputs.molar_composition
  temp_k = fin_state.temperature
  vps = get_vapor_pressures_pa(inputs=discharge.inputs, temp_k=temp_k)
  ks = []
  k_times_zi = []
  for i in range(len(vps)):
    k = min(vps[i] / discharge.inputs.press_pa, 100) 
    ks.append(k)
    k_times_zi.append(k * discharge.inputs.molar_composition[i])

  args = {
    'molfs': discharge.inputs.molar_composition,
    'ks': ks
  }

  # test for subcooled condition (vf = 0)
  rr_sum_vf_0 = get_rachford_rice_sum(0, args)

  rr_sum_vf_1 = get_rachford_rice_sum(1, args)

  if abs(rr_sum_vf_0) < 1e-6 or (rr_sum_vf_0 < 0 and rr_sum_vf_1 < 0):
    # saturated or subcooled liquid.  use vapor pressure for vapor phase
    ys = np.array(k_times_zi)
    ys /= ys.sum()
    return ys

  if abs(rr_sum_vf_1) < 1e-6 or (rr_sum_vf_0 > 0 and rr_sum_vf_1 > 0):
    # saturated or superheated vapor.  use vapor pressure for vapor phase
    return discharge.inputs.molar_composition
  
  
  
  
def get_rachford_rice_sum(vap_fract, args):
  molfs = args['molfs']
  ks = args['ks']
  sum = 0
  for i in range(len(molfs)):
    sum += rachford_rice_eqn(vap_fract, molfs[i], ks[i])

def rachford_rice_eqn(vf, molf, k):
  return (molf * (k - 1)) / (1 + vf * (k - 1))

def get_vapor_pressures_pa(inputs, temp_k):
  material:Material = inputs.material
  mc:MaterialComponent
  vps = []
  for mc in material.components:
    molf = mc.mole_fraction
    for di in mc.data_item:
      if di.description == "vapourPressure":
        # vps.append({
        #   "cas_id": mc.cas_id,
        #   "vp_consts": di.equation_coefficients,
        #   "calculation_limits": di.calculation_limits,
        #   "equation_number": di.equation_number,
        #   "equation_string": di.equation_string
        # })
        vp_pa = dippr_eqn_101(di.equation_coefficients, temp_k)
        vps.append(molf * vp_pa)
  return vps

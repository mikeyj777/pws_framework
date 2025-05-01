import numpy as np

from pypws.entities import MaterialComponent, Material

from calculations.dippr_eqns import dippr_eqn_101
from helpers.secant_solver_with_bisect import Solver

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
    if ys.sum() != 0:
      ys /= ys.sum()
    return ys

  if abs(rr_sum_vf_1) < 1e-6 or (rr_sum_vf_0 > 0 and rr_sum_vf_1 > 0):
    # saturated or superheated vapor.  use vapor pressure for vapor phase
    return discharge.inputs.molar_composition

  solver = Solver(
    f=get_rachford_rice_sum,
    args=args,
    x0=0.5,
    dx=0.01,
    target=0,
    max_iter=100,
    bisect_min_max=[0, 1],
    f_increases_with_x=False
  )
  
  if not solver.solve():
    raise ValueError("Rachford-Rice solver failed to converge.")

  vf = solver.answer
  zs = discharge.inputs.molar_composition
  ks = np.array(ks)
  xs = np.array(zs / (1 + vf * (ks - 1)))
  ys = xs * ks
  if ys.sum() != 0:
    ys /= ys.sum()
  return ys.tolist()

def get_rachford_rice_sum(vap_fract, args):
  molfs = args['molfs']
  ks = args['ks']
  sum = 0
  for i in range(len(molfs)):
    sum += rachford_rice_eqn(vap_fract, molfs[i], ks[i])
  return sum

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
        vps.append(vp_pa)
  return vps

def get_threshold_concs(inputs, cheminfo, vapor_phase_composition):
  # for mixtures of chemicals, get the threshold concentrations for each chemical in the mixture
  # this uses the vapor phase composition and the toxicity limits from the cheminfo table
  shi_idx = -1
  max_shi = 0
  lel_inv = 0
  lel = 0
  tox_values = {
    1: None,
    2: None,
    3: None
  }
  for i in range(len(inputs.chem_mix)):
    cas = inputs.chem_mix[i]
    if cas in cheminfo['cas_no'].values:
      erpg_3 = cheminfo.loc[cheminfo['cas_no'] == cas, 'erpg_3'].values[0]
      if erpg_3 > 0 and erpg_3 < 1e6:
        shi = float(vapor_phase_composition[i] / erpg_3)
        if shi > max_shi:
          max_shi = shi
          shi_idx = i
      lel_comp = cheminfo.loc[cheminfo['cas_no'] == cas, 'lel'].values[0]
      if lel_comp > 0 and lel < 1e6:
        lel_inv += float(vapor_phase_composition[i] / lel_comp)
  
  if shi_idx >= 0:
    fract = vapor_phase_composition[shi_idx]
    for i in range(3,0,-1):
      tox_value = cheminfo.loc[cheminfo['cas_no'] == cas, f'erpg_{i}'].values[0]
      if tox_value > 0 and tox_value < 1e6:
        tox_values[i] = float(tox_value / fract)
      if tox_values[i] is None and (i + 1) in tox_values and tox_values[i + 1] is not None:
        # in some cases, an erpg_3 will be available while an erpg_2 is not.  In this case, we can use the erpg_3 value to calculate the erpg_2 value.
        # the difference is estimated as a factor of 7.  
        tox_values[i] = tox_values[i + 1] / 7
        

  if lel_inv > 0:
    lel = 1 / lel_inv
  
  tox_keys_sorted = sorted(list(tox_values.keys()))


  return {
    'flammable': [0.25 * lel, 0.5 * lel, lel],
    'toxic': [tox_values[k] for k in tox_keys_sorted],
  }



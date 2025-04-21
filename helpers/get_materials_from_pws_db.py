import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypws.materials import get_dnv_components, get_component_by_id
from pypws.entities import Material, MaterialComponent

def get_pws_materials():
  mats = get_dnv_components()
  return mats

def parse_data_for_export(mats):
  out = []
  for mat in mats:
    a = str(mat.cas_id)
    out.append({
      'cas_id': mat.cas_id,
      'cas_no':  f"{a[:-3]}-{a[-3:-1]}-{a[-1]}",
      'chem_name': mat.name,
      'id': str(mat.id),
    })
  return out

def export_csv(chems_list_of_dicts):
  df = pd.DataFrame(chems_list_of_dicts)
  df.to_csv("cheminfo.csv", index=False)

def get_erpg_and_lel_data():
  chems_db = pd.read_csv('chems_db.csv')
  chems_db = chems_db[['cas_no', 'erpg_1', 'erpg_2', 'erpg_3', 'aegl_1_60_min', 'aegl_2_60_min', 'aegl_3_60_min', 'lel']]
  cheminfo = pd.read_csv('data/cheminfo.csv')
  merged = pd.merge(cheminfo, chems_db, on="cas_no")
  merged.to_csv('cheminfo_with_tox_and_flam.csv')

def get_vp_data(mats):
  vps = []
  for mc in mats:
    vps_found = False
    comp = get_component_by_id(str(mc.id))
    for di in comp.data_item:
      if di.description == "vapourPressure":
        vps_found = True
        vps.append({
          "cas_id": mc.cas_id,
          "vp_consts": di.equation_coefficients,
          "calculation_limits": di.calculation_limits,
          "equation_number": di.equation_number,
          "equation_string": di.equation_string
        })
    if not vps_found:
      print(f"vps not available for {mc.display_name} | cas id: {mc.cas_id}")
  return vps

def main():
  mats = get_pws_materials()
  vps = get_vp_data(mats)
  vps_df = pd.DataFrame(vps)
  vps_df.to_csv("vp_data.csv")
  apple = 1

if __name__ == '__main__':
  main()
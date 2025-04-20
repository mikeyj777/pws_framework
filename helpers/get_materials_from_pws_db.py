import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypws.materials import get_dnv_components

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
  apple = 1

def main():
  # cas_ids = get_all_cas_ids()
  # mat_ids = get_materials_from_cas_ids(cas_ids)
  # chem_names = get_chem_names(mat_ids)
  # export_csv(cas_ids, chem_names)
  get_erpg_and_lel_data()

  apple = 1

if __name__ == '__main__':
  main()
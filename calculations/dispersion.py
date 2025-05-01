import numpy as np
import pandas as pd

from pypws.calculations import DispersionCalculation, DistancesAndFootprintsToConcentrationLevelsCalculation
from pypws.entities import DispersionParameters, DispersionOutputConfig
from pypws.enums import ResultCode, Resolution, ContourType

from data.tables import Tables
from calculations.thermo import get_threshold_concs
from entities.prep import weather, substrate
from data.exceptions import Exceptions

class Dispersion:

  def __init__(self, vapor_phase_composition, discharge_data_vlc, inputs):
    self.vapor_phase_composition = vapor_phase_composition
    self.inputs = inputs
    self.vlc = discharge_data_vlc
    self.threshold_concs_ppm = None
    self.cheminfo = pd.read_csv(Tables().cheminfo)
    self.weather = None
    self.substrate = None
    self.dispersion_calc = None
    self.distsAndFootprintsCalc = None
    self.post_process_results = {
      "flammable": None,
      "toxic": None,
    }
  
  def run(self) -> ResultCode:
    self.get_limits()
    self.get_entities()
    for hazard in ["flammable", "toxic"]:
      if self.threshold_concs_ppm[hazard][0] is None or self.threshold_concs_ppm[hazard][0] <= 0 or self.threshold_concs_ppm[hazard][-1] >= 1e6:
        continue
      disp_params = self.get_dispersion_parameters(hazard_type=hazard)
      self.run_dispersion_calculation(disp_params=disp_params, hazard_type=hazard)
      self.run_post_processing_calcs(hazard_type=hazard)
    return ResultCode.SUCCESS
  
  def get_limits(self):
    # Get the flammable limits and toxicity limits from the vapor phase composition
    self.threshold_concs_ppm = get_threshold_concs(
      inputs=self.inputs,
      cheminfo=self.cheminfo,
      vapor_phase_composition=self.vapor_phase_composition
    )

  def get_entities(self):
    self.weather = weather()
    self.substrate = substrate(inputs=self.inputs)

  def get_dispersion_parameters(self, hazard_type) -> DispersionParameters:
    disp_params = DispersionParameters()
    disp_params.averaging_time = 18.75
    if hazard_type == "toxic":
      disp_params.averaging_time = 600
    # recommended from vendor
    disp_params.relative_tolerance = 1e-4

    return disp_params
    

  def run_dispersion_calculation(self, disp_params, hazard_type):
    # Run the dispersion calculation using the vapor phase composition and the discharge data
    self.dispersion_calc = DispersionCalculation(
      material=None,substrate=None,discharge_result=None, discharge_records=None, discharge_record_count=None, weather=None, dispersion_parameters=None, end_point_concentration=None)

    self.dispersion_calc.material = self.inputs.material
    self.dispersion_calc.substrate = self.substrate
    self.dispersion_calc.discharge_result = self.vlc.discharge_result
    self.dispersion_calc.discharge_records = self.vlc.discharge_records
    self.dispersion_calc.discharge_record_count = len(self.vlc.discharge_records)
    self.dispersion_calc.weather = self.weather
    self.dispersion_calc.dispersion_parameters = disp_params
    self.dispersion_calc.end_point_concentration = self.threshold_concs_ppm[hazard_type][0] * 1e-6  # convert to vol fract

    if self.dispersion_calc.run() != ResultCode.SUCCESS:
      self.inputs.log_handler(f'\n\n\n***\n\n\nDispersion Calculation did not complete.  Messages:\n\n\n{self.dispersion_calc.messages}')
      raise Exception(Exceptions.dispersion_calc_failed)

  def run_post_processing_calcs(self, hazard_type):
    # Run the post-processing calculations to get the distances and footprints to the concentration levels
    self.distsAndFootprintsCalc = DistancesAndFootprintsToConcentrationLevelsCalculation(
      scalar_udm_outputs = self.dispersion_calc.scalar_udm_outputs, 
      weather = self.dispersion_calc.weather, 
      dispersion_records = self.dispersion_calc.dispersion_records, 
      dispersion_record_count = len(self.dispersion_calc.dispersion_records), 
      substrate = self.dispersion_calc.substrate, 
      dispersion_output_configs = [], 
      dispersion_output_config_count = 0, 
      dispersion_parameters = self.dispersion_calc.dispersion_parameters, 
      material = self.dispersion_calc.material)
    
    elevs_m = self.get_elevations()
    concs = self.threshold_concs_ppm[hazard_type]
    for elev in elevs_m:
      for conc in concs:
        if conc is None or conc == 0 or conc >= 1e6:
          continue
        c = conc * 1e-6  # convert to ppm
        disp_output_config = DispersionOutputConfig(resolution=Resolution.LOW, contour_type=ContourType.FOOTPRINT, elevation=elev, concentration=c, special_concentration=None)
        self.distsAndFootprintsCalc.dispersion_output_configs.append(disp_output_config)
        self.distsAndFootprintsCalc.dispersion_output_config_count += 1
    
    if self.distsAndFootprintsCalc.run() != ResultCode.SUCCESS:
      self.inputs.log_handler(f'\n\n\n***\n\n\nPost-processing calculation did not complete.  Messages:\n\n\n{self.distsAndFootprintsCalc.messages}')
      raise Exception(Exceptions.dispersion_calc_failed)
    
    self.post_process_results[hazard_type] = {
      'n_contour_points' : self.distsAndFootprintsCalc.n_contour_points,
      'contour_points' : self.distsAndFootprintsCalc.contour_points,
      'dispersion_output_configs' : self.distsAndFootprintsCalc.dispersion_output_configs,
    }

    apple = 1

  def get_elevations(self):
    # Get the elevations from the discharge data and the dispersion calculation
    h = self.inputs.elevation_m
    # determine the number of elevations to analyze below the release elevation
    # min of 5, max of 20.  targeting intervals of ~1/3rd the height of the release elevation
    num_points_below_h = max(5, int(h / 3))
    num_points_below_h = min(num_points_below_h, 20)
    elevs_m = np.linspace(0, h, num_points_below_h)
    elevs_m = np.append(elevs_m, h + np.linspace(3, 51, 17, endpoint=True))
    elevs_m = list(set(elevs_m.tolist()))
    elevs_m = sorted(elevs_m)
    return elevs_m

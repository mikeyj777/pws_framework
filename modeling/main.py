from pypws.enums import ResultCode

from entities.inputs import Inputs
from entities.vessel_leak import vessel_and_leak
from calculations.discharge import Discharge
from calculations.thermo import get_vapor_phase_composition

class Main:
  def __init__(self):
    self.inputs = None

  def run(self, app_inputs):
# set inputs for model.  Also gets materials and state, stored as properties of "inputs"
    self.inputs = Inputs()
    self.inputs.set_values(inputs_dict=app_inputs)

    # vessel state calc
    vessel, leak = vessel_and_leak(inputs=self.inputs)
    self.discharge_calc = Discharge(inputs=self.inputs, vessel=vessel, leak=leak)
    self.discharge_calc.run()
    if not hasattr(self.discharge_calc.vlc, "discharge_records") or len(self.discharge_calc.vlc.discharge_records) == 0:
      return ResultCode.NO_DISCHARGE_RECORDS_ERROR
    vps = get_vapor_phase_composition(self.discharge_calc)
    # dispersion
    apple = 1

    # post-processing

    # parse conc data
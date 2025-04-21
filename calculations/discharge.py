from pypws.calculations import VesselLeakCalculation
from pypws.enums import ResultCode
from pypws.entities import DischargeParameters

from data.exceptions import Exceptions

class Discharge:

  def __init__(self, inputs, vessel, leak):
    self.inputs = inputs
    self.vessel = vessel
    self.leak = leak
    self.vlc:VesselLeakCalculation = None
    
  def run(self):
    self.vlc = VesselLeakCalculation(vessel=self.vessel, leak=self.leak, discharge_parameters=DischargeParameters())
    if self.vlc.run() != ResultCode.SUCCESS:
      self.inputs.log_handler(f"\n\n\n***\n\n\nVessel Leak Calculation did not complete properly.  Messages:\n\n{self.vlc.messages}")
      raise Exception(Exceptions.discharge_calc_failure)
    apple = 1
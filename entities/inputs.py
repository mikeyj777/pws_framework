class Inputs:

  def __init__(self):
    pass

  def set_values(self, inputs):
    for k, v in inputs.items():
      setattr(self, k, v)
  
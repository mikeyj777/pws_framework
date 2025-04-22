import math

def dippr_eqn_101(constants, temp_k):
  """
  Calculate DIPPR Equation 101: Y = A * exp(-B / (T + C)) + D * T^E

  Parameters:
    constants (list): A list of 5 constants [A, B, C, D, E].
    temp_k (float): Temperature in Kelvin (T).

  Returns:
    float: Calculated value of the equation.
  """
  if len(constants) != 5:
    raise ValueError("Constants array must contain exactly 5 elements: [A, B, C, D, E].")
  
  A, B, C, D, E = constants
  ans = -1
  try:
    ans = math.exp(A + B / temp_k + C * math.log(temp_k) + D * (temp_k ** E))
  except Exception as e:
    raise Exception(e)
  return ans

# Example usage
if __name__ == "__main__":
  constants = [1.0, 500.0, 0.0, 0.1, 1.5]  # Example constants
  temp_k = 300.0  # Example temperature in Kelvin
  result = dippr_eqn_101(constants, temp_k)
  print(f"Result: {result}")
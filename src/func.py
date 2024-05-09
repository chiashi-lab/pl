import numpy as np
def optical_density_step(step):
    if step <= 1.6e6:
        return (step- 0.7e6) * 2 /0.9e6
    else:
        return 2

def transmisson(od):
    """
    od: optical density
    """
    return 10 ** (-od)

def func(x, a, b, c, d):
    return -1 * a * np.exp(b * (x-c)) + d

def mid_targetratio(step):
    return func(step, 5.31132122e-02, 2.10348740e-06, 9.89312965e+04, 5.38950264e+00)

def step2ratio(step):
    """
    step: step number
    """
    return transmisson(optical_density_step(step)) * mid_targetratio(step)

def inverse_func(y, a, b, c, d):
    return -1 * a * np.log((y + b) / c) + d

def ratio2step(ratio):
    """
    step: step number
    """
    return inverse_func(ratio, 1.90690987e+05, 5.73903933e-03, 4.30286157e-02, 1.61579563e+06)
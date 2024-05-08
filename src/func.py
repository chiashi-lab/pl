import numpy as np
def optical_density_step(step):
    if step <= 1.6e7:
        return (step- 0.7e7) * 2 /0.9e7
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
    return func(step, 2.92800423e-01, 2.10349362e-07, 9.10476001e+06, 5.38950106e+00)

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
    return inverse_func(ratio, 1.90691015e+06, 5.73903423e-03, 3.77973757e-02, 1.64051423e+07)
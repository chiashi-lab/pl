def linear(x:float, a:float, b:float) -> float:
    return a * x + b

def wavelength2ratio(wavelength: int) -> float:
    return linear(float(wavelength), -0.0165, 1.677)

def waittime4exposure(exposure:float)->float:
    return linear(float(exposure), 1.1, 2.0)
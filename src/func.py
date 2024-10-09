def linear(x:float, a:float, b:float) -> float:
    return a * x + b

def wavelength2ratio(wavelength: int) -> float:
    return linear(float(wavelength), -0.0039, 9.3265)
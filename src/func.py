def linear(x:float, a:float, b:float) -> float:
    return a * x + b

def make_linear_from_two_points(x1:float, y1:float, x2:float, y2:float) -> callable:
    if x1 == x2:
        a = (y2 - y1) / (x2 - x1 + 1e-10)
    else:
        a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    def linear(x:float) -> float:
        return a * x + b
    return linear

def wavelength2ratio(wavelength: int) -> float: # Remove Me
    return linear(float(wavelength), -0.0165, 16.77)

def waittime4exposure(exposure:float)->float:
    return linear(float(exposure), 1.1, 2.0)

if __name__ == '__main__':
    def pre(wavelength: int) -> float:
        return linear(float(wavelength), -0.0039, 9.3265)

    print("ratio pre(785) = ", pre(785))
    print("ratio now(785) = ", wavelength2ratio(785))
    print("diff = ", pre(785) - wavelength2ratio(785))
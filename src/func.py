def linear(x:float, a:float, b:float) -> float:
    return a * x + b

def wavelength2tisp_pos(wavelength:float) -> float:
    return linear(float(wavelength), -0.045363842040440305, 56.180364104778796)

def make_linear_from_two_points(x1:float, y1:float, x2:float, y2:float) -> callable:
    if x1 == x2:
        a = (y2 - y1) / (x2 - x1 + 1e-10)
    else:
        a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    def linear(x:float) -> float:
        return a * x + b
    return linear

def waittime4exposure(exposure:float)->float:
    return linear(float(exposure), 1.05, 5.0)

def ndstep2ratio(ndstep:int)->float:
    a, b = 2.95260088e-12, 2.47359842e+00
    return a * ndstep ** 2 + b

if __name__ == '__main__':
    def pre(wavelength: int) -> float:
        return linear(float(wavelength), -0.0039, 9.3265)

    print("ratio pre(785) = ", pre(785))
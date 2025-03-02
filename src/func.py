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

def waittime4exposure(exposure:float)->float:
    return linear(float(exposure), 1.05, 5.0)

def ndstep2ratio(ndstep:int)->float:
    return 2.9526e-12 * ndstep ** 2 + 2.4736

if __name__ == '__main__':
    def pre(wavelength: int) -> float:
        return linear(float(wavelength), -0.0039, 9.3265)

    print("ratio pre(785) = ", pre(785))
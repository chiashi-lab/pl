def linear(x:float, a:float, b:float) -> float:
    return a * x + b

def wavelength2ratio(wavelength: int) -> float:
    return linear(float(wavelength), -0.0165, 16.77)

def waittime4exposure(exposure:float)->float:
    return linear(float(exposure), 1.1, 2.0)

if __name__ == '__main__':
    def pre(wavelength: int) -> float:
        return linear(float(wavelength), -0.0039, 9.3265)

    print("ratio pre(785) = ", pre(785))
    print("ratio now(785) = ", wavelength2ratio(785))
    print("diff = ", pre(785) - wavelength2ratio(785))
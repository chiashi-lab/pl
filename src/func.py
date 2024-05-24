import numpy as np

def func(x, a, b, c, d):
    return -1 * a * np.exp(b * (x-c)) + d

def log(x, a, b, c, d):
    return a * np.log(b * (x-c)) +d

def ratio(step):
    return func(step, 7.77263496e-01, 3.45229002e-06, 1.32827965e+06, 4.86291339e+00)

def a(step):
    return log(step, 1.62850538e-01, 4.80427255e-01, 5.14203755e+02, 2.07196791e-01)

def lenear(x, a, b):
    return a * x + b

def alnear(l):
    return lenear(l, -0.0039, 9.3265)
import numpy as np

def get_scientific_components(number):
    if number == 0.0:
        return 0,0
    else :
        exponent = np.floor(np.log10(abs(number)))
        mantissa = number / 10 ** exponent
        return mantissa, int(exponent)

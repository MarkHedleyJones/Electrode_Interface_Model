import numpy as np


def get(measurementType, concentration):
    dir = 'measurements/'
    if type(measurementType) == list:
        for tmp in measurementType:
            dir += tmp + '/'
    else:
        dir += measurementType + '/'

    filename = str(concentration) + 'X-PBS.npy'

    return np.load(dir + filename)


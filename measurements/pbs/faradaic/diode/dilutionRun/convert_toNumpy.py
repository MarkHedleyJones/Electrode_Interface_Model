import os
import numpy as np

filenames = filter(lambda x: x[0] != '.' and x[-4:] == '.csv', os.listdir('.'))
for filename in filenames:
    with open (filename, 'r') as f:
        arr = []
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        parts = line.split(',')
        time0 = int(parts[0])
        voltage = float(parts[1])
        while line:
            parts = line.split(',')
            arr.append((int(parts[0]) - time0,
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3])))
            line = f.readline()
        out = np.array(arr, dtype={'names':('time',
                                            'voltage',
                                            'current',
                                            'stdDev'),
                                   'formats':('i',
                                              'f',
                                              'f',
                                              'f')})
        np.save(filename[:-4], out)

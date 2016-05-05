import os
import math
import sys

filenames = os.listdir('.')


currents = []
for filename in filenames:
    if filename[-4:] == '.ssv':
        if filename.find(str(0.2)) != -1:
            print(filename)
            with open(filename, 'r') as f:
                f.readline()
                line = f.readline()
                while line:
                    parts = line.split(' ')
                    print(parts)
                    currents.append(float(parts[3]))
                    line = f.readline()

current_max = max(currents)
current_min = min(currents)

print('min = ' + str(min(currents)))
print('max = ' + str(max(currents)))

surface_area_mm = float(14.0)
surface_area_root_mm = math.sqrt(surface_area_mm)
surface_area_root_m = surface_area_mm / float(1000.0)
surface_area_m = math.pow(surface_area_root_m, 2.0)

print('surface_area_m = ' + str(surface_area_m))

current_density_max = current_max / surface_area_m
current_density_min = current_min / surface_area_m

print('Current density (max) = ' + str(current_density_max))
print('Current density (min) = ' + str(current_density_min))

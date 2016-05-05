import os
import math
import numpy
dataPath = '/home/mark/Dropbox/University/PhD/Workbench/electrodeInterface/measurements/pbs/displacement'

# Converts measurments from square mm to sqare cm
def mm2_to_cm2(area):
    return math.pow(math.sqrt(area) / 10, 2)

# Retrieves a list of filenames ending in .ssv from specified directory
def get_dataset_filenames(path):
    return [x for x in os.listdir(path) if x[-4:] == '.ssv']

# Opens a dataset, reads the contents in and returns it as a numpy array
def get_dataset(path, filename):
    out = []
    with open(path + '/' + filename, 'r') as f:
        f.readline()
        line = f.readline()
        while line:
            parts = line.split(' ')
            out.append((float(parts[0]), float(parts[3])))
            line = f.readline()
    return numpy.array(out, dtype={'formats':['f','f'],
                                   'names': ['frequency', 'current']})

def charge_injected(frequency, amplitude):
    return (2.0 * amplitude) / float(frequency)


def get_maxCurrent(dataset):
    max_current = max(dataset['current'])
    for row in dataset:
        if row['current'] >= max_current:
            return row


electrode_surfaceArea_geometric_mm2 = 10
electrode_surfaceArea_effective_mm2 = 14
print('geometric surface area = ' + str(electrode_surfaceArea_geometric_mm2) + ' mm2')

electrode_surfaceArea_geometric_cm2 = mm2_to_cm2(electrode_surfaceArea_geometric_mm2)
electrode_surfaceArea_effective_cm2 = mm2_to_cm2(electrode_surfaceArea_effective_mm2)
print('geometric surface area = ' + str(electrode_surfaceArea_geometric_cm2) + ' cm2')

concentrations = [1.0, 0.5, 0.25, 0.1, 0.05, 0.025]
data = {}

max_density_val = 0
max_density_pbs = ''
max_density_freq = 0

min_density_val = 100000
min_density_pbs = ''
min_density_freq = 0

filenames = get_dataset_filenames(dataPath)
for filename in filenames:
    dataset = get_dataset(dataPath, filename)
    conc = float(filename.split('X-PBS')[0])
    data[conc] = {'xs':[], 'ys':[]}
    for scenario in dataset:
        current_density = scenario['current'] / electrode_surfaceArea_geometric_cm2
        if conc == 1.0:
            print current_density
            print scenario['frequency']
        if current_density > max_density_val:
            max_density_val = current_density
            max_density_pbs = conc
            max_density_freq = scenario['frequency']
        elif current_density < min_density_val:
            min_density_val = current_density
            min_density_pbs = conc
            min_density_freq = scenario['frequency']

        #print('Frequency = ' + str(scenario['frequency']) + ' Hz')
        amplitude = scenario['current']
        frequency = scenario['frequency']
        charge = charge_injected(frequency, amplitude)
        charge_per_area = charge / electrode_surfaceArea_geometric_cm2
        charge_density_uC_per_cm2 = charge_per_area
        data[conc]['xs'].append(frequency)
        data[conc]['ys'].append(charge_density_uC_per_cm2)
        #print('Charge density = ' + str(charge_per_area * 1e6) + ' uC/cm2')

print 'max current density = ' + str(max_density_val) + ' at ' + str(max_density_freq) + ' Hz in ' + str(max_density_pbs) + ' X PBS'
print 'min current density = ' + str(min_density_val) + ' at ' + str(min_density_freq) + ' Hz in ' + str(min_density_pbs) + ' X PBS'

#print(filenames)
#print(max(get_dataset(dataPath, filenames[0])['frequency']))
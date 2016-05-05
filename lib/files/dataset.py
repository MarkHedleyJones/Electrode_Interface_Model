import numpy as np
import os


def import_dataset(filename):
    store = []
    settings = {}

    with open(filename, 'r') as f:

        line = f.readline().rstrip('\n')

        # Check if the file has a settings header and read out
        if line[:5] == 'START':
            line = f.readline().rstrip('\n')
            while line[:3] != 'END':
                parts = line.split(',')
                settings[parts[0]] = parts[1]
                line = f.readline().rstrip('\n')
            line = f.readline().rstrip('\n')

        # Extract the column names and data formats
        names = tuple(line.split(','))
        line = f.readline().rstrip('\n')
        formats = tuple(line.split(','))

        # Populate the store with data fields
        for line in f.readlines():
            parts = line.rstrip('\n').split(',')
            store.append(tuple(parts))

    # File is now closed
    out = np.array(store, dtype={'names': names, 'formats': formats})
    return out, settings


# def export_dataset(filename, data, settings={}, overwrite=False):
#     count = 0
#     while os.path.isfile(filename) and overwrite == False:
#         if filename.find('_overwritePrevention') == -1:
#             filename += '_overwritePrevention0'
#         else:
#             filename = filename[:filename.find('_overwritePrevention') + 20]
#             filename += str(count)
#         count += 1
#
#     # filename is safe to write to
#     with open(filename, 'w') as f:
#         if settings != {}:
#             f.write('START SETTINGS\n')
#             for setting, value in settings.items():
#                 f.write(str(setting) + ',' + str(value) + '\n')
#             f.write('END SETTINGS\n')
#
#         # UNFINISHED!!!!!

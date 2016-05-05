import sys
import os
import numpy as np
import cmath
import math
import matplotlib.pyplot as plt
sys.path.append('../../../')
import lib.plot.formatter

# lib.plot.formatter.plot_params['ratio'] = 1.0
lib.plot.formatter.format()

def plotABunch():
    filenames = os.listdir('.')
    for ptype in ['Sheep', 'Saline']:
        for i, filename in enumerate(filenames):
            if (filename[-4:] == '.npy' and filename.find('Day2') != -1 and
                filename.find('0:14:35') == -1 and filename.find('0:22:53') == -1):
                parts = filename[:-4].split('_')
                if parts[1] == ptype:
                    print parts
                    data = np.load(filename)
                    if parts[1] == 'Sheep':
                        if parts[2][0] == '-':
                            label = parts[2][1:] + ' before death'
                        else:
                            label = parts[2] + ' after death'
                    else:
                        label = 'Saline'
#                     plt.plot(data['frequency'],
#                              map(abs, data['impedance']),
#                              markersize=2,
#                              marker='D',
#                              label=label)
                    plt.plot(data['frequency'],
                             map(lambda z: math.degrees(cmath.phase(z)), data['impedance']),
                             markersize=2,
                             marker='D',
                             label=label)

    plt.gca().set_xscale('log')
#     plt.gca().set_yscale('log')
    # plt.title('CPE - Day 1', size=10.0)
    plt.gca().set_xlabel('Frequency (Hz)')
    plt.gca().set_ylabel('$|Z|$ ($\Omega$)')
    plt.gca().set_xlim(1e-1, 1e5)
    plt.legend(frameon=False, loc=0)
    plt.show()


def plotTheDataset():
    data = np.load('LiveSheep.npy')
    plt.gca().set_xscale('log')
    plt.gca().set_yscale('log')
    plt.plot(data['frequency'],
             map(abs, data['impedance']),
             markersize=2,
             marker='D')
    plt.gca().set_xlabel('Frequency (Hz)')
    plt.gca().set_ylabel('$|Z|$ ($\Omega$)')
    plt.gca().set_xlim(1e-1, 1e5)
    plt.savefig('LiveSheep_mag.pdf', format='pdf')
    plt.cla()
    plt.gca().set_xscale('log')
    ys = map(lambda z:-math.degrees(cmath.phase(z)) - 180, data['impedance'])
    plt.plot(data['frequency'],
             ys,
             markersize=2,
             marker='D')
    b = lib.plot.formatter.format_labels(plt.gca().yaxis, ys)
    plt.gca().set_xlabel('Frequency (Hz)')
    plt.gca().set_ylabel('Z phase ($Degrees$)')
    plt.gca().set_xlim(1e-1, 1e5)
    plt.savefig('LiveSheep_phi.pdf', format='pdf')


# plotTheDataset()
# sys.exit()
#==============================================================================
# Day 1 Plot
#==============================================================================

filenames = os.listdir('.')
filenames.sort()
for ptype in ['Sheep', 'Saline']:
    for i, filename in enumerate(filenames):
        if filename[-4:] == '.npy':
            parts = filename[:-4].split('_')
            if parts[0] == 'Day1' and parts[1] == ptype:
                print parts
                data = np.load(filename)
                if parts[1] == 'Sheep':
                    if parts[2][0] == '-':
                        label = 'Termination -' + parts[2] + 's'
                    else:
                        label = 'Termination +' + parts[2] + 's'
                else:
                    label = 'Saline test solution'
                plt.plot(data['frequency'],
                         map(abs, data['impedance']),
                         markersize=2,
                         marker='D',
                         label=label)

plt.gca().set_xscale('log')
plt.gca().set_yscale('log')
# plt.title('CPE - Day 1', size=10.0)
plt.gca().set_xlabel('Frequency (Hz)')
plt.gca().set_ylabel('$|Z|$ ($\Omega$)')
plt.gca().set_xlim(1e-1, 1e5)
plt.legend(frameon=False, loc=0)
plt.savefig('graph_Sheep_Day1_Thesis.pdf', format='pdf')

#==============================================================================
# Day 2 Plot
#==============================================================================

plt.cla()
filenames = os.listdir('.')
filenames.sor(t)
for i, filename in enumerate(filenames):
    if filename[-4:] == '.npy':
        parts = filename[:-4].split('_')
        if parts[0] == 'Day2':
            print parts
            data = np.load(filename)
            if parts[2][0] == '-':
                label = 'Termination -' + parts[2] + 's'
            else:
                label = 'Termination +' + parts[2] + 's'
            if parts[1] == 'Saline':
                label = 'Saline test solution'
            plt.plot(data['frequency'],
                     map(abs, data['impedance']),
                     markersize=2,
                     marker='D',
                     label=label)

plt.gca().set_xscale('log')
plt.gca().set_yscale('log')
# plt.title('CPE - Day 2', size=10.0)
plt.gca().set_xlabel('Frequency (Hz)')
plt.gca().set_ylabel('$|Z|$ ($\Omega$)')
plt.gca().set_xlim(1e-1, 1e5)
plt.legend(frameon=False, loc=0)
plt.savefig('graph_Sheep_Day2_Thesis.pdf', format='pdf')

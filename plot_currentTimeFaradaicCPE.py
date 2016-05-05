import sys
import matplotlib.pyplot as plt
import lib.plot.formatter
import lib.files.dataset
import numpy as np
import os
# from pyPdf import PdfFileWriter, PdfFileReader
from matplotlib.ticker import FuncFormatter


def fetch(filename):
    filename = 'measurements/pbs/faradaic/diode/dilutionRun' + filename
    if os.path.isfile(filename):
        data, settings = lib.files.dataset.import_dataset(filename)
        return data
    else:
        return None

def combine_graphs(filenames, outputFilename):
    """
    Combines multiple graphs into a single document
    """
    # print "Starting pdf export"
    # print filenames
    output = PdfFileWriter()
    files = []
    inputStreams = []
    for filename in filenames:
        files.append(file(filename, "rb"))
        num = len(files) - 1
        inputStreams.append(PdfFileReader(files[num]))
        output.addPage(inputStreams[num].getPage(0))
    outputStream = file(outputFilename, "wb")
    output.write(outputStream)
    outputStream.close()
    for filename in files:
        filename.close()


concs = [1.0 / (2 ** x) for x in range(4)]
colours = ['red', 'green', 'blue']
colours = ['blue', 'orange', 'green', 'red']


filenames = []
waitTime = 64
lib.plot.formatter.plot_params['margin']['top'] = 0.05
lib.plot.formatter.plot_params['margin']['left'] = 0.10
lib.plot.formatter.format(style='Thesis')
times = []
currents = []
voltages = []
pos = []
for i, conc in enumerate(concs):

    filename = 'measurements/pbs/faradaic/diode/dilutionRun/'
    filename += str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.npy'
    data = np.load(filename)

    #==========================================================================
    # Add hinters
    #==========================================================================
    bins = []
    for j in [x * 64 for x in range(11)]:
        bins.append(data[j:j + 64])

    bags = []
    for tmp in bins:
        tmp = list(tmp)
        tmp = zip(*tmp)
        maxCurrent = max(tmp[2])
        maxIndex = tmp[2].index(maxCurrent)
        # print maxIndex
        maxIndex += 10
        if maxIndex > 64:
            maxIndex = 63
        bags.append((tmp[0][maxIndex], tmp[2][maxIndex]))
    print(bags)
    hinters = np.array(bags, dtype={'names':('time', 'current'), 'formats':('i', 'f')})

    if i == 0 or i == len(concs) - 1:
        plt.plot(hinters['time'], hinters['current'], linestyle=':', color=colours[i])


    plt.plot(map(lambda x: x - data['time'][0], data['time'][:650]),
                data['current'][:650],
                label=str(conc) + 'X-PBS',
                color=colours[i])

    if i == 0:
        last = 0
        for row in data:
            if row['voltage'] > last:
                times.append(row['time']-15)
                currents.append(row['current'] + 0.2e-6)
                voltages.append(row['voltage'])
                last = row['voltage']


pos = zip(times, currents)
pos = zip(pos, voltages)
print(pos)
for pos, voltage in pos:
    plt.annotate(str(voltage)+' V', xy=pos, fontsize=6)
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.1f' % (x * 1e6)))
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x)))
plt.gca().set_ylabel('Current ($\mu A$)')
plt.gca().set_xlabel('Time (seconds)')
plt.annotate('0.125X', xy=(670, 2.4e-6), fontsize=6)
plt.annotate('1.0X', xy=(670, 4.7e-6), fontsize=6)
plt.legend(frameon=False, loc=0)
plt.gca().set_xlim(0, 700)
plt.gca().set_ylim(-0.125e-6, 5e-6)

plt.savefig('plot_currentTimeFaradaicCPE_Stacked_Thesis.pdf',
            format='pdf')


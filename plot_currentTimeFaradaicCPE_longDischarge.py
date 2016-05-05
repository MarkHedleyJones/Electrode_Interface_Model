import sys
import matplotlib.pyplot as plt
import lib.plot.formatter
import lib.files.dataset
import numpy as np
import os
from pyPdf import PdfFileWriter, PdfFileReader
from matplotlib.ticker import FuncFormatter


def fetch(filename):
    filename = 'measurements/pbs/faradaic/diode/' + filename
    if os.path.isfile(filename):
        data, settings = lib.files.dataset.import_dataset(filename)
        return data
    else:
        return None

def combine_graphs(filenames, outputFilename):
    """
    Combines multiple graphs into a single document
    """
    print "Starting pdf export"
    print filenames
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
lib.plot.formatter.plot_params['margin']['left'] = 0.08
lib.plot.formatter.format(style='IEEE')

voltages = [0.08 * (x + 1) for x in range(15)]

voltages = voltages[7:-3]

for i, voltage in enumerate(voltages):

    filename = 'measurements/pbs/cpe_charge_10000s/'
    filename += str(voltage) + 'V_10000s.npy'
    data = np.load(filename)

    plt.plot(map(lambda x: x - data['time'][0], data['time']),
                data['current'],
                label=str(voltage) + 'V')
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x * 1e6)))
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x)))
plt.gca().set_ylabel('Current ($\mu A$)')
plt.gca().set_xlabel('Time (seconds)')
plt.legend(frameon=False, loc=0)
plt.gca().set_xlim(0, 10000)
plt.gca().set_yscale('log')
plt.gca().set_ylim(1e-8, 3e-6)

plt.savefig('plot_currentTimeFaradaicCPE_longDischarge_10000s_Stacked_IEEE.pdf',
            format='pdf')

#
# def time_current(conc, waitTime):
#     filename = str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
#     data = fetch(filename)
#
#     plt.scatter(map(lambda x: x - data['time'][0], data['time']),
#                 data['current'],
#                 label=str(conc),
#                 edgecolors='none',
#                 s=2)
#     plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x * 1e6)))
#     plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x)))
#     plt.gca().set_ylabel('Current ($\mu A$)')
#     plt.gca().set_xlabel('Time (seconds)')
#     plt.title(str(conc) + 'X PBS - ' + str(waitTime) + ' second wait time', size=8)
#
#     plt.gca().set_xlim(0, 1000)
#     plt.gca().set_ylim(-0.5e-5, 1.6e-5)
#     filename = '../graphs/currentTimeFaradaicCPE_' + str(conc) + 'X-PBS.pdf'
#     plt.savefig(filename, format='pdf')
#     return filename
#
# filenames = []
# for conc in concs:
#     plt.clf()
#     lib.plot.formatter.plot_params['margin']['top'] = 0.1
#     lib.plot.formatter.format()
#     filenames.append(time_current(conc, 64))
#
# combine_graphs(filenames, '../graphs/currentTimeFaradaicCPE_All.pdf')

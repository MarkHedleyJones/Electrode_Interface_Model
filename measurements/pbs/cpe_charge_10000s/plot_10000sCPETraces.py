import sys
sys.path.append('/home/mark/Dropbox/University/PhD/Workbench')
import matplotlib.pyplot as plt
# import lib.plot.formatter
import plot_formatting
# import lib.files.dataset
import numpy as np
import os
import math
import scipy.optimize
# from pyPdf import PdfFileWriter, PdfFileReader
from matplotlib.ticker import FuncFormatter

# lib.plot.formatter.format()
concs = [1.0 / (2 ** x) for x in range(5)]
waitTimes = [32, 64]
hues = [211, 0, 200]

sat = lambda x: list(np.linspace(0, 100, x))
val = lambda x: list(np.linspace(100, 100, x))


plot_formatting.format(style='thesis')


voltages = [0.08 * (x + 1) for x in range(15)]

voltages = voltages[2:-7]
upper = 60*16
for i, voltage in enumerate(voltages):
    data = np.load(str(voltage) + 'V_10000s.npy')
    plt.plot(list(map(lambda x: x / 60, data['time'][:upper])),
             data['current'][:upper],
             label=str(voltage) + 'V')
plt.gca().set_ylim(1e-9, 1e-6)
plt.gca().set_yscale('log')

plt.gca().set_ylabel('Current (A)')
plt.gca().set_xlabel('Time (Minutes)')
plt.legend(frameon=False, loc=0, ncol=3)
plt.savefig(filename='Graph_longsweep_CPE.pdf', format='pdf')



with open('1X-PBS_CurrentVsTime_10000sWait_Still.csv', 'r') as f:

    f.readline()
    f.readline()
    lastVoltage = 0.0
    line = f.readline()
    o = None
    while line:
        splits = line.split(',')
        voltage = float(splits[1])
        if voltage != lastVoltage:
            if o is not None:
                o.close()
            o = open('1X-PBS_CurrentVsTime_10000s_' + splits[1] + 'V.csv', 'w')
        o.write(line)
        line = f.readline()
        lastVoltage = voltage
    o.close()


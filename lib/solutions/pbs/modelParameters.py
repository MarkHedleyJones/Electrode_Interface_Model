import math


class ParameterSet(object):

    concentration = None

    def __init__(self, concentration):
        self.concentration = concentration
        self.conductivity()

    def conductivity(self):
        """
        Converts a concentration of PBS into a conductivity according to a
        least squares fit of the solutions used
        """
        m = 1.67296736e-02  # Determined from optimisation
        c = 8.54665149e-05  # Determined from optimisation
        return m * self.concentration + c


    def ladder_Resistor_RadialElectrode(self):
        return 0.407 / self.conductivity()

    def ladder_Resistor_RadialInsulator(self):
        return self.ladder_Resistor_RadialElectrode() * (3.0 / 4.0)

    def ladder_Resistor_LongitudinalCommence(self):
        return 3.71 / self.conductivity()


    def displacement_m(self):
        return 1.34

    def displacement_k(self):
        return 1.773

    def displacement_mag(self):
        """
        The value of the CPE impedance magnitude at 1Hz
        """
        print(3284 * math.pow(self.concentration, -0.158))

        return 3284 * math.pow(self.concentration, -0.158)

    def displacement_slope(self):
        return -0.79052566


    def faradaic_CM(self):
        return 2.316e-04 + 1.224e-04 * math.exp(-self.concentration / 6.832e-01)

    def faradaic_RM(self):
        return 10000000.0

    def faradaic_i0(self):
        return 3.5e-7

    def faradaic_n(self):
        return -0.025 * self.concentration + 0.164


    def seriesResistance(self):
        """
        Model series resistance or Rs as it is called in the paper.
        """
        return 13.38 * math.pow(self.concentration, -0.8397)

    def temperature(self):
        return 20.0

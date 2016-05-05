import lib.solutions.recipie as recipie


class PBS_Recipie(object):

    concentrations = None
    volumes = None
    mix = None
    stock_volume = None
    stock_concentration = None

    def __init__(self, solutions):
        """
        Takes an array of solution tuples of the form [(volume, concentration)]
        """
        self.concentrations = []
        self.volumes = []
        for solution in solutions:
            self.volumes.append(solution[0])
            self.concentrations.append(solution[1])
        self.solutions = solutions
        self.mix = recipie.Recipie()

        ingredients = [recipie.Ingredient('NaCl', recipie.Unit(8.0, 'gm')),
                       recipie.Ingredient('KCl', recipie.Unit(0.2, 'gm')),
                       recipie.Ingredient('Na2HPO4', recipie.Unit(1.44, 'gm')),
                       recipie.Ingredient('KH2PO4', recipie.Unit(0.24, 'gm')),
                       recipie.Ingredient('Water', recipie.Unit(1000, 'ml'))]

        self.mix.add_ingredients(ingredients)
        self.stock_concentration = max(self.concentrations)

        concentrations_fromStock = map(lambda conc: conc / self.stock_concentration,
                                       self.concentrations)

        self.stock_volume = recipie.get_stockVolume(concentrations_fromStock,
                                                    self.volumes,
                                                    10)

        self.mix.set_concentration(self.stock_concentration)
        self.mix.set_volume(self.stock_volume)


    def print_instructions(self):

        print 'To make the stock:'
        print
        print 'Mix:'
        for ingredient in self.mix.get_ingredientBy('mass'):
            print ingredient.name, ingredient.quantity.value, ingredient.quantity.unit
        print
        print 'Into:'
        for ingredient in self.mix.get_ingredientBy('volume'):
            print ingredient.name, ingredient.quantity.value, ingredient.quantity.unit

        print
        print
        print 'To make the individual solutions:'
        print
        stockVolRemaining = self.stock_volume
        for conc, vol in zip(map(lambda x: x / self.stock_concentration,
                                 self.concentrations),
                             self.volumes):
            addStock = vol * conc
            stockVolRemaining -= addStock
            print ('Mix ' + str(addStock) + ' ml of stock solution with ' +
                   str(vol - addStock) + ' ml water')

        print
        print ('If done correctly you now have ' + str(stockVolRemaining) + ' ml stock'
               + ' remaining')


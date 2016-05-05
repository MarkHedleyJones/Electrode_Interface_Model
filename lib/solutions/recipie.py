class UnitError(Exception):
    """
    My unit error exception class
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class Unit(object):
    value = None
    name = None
    unit = None
    unitType = None

    def __init__(self, value, name):
        if (name.lower().find('gram') != -1
            or name.lower().find('gm') != -1):
            self.name = 'gram'
            self.unitType = 'mass'
            self.unit = 'g'
        elif (name.lower().find('millilitre') != -1
              or name.lower().find('ml') != -1):
            self.name = 'millilitre'
            self.unitType = 'volume'
            self.unit = 'ml'
        else:
            raise UnitError('Unit not recognised')
        self.value = float(value)


class Solution(object):
    volume = None
    concentration = None

    def __init__(self, volume=None, concentration=None):
        self.volume = volume
        self.concentration = concentration


class Ingredient(object):
    name = None
    quantity = None

    def __init__(self, name=None, quantity=None):
        self.name = name
        self.quantity = quantity


class Recipie(object):
    ingredients = []

    def __init__(self):
        pass

    def add_ingredients(self, ingredients):
        self.ingredients = ingredients
        self.normalise_ingredients()

    def normalise_ingredients(self):
        vol = self.get_totalVolume()
        for ingredient in self.ingredients:
            ingredient.quantity.value /= vol

    def get_totalVolume(self):
        vol = 0.0
        for ingredient in self.ingredients:
            if ingredient.quantity.unitType == 'volume':
                vol += ingredient.quantity.value
        return vol

    def set_concentration(self, concentration):
        for ingredient in self.ingredients:
            if ingredient.quantity.unitType == 'mass':
                ingredient.quantity.value *= float(concentration)

    def set_volume(self, volume):
        for ingredient in self.ingredients:
            ingredient.quantity.value *= float(volume)

    def get_ingredientBy(self, unitType):
        ingredients = []
        for ingredient in self.ingredients:
            if ingredient.quantity.unitType == unitType:
                ingredients.append(ingredient)
        return ingredients


def get_stockVolume(concentrations, volumes, resolution=10):
    import math
    neededVol = sum(map(lambda (conc, vol): conc * vol,
                        zip(concentrations,
                            volumes)))
    tmpVol = (math.ceil(neededVol / float(resolution)) * float(resolution))
    return tmpVol

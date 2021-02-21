validColors = [
    'White',
    'Red',
    'Green',
    'Blue',
    'Light Blue',
    'Pink',
    'Yellow',
    'Black'
]

class Goal(object):

    def __init__(self, name, color, items=None, locations=None):
        # early exit if goal initialized incorrectly
        if (items is None and locations is None):
            raise Exception('Invalid goal: no items or destinations set')
        self.name = name
        if (color in validColors):
            self.color = color
        else:
            raise Exception('Invalid goal: Color not supported')
        self.items = items
        self.locations = locations
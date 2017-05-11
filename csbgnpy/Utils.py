class Undefined(object):
    def __init__(self, num = None):
        self.num = num

    def __eq__(self, other):
        return isinstance(other, csbgnpy.Utils.Undefined) and self.num == other.num

    def __hash__(self):
        return hash(("undefined", self.num,))

    def __str__(self):
        return "Undefined({0})".format(self.num)

def mean(c):
    return sum(c) / len(c)


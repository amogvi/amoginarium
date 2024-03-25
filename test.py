class PolyMatcher:
    def __init__(self, a, b, c, d) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d


x = PolyMatcher(False, False, False, True)

match x:
    # single
    case PolyMatcher(a=False, b=False, c=False, d=False):
        print("0000")

    # dirt
    case PolyMatcher(a=True, b=True, c=True, d=True):
        print("1111")

    # grass top
    case PolyMatcher(a=True, b=False, c=False, d=False):
        print("1000")

    # grass bottom
    case PolyMatcher(a=False, b=True, c=False, d=False):
        print("0100")

    # left wall
    case PolyMatcher(a=False, b=False, c=True, d=False):
        print("0010")

    # right wall
    case PolyMatcher(a=False, b=False, c=False, d=True):
        print("0001")

    # top and bottom
    case PolyMatcher(a=True, b=True, c=False, d=False):
        print("1100")

    # left and right
    case PolyMatcher(a=False, b=False, c=True, d=True):
        print("0011")

    # bottom empty
    case PolyMatcher(a=True, b=False, c=True, d=True):
        print("1011")

    # top empty
    case PolyMatcher(a=False, b=Treu, c=True, d=True):
        print("0111")

    # left empty
    case PolyMatcher(a=True, b=True, c=False, d=True):
        print("1101")

    # right empty
    case PolyMatcher(a=True, b=True, c=False, d=False):
        print("1110")

    # left top corner
    case PolyMatcher(a=True, b=False, c=True, d=False):
        print("1010")

    # right top corner
    case PolyMatcher(a=True, b=False, c=False, d=True):
        print("1001")

    # right bottom corner
    case PolyMatcher(a=False, b=True, c=False, d=True):
        print("0101")

    # left bottom corner
    case PolyMatcher(a=False, b=True, c=True, d=False):
        print("0110")

    case _:
        print("????")

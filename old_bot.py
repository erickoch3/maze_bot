import math


class Location:
    
    def __init__(self, value, coords=None):
        self.value = value
        self.coords = coords

class Map:

    def __init__(self, frame):
        self.frame = frame
        self.center = frame[1][1]
    
    def expand(self):
        """ Add ? to show regions we haven't explored. """
        for row in self.frame:
            row = [Location("?")] + row + [Location("?")]
        self.frame = [[Location("?")]*len(self.frame[0])] + \
                     self.frame + \
                     [[Location("?")]*len(self.frame[-1])]
        self.update_coords()
    
    def update_coords(self):
        for row, row_locs in enumerate(self.frame):
            for col, loc in enumerate(row_locs):
                loc.coords = [row, col]

class Bot:

    def __init__(self):
        self.id = input()
        self.frame = [[Location(value, [row, col]) for col, value in enumerate(input())] 
                      for row in range(3)]
        self.map = Map(self.frame)
        self.loc = self.map.center
        self.map.expand()
        self.direction = None
    
    def explore(self):
        for row, row_locs in enumerate(self.map.frame):
            for col, loc in enumerate(row_locs):
                if loc.value == "?":
                    dest = loc
                    dest.coords = [row,  col]
                    self.route_to(dest)
                    return True
        return False
    
    def route_to(self, dest):
        """ Travel directly towards the location """
        x = dest.coords[0] - self.loc.coords[0]
        y = dest.coords[1] - self.loc.coords[1]
        if x > 0:
            self.move('UP')
        elif x < 0:
            self.move('DOWN')
        elif y > 0:
            self.move('RIGHT')
        elif y < 0:
            self.move('LEFT')

    def move(self, direction):
        print(direction.upper())

if __name__ == "__main__":
    bot = Bot()
    bot.explore()
    
        
        
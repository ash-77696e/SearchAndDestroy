import numpy as np
import random

class Cell:

    def __init__(self, terrain):
        self.terrain = terrain
        
        if terrain == 'flat':
            self.fnr = 0.1
        elif terrain == 'hilly':
            self.fnr = 0.3
        elif terrain == 'forested':
            self.fnr = 0.7
        else:
            self.fnr = 0.9
        
        self.is_target = False
    
    def __str__(self):
        return 'true' if self.is_target == True else 'false'

def generate_map(dim):
    map = []

    for i in range(dim):
        row = []
        for j in range(dim):
            cell = None
            rand = random.random()

            if rand <= 0.25:
                cell = Cell('flat')
            elif rand <= 0.50:
                cell = Cell('hilly')
            elif rand <= 0.75:
                cell = Cell('forested')
            else:
                cell = Cell('cave')
            
            row.append(cell)
        
        map.append(row)
    
    return map

def place_target(map):
    i = random.randint(0, len(map) - 1)
    j = random.randint(0, len(map) - 1)
    map[i][j].is_target = True

def init_belief(belief_matrix):
    for i in range(belief_matrix.shape[0]):
        for j in range(belief_matrix.shape[1]):
            belief_matrix[i][j] = 1 / (belief_matrix.shape[0] * belief_matrix.shape[1])

def agent1(map):
    belief_matrix = np.zeros((len(map), len(map)))
    init_belief(belief_matrix)
    print(belief_matrix)

def main():
    map = generate_map(50)
    agent1(map)
    

if __name__ == '__main__':
    main()

import numpy as np
import random
import heapq
import concurrent.futures
'''
This python file is used to play a game of search and destroy on a randomly generated 50 x 50 board with either one of two basic agents 
or an improved agent. The cells of the board are randomly given terrain types with an equal probability. Then, a target is randomly
assigned to a cell. Depending on the type of terrain, searching a cell may return a failure due to the false negative rate. The total
score of the game is calculated by summing the total number of searches with the total distance the agent had to travel.

Authors: Ashwin Haridas, Ritin Nair

'''

'''
This class is for the the cell object. It specifies the terrain for a cell and a search function for finding the target in a cell
based on the false negative search rate associated with the specific terrain type of the cell.

'''
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
    
    def search(self):
        if self.is_target == True:
            if random.random() <= self.fnr:
                return 'Failure'
            return 'Success'
        return 'Failure'
    
    def __str__(self):
        return self.terrain

'''
This function generates a map with the specified dimensions. Each cell on the board is assigned a Cell object of one of four terrain
types with an equal probability. 

Input: Dimensions of board
Output: Board filled with Cells that have terrain types

'''

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

'''
This function places a target in a random cell on the board
Input: The board
Output: The board with a target in a random cell
'''
def place_target(map):
    i = random.randint(0, len(map) - 1)
    j = random.randint(0, len(map) - 1)
    map[i][j].is_target = True

    output = map[i][j].search()
    #print(output)
    #print(map[i][j])

'''
This function initializes the belief state where each cell contains the probability of the target being in the cell given the
current known observations.
Input: Empty belief state
Output: Belief state where every cell has an equal belief probability
'''

def init_belief(belief_matrix):
    for i in range(belief_matrix.shape[0]):
        for j in range(belief_matrix.shape[1]):
            belief_matrix[i][j] = 1 / (belief_matrix.shape[0] * belief_matrix.shape[1])

'''
This function updates the belief state of the board to account for an extra failed search on the current cell (i, j). Each cell
contains the probability that the target is in the cell given the current observations and the extra observed failure at cell (i, j).
Input: Belief state, map, current cell with indices i and j
Output: No returned output but the belief state is updated

'''

def update_belief_matrix(belief_matrix, map, i, j):
    old_belief = belief_matrix[i][j]
    for x in range(belief_matrix.shape[0]):
        for y in range(belief_matrix.shape[1]):
            if x == i and y == j:
                belief_matrix[x][y] = (map[x][y].fnr * belief_matrix[x][y]) / ((1 * (1 - old_belief)) + (map[x][y].fnr * old_belief))
            else:
                belief_matrix[x][y] = (1 * belief_matrix[x][y]) / ((1 * (1 - old_belief)) + (map[i][j].fnr * old_belief))

'''
This function uses the current belief state to create a matrix containing the probabilities of the target being found in each cell
given the observations so far.

Input: Found matrix, belief state, map
Output: Updated found matrix
'''

def update_found_matrix(found_matrix, belief_matrix, map):
    for x in range(found_matrix.shape[0]):
        for y in range(found_matrix.shape[1]):
            found_matrix[x][y] = (1 - map[x][y].fnr) * belief_matrix[x][y]    

'''
This function uses the matrix containing the probabilities of the target being found in each cell
given the observations so far to create a new matrix containing the ratio between the probability of the target being found in each
cell and the distance from the current cell to each cell to decide which cell to search next.

Input: Found matrix, map, and indices of current cell
Output: Matrix containing ratios of probability of target being found given observations to distance
'''

def update_ratio_matrix(found_matrix, map, i , j):
    ratio_matrix = np.zeros((len(map), len(map)))
    for x in range (found_matrix.shape[0]):
        for y in range(found_matrix.shape[1]):
            # can assign a low value because there is no point in moving to the same cell after it has been searched already
            if (x == i and y == j): 
                ratio_matrix[x][y] = 0
                continue
            distance = abs(i - x) + abs(j - y) # from current cell to each cell
            ratio = found_matrix[x][y] / distance # want to maximize probability and minimize distance
            ratio_matrix[x][y] = ratio
    return ratio_matrix

'''
This function uses the given matrix to pick the cell with the highest value as the next cell to search. It also calculates the distance
from the current cell to the next cell to search. Any ties between picking cells are broken by distance where the next cell with the 
lower distance from the current cell is picked. Any ties in distance after this are broken by random with each cell having an equal
chance of being picked.

Input: Matrix with priority values, current cells indices which are i and j
Output: Indices of the next cell to search and the distance to the next cell from the current cell
'''


def find_next_move(prob_matrix, i, j):
    best_prob = 0
    best_distance = 60
    best_i = -1
    best_j = -1

    for x in range(prob_matrix.shape[0]):
        for y in range(prob_matrix.shape[1]):
            if prob_matrix[x][y] > best_prob:
                best_i = x
                best_j = y
                best_prob = prob_matrix[x][y]
                best_distance = abs(i - x) + abs(j - y)
            elif prob_matrix[x][y] == best_prob:
                distance = abs(i - x) + abs(j - y)
                if distance < best_distance:
                    best_i = x
                    best_j = y
                    best_distance = distance
                elif distance == best_distance:
                    rand = random.randint(1, 2)
                    if rand == 2:
                        best_i = x
                        best_j = y
                        best_distance = distance
    
    #print((best_i, best_j))
    return best_i, best_j, best_distance
'''
This is the first basic agent. It decides which cell to search next given the probability of the target being in each cell given 
the current observations taken so far.

Input: The board
Output: The score from the game
'''

def agent1(map):
    belief_matrix = np.zeros((len(map), len(map)))
    init_belief(belief_matrix)
    #print(belief_matrix)

    searches = 0
    distance_traveled = 0

    found = False

    i = random.randint(0, len(map) - 1)
    j = random.randint(0, len(map) - 1)

    searches += 1

    if map[i][j].search() == 'Success':
        print('Success!')
        return (searches + distance_traveled, map[i][j].terrain)
    
    update_belief_matrix(belief_matrix, map, i, j)
    i, j, distance = find_next_move(belief_matrix, i, j)
    distance_traveled += distance

    while not(found):
        searches += 1
        if map[i][j].search() == 'Success':
            print('Success!')
            print(map[i][j].terrain)
            return (searches + distance_traveled, map[i][j].terrain)
        
        update_belief_matrix(belief_matrix, map, i, j)
        i, j, distance = find_next_move(belief_matrix, i, j)
        distance_traveled += distance
        #print(np.sum(belief_matrix))
'''
This is the second basic agent. It uses the probability of the target being found in a cell given the current observations to determine
which cell should be searched next.

Input: The board
Output: The score from the game
'''
def agent2(map):
    belief_matrix = np.zeros((len(map), len(map)))
    init_belief(belief_matrix)
    #print(belief_matrix)

    found_matrix = np.zeros((len(map), len(map)))
    update_found_matrix(found_matrix, belief_matrix, map)
    #print(found_matrix)

    searches = 0 
    distance_traveled = 0

    found = False
    # randomly pick first cell to search
    i = random.randint(0, len(map) - 1)
    j = random.randint(0, len(map) - 1)

    searches += 1
    
    if (map[i][j].search() == 'Success'):
        print('Success!')
        return (searches + distance_traveled, map[i][j].terrain)

    update_belief_matrix(belief_matrix, map, i, j)
    update_found_matrix(found_matrix, belief_matrix, map)

    i, j, distance = find_next_move(found_matrix, i, j)
    distance_traveled += distance

    while not(found):
        searches += 1
        if map[i][j].search() == 'Success':
            print('Success')
            print(map[i][j].terrain)
            return (searches + distance_traveled, map[i][j].terrain)
        
        # failed to find target

        update_belief_matrix(belief_matrix, map, i, j)
        update_found_matrix(found_matrix, belief_matrix, map)
        
        
        i, j, distance = find_next_move(found_matrix, i, j)
        distance_traveled += distance
        #print(np.sum(belief_matrix))
        #print(np.sum(found_matrix))
'''
This is the improved agent. The first improvement is that it uses a ratio between the probability of the target being found in each
cell and the distance from the current cell to each cell to decide which cell to search next. This helps account for the cost of the 
distance traveled before choosing which cell to search. The second improvement is that it searches cells with terrain types with higher
false negative rates more times before moving on to find a new cell to search. This helps combat failures due to false negatives and 
tries to increase the likelihood of a failure being due to the target not actually being in the cell.

Input: The board
Output: The score of the game

'''
def agent3(map):
    belief_matrix = np.zeros((len(map), len(map)))
    init_belief(belief_matrix)
    #print(belief_matrix)

    found_matrix = np.zeros((len(map), len(map)))
    update_found_matrix(found_matrix, belief_matrix, map)
    #print(found_matrix)


    searches = 0 
    distance_traveled = 0

    found = False
    # randomly pick first cell to search
    i = random.randint(0, len(map) - 1)
    j = random.randint(0, len(map) - 1)

    searches += 1
    
    if (map[i][j].search() == 'Success'):
        print('Success!')
        return (searches + distance_traveled, map[i][j].terrain)

    update_belief_matrix(belief_matrix, map, i, j)
    update_found_matrix(found_matrix, belief_matrix, map)
    ratio_matrix = update_ratio_matrix(found_matrix, map, i, j)
    
    i, j, distance = find_next_move(ratio_matrix, i, j)
    distance_traveled += distance

    while not(found):
        
        #perform amount of searches based on type of terrain
        if (map[i][j].terrain == 'flat'):
            searches += 1
            if map[i][j].search() == 'Success':
                print('Success')
                print(map[i][j].terrain)
                return (searches + distance_traveled, map[i][j].terrain)
            else:
                update_belief_matrix(belief_matrix, map, i, j)
                update_found_matrix(found_matrix, belief_matrix, map)
        elif (map[i][j].terrain == 'hilly'):
            for iter in range(2):
                searches += 1
                if map[i][j].search() == 'Success':
                    print('Success')
                    print(map[i][j].terrain)
                    return (searches + distance_traveled, map[i][j].terrain)
                else: # failed search so update relevant probability matrices
                    update_belief_matrix(belief_matrix, map, i, j)
                    update_found_matrix(found_matrix, belief_matrix, map)
        elif (map[i][j].terrain == 'forested'):
            for iter in range(4):
                searches += 1
                if map[i][j].search() == 'Success':
                    print('Success')
                    print(map[i][j].terrain)
                    return (searches + distance_traveled, map[i][j].terrain)
                else: # failed search so update relevant probability matrices
                    update_belief_matrix(belief_matrix, map, i, j)
                    update_found_matrix(found_matrix, belief_matrix, map)
        elif (map[i][j].terrain == 'cave'):
            for iter in range(10):
                searches += 1
                if map[i][j].search() == 'Success':
                    print('Success')
                    print(map[i][j].terrain)
                    return (searches + distance_traveled, map[i][j].terrain)
                else: # failed search so update relevant probability matrices
                    update_belief_matrix(belief_matrix, map, i, j)
                    update_found_matrix(found_matrix, belief_matrix, map)

        searches += 1

        if map[i][j].search() == 'Success':
            print('Success')
            print(map[i][j].terrain)
            return (searches + distance_traveled, map[i][j].terrain)

        # failed to find target
        ratio_matrix = update_ratio_matrix(found_matrix, map, i, j)
        
        i, j, distance = find_next_move(ratio_matrix, i, j)
        distance_traveled += distance
        #print(np.sum(belief_matrix))
        #print(np.sum(found_matrix))

'''
This function generates a 50 x 50 board and runs one trial of the game with the first basic agent.

Input: No input
Output: The score of the game
'''
def agent1_trial():
    map = generate_map(50)
    place_target(map)
    return agent1(map)

'''
This function generates a 50 x 50 board and runs one trial of the game with the second basic agent.

Input: No input
Output: The score of the game
'''
def agent2_trial():
    map = generate_map(50)
    place_target(map)
    return agent2(map)

'''
This function generates a 50 x 50 board and runs one trial of the game with the improved agent.

Input: No input
Output: The score of the game
'''
def agent3_trial():
    map = generate_map(50)
    place_target(map)
    return agent3(map)

''' 
This is the main function for the program
'''
def main():


    exec = concurrent.futures.ProcessPoolExecutor(max_workers=50)

    futures, results = {}, []

    # run 50 trials for the agent type
    for i in range(50):
        futures[exec.submit(agent1_trial)] = 0
    
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())
    
    total = 0

    for item in results:
        total += item[0]
    
    # average the sum of the scores to get the average score for the agent type over 50 trials
    print(total / 50)
    

if __name__ == '__main__':
    main()
    # 8498.80 (improved agent)
    # 25949.24 (agent 2)
    # 46553.76 (agent 1)

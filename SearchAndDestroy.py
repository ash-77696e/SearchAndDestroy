import numpy as np
import random
import heapq
import concurrent.futures

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

    output = map[i][j].search()
    #print(output)
    #print(map[i][j])

def init_belief(belief_matrix):
    for i in range(belief_matrix.shape[0]):
        for j in range(belief_matrix.shape[1]):
            belief_matrix[i][j] = 1 / (belief_matrix.shape[0] * belief_matrix.shape[1])

def update_belief_matrix(belief_matrix, map, i, j):
    old_belief = belief_matrix[i][j]
    for x in range(belief_matrix.shape[0]):
        for y in range(belief_matrix.shape[1]):
            if x == i and y == j:
                belief_matrix[x][y] = (map[x][y].fnr * belief_matrix[x][y]) / ((1 * (1 - old_belief)) + (map[x][y].fnr * old_belief))
            else:
                belief_matrix[x][y] = (1 * belief_matrix[x][y]) / ((1 * (1 - old_belief)) + (map[i][j].fnr * old_belief))

def update_found_matrix(found_matrix, belief_matrix, map):
    for x in range(found_matrix.shape[0]):
        for y in range(found_matrix.shape[1]):
            found_matrix[x][y] = (1 - map[x][y].fnr) * belief_matrix[x][y]    

    return found_matrix

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


def update_ratio_matrix(found_matrix, map, i , j):
    ratio_matrix = np.zeros((len(map), len(map)))
    for x in range (found_matrix.shape[0]):
        for y in range(found_matrix.shape[1]):
            # can assign a low value because there is no point in moving to the same cell after it has been searched already
            if (x == i and y == j): 
                ratio_matrix[x][y] = 0
                continue
            distance = abs(i - x) + abs(j - y) # from current cell to each cell
            ratio = found_matrix[x][y] / distance # want to maximize probability and minimize ratio
            ratio_matrix[x][y] = ratio
    return ratio_matrix

def agent1_trial():
    map = generate_map(50)
    place_target(map)
    return agent1(map)

def agent2_trial():
    map = generate_map(50)
    place_target(map)
    return agent2(map)

def agent3_trial():
    map = generate_map(50)
    place_target(map)
    return agent3(map)

def main():
    exec = concurrent.futures.ProcessPoolExecutor(max_workers=50)

    futures, results = {}, []

    for i in range(50):
        futures[exec.submit(agent1_trial)] = 0
    
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())
    
    total = 0

    for item in results:
        total += item[0]
    
    print(total / 50)
    

if __name__ == '__main__':
    main()
    # 8498.80 (improved agent)
    # 25949.24 (agent 2)
    # 46553.76 (agent 1)

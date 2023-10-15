import itertools
import math
from logger import get_logger
import multiprocessing
from enum import Enum
import pprint



logger = get_logger(__name__)

class Symmetry(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


def get_best_r2(r1, b1, b2, grid_points):
    optimal_r2 = []
    max_red_score = -math.inf
    for r2 in grid_points:
        if r2 not in (r1, b1, b2):
            red_score = get_red_score(r1, r2, b1, b2, grid_points)

            # Update the optimal strategy for red if necessary
            if red_score >= max_red_score:
                if red_score > max_red_score:
                    max_red_score = red_score
                    optimal_r2 = []
                optimal_r2.append(r2)

    return (max_red_score, optimal_r2)


def get_red_score(r1, r2, b1, b2, grid_points):
    exclusions = set([r1, r2, b1, b2])
    red_distances = [distance(p, (r1, r2)) for p in grid_points]
    blue_distances = [distance(p, (b1, b2)) for p in grid_points]
    score = 0
    for red_dist, blue_dist, p in zip(red_distances, blue_distances, grid_points):
        if p in exclusions:
            continue
        if red_dist == blue_dist:
            score += 0.5
        elif red_dist < blue_dist:
            score += 1
        else:
            continue
    return score


def get_best_b1_and_b2_based_on_optimal_r2(r1, grid_points):
    blue_optimal_strategy = []
    # Generate all possible pairs of points that Blue can choose
    blue_pairs = list(itertools.combinations(set(grid_points) - {r1}, 2))
    min_max_red_score = math.inf
    # Find the optimal pair of b1 and b2 for this value of r1
    for b1, b2 in blue_pairs:
        max_red_score, optimal_r2 = get_best_r2(r1, b1, b2, grid_points)
        logger.debug(
            f"strategy:max red score:{max_red_score},r1:{r1},b1:{b1},b2:{b2},r2:{optimal_r2}")
        # Update the optimal strategy for Blue if necessary
        if max_red_score <= min_max_red_score:
            if max_red_score < min_max_red_score:
                blue_optimal_strategy = []
                min_max_red_score = max_red_score
            blue_optimal_strategy.append((b1, b2, optimal_r2))

    logger.debug(
        f" finished strategy max red score:{min_max_red_score} ,r1:{r1},b1:{b1},b2:{b2},r2:{optimal_r2}")
    return (min_max_red_score, blue_optimal_strategy)


def distance(start, endpoints):
    distances = [math.dist(start, end) for end in endpoints]
    return min(distances)


def distance_int(p, points, n):
    x1, y1 = divmod(p, n)
    x2, y2 = divmod(points[0], n)
    x3, y3 = divmod(points[1], n)
    return min(math.dist((x1, y1), (x2, y2)), math.dist((x1, y1), (x3, y3)))


def get_points_smaller_than_symmetrical_line(points, x,y):
    # Initialize the sublist of points
    filtered_points = []
    
    # Go over all the points
    for point in points:
        # Check if the point has x and y values smaller than the specific x and y values
        if (x is None or point[0] <= x) and (y is None or point[1] <= y):
            # Add the point to the sublist of points
            filtered_points.append(point)
    
    # Return the sublist of points
    return filtered_points

def calculate_winner(grid_points):
    # Initialize variables to keep track of optimal strategies
    pprint.pprint(grid_points)
    optimal_strategies = []
    max_min_max_red_score = -math.inf
    i = 0
    calculations_count = len(grid_points)

    logger.info(f"started:{calculations_count} calculations")
    # Iterate over all possible choices of r1
    for r1 in grid_points:
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        i += 1
        logger.info(f"finished:{i}/{calculations_count} calculations")

        # Update the optimal strategy for Red if necessary
        if min_max_red_score >= max_min_max_red_score:
            if min_max_red_score > max_min_max_red_score:
                optimal_strategies = []
                max_min_max_red_score = min_max_red_score
                logger.info(f"best red score:{max_min_max_red_score}")
            optimal_strategies.append((r1, blue_optimal_strategy))
    logger.info(f"best red score:{max_min_max_red_score}")
    
    pprint.pprint(optimal_strategies)
    
    return optimal_strategies

def calculate_winner_symmetric(grid_points):
    # Initialize variables to keep track of optimal strategies
    optimal_strategies = []
    max_min_max_red_score = -math.inf
    i = 0
        
    vertical_line_of_symmetry = get_vertical_line_of_symmetry(grid_points)
    if vertical_line_of_symmetry is not None:
        logger.info("The shape is vertically symmetric.")
        
    horizontal_line_of_symmetry = get_horizontal_line_of_symmetry(grid_points)
    if horizontal_line_of_symmetry is not None:
        logger.info("The shape is horizontally symmetric.")
        
    filtered_points = get_points_smaller_than_symmetrical_line(grid_points,vertical_line_of_symmetry,horizontal_line_of_symmetry)
    
    calculations_count = len(filtered_points)


    logger.info(f"started:{calculations_count} calculations")
    # Iterate over all possible choices of r1
    for r1 in filtered_points:
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        i += 1
        logger.info(f"finished:{i}/{calculations_count} calculations")

        # Update the optimal strategy for Red if necessary
        if min_max_red_score >= max_min_max_red_score:
            if min_max_red_score > max_min_max_red_score:
                optimal_strategies = []
                max_min_max_red_score = min_max_red_score
                logger.info(f"best red score:{max_min_max_red_score}")
            optimal_strategies.append((r1, blue_optimal_strategy))
    logger.info(f"best red score:{max_min_max_red_score}")
        
    vertical_symmetric_list =get_points_vertical_symmetric(optimal_strategies,vertical_line_of_symmetry)
    optimal_strategies+=vertical_symmetric_list
    horizontal_symmetric_list =get_points_horizontal_symmetric(optimal_strategies,horizontal_line_of_symmetry)
    
    return optimal_strategies + horizontal_symmetric_list

def get_symmetric_point(point, line_of_symmetry, symmetry_type):
    if symmetry_type == Symmetry.HORIZONTAL:
        return (point[0], int(2 * line_of_symmetry) - point[1])
    elif symmetry_type == Symmetry.VERTICAL:
        return (int(2 * line_of_symmetry) - point[0], point[1])

def get_symmetric_strategy(strategy, line_of_symmetry, symmetry_type):
    symmetric_r1 = get_symmetric_point(strategy[0], line_of_symmetry, symmetry_type)
    new_strategy=(symmetric_r1, [])
    for blue_dots in strategy[1]:
        symmetric_b1 = get_symmetric_point(blue_dots[0], line_of_symmetry, symmetry_type)
        symmetric_b2 = get_symmetric_point(blue_dots[1], line_of_symmetry, symmetry_type)
        
        #since I want this to be the same as the regular algorithm the bigger point should be b1
        symmetric_b1, symmetric_b2 = (symmetric_b2, symmetric_b1) if symmetric_b2 > symmetric_b1 else (symmetric_b1, symmetric_b2)
        symmetric_red_dots_list=[]
        for red_dot in blue_dots[2]:
            symmetric_red_dot = get_symmetric_point(red_dot, line_of_symmetry, symmetry_type)
            symmetric_red_dots_list.append(symmetric_red_dot)
        new_strategy[1].append((symmetric_b1,symmetric_b2,symmetric_red_dots_list))
    return new_strategy

def get_points_horizontal_symmetric(optimal_strategies, horizontal_line_of_symmetry):
    symmetric_strategies_list=[]
    if horizontal_line_of_symmetry==None:
        return []
    for strategy in optimal_strategies:
        # if the point has a symmetric counterpart 
        if strategy[0][1] < horizontal_line_of_symmetry:
            symmetric_strategy = get_symmetric_strategy(strategy, horizontal_line_of_symmetry,Symmetry.HORIZONTAL)
            symmetric_strategies_list.append(symmetric_strategy)
    return symmetric_strategies_list

def get_points_vertical_symmetric(optimal_strategies, vertical_line_of_symmetry):
    symmetric_strategies_list=[]
    if vertical_line_of_symmetry== None:
        return []
    for strategy in optimal_strategies:
        # if the point has a symmetric counterpart 
        if strategy[0][0] < vertical_line_of_symmetry:
            symmetric_strategy = get_symmetric_strategy(strategy, vertical_line_of_symmetry,Symmetry.VERTICAL)
            symmetric_strategies_list.append(symmetric_strategy)
    return symmetric_strategies_list


def update_optimal_strategies(optimal_strategies, max_score, new_score, new_strategy):
    if new_score >= max_score:
        if new_score > max_score:
            optimal_strategies = []
            max_score = new_score
            logger.info(f"best red score: {max_score}")
        optimal_strategies.append(new_strategy)
    return optimal_strategies, max_score


def iterate_get_best_b1_and_b2_based_on_optimal_r2(grid_points, grid_points_chunk, result_queue, process_id):
    # Initialize variables to keep track of optimal strategies
    optimal_strategies = []
    max_min_max_red_score = -math.inf

    i = 0
    calculations_count = len(grid_points_chunk)
    logger.info(
        f"process number {process_id} started calculating:{calculations_count} calculations")

    # Iterate over all possible choices of r1
    for r1 in grid_points_chunk:
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        i += 1
        logger.info(
            f"process number {process_id} finished:{i}/{calculations_count} calculations")
        # Update the optimal strategy for Red if necessary
        optimal_strategies, max_min_max_red_score = update_optimal_strategies(
            optimal_strategies, max_min_max_red_score, min_max_red_score, (r1, blue_optimal_strategy))
    logger.info(
        f"best red score:{max_min_max_red_score}, finished calculation number {process_id}")

    result_queue.put((max_min_max_red_score, optimal_strategies))


def get_vertical_line_of_symmetry(grid_points):
    # Find the minimum and maximum x values
    min_x = min([point[0] for point in grid_points])
    max_x = max([point[0] for point in grid_points])

    # Calculate the line of symmetry
    line_of_symmetry =(min_x + max_x) / 2

    # Check if all points are symmetric with respect to the line of symmetry
    for point in grid_points:
        # Find the grid_points point
        symmetric_point = (2 * line_of_symmetry - point[0], point[1])

        # Check if the symmetric point is in the list of points
        if symmetric_point not in grid_points:
            return None

    return line_of_symmetry


def get_horizontal_line_of_symmetry(grid_points):
    # Find the minimum and maximum y values
    min_y = min([point[1] for point in grid_points])
    max_y = max([point[1] for point in grid_points])

    # Calculate the line of symmetry
    line_of_symmetry = (min_y + max_y) / 2

    # Check if all points are symmetric with respect to the line of symmetry
    for point in grid_points:
        # Find the symmetric point
        symmetric_point = (point[0], 2 * line_of_symmetry - point[1])

        # Check if the symmetric point is in the list of points
        if symmetric_point not in grid_points:
            return None

    return line_of_symmetry


def calculate_winner_multiprocessing(grid_points):
    num_cores = multiprocessing.cpu_count()
    num_processes = num_cores - 1 if num_cores > 2 else num_cores
    
    
    vertical_line_of_symmetry = get_vertical_line_of_symmetry(grid_points)
    if vertical_line_of_symmetry is not None:
        logger.info("The shape is vertically symmetric.")
        
    horizontal_line_of_symmetry = get_horizontal_line_of_symmetry(grid_points)
    if horizontal_line_of_symmetry is not None:
        logger.info("The shape is horizontally symmetric.")
        
    filtered_points = get_points_smaller_than_symmetrical_line(grid_points,vertical_line_of_symmetry,horizontal_line_of_symmetry)
    
    

    chunk_size = len(filtered_points) // num_processes
    result_queue = multiprocessing.Queue()

    logger.info(f"start to calculate:{len(filtered_points)} calculation")
    processes = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - \
            1 else len(filtered_points)
        grid_points_chunk = filtered_points[start_idx:end_idx]
        process = multiprocessing.Process(target=iterate_get_best_b1_and_b2_based_on_optimal_r2, args=(
            grid_points, grid_points_chunk, result_queue, i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    optimal_strategies = []
    max_min_max_red_score = -math.inf

    for (min_max_red_score, optimal_strategy) in results:

        optimal_strategies, max_min_max_red_score = update_optimal_strategies(
            optimal_strategies, max_min_max_red_score, min_max_red_score, optimal_strategy)
    logger.info(f"final best red score:{max_min_max_red_score}")

    flattened_list = [
        item for sublist in optimal_strategies for item in sublist]
    
    vertical_symmetric_list =get_points_vertical_symmetric(flattened_list,vertical_line_of_symmetry)
    flattened_list+=vertical_symmetric_list
    horizontal_symmetric_list =get_points_horizontal_symmetric(flattened_list,horizontal_line_of_symmetry)

    return flattened_list + horizontal_symmetric_list

import itertools
import math
from logger import get_logger
import multiprocessing



logger = get_logger(__name__)


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
        logger.debug(f"strategy:max red score:{max_red_score},r1:{r1},b1:{b1},b2:{b2},r2:{optimal_r2}")
        # Update the optimal strategy for Blue if necessary
        if max_red_score <= min_max_red_score:
            if max_red_score < min_max_red_score:
                blue_optimal_strategy = []
                min_max_red_score = max_red_score
            blue_optimal_strategy.append((b1, b2, optimal_r2))

    logger.debug(f" finished strategy max red score:{min_max_red_score} ,r1:{r1},b1:{b1},b2:{b2},r2:{optimal_r2}")
    return (min_max_red_score, blue_optimal_strategy)


def distance(start, endpoints):
    distances = [math.dist(start, end) for end in endpoints]
    return min(distances)


def distance_int(p, points, n):
    x1, y1 = divmod(p, n)
    x2, y2 = divmod(points[0], n)
    x3, y3 = divmod(points[1], n)
    return min(math.dist((x1, y1), (x2, y2)), math.dist((x1, y1), (x3, y3)))


def calculate_winner(grid_points):
    # Initialize variables to keep track of optimal strategies
    optimal_strategies = []
    max_min_max_red_score = -math.inf
    i=0
    calculations_count=len(grid_points)
    logger.info(f"started:{calculations_count} calculations")
    # Iterate over all possible choices of r1
    for r1 in grid_points:
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        i+=1
        logger.info(f"finished:{i}/{calculations_count} calculations")

        # Update the optimal strategy for Red if necessary
        if min_max_red_score >= max_min_max_red_score:
            if min_max_red_score > max_min_max_red_score:
                optimal_strategies = []
                max_min_max_red_score = min_max_red_score
                logger.info(f"best red score:{max_min_max_red_score}")
            optimal_strategies.append((r1, blue_optimal_strategy))
    logger.info(f"best red score:{max_min_max_red_score}")

    return optimal_strategies


def update_optimal_strategies(optimal_strategies, max_score, new_score, new_strategy):
    if new_score >= max_score:
        if new_score > max_score:
            optimal_strategies = []
            max_score = new_score
            logger.info(f"best red score: {max_score}")
        optimal_strategies.append(new_strategy)
    return optimal_strategies, max_score 

def iterate_get_best_b1_and_b2_based_on_optimal_r2(grid_points,grid_points_chunk, result_queue,process_id):
    # Initialize variables to keep track of optimal strategies
    optimal_strategies = []
    max_min_max_red_score = -math.inf
    
    i=0
    calculations_count=len(grid_points_chunk)
    logger.info(f"process number {process_id} started calculating:{calculations_count} calculations")

    # Iterate over all possible choices of r1
    for r1 in grid_points_chunk:
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        i+=1
        logger.info(f"process number {process_id} finished:{i}/{calculations_count} calculations")
        # Update the optimal strategy for Red if necessary
        optimal_strategies, max_min_max_red_score = update_optimal_strategies(
        optimal_strategies, max_min_max_red_score, min_max_red_score, (r1, blue_optimal_strategy))
    logger.info(f"best red score:{max_min_max_red_score}, finished calculation number {process_id}")

    result_queue.put((max_min_max_red_score,optimal_strategies))
    
    
def calculate_winner_multiprocessing(grid_points):
    num_cores = multiprocessing.cpu_count()
    num_processes = num_cores -1 if num_cores > 2 else num_cores

    chunk_size = len(grid_points) // num_processes
    result_queue = multiprocessing.Queue()

    logger.info(f"start to calculate:{len(grid_points)} calculation")
    processes = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else len(grid_points)
        grid_points_chunk = grid_points[start_idx:end_idx]
        process = multiprocessing.Process(target=iterate_get_best_b1_and_b2_based_on_optimal_r2, args=(grid_points,grid_points_chunk, result_queue,i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
        
    
    optimal_strategies = []
    max_min_max_red_score = -math.inf

    for (min_max_red_score,optimal_strategy) in results:

        optimal_strategies, max_min_max_red_score = update_optimal_strategies(
        optimal_strategies, max_min_max_red_score, min_max_red_score, optimal_strategy)
    logger.info(f"final best red score:{max_min_max_red_score}")
    
    flattened_list = [item for sublist in optimal_strategies for item in sublist]

    return flattened_list

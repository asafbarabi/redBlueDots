import itertools
import math
from logger import get_logger


logger = get_logger(__name__)

def get_best_r2(r1,b1,b2,grid_points):
    optimal_r2 = None
    max_red_score = -math.inf
    for r2 in grid_points:
        if r2 not in (r1, b1, b2):
            red_score = sum(1 for p in grid_points if distance(p, (r1, r2)) < distance(p, (b1, b2)))
            if red_score > max_red_score:
                max_red_score = red_score
                optimal_r2 = r2
    return (max_red_score,optimal_r2)

def distance(start, endpoints):
    distances = [math.dist(start, end) for end in endpoints]
    return min(distances)

def distance_int(p, points, n):
    # Calculate coordinates of p1
    x1, y1 = p % n, p // n
    
    # Calculate coordinates of p2 and p3
    x2, y2 = points[0] % n, points[0] // n
    x3, y3 = points[1] % n, points[1] // n
    
    # Calculate distances squared
    dist_12_sq = (x2 - x1)**2 + (y2 - y1)**2
    dist_13_sq = (x3 - x1)**2 + (y3 - y1)**2
    
    # Return the minimum distance
    return math.sqrt(min(dist_12_sq, dist_13_sq))

def calculate_winner(grid_points):
    # Initialize variables to keep track of optimal strategies
    optimal_strategies =[]
    red_optimal_strategy = []
    blue_optimal_strategy = None
    min_max_red_score = math.inf
    max_min_max_red_score=-math.inf
    blue_optimal_strategy_optimal_r2=None
    
    
    # Iterate over all possible choices of r1
    for r1 in grid_points:
        # Generate all possible pairs of points that Blue can choose
        blue_pairs = list(itertools.combinations(set(grid_points) - {r1}, 2))
        min_max_red_score=math.inf
        # Find the optimal pair of b1 and b2 for this value of r1
        for b1, b2 in blue_pairs:
            # Find the optimal value of r2 for this pair of b1 and b2
            max_red_score,optimal_r2= get_best_r2(r1,b1,b2,grid_points)

            # Update the optimal strategy for Blue if necessary
            #TODO add support to more then one optimal strategy for blue
            if max_red_score < min_max_red_score:
                blue_optimal_strategy = (b1, b2)
                min_max_red_score =max_red_score
                blue_optimal_strategy_optimal_r2=optimal_r2

            
        # Update the optimal strategy for Red if necessary
        if min_max_red_score==max_min_max_red_score:
            red_optimal_strategy=(r1,blue_optimal_strategy_optimal_r2)
            optimal_strategies.append((red_optimal_strategy,blue_optimal_strategy))
        elif min_max_red_score>max_min_max_red_score:
            max_min_max_red_score=min_max_red_score
            red_optimal_strategy =(r1,blue_optimal_strategy_optimal_r2)
            optimal_strategies =[(red_optimal_strategy,blue_optimal_strategy)]
            logger.info(f"current optimal strategy for red:{optimal_strategies} score for red:{max_min_max_red_score - 2}")

    return optimal_strategies
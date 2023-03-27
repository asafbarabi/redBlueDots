import itertools
import math
from logger import get_logger


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

        # Update the optimal strategy for Blue if necessary
        if max_red_score <= min_max_red_score:
            if max_red_score < min_max_red_score:
                blue_optimal_strategy = []
                min_max_red_score = max_red_score
            blue_optimal_strategy.append((b1, b2, optimal_r2))

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

    # Iterate over all possible choices of r1
    for r1 in grid_points:
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)

        # Update the optimal strategy for Red if necessary
        if min_max_red_score >= max_min_max_red_score:
            if min_max_red_score > max_min_max_red_score:
                optimal_strategies = []
                max_min_max_red_score = min_max_red_score
                logger.info(f"best red score:{max_min_max_red_score}")
            optimal_strategies.append((r1, blue_optimal_strategy))
    logger.info(f"best red score:{max_min_max_red_score}")

    return optimal_strategies

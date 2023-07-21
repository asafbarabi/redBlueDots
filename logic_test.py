import unittest
from Logic import distance, distance_int, get_best_r2, get_best_b1_and_b2_based_on_optimal_r2, get_red_score
import pickle
import os


class TestOptimalStrategies(unittest.TestCase):

    def test_distance(self):
        self.assertAlmostEqual(distance(
            (0, 0), [(3, 4), (4, 3)]), 5.0)
        
    def test_CPU_count(self):
        num_cores = os.cpu_count()
        self.assertGreater(num_cores, 11)
        print("Number of CPU cores:", num_cores)

    def test_get_red_score(self):
        r1 = (0, 0)
        r2 = (1, 0)
        b1 = (0, 1)
        b2 = (1, 1)
        grid_points = ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1))
        red_score = get_red_score(r1, r2, b1, b2, grid_points)
        self.assertEqual(red_score, 1)

    def test_distance_int(self):
        self.assertAlmostEqual(distance_int(0, [6, 10], 5), 1.4142135623730951)

    def test_get_best_r2(self):
        grid_points = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1),
                       (2, 1), (0, 2), (1, 2), (2, 2)]
        r1, b1, b2 = (0, 0), (1, 0), (0, 1)
        max_red_score, optimal_r2 = get_best_r2(r1, b1, b2, grid_points)
        self.assertEqual(max_red_score, 3)
        self.assertEqual(optimal_r2, [(1, 1)])
        
        
    def test_get_best_special(self):
        with open('grid.pickle', 'rb') as f:
            grid_points = pickle.load(f)
        r1 = (4, 3)
        b1= (3,3)
        b2= (7,5)
        r2= (8,5)
        max_red_score, optimal_r2 = get_best_r2(r1, b1, b2, grid_points)
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        self.assertEqual(min_max_red_score, 3)

    def test_get_best_b1_and_b2_based_on_optimal_r2(self):
        grid_points = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1),
                       (2, 1), (0, 2), (1, 2), (2, 2)]
        r1 = (1, 2)
        min_max_red_score, blue_optimal_strategy = get_best_b1_and_b2_based_on_optimal_r2(
            r1, grid_points)
        self.assertEqual(min_max_red_score, 2.5)
        self.assertEqual(blue_optimal_strategy[0], ((
            0, 1), (2, 1), [(0, 0), (1, 0), (2, 0)]))
        self.assertEqual(blue_optimal_strategy[1], ((0, 1), (2, 0), [
                         (0, 0), (1, 0), (1, 1)]))
        self.assertEqual(blue_optimal_strategy[2], ((2, 1), (0, 0), [
                         (1, 0), (2, 0), (1, 1)]))

    # def test_calculate_winner(self):
    #     grid_points = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1),
    #                    (2, 1), (0, 2), (1, 2), (2, 2)]
    #     optimal_strategies = calculate_winner(grid_points)
    #     self.assertEqual(
    #         optimal_strategies[0][0], ((1, 1), (0, 0)))
    #     self.assertEqual(
    #         optimal_strategies[0][1], ((0, 1), (2, 1)))


if __name__ == '__main__':
    unittest.main()

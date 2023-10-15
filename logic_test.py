import unittest
from Logic import distance, distance_int, get_best_r2, get_best_b1_and_b2_based_on_optimal_r2, get_red_score,calculate_winner,calculate_winner_symmetric,calculate_winner_multiprocessing
from Shapes import *
import pickle
import os
import pprint



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
        
    def my_deep_sort(self,optimal_strategies):
        #n suppose to be the same as init n
        n = 15
        Points_optimal_strategies = []
        for Strategy in sorted(optimal_strategies):
            r1 = self.convert_grid_to_point(Strategy[0], n)
            b1s_b2s_r2s = []
            for subStrategy in sorted(Strategy[1]):
                b1 = self.convert_grid_to_point(subStrategy[0], n)
                b2 = self.convert_grid_to_point(subStrategy[1], n)
                #it does not matter the order of those points
                b1, b2 = (b2, b1) if b2 > b1 else (b1, b2)
                r2s = []
                for subSubStrategy in sorted(subStrategy[2]):
                    r2 = self.convert_grid_to_point(subSubStrategy, n)
                    r2s.append(r2)
                b1s_b2s_r2s.append((b1, b2, sorted(r2s)))
            Points_optimal_strategies.append((r1, sorted(b1s_b2s_r2s)))
        return sorted(Points_optimal_strategies)
    
    def convert_grid_to_point(self, num, n):
        return num[0]+num[1]*n
        
    def test_Calculate_winner3x3_vs_symmetric(self):
        optimal_strategies_regular = calculate_winner_symmetric(square3x3_grid)
        optimal_strategies_regular= self.my_deep_sort(optimal_strategies_regular)
        square3x3_strategy_local= square3x3_strategy
        square3x3_strategy_local= self.my_deep_sort(square3x3_strategy_local)
        self.assertEqual(optimal_strategies_regular,square3x3_strategy_local)
        
    def test_Calculate_winner_square434(self):
        optimal_strategies = calculate_winner_symmetric(square434_grid)
        optimal_strategies =self.my_deep_sort(optimal_strategies)
        square434_strategy_local= square434_strategy
        square434_strategy_local=self.my_deep_sort(square434_strategy_local)
        self.assertEqual(optimal_strategies,square434_strategy_local)
        
    def test_Calculate_winner_3x3_vs_multi_processing(self):
        optimal_strategies = calculate_winner_multiprocessing(square3x3_grid)
        optimal_strategies =self.my_deep_sort(optimal_strategies)
        square3x3_strategy_local= square3x3_strategy
        square3x3_strategy_local=self.my_deep_sort(square3x3_strategy_local)
        self.assertEqual(optimal_strategies,square3x3_strategy_local)
        
    def test_Calculate_winner_6x6_vs_multi_processing(self):
        optimal_strategies = calculate_winner_multiprocessing(square6x6_grid)
        optimal_strategies =self.my_deep_sort(optimal_strategies)
        square6x6_strategy_local= square6x6_strategy
        square6x6_strategy_local=self.my_deep_sort(square6x6_strategy_local)
        self.assertEqual(optimal_strategies,square6x6_strategy_local)
        
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
    unittest.main(buffer=False)

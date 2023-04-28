from UI import UI
import tkinter as tk
from itertools import product
from logger import get_logger
from Logic import calculate_winner, distance_int
import random



class GameBoard:

    MAX_BOARD_SIZE=20

    def __init__(self, master, width=500, height=500, n=15):
        self.logger = get_logger(__name__)
        self.logger.info('Logging initialized')
        self.master = master
        self.selected_point_gameboard_color="green"
        self.unselected_point_color="white"
        self.width = width
        self.height = height
        self.n = n
        self.points = []
        self.selected_points = set()
        self.ui = UI(self.master)
        self.draw_points()
        self.optimal_strategies = None
        self.ui.canvas.bind("<Button-1>", self.handle_click)
        self.init_r1_r2_b1_b2()
        
        # Range for buttons that generate game board
        board_range=(2,self.MAX_BOARD_SIZE)
        random_gameboard_range=(4,self.n**2)

        # Add two buttons to the bottom of the canvas
        self.clear_button = self.ui.add_button(
            but_parent=self.master, but_text="Clear", but_command=self.clear_board, but_width=10)
        self.calculate_winner_button = self.ui.add_button(but_parent=self.master, but_text="Calculate Winner",
                                          but_command=self.calculate_winner, but_width=15, but_state='disabled')
        
        self.ui.add_label_and_text_box_and_button(self.master,self.generate_grid_board,board_range,"board grid size:","generate")
        self.ui.add_label_and_text_box_and_button(self.master,self.generate_random_game_board,random_gameboard_range,"Game board Random shape size:","generate")
        self.winner_label=self.ui.add_label(self.master,"")
        

    def generate_random_game_board(self,size):
        #TODO add here edge cases checks
        self.clear_board()

        # Select a random starting point and add it to the shape
        seed = random.randint(0, self.n*self.n-1)
        shape = set([seed])
        self.select_point_for_gameboard(seed)

        # Loop until the shape reaches the desired size
        while len(shape) < size:
            # Find the neighbors of the current shape
            neighbors = self.find_shape_neighbors(shape,self.n)

            # If there are no available neighbors, stop generating the shape
            if not neighbors:
                break

            # Select a random neighbor and add it to the shape
            next_point = random.choice(list(neighbors))
            shape.add(next_point)
            self.select_point_for_gameboard(next_point)
            
    def find_shape_neighbors(self,shape,n):
        neighbors = set()
        for point in shape:
            x, y = divmod(point, n)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                #take into account the fact that some points in the grid are not neighbors because they are at the boundaries between two adjacent rows
                if 0 <= nx < n and 0 <= ny < n:
                    neighbor = nx * n + ny
                    if neighbor not in shape and abs(ny-y) <= 1:
                        neighbors.add(neighbor)
        return neighbors
        
        
    # def generate_grid_gameboard(self,k):
    #     #TODO add here edge cases checks
    #     self.clear_board()
    #     for i in range(k):
    #         for j in range(k):
    #             self.select_point_for_gameboard((i*self.n)+j)
    
    def generate_grid_board(self,size):
        self.ui.remove_all_circles()
        self.points = []
        self.n = size
        self.draw_points()
        self.ui.canvas.bind("<Button-1>", self.handle_click)
        self.init_r1_r2_b1_b2()
        self.clear_button.pack_forget()
        self.calculate_winner_button.pack_forget()
        # add the buttons with a consistent side value
        self.clear_button.pack(side="bottom", padx=10, pady=10)
        self.calculate_winner_button.pack(side="bottom", padx=10, pady=10)
                

    def calculate_winner(self):
        grid = self.convertPointsToGrid(self.selected_points)
        gridWinner = calculate_winner(grid)
        self.optimal_strategies = self.convert_grid_to_points(gridWinner)
        self.logger.info(f"optimal_strategy:{self.optimal_strategies}")
        for strategy in self.optimal_strategies:
            r1 = strategy[0]
            self.ui.set_circle_color(self.points[r1], "red")
        self.ui.change_button_state(self.calculate_winner_button,button_state='disabled')

    def draw_points(self):
        radius = min(self.width, self.height) / (3 * self.n)
        for i, j in product(range(self.n), range(self.n)):
            x = ((2*j + 1) * self.width) / (2*self.n)
            y = ((2*i + 1) * self.height) / (2*self.n)
            circle = self.ui.add_circle(x, y, radius)
            self.points.append(circle)

    def convertPointsToGrid(self, points):
        gridPoints = []
        for point in points:
            x = point.id % self.n
            y = point.id // self.n
            gridPoints.append((x, y))
        return gridPoints

    def convert_grid_to_points(self, optimal_strategies):
        Points_optimal_strategies = []
        for Strategy in optimal_strategies:
            r1 = self.convert_grid_to_point(Strategy[0], self.n)
            b1s_b2s_r2s = []
            for subStrategy in Strategy[1]:
                b1 = self.convert_grid_to_point(subStrategy[0], self.n)
                b2 = self.convert_grid_to_point(subStrategy[1], self.n)
                r2s = []
                for subSubStrategy in subStrategy[2]:
                    r2 = self.convert_grid_to_point(subSubStrategy, self.n)
                    r2s.append(r2)
                b1s_b2s_r2s.append((b1, b2, r2s))
            Points_optimal_strategies.append((r1, b1s_b2s_r2s))
        return Points_optimal_strategies

    def convert_grid_to_point(self, num, n):
        return num[0]+num[1]*n

    def showBlueOptimal(self, r1):
        for strategy in self.optimal_strategies:
            # show the blue strategy based on the red strategy that's been picked
            if strategy[0] == r1:
                for subStrategy in strategy[1]:
                    b1 = subStrategy[0]
                    b2 = subStrategy[1]
                    self.change_circle_color(b1, "blue")
                    self.change_circle_color(b2, "blue")
            # remove other red strategies
            if self.points[strategy[0]].get_color() == "red" and strategy[0] != r1:
                self.change_circle_color(strategy[0], "green")

    def remove_other_blue_strategies(self, b1, b2, selected_points):
        for point in selected_points:
            if(point.get_color() == "blue" and point.id != b1 and point.id != b2):
                self.change_circle_color(point.id, "green")

    def showR2Optimal(self, b):
        for strategy in self.optimal_strategies:
            # show the red strategy based on the blue strategy that's been picked
            if strategy[0] == self.r1:
                for subStrategy in strategy[1]:
                    if(subStrategy[0] == b or subStrategy[1] == b):
                        self.b1 = subStrategy[0]
                        self.b2 = subStrategy[1]
                        # TODO check what to show if more then one r2 is optimal - now its selecting the first
                        self.r2 = subStrategy[2][0]
                        self.change_circle_color(self.r2, "red")
                        break_outer_loop = True
                        break
                if break_outer_loop:
                    break
        self.remove_other_blue_strategies(
            self.b1, self.b2, self.selected_points)

    def get_border_color_based_on_distance(self, point):
        distance_red = distance_int(point, (self.r1, self.r2), self.n)
        distance_blue = distance_int(point, (self.b1, self.b2), self.n)
        if distance_red < distance_blue:
            return "red"
        elif distance_blue < distance_red:
            return "blue"
        else:
            return "green"
        
    def get_distances(self,point):
        distance_red = distance_int(point, (self.r1, self.r2), self.n)
        distance_blue = distance_int(point, (self.b1, self.b2), self.n)
        return (distance_red,distance_blue)

    def show_winner(self):
        red_score=0
        blue_score=0
        for p in self.selected_points:
            if p.id not in (self.r1, self.r2, self.b1, self.b2):
                distance_red,distance_blue = self.get_distances(p.id)
                if distance_red < distance_blue:
                    new_border_color= "red"
                    red_score+=1
                elif distance_blue < distance_red:
                    new_border_color= "blue"
                    blue_score+=1
                else:
                    new_border_color = "green"
                    red_score+=0.5
                    blue_score+=0.5
                
                self.change_circle_color(p.id, self.unselected_point_color, new_border_color)
                
        self.update_winner_label_with_winner(red_score,blue_score)
        
        
    def update_winner_label_with_winner(self,red_score,blue_score):
        label_text=""
        if red_score>blue_score:
            label_text=f"Red won with score of {red_score}"
        elif blue_score>red_score:
            label_text=f"Blue won with score of {blue_score}"
        else:
            label_text=f"Tie with score of {blue_score}"
            
        self.ui.change_label_text(self.winner_label,label_text)
        
    
    def clear_board(self):
        self.logger.info('clear board initiated')
        self.ui.change_label_text(self.winner_label,"")
        for point in self.points:
            self.change_circle_color(point.id, self.unselected_point_color)
        self.selected_points = set()
        self.ui.change_button_state(self.calculate_winner_button,button_state='disabled')
        self.init_r1_r2_b1_b2()

    def init_r1_r2_b1_b2(self):
        self.r1 = None
        self.r2 = None
        self.b1 = None
        self.b2 = None

    def getPointClicked(self, event):
        x, y = event.x, event.y
        overlapping_items = self.ui.canvas.find_overlapping(
            x, y, x, y)
        if overlapping_items:
            point = overlapping_items[0]-1
            return point
        else:
            return None

    def change_circle_color(self, point, new_color, border_color='black'):
        self.ui.set_circle_color(
            self.points[point], new_color, border_color)

    def handle_click(self, event):
        point = self.getPointClicked(event)
        if point is None:
            self.logger.debug(f"didn't press on point")
            return
        self.logger.debug(f"point {point} was clicked")
        color = self.points[point].get_color()
        
        # after choosing possible optimal strategies for Red
        if self.r1 == None and color == "red":
            self.r1 = point
            self.showBlueOptimal(self.r1)
            return

        # after choosing possible optimal strategies for blue
        if self.r2 == None and color == "blue":
            self.showR2Optimal(point)
            self.show_winner()
            return
        
        # When choosing game board
        if self.r1 == None:
            if color == "white":
                self.select_point_for_gameboard(point)
            else:
                self.unselect_point_for_gameboard(point)

            
            
    
    def select_point_for_gameboard(self,point):
        self.logger.debug(f"points: {len(self.points)} point:{point}")
        self.selected_points.add(self.points[point])
        self.ui.change_button_state(self.calculate_winner_button,button_state='normal' if len(
            self.selected_points) >= 4 else 'disabled')
        self.change_circle_color(point, self.selected_point_gameboard_color)
        
    def unselect_point_for_gameboard(self,point):
        self.selected_points.remove(self.points[point])
        self.ui.change_button_state(self.calculate_winner_button,button_state='disabled' if len(
            self.selected_points) < 4 else 'normal')
        self.change_circle_color(point, self.unselected_point_color)
        


if __name__ == '__main__':
    root = tk.Tk()
    game_board = GameBoard(root)
    root.mainloop()

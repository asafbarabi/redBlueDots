from circle_drawer import CircleDrawer
import tkinter as tk
from itertools import product
from logger import get_logger
from Logic import calculate_winner, distance_int


class GameBoard:

    def __init__(self, master, width=500, height=500, n=5):
        self.logger = get_logger(__name__)
        self.logger.info('Logging initialized')
        self.master = master
        self.width = width
        self.height = height
        self.n = n
        self.canvas = tk.Canvas(
            self.master, width=self.width, height=self.height)
        self.canvas.pack()
        self.points = []
        self.selectedPoints = set()
        self.circle_drawer = CircleDrawer(self.canvas)
        self.draw_points()
        self.optimal_strategies = None
        print("Canvas object:", self.canvas)
        self.circle_drawer.canvas.bind("<Button-1>", self.handle_click)

        self.r1 = None
        self.r2 = None
        self.b1 = None
        self.b2 = None

        # Add two buttons to the bottom of the canvas
        self.button1 = tk.Button(
            self.master, text="Clear", command=self.clear_board, width=10, height=2)
        self.button1.pack(side="top", padx=10, pady=10)
        self.button2 = tk.Button(self.master, text="Calculate Winner",
                                 command=self.CalculateWinner, state='disabled',  width=15, height=2)
        self.button2.pack(side="top", padx=10, pady=10)

    def CalculateWinner(self):
        grid = self.convertPointsToGrid(self.selectedPoints)
        self.optimal_strategies = self.convert_grid_to_points(
            calculate_winner(grid))
        self.logger.info(f"optimal_strategy:{self.optimal_strategies}")
        for strategy in self.optimal_strategies:
            r1 = strategy[0]
            self.circle_drawer.set_circle_color(self.points[r1], "red")
        self.button2.configure(state='disabled')

    def draw_points(self):
        radius = min(self.width, self.height) / (3 * self.n)
        for i, j in product(range(self.n), range(self.n)):
            x = ((2*j + 1) * self.width) / (2*self.n)
            y = ((2*i + 1) * self.height) / (2*self.n)
            circle = self.circle_drawer.add_circle(x, y, radius)
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
            r1 = self.convert_grid_to_point(Strategy[0][0], self.n)
            r2 = self.convert_grid_to_point(Strategy[0][1], self.n)
            b1 = self.convert_grid_to_point(Strategy[1][0], self.n)
            b2 = self.convert_grid_to_point(Strategy[1][1], self.n)
            Points_optimal_strategies.append((r1, r2, b1, b2))
        return Points_optimal_strategies

    def convert_grid_to_point(self, num, n):
        return num[0]+num[1]*n

    def showBlueOptimal(self, r1):
        for strategy in self.optimal_strategies:
            # show the blue strategy based on the red strategy that's been picked
            if strategy[0] == r1:
                self.b1 = strategy[2]
                self.b2 = strategy[3]
                self.change_circle_color(self.b1, "blue")
                self.change_circle_color(self.b2, "blue")
            # remove other red strategies
            if self.points[strategy[0]].get_color() == "red" and strategy[0] != r1:
                self.change_circle_color(strategy[0], "green")

    def showR2(self, b):
        for strategy in self.optimal_strategies:
            # show the blue strategy based on the red strategy that's been picked
            if (strategy[0] == self.r1) and (strategy[2] == b or strategy[3] == b):
                r2 = strategy[1]
                self.r2 = r2
                self.change_circle_color(r2, "red")

    def get_border_color_based_on_distance(self, point):
        distance_red = distance_int(point, (self.r1, self.r2), self.n)
        distance_blue = distance_int(point, (self.b1, self.b2), self.n)
        if distance_red < distance_blue:
            return "red"
        elif distance_blue < distance_red:
            return "blue"
        else:
            return "black"

    def show_winner(self):
        for p in self.selectedPoints:
            if p.id not in (self.r1, self.r2, self.b1, self.b2):
                new_border_color = self.get_border_color_based_on_distance(p.id)
                self.change_circle_color(p.id, "white", new_border_color)

    def clear_board(self):
        self.logger.info('clear board pressed')
        for point in self.points:
            self.change_circle_color(point.id, "white")
        self.selectedPoints=set()
        self.button2.configure(state='disabled')
        self.r1 = None
        self.r2 = None
        self.b1 = None
        self.b2 = None

    def getPointClicked(self, event):
        x, y = event.x, event.y
        overlapping_items = self.circle_drawer.canvas.find_overlapping(
            x, y, x, y)
        if overlapping_items:
            point = overlapping_items[0]-1
            return point
        else:
            return None

    def change_circle_color(self, point, new_color, border_color='black'):
        self.circle_drawer.set_circle_color(
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
            self.showR2(point)
            self.show_winner()
            return
        if self.r1 == None:
            if color == "white":
                newColor = "green"
                self.selectedPoints.add(self.points[point])
                self.button2.configure(state='normal' if len(
                    self.selectedPoints) >= 4 else 'disabled')
            else:
                newColor = "white"
                self.selectedPoints.remove(self.points[point])
                self.button2.configure(state='disabled' if len(
                    self.selectedPoints) < 4 else 'normal')
            self.change_circle_color(point, newColor)


if __name__ == '__main__':
    root = tk.Tk()
    game_board = GameBoard(root)
    root.mainloop()

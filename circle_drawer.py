import tkinter as tk


class Circle:
    def __init__(self, id, x, y, radius, color='white'):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius,
                           self.y + self.radius, fill=self.color, outline='black', width=3, tags=('circle', self.id))

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color


class CircleDrawer:
    def __init__(self, master, width=500, height=500):
        self.master = master
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(
            self.master, width=self.width, height=self.height)
        self.canvas.pack()
        self.circle_count = 0

    def add_circle(self, x, y, radius, color='white'):
        circle = Circle(self.circle_count, x, y, radius, color)
        circle.draw(self.canvas)
        self.circle_count += 1
        return circle

    def set_circle_color(self, circle, color, border_color='black'):
        circle.set_color(color)
        self.canvas.itemconfigure(
            circle.id+1, fill=color, outline=border_color)

    def get_circle_color(self, circle):
        return circle.get_color()

    def redraw(self):
        self.canvas.delete('circle')
        self.circle_count = 0

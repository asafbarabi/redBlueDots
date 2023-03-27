import tkinter as tk
from tkinter import messagebox


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


class UI:
    def __init__(self, master, width=500, height=500):
        self.master = master
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(
            self.master, width=self.width, height=self.height)
        self.canvas.pack()
        self.circle_count = 0

    def deleteCanvas(self):
        self.canvas.delete("all")
        self.canvas.pack()

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

    def add_button(self, but_parent, but_text, but_command, but_width, but_height=2, but_state='active'):
        button = tk.Button(master=but_parent, text=but_text, command=but_command,
                           width=but_width, height=but_height, state=but_state)
        button.pack(side="bottom", padx=10, pady=10)
        return button

    def add_label_and_text_box_and_button(self, master, button_command, range=(2, 10), label_text="Label:", button_text="Button", error_message="Please enter a number between range"):
        if error_message == "Please enter a number between range":
            error_message = f"Please enter a number between {range[0]} to {range[1]}"

        frame = tk.Frame(master)
        frame.pack(side=tk.BOTTOM)

        label = tk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)

        textbox = tk.Entry(frame)
        textbox.pack(side=tk.LEFT)

        button = tk.Button(
            frame, text=button_text, command=lambda: self.check_input(textbox.get(), range, button_command))
        button.pack(side=tk.RIGHT)

    def check_input(self, str, range, command):
        try:
            value = int(str)
            if value < range[0] or value > range[1]:
                # Display error message if value is out of range
                messagebox.showerror(
                    "Error", "Please enter a number between 2 and 10")
            else:
                # Call create_new_board() function if value is valid
                command(value)
        except ValueError:
            # Display error message if input is not a valid integer
            messagebox.showerror("Error", "Please enter a valid integer")
            
    def add_label(self, master,label_text="Label:"):
        frame = tk.Frame(master)
        frame.pack(side=tk.BOTTOM)

        label = tk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)
        return label
    
    def change_label_text(self,label,label_text):
        label.config(text=label_text)
        
    def change_button_state(self,button,button_state):
        button.configure(state=button_state)

    def remove_all_circles(self):
        self.canvas.delete('circle')
        self.circle_count = 0
        self.canvas.destroy()
        self.canvas = tk.Canvas(
            self.master, width=self.width, height=self.height)
        self.canvas.pack()

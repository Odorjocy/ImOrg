import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox as mb
from PIL import Image, ImageTk
import os
import shutil


def refresh_checkboxes():
    global collections
    global collection_assignments
    global images
    global current_image_index

    image = images[current_image_index]

    for collection in collections:
        collection_name = collection.cget("text")
        assignments = collection_assignments[collection_name]
        if image in assignments:
            collection.select()
        else:
            collection.deselect()


def assign_a_collection(collection_name):
    global collection_assignments
    global current_image_index
    global images

    picture_name = images[current_image_index]

    if picture_name in collection_assignments[collection_name]:
        collection_assignments[collection_name].remove(picture_name)
    else:
        collection_assignments[collection_name].append(picture_name)



def initialize_a_folder(path):
    global number_of_images, images, menu_bar
    files_in_working_dir = []

    for file in os.listdir(path):
        if file.endswith(".jpg") or file.endswith(".png"):
            files_in_working_dir.append(file)

    if len(files_in_working_dir) > 0:
        images = files_in_working_dir
        number_of_images = len(files_in_working_dir)
        status_text = f"Opened folder: {working_directory} | Number of files: {number_of_images}"
        statusvar.set(status_text)
        first_image_path = os.path.join(path, files_in_working_dir[0])
        show_image(first_image_path)
        new_collection_button.config(state="active")
        menu_bar.entryconfig(2, state="active")
        menu_bar.entryconfig(3, state="active")
        menu_bar.entryconfig(4, state="active")
        previous_image_button.config(state="active")
        next_image_button.config(state="active")
    else:
        mb.showwarning("Warning", "There is picture in this folder!")


def show_image(path):
    global image_label
    initial_image = Image.open(path)
    if initial_image.width > IMAGE_GEOMETRY_Y or initial_image.height > IMAGE_GEOMETRY_X:
        divider = 0
        new_width = 0
        new_height = 0
        too_big = True
        while too_big:
            divider += 2
            new_width = int(initial_image.width / divider)
            new_height = int(initial_image.height / divider)
            if IMAGE_GEOMETRY_Y > new_width and IMAGE_GEOMETRY_X > new_height:
                too_big = False

        temp_image = initial_image.resize((new_width, new_height))
        image = ImageTk.PhotoImage(image=temp_image, width=400, height=40)
    else:
        image = ImageTk.PhotoImage(image=initial_image)

    image_label.config(image=image)
    image_label.image = image


def open_a_folder():
    global working_directory
    working_directory = filedialog.askdirectory()
    if len(working_directory) > 1:
        initialize_a_folder(working_directory)


def show_next_image():
    global number_of_images, current_image_index, images, working_directory

    if current_image_index < number_of_images -1:
        current_image_index += 1
        next_image_path = os.path.join(working_directory, images[current_image_index])
    else:
        next_image_path = os.path.join(working_directory, images[0])
        current_image_index = 0

    show_image(next_image_path)
    refresh_checkboxes()


def show_previous_image():
    global number_of_images, current_image_index, images, working_directory

    if current_image_index < number_of_images -1:
        current_image_index -= 1
        next_image_path = os.path.join(working_directory, images[current_image_index])
        show_image(next_image_path)
    else:
        next_image_path = os.path.join(working_directory, images[0])
        current_image_index = 0
        show_image(next_image_path)

    refresh_checkboxes()


def close():
    check = mb.askyesno("Exit", "Do you want to exit?")

    if check:
        main_window.destroy()


def add_new_collection():
    global collections
    global collection_window_last_position
    global collection_assignments
    collection_name = simpledialog.askstring(title="Adding new collection", prompt="What should be the name?", parent=main_window)
    if collection_name:
        new_collection = tk.Checkbutton(main_window, text=collection_name, variable=collection_name, onvalue=1, offvalue=0, font=("Times", "14", "bold italic"), command=lambda: assign_a_collection(collection_name))
        collections.append(new_collection)
        collection_assignments[collection_name] = []
        collections_canvas.create_window(90, collection_window_last_position, window=new_collection)
        collection_window_last_position += 30


def clear():
    global images
    global working_directory
    global collections
    global collection_window_last_position

    collection_window_last_position = 65
    working_directory = None
    statusvar.set("Ready")
    images = []
    image_label.config(image="")
    new_collection_button.config(state="disabled")
    menu_bar.entryconfig(2, state="disabled")
    menu_bar.entryconfig(3, state="disabled")
    previous_image_button.config(state="disabled")
    next_image_button.config(state="disabled")
    for collection in collections:
        collection.destroy()


def checker(option):
    global method_window
    print(option)
    method_window.destroy()
    return option


def method_question(title, text):
    global method_window
    method_window = tk.Toplevel(width=500)
    method_window.title(title)
    message = text
    tk.Label(method_window, text=message, pady=15, padx=15, width=30).grid(row=0, column=1)
    tk.Button(method_window, text="Copy", padx=10, pady=10, command=lambda: checker("Copy")).grid(row=1, column=0)
    tk.Button(method_window, text="Move", padx=10, pady=10, command=lambda: checker("Move")).grid(row=1, column=1)


def finish(method):
    global collection_assignments
    global working_directory
    keys = collection_assignments.keys()
    check = mb.askyesno("Finish the project", "Do you really want to finish the session?")

    if check and len(keys) > 0:
        for collection in keys:
            collection_images = collection_assignments[collection]
            collection_path = os.path.join(working_directory, collection)
            if not os.path.exists(collection_path):
                os.makedirs(collection_path)

            for image in collection_images:
                original_path = os.path.join(working_directory, image)
                new_path = os.path.join(collection_path, image)
                shutil.copy(original_path, new_path)

        if method == "Move":
            for collection in keys:
                collection_images = collection_assignments[collection]
                for image in collection_images:
                    original_path = os.path.join(working_directory, image)
                    if os.path.exists(original_path):
                        os.remove(original_path)

        clear()
        mb.showinfo("Session finished", "The session has been finished, all the related data has been cleared")
    else:
        mb.showwarning("No data", "You dont have any collection to fill")


# Variables
MAIN_GEOMETRY_Y = 1400
MAIN_GEOMETRY_X = 900
STATUSBAR_GEOMETRY_X = 25
COLLECTION_GEOMETRY_Y = round(MAIN_GEOMETRY_Y / 5.5)
COLLECTION_GEOMETRY_X = MAIN_GEOMETRY_X - STATUSBAR_GEOMETRY_X
IMAGE_GEOMETRY_Y = MAIN_GEOMETRY_Y - 260
IMAGE_GEOMETRY_X = MAIN_GEOMETRY_X - 25
MAIN_GEOMETRY = f"{MAIN_GEOMETRY_Y}x{MAIN_GEOMETRY_X}"
collections = []
collection_remove_buttons = []
collection_assignments = {}
collection_window_last_position = 65
border_color = "gray"
method_window = None
working_directory = None
images = []
number_of_images = 0
current_image_index = 0

main_window = tk.Tk()
main_window.geometry(MAIN_GEOMETRY)
main_window.title("Image organizer")

photo = tk.PhotoImage(file='ImOrg.png')
main_window.iconphoto(False, photo)
menu_bar = tk.Menu(main_window)
menu_bar.add_command(label="Open", command=open_a_folder)
menu_bar.add_command(label="Close current", command=clear, state="disabled")
finish_menu = tk.Menu(menu_bar, tearoff=False)
finish_menu.add_command(label="Copy", command=lambda: finish(method="Copy"))
finish_menu.add_command(label="Move", command=lambda: finish(method="Move"))
menu_bar.add_cascade(label="Finish", menu=finish_menu, state="disabled")
menu_bar.add_command(label="Exit", command=close)

collections_canvas = tk.Canvas(main_window, width=COLLECTION_GEOMETRY_Y, height=COLLECTION_GEOMETRY_X, highlightthickness=1, highlightbackground=border_color)
collection_label = tk.Label(text="Collections", width=COLLECTION_GEOMETRY_Y, height=2, font=("Times", "14", "bold italic"), highlightthickness=2, highlightbackground=border_color)
new_collection_button = tk.Button(collections_canvas, text="+Add new collection", command=add_new_collection, state="disabled")
collections_canvas.create_window(120, 18, window=collection_label)
collections_canvas.create_window(60, 860, anchor=tk.W, window=new_collection_button)

image_canvas = tk.Canvas(main_window, width=IMAGE_GEOMETRY_Y, height=IMAGE_GEOMETRY_X, highlightthickness=1, highlightbackground=border_color)
image_label = tk.Label(image_canvas)
image_canvas.create_window(572.5, 437.5, anchor=tk.CENTER, window=image_label)
next_image_button = tk.Button(image_canvas, width=2, height=10, text=">", command=show_next_image, state="disabled")
previous_image_button = tk.Button(image_canvas, width=2, height=10, text="<", command=show_previous_image, state="disabled")
image_canvas.create_window(1120, 437.5, window=next_image_button)
image_canvas.create_window(20, 437.5, window=previous_image_button)
image_canvas.grid(row=0, column=1)

statusvar = tk.StringVar()
statusvar.set("Ready")
bottom_bar = tk.Label(main_window, textvariable=statusvar, anchor="w", bd=1, relief=tk.SUNKEN)
collections_canvas.grid(row=0, column=0)
bottom_bar.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)

main_window.config(menu=menu_bar)
main_window.mainloop()
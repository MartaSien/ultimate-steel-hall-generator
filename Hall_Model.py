import io
from PIL import Image
import PySimpleGUI as sg
from pathlib import Path
import configparser

# TITLE:        PARAMETRIC HALL MODEL
# DESCRIPTION:  THE SCRIPT GENERATES A PNG IMAGES OF A STEEL HALL WITH CHOSEN PARAMETERS
# AUTHOR:       MARTA SIENKIEWICZ
# LICENSE:      Creative Commons Zero v1.0 Universal

# ------------------------ GLOBAL VARIABLES ------------------------ #

Resources = Path('Resources')                            # Path to resources folder
Sandwich = Path(Resources / "Sandwich")                  # Path to resources sandwich folder
Construction = Path(Resources / "Construction")          # Path to resources construction folder
Equipment = Path(Resources / "Equipment")                # Path to resources equipment folder

config = configparser.ConfigParser()
config.read(Resources / "config.rc")                     # Configuration file

# ---------------------- FUNCTION DEFINITIONS ---------------------- #
def recolor_transparent(image, RGB):
    alpha = image.split()[-1] # Get alpha
    colour_overlay = Image.new("RGBA", image.size,(RGB[0],RGB[1],RGB[2]))
    image = Image.blend(image, colour_overlay, 0.5).convert("RGBA") # Apply colour overlay
    image.putalpha(alpha) # Apply original alpha
    return image


def create_window(type):
    if type == 'Help':
        type_layout = [[sg.Text('To create an image change options in the left column and select "Submit".\nTo save your image to .png file select "Save".\n', justification='center')]]
        return sg.Window('Help', font=("Raleway", 14)).Layout(type_layout)
    elif type == 'Version':
        type_layout = [[sg.Text('AUTHOR: Marta Sienkiewicz\nLICENCE: Creative Commons Zero v1.0 Universal', justification='center')]]
        return sg.Window('Version', font=("Raleway", 14)).Layout(type_layout)
    elif type == 'MaxEquipment':
        type_layout = [[sg.Text('Maximum number of equipment exceeded. To fit more doors, gates and windows adjust the number of hall segments.', justification='center')]]
        return sg.Window('Version', font=("Raleway", 14)).Layout(type_layout)

def overlay_image(foreground_list, background, x, y):   # Overlaying one image over many images:
    for overlay in foreground_list:
        background.paste(overlay, (x,y), overlay)

def update_image(bio, values, event):
   
    # Getting hall dimentions
    segments = int(values['-FRAMES-'])
    doors_num = int(values['-DOORS-'])
    gates_num = int(values['-GATES-'])
    
    # Do doors and gates have enough space?
    if (doors_num>segments):
        doors_num = segments
        h_window = create_window('MaxEquipment')
        event = h_window.Read()
    if (gates_num>segments):
        gates_num = segments
        h_window = create_window('MaxEquipment')
        event = h_window.Read()
    
    hallWidth = int(values['-WIDTH-'])
    hallHeight = int(values['-HEIGHT-'])

    # Background image size (resizes with the hall size)
    im_width = 900 + 275 * (segments-1)
    im_height = 710 + 198 * (segments-1)

    target_image = Image.new("RGBA", (im_width, im_height), (255, 255, 255)) # Creates an image with white background.

    # Loading construction and equipment images
    frame = Image.open(Construction / "frame_{0}_3.png".format(hallWidth))
    sidewall = Image.open(Sandwich / "wall.png")
    wallplus = Image.open(Sandwich / "wall_plus.png" ) # For adding hall height
    gableplus = Image.open(Sandwich / "gable_plus_{0}.png".format(hallWidth)) # For adding hall height 
    roof = Image.open(Sandwich / "roof_{}.png".format(hallWidth))
    gablewall = Image.open(Sandwich / "gablewall_{0}.png".format(hallWidth))
    doors = Image.open(Equipment / "door.png")
    gate = Image.open(Equipment / "gate.png")
    
    if values['-COLOR-'] == 'RAL7016':
        RGB = [53,60,68]
    elif values['-COLOR-'] == 'RAL3011': #'RAL5010', 'RAL6011'
        RGB = [158,25,30]
    elif values['-COLOR-'] == 'RAL5010':
        RGB = [1,92,157]
    elif values['-COLOR-'] == 'RAL6011':
        RGB = [106,140,92]
    else:
        RGB = [157,159,162]

    sidewall = recolor_transparent(sidewall, RGB)
    gablewall = recolor_transparent(gablewall, RGB)
    wallplus = recolor_transparent(wallplus, RGB)
    gableplus = recolor_transparent(gableplus, RGB)
    roof = recolor_transparent(roof, RGB)

    main_queue = []
    if values['-VIEW-']:
        main_queue.append(frame)
    else:
        main_queue.append(sidewall)
        main_queue.append(gablewall)
    
    heightOffset = hallHeight - 3

    # Main overlay loop
    for offset in range(segments):
        overlay_image(main_queue, target_image, 177*offset, 102*offset)
        
    # Equipment and roof overlay loop
    if not values['-VIEW-']:
        for offset in range(segments): # Height offset
             for offset2 in range(heightOffset):
                target_image.paste(wallplus, (177*offset, 102*offset + offset2*30), wallplus)
                if offset == segments-1: # Gable wall
                    target_image.paste(gableplus, (177*offset, 102*offset + offset2*30), gableplus)
        for offset in range(doors_num):
            target_image.paste(doors, (177*offset, 102*offset + heightOffset*30), doors)
        for offset in range(gates_num):
            target_image.paste(gate, (177*offset, 102*offset + heightOffset*30), gate)
        for offset in range(segments): # Roof
            target_image.paste(roof, (177*offset, 102*offset), roof)
           

    if event == "Save":
        target_image.save("hall.png", "PNG")
    
    target_image.thumbnail((int(config['img size']['thumbw']), int(config['img size']['thumbh']))) 
    target_image.save(bio, format="PNG")

def main_menu():
    sg.theme('Light Gray 1') # Menu box theme
    menu_column = [
        [ # ---- 0
            sg.Text('Welcome to the ultimate steel hall generator.\n\n', justification='center') 
        ], [ # ---- 1
            sg.Text('Number of segments:') 
        ], [ # ----2 
            sg.Spin(values=('1', '2', '3', '4',  '5',  '6'), initial_value=int(config['DEFAULT']['segments']), size=(20, 10), key="-FRAMES-")
        ], [ # ---- 3
            sg.Text('Hall width [m]:') 
        ], [# ----4 
            sg.Spin(values=('6', '12', '18'), initial_value=int(config['DEFAULT']['width']), size=(20, 10), key="-WIDTH-")
        ], [ # ---- 5
            sg.Text('Hall height [m]:')
        ], [# ----6 
            sg.Spin(values=('3','4','5','6','7','8','9'), initial_value=int(config['DEFAULT']['height']), size=(20, 10), key="-HEIGHT-")
        ],[ # ---- 7
            sg.Text('Number of doors:') 
        ], [# ----8
            sg.Spin(values=('0', '1', '2', '3', '4',  '5',  '6'), initial_value=1, size=(20, 10), key="-DOORS-")
        ], [ # ---- 9
            sg.Text('Number of gates:') 
        ], [# ----10
            sg.Spin(values=('0', '1', '2', '3', '4',  '5',  '6'), initial_value=1, size=(20, 10), key="-GATES-")
        ], [ # ---- 11
            sg.Text('Colour:') 
        ], [# ----12
            sg.Spin(values=('RAL7016', 'RAL9007', 'RAL3011', 'RAL5010', 'RAL6011'), initial_value='RAL7016', size=(20, 10), key="-COLOR-")
        ], 
        [ # ----13
            sg.Checkbox('Construction frame view', default=False, key="-VIEW-")
        ]
        ]
    viewer_column = [ # Hall view and action buttons
        [ # ----6
            sg.Image(size=(485, 375), key="-IMAGE-")
        ],[ # ----7
            sg.Submit(), sg.Save(), sg.Cancel(), sg.Help(), sg.Button('Version')
        ]
    ]
    
    layout = [ # Whole script window
    [
    sg.Column(menu_column),
    sg.VSeperator(),
    sg.Column(viewer_column),
    ]
    ]

    window = sg.Window('Steel Hall Generator', font=("Raleway", 14)).Layout(layout)

    while True:
        event, values = window.Read() # Run the window until an "event" is triggered
        if event == "Submit" or event == "Save":
            bio = io.BytesIO() # Byte stream
            update_image(bio, values, event)
            window["-IMAGE-"].update(data=bio.getvalue())
        elif event == "Help" or event == "Version":
            h_window = create_window(event)
            event = h_window.Read()
        elif event is None or event == "Cancel":
            return "Program closed"

# ---------------------- MAIN ---------------------- #

if __name__ == "__main__":
    menu = main_menu()
    print(menu)

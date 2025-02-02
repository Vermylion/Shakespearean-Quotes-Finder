from tkinter import *
from tkinter.ttk import *

from bs4 import BeautifulSoup
import requests
import time


# Titles
titles_links = {
    "All's Well That Ends Well": 'allswell',
    'As You Like It': 'asyoulikeit',
    'The Comedy of Errors': 'comedy_errors',
    'Cymbeline': 'cymbeline',
    "Love's Labours Lost": 'lll',
    'Measure for Measure': 'measure',
    'The Merry Wives of Windsor': 'merry_wives',
    'The Merchant of Venice': 'merchant',
    "A Midsummer Night's Dream": 'midsummer',
    'Much Ado About Nothing': 'much_ado',
    'Pericles, Prince of Tyre': 'pericles',
    'Taming of the Shrew': 'taming_shrew',
    'The Tempest': 'tempest',
    'Troilus and Cressida': 'troilus_cressida',
    'Twelfth Night': 'twelfth_night',
    'Two Gentlemen of Verona': 'two_gentlemen',
    "Winter's Tale": 'winters_tale',
    'Henry IV, part 1': '1henryiv',
    'Henry IV, part 2': '2henryiv',
    'Henry V': 'henryv',
    'Henry VI, part 1': '1henryvi',
    'Henry VI, part 2': '2henryvi',
    'Henry VI, part 3': '3henryvi',
    'Henry VIII': 'henryviii',
    'King John': 'john',
    'Richard II': 'richardii',
    'Richard III': 'richardiii',
    'Antony and Cleopatra': 'cleopatra',
    'Coriolanus': 'coriolanus',
    'Hamlet': 'hamlet',
    'Julius Caesar': 'julius_caesar',
    'King Lear': 'lear',
    'Macbeth': 'macbeth',
    'Othello': 'othello',
    'Romeo and Juliet': 'romeo_juliet',
    'Timon of Athens': 'timon',
    'Titus Andronicus': 'titus'
}


def load_play(title_link):
    global full_play
    
    start_loading()
    
    # Get play
    try:
        full_r = session.get(f'http://shakespeare.mit.edu/{title_link}/full.html')
    except:
        show_error()
        return False
    
    soup_full = BeautifulSoup(full_r.text, 'html.parser')
    
    # Parse the whole play and store it as {Scene: [(Character, Quote)]}
    full_play = {}
    
    blockquotes = soup_full.find_all('blockquote')
    # Remove first blockquote as it isn't a quote
    del blockquotes[0]
    
    for blockquote in blockquotes:
        
        character = blockquote.find_previous('b').get_text().title()
        
        raw_scene = blockquote.find_next('a').get('name')
        
        # Check if blockquote is a stage direction
        if raw_scene.count('.') != 2:
            continue
        
        scene = 'Act {0}, Scene {1}'.format(*raw_scene.split('.'))
        
        lines = blockquote.find_all('a')
        quote = "\n".join(line.get_text() for line in lines)
        
        if scene not in full_play:
            full_play[scene] = []
        
        full_play[scene].append((character, quote))
        
    # Configure combo boxes
    scenes = [''] + list(full_play.keys())
    
    characters = [''] + list(set(character for scene in full_play.values() for character, _ in scene))
    characters.sort()
    
    combo_scene.config(values = scenes)
    combo_scene.current(1)
    
    combo_chrct.config(values = characters)
    combo_chrct.current(1)
    
    stop_loading()


def set_quotes(scene, character, keywords):
    global full_play
    
    start_loading()
    
    scenes = [scene] if scene != '' else list(full_play.keys())
    
    quotes = {}
    for scene in scenes:
        
        quotes[scene] = []
        
        for chrct, quote in full_play[scene]:
            
            if character != '' and chrct != character:
                continue
                
            if len(keywords) != 0:
                
                quote_modif = ''.join(e for e in quote.lower() if e.isalnum() or e.isspace())
                words = quote_modif.split()
                
                valids = [word for word in words for keyword in keywords if keyword.lower() == word]
                
                if len(valids) == 0:
                    continue
                        
            quotes[scene].append((chrct, quote))
            
    display_quotes(quotes)
    
    # Reset keywords
    combo_keywords.config(values = [])
    combo_keywords.delete(0, 'end')
    combo_keywords.insert(0, '')
    
    stop_loading()
    
    
def display_quotes(quotes):
    global offset
    
    # Number of total quotes
    num_quotes = sum(len(quotes[scene]) for scene in quotes)
    globals()["quotes_found_lbl"] = Label(second_frame, text = f'Found {num_quotes} Quotations:', foreground="#39353a")
    globals()["quotes_found_lbl"].place(x = 35, y = 0)

    # Set starting offset
    offset = 35
    
    iter = 0
    for scene in quotes:
    
        for quote in quotes[scene]:
            chrct, quote = quote
        
            globals()['label_info' + str(iter)] = Label(second_frame, text = f'{chrct} - {scene}', foreground="#555256")
            globals()['label_info' + str(iter)].place(x = 35, y = offset)
            
            offset += 20
        
            globals()['button' + str(iter)] = Button(second_frame, text = quote, width=50, command = lambda n=iter: copy_quote(n))
            globals()['button' + str(iter)].place(x = 35, y = offset)
            
            offset += (quote.count('\n') - 1) * 15 + 55
            
            iter += 1
            
    resize()


def resize():
    global frame_height

    second_frame.configure(height = frame_height - 1)
    scrollregion = canvas.bbox("all")
    canvas.configure(scrollregion = scrollregion)
    
    
def reset_region():
    for widget in second_frame.winfo_children():
        widget.destroy()
        
    window.update_idletasks()
    

def start_loading():
    reset_region()
    
    global offset; offset = 0
    resize()
    
    globals()["loading_lbl"] = Label(second_frame, text = "Loading...", foreground="#555256", font=("TkDefaultFont", 12))
    globals()["loading_lbl"].place(relx=0.5, y=30, anchor=CENTER)
    
    window.update_idletasks()
    
    
def stop_loading():
    globals()["loading_lbl"].destroy()
    
    window.update_idletasks()
    
    
def show_error():
    globals()["loading_lbl"] = Label(second_frame, text = "An error occurred. Please try again.", foreground="#555256", font=("TkDefaultFont", 12))
    globals()["loading_lbl"].place(relx=0.5, y=30, anchor=CENTER)
    
    window.update_idletasks()


def copy_quote(btn_nbr):
    window.clipboard_clear()
    window.clipboard_append(globals()['button' + str(btn_nbr)]['text'])


def on_resize(event):
    global frame_height, offset, is_loaded

    c_width = window.winfo_width()  # Get dynamic width
    height = window.winfo_height()  # Get dynamic height
    
    if c_width != width and is_loaded:
        # Manually combat weird shift when pinned to right side of screen
        if window.winfo_screenwidth() - window.winfo_rootx() < 400:
            window.geometry(f'{width}x{height}+{window.winfo_screenwidth() - width - 8}+{window.winfo_rooty() - 32}')
        
        else:
            window.geometry(f'{width}x{height}')
    
    main_frame.config(height=height + 5)
    frame_height = height + 5
    second_frame.config(height=frame_height + offset)

    canvas.configure(height=height + 5)
    
    # Update scrollregion
    scrollregion = canvas.bbox("all")
    canvas.configure(scrollregion=(0, 0, c_width, max(scrollregion[3] - height + 160, height - 160)))

    # Place scrollbar dynamically based on current window width
    scrollbar.place(x=c_width - 17, y=0, height=height - 155)
    
def on_search():
    if combo_keywords.get() != '':
        update_combo_keywords(combo_keywords.get())
    
    set_quotes(combo_scene.get(), combo_chrct.get(), combo_keywords['values'])
    
    
def update_combo_keywords(keyword):
    combo_keywords.config(values = list(combo_keywords['values']) + [keyword])
    combo_keywords.delete(0, 'end')
    combo_keywords.insert(0, '')


if __name__ == '__main__':
    # Session
    session = requests.Session()
    
    # Loading check
    is_loaded = False

    # Window
    window = Tk()
    width = 380
    height = 600
    window.geometry(f'{width}x{height}')
    window.bind("<Configure>", on_resize)
    window.resizable(0, 1)
    window.title('Shakespearean Quotes Finder')
    window.attributes('-topmost', True)

    # Canvas (to draw on)
    canvas = Canvas(window, width = width, height = width)
    canvas.place(x = 0, y = 0)

    # Title Selection
    lbl_title = Label(window, text = 'Title:')
    lbl_title.place(x = 30, y = 10)

    titles_links = dict(sorted(titles_links.items()))

    combo_title = Combobox(window, width = 25, values = list(titles_links.keys()), state = 'readonly')
    combo_title.current(0)
    combo_title.place(x = 70, y = 10)

    btn_title = Button(window, text = 'Go', command = lambda: load_play(titles_links[combo_title.get()]))
    btn_title.place(x = 260, y = 8)

    canvas.create_line(20, 45, 355, 45, fill = 'light grey', width = 2)

    # Character Selection
    lbl_chrct = Label(window, text = 'Character:')
    lbl_chrct.place(x = 10, y = 60)

    combo_chrct = Combobox(window, width = 15, values = [], state = 'readonly')
    combo_chrct.place(x = 80, y = 60)

    # Scene Selection
    lbl_scene = Label(window, text = 'Scene:')
    lbl_scene.place(x = 215, y = 60)

    combo_scene = Combobox(window, width = 13, values = [], state = 'readonly')
    combo_scene.place(x = 265, y = 60)

    # Key Words
    lbl_keywords = Label(window, text = 'Key Word:')
    lbl_keywords.place(x = 10, y = 100)

    combo_keywords = Combobox(window, width = 15, values = [])
    combo_keywords.place(x = 80, y = 100)
    
    combo_keywords.bind("<Return>", lambda e: update_combo_keywords(combo_keywords.get()))

    btn_keywords = Button(window, text = 'Add', width = 5, command = lambda: update_combo_keywords(combo_keywords.get()))
    btn_keywords.place(x = 200, y = 98)

    # Search
    btn_search = Button(window, text = 'Search...', command = on_search)
    btn_search.place(x = 275, y = 98)

    canvas.create_line(20, 140, 355, 140, fill = 'light grey', width = 2)

    # Scroll Region
    offset = 0

    main_frame = Frame(window, width = width, height = height)
    main_frame.place(x = 0, y = 150)

    canvas = Canvas(main_frame, width = width + 5, height = height + 5)
    canvas.place(x = -5, y = -5)

    scrollbar = Scrollbar(main_frame, orient = VERTICAL, command = canvas.yview)
    scrollbar.place(x = width - 17, y = 0, height = height - 160)

    canvas.configure(yscrollcommand = scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

    def _on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    frame_height = height + 5
    second_frame = Frame(canvas, width = width + 5, height = frame_height + offset)

    canvas.create_window(0, 0, window = second_frame, anchor = "nw")
    
    window.wait_visibility()
    is_loaded = True

    window.mainloop()

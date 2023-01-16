from tkinter import *
from tkinter.ttk import *

from bs4 import BeautifulSoup
import requests

#from TkHoverMsg import HoverInfo

scene_href = []
quotations = []
global_height = 0

def load_info(title):
    global titles, keywords, scenes, scene_href

    title_links = ['allswell', 'asyoulikeit', 'comedy_errors', 'cymbeline', 'lll', 'measure', 'merry_wives', 'merchant', 'midsummer', 'much_ado', 'pericles', 'taming_shrew', 'tempest', 'troilus_cressida', 'twelfth_night', 'two_gentlemen', 'winters_tale', '1henryiv', '2henryiv', 'henryv', '1henryvi', '2henryvi', '3henryvi', 'henryviii', 'john', 'richardii', 'richardiii', 'cleopatra', 'coriolanus', 'hamlet', 'julius_caesar', 'lear', 'macbeth', 'othello', 'romeo_juliet', 'timon', 'titus']
    title = title_links[titles.index(title)]
    #Get characters
    full_r = requests.get(f'http://shakespeare.mit.edu/{title}/full.html')
    soup_full = BeautifulSoup(full_r.text, 'html.parser')

    characters = ['']
    characters_html = soup_full.find_all('b')

    for character in characters_html:
        characters.append(character.text.title())

    characters = list(set(characters))
    characters.sort()

    #Get Scenes
    scenes_r = requests.get(f'http://shakespeare.mit.edu/{title}/index.html')
    soup_scenes = BeautifulSoup(scenes_r.text, 'html.parser')

    scenes_p = soup_scenes.find_all('p')
    scenes_p = scenes_p[2]

    scenes_a = scenes_p.find_all('a')

    scene_href = []
    scenes = ['']
    for href in scenes_a:
        scene_href.append(href['href'])
        scene_dotted = href['href'].removeprefix(title + '.').removesuffix('.html')
        scenes.append('Act {0}, Scene {1}'.format(scene_dotted.split('.')[0], scene_dotted.split('.')[1], href.text))

    #Set Elements
    combo_scene.config(values = scenes)
    combo_scene.current(1)
    combo_chrct.config(values = characters)
    combo_chrct.current(1)

def resize():
    global frame_height

    #print('Frame height:', frame_height, '; Offset:', offset)
    second_frame.configure(height = frame_height - 1)
    scrollregion = canvas.bbox("all")
    #canvas.configure(scrollregion = (0, 0, 385, global_height + 5))
    canvas.configure(scrollregion = scrollregion)
    #print(canvas['scrollregion'])

def copy_quote(btn_nbr):
    global quotations

    window.clipboard_clear()
    window.clipboard_append(quotations[btn_nbr])

def find_quotes(title, character, scene):
    global titles, keywords, scenes, scene_href, offset, quotations

    #Reset Canvas/Board
    n = 0
    while True:
        try:
            globals()['button' + str(n)].destroy()
        except:
            break
        n += 1

    offset = 0

    #Get quotations
    title_links = ['allswell', 'asyoulikeit', 'comedy_errors', 'cymbeline', 'lll', 'measure', 'merry_wives', 'merchant', 'midsummer', 'much_ado', 'pericles', 'taming_shrew', 'tempest', 'troilus_cressida', 'twelfth_night', 'two_gentlemen', 'winters_tale', '1henryiv', '2henryiv', 'henryv', '1henryvi', '2henryvi', '3henryvi', 'henryviii', 'john', 'richardii', 'richardiii', 'cleopatra', 'coriolanus', 'hamlet', 'julius_caesar', 'lear', 'macbeth', 'othello', 'romeo_juliet', 'timon', 'titus']
    title = title_links[titles.index(title)]

    if scene != '':
        speech_r = requests.get(f'http://shakespeare.mit.edu/{title}/{scene_href[scenes.index(scene) - 1]}')
        soup_speech = BeautifulSoup(speech_r.text, 'html.parser')
        print(f'http://shakespeare.mit.edu/{title}/{scene_href[scenes.index(scene) - 1]}')
    else:
        speech_r = requests.get(f'http://shakespeare.mit.edu/{title}/full.html')
        soup_speech = BeautifulSoup(speech_r.text, 'html.parser')
        print(f'http://shakespeare.mit.edu/{title}/full.html')

    characters_speaking = soup_speech.find_all('b')
    speeches = soup_speech.find_all('blockquote')
    for x in range(len(speeches)):
        speeches_lignes = speeches[x].find_all('a')
        speech_total = ''
        for lign in speeches_lignes:
            speech_total += lign.text + '\n'
        speeches[x] = speech_total.removesuffix('\n')

    del_index = 0
    for i in range(len(speeches)):
        if speeches[i - del_index] == '':
            del speeches[i - del_index]
            #del characters_speaking[i - del_index]
            del_index += 1

    for x in range(len(characters_speaking)):
        characters_speaking[x] = characters_speaking[x].text.title()

    if combo_keywords.get() != '':
        keywords.append(combo_keywords.get())

    quotation_speaker = []
    quotations = []
    print(len(speeches), len(characters_speaking))
    for i in range(min(len(speeches), len(characters_speaking))):
        keyinside = 0
        if characters_speaking[i] == character or character == '':
            if not keywords == []:
                for key in keywords:
                    if speeches[i].find(key) != -1:
                        keyinside += 1
            if keyinside == len(keywords):
                quotations.append(speeches[i])
                quotation_speaker.append(characters_speaking[i])


    print('Quotations found:', len(quotations))

    for x in range(len(quotations)):
        globals()['button' + str(x)] = Button(second_frame, text = quotations[x], width = 50, command = lambda q = x: copy_quote(q))
        globals()['button' + str(x)].place(x = 35, y = offset + 10)
        #CreateToolTip(globals()['button' + str(x)], text = f'{quotation_speaker[x]}, {scene}')

        offset += 60
        offset += (quotations[x].count('\n') - 1) * 15

    resize()

    keywords = []
    combo_keywords.config(values = keywords)
    combo_keywords.delete(0, 'end')
    combo_keywords.insert(0, '')

def on_resize(event):
    global frame_height, offset, global_height

    width = window.winfo_width()
    height = window.winfo_height()
    global_height = height
    
    main_frame.config(height = height + 5)
    frame_height = height + 5
    second_frame.config(height = frame_height + offset)

    canvas.configure(height = height + 5)
    scrollregion = canvas.bbox("all")
    canvas.configure(scrollregion = (0, 0, 385, [scrollregion[3] - height + 160 if scrollregion[3] - height + 160 > height - 160 else scrollregion[3]]))
    scrollbar.place(x = width - 17, y = 0, height = height - 155)

window = Tk()
width = 380
height = 600
window.geometry(f'{width}x{height}')
window.bind("<Configure>", on_resize)
window.resizable(0, 1)
window.title('Shakespearian Quotes Finder')
window.attributes('-topmost', True)

#Canvas (to draw on)
canvas = Canvas(window, width = 400, height = 600)
canvas.place(x = 0, y = 0)

#Title Selection
lbl_title = Label(window, text = 'Title:')
lbl_title.place(x = 30, y = 10)

titles = ["All's Well That Ends Well", 'As You Like It', 'The Comedy of Errors', 'Cymbeline', "Love's Labours Lost", 'Measure for Measure', 'The Merry Wives of Windsor', 'The Merchant of Venice', "A Midsummer Night's Dream", 'Much Ado About Nothing', 'Pericles, Prince of Tyre', 'Taming of the Shrew', 'The Tempest', 'Troilus and Cressida', 'Twelfth Night', 'Two Gentlemen of Verona', "Winter's Tale", 'Henry IV, part 1', 'Henry IV, part 2', 'Henry V', 'Henry VI, part 1', 'Henry VI, part 2', 'Henry VI, part 3', 'Henry VIII', 'King John', 'Richard II', 'Richard III', 'Antony and Cleopatra', 'Coriolanus', 'Hamlet', 'Julius Caesar', 'King Lear', 'Macbeth', 'Othello', 'Romeo and Juliet', 'Timon of Athens', 'Titus Andronicus']
combo_title = Combobox(window, width = 25, values = titles, state = 'readonly')
combo_title.current(0)
combo_title.place(x = 70, y = 10)

btn_title = Button(window, text = 'Go', command = lambda: load_info(combo_title.get()))
btn_title.place(x = 260, y = 8)

canvas.create_line(20, 45, 355, 45, fill = 'light grey', width = 2)

#Character Selection
lbl_chrct = Label(window, text = 'Character:')
lbl_chrct.place(x = 10, y = 60)

characters = []
combo_chrct = Combobox(window, width = 15, values = characters, state = 'readonly')
combo_chrct.place(x = 80, y = 60)

#Scene Selection
lbl_scene = Label(window, text = 'Scene:')
lbl_scene.place(x = 215, y = 60)

scenes = []
combo_scene = Combobox(window, width = 13, values = scenes, state = 'readonly')
combo_scene.place(x = 265, y = 60)

#Key Words
lbl_keywords = Label(window, text = 'Key Word:')
lbl_keywords.place(x = 10, y = 100)

keywords = []
combo_keywords = Combobox(window, width = 15, values = keywords)
combo_keywords.place(x = 80, y = 100)

btn_keywords = Button(window, text = 'Add', width = 5, command = lambda: (keywords.append(combo_keywords.get()), combo_keywords.config(values = keywords)))
btn_keywords.place(x = 200, y = 98)

#Search
btn_search = Button(window, text = 'Search...', command = lambda: find_quotes(combo_title.get(), combo_chrct.get(), combo_scene.get()))
btn_search.place(x = 275, y = 98)

canvas.create_line(20, 140, 355, 140, fill = 'light grey', width = 2)

#Scroll Region
offset = 0

main_frame = Frame(window, width = width + 17, height = height)
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

window.mainloop()
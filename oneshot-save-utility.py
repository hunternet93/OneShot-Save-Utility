# OneShot Save Utility
# https://github.com/hunternet93/oneshot-save-utility

# ===========
# UI Settings
# ===========

bgcolor = '#13041B'
textcolor = '#FFFFAA'
highlightcolor = '#888844'
font = ('vgasys', 14)


# ===============
# Initial imports
# ===============

from rubymarshal.reader import load as rb_load
from rubymarshal.writer import write as rb_write

import platform
import base64
import shutil
import psutil
import os

if platform.python_version_tuple()[0] == '2':
    from Tkinter import *
    import tkMessageBox as tkmessagebox
else:
    from tkinter import *
    import tkinter.messagebox as tkmessagebox


# =========================================
# Find and initalize the OneShot directory
# =========================================

# Currently only supports Windows, support for Linux and MacOS will be added after OneShot is available on those platforms.

if platform.system() == 'Windows':
    dirpath = os.path.join(os.path.expandvars('%appdata%'), 'OneShot')

psettingspath = os.path.join(dirpath, 'p-settings.dat')
archivepath = os.path.join(dirpath, 'OneShot Save Utility Archive')
if not os.path.exists(archivepath): os.makedirs(archivepath)

# =====================
# Save / load functions
# =====================

def check_oneshot_running():
    # Random trivia: the psutil Process class has a oneshot() method. It weirded me out of a second when I came across it in the docs. :D
    if 'oneshot.exe' in [psutil.Process(i).name() for i in psutil.pids()]:
        tkmessagebox.showwarning('OneShot running', 'OneShot is currently running. Please close OneShot before using Oneshot Save Utility.')
        return True
    
    else: return False

def update_loadnamelist():
    saves = []

    for filename in os.listdir(archivepath):
        try:
            saves.append(base64.urlsafe_b64decode(filename[:-4].encode('utf-8')).decode())
        except:
            continue
            
    loadnamelist.delete(0, END)
    for save in sorted(saves): loadnamelist.insert(END, save)
    
def save():
    if check_oneshot_running(): return

    title = savenamebox.get().strip()
    if len(title) == 0:
        tkmessagebox.showwarning('No title entered', 'Please enter a title for your save.')
        return

    # Save titles are base64-encoded to prevent issues with using illegal characters in filenames.
    path = os.path.join(archivepath, base64.urlsafe_b64encode(title.encode('utf-8')).decode() + '.dat')

    if os.path.exists(path):
        if not tkmessagebox.askyesno('Overwrite?', 'A save with the name "{}" already exists, do you want to overwrite it?'.format(title)):
            return

    shutil.copy(os.path.join(dirpath, 'save.dat'), path)
    
    savenamebox.delete(0, END)

    tkmessagebox.showinfo('Save created', 'Save "{}" was successfully created.'.format(title))
    update_loadnamelist()
    
    
def load():
    if check_oneshot_running(): return

    title = loadnamelist.get(loadnamelist.curselection()[0])
    path = os.path.join(archivepath, base64.urlsafe_b64encode(title.encode('utf-8')).decode() + '.dat')
    shutil.copy(path, os.path.join(dirpath, 'save.dat'))
    
    tkmessagebox.showinfo('Save loaded', 'Save "{}" was successfully loaded.'.format(title))
    
    
def delete():
    title = loadnamelist.get(loadnamelist.curselection()[0])

    if tkmessagebox.askyesno('Confirm delete', 'Delete save "{}"?'.format(title)):
        path = os.path.join(archivepath, base64.urlsafe_b64encode(title.encode('utf-8')).decode() + '.dat')
        os.remove(path)
    
    update_loadnamelist()


def get_playername():
    with open(psettingspath, 'rb') as psettings:
        # Ruby marshal format is weird, you have to load past the first chunks of data to get to the name.
        rb_load(psettings)
        rb_load(psettings)
        name = rb_load(psettings)
        
        namebox.delete(0, END)
        namebox.insert(0, name)

def set_playername():
    if check_oneshot_running(): return

    name = namebox.get().strip()
    
    if len(name) == 0:
        tkmessagebox.showwarning('No name entered', 'Please enter a name.')
        return

    with open(psettingspath, 'rb') as psettings:
        data = [rb_load(psettings), rb_load(psettings), name]
    
    with open(psettingspath, 'wb') as psettings:
        for d in data: rb_write(psettings, d)
    
    tkmessagebox.showinfo('Name changed', 'Player name has been changed to {}.'.format(name))
    
    namebox.delete(0, END)
    namebox.insert(0, name)        
    
    
# =================
# Initialize the UI
# =================

# Yeah, Tkinter's ugly, but also comes bundled with Python, so...

root = Tk()
root.title('OneShot Save Utility')
root.config(bg = bgcolor)
root.minsize(400, 600)

saveframe = Frame(root, bg = bgcolor)
saveframe.pack(fill = BOTH, expand = 1, padx = 5, pady = 5)

Label(saveframe, text = 'Create Save:', bg = bgcolor, fg = textcolor, font = font).pack()
savenamebox = Entry(saveframe, selectbackground = highlightcolor, bg = bgcolor, fg = textcolor, font = font)
savenamebox.pack(fill = X)

Button(saveframe, text = 'Save', command = save, bg = bgcolor, fg = textcolor, font = font).pack(anchor = S, expand = 1)

Frame(root, borderwidth = 1).pack(fill = X)

loadframe = Frame(root, bg = bgcolor)
loadframe.pack(fill = BOTH, expand = 1, padx = 20, pady = 20)

Label(loadframe, text = 'Load Save:', bg = bgcolor, fg = textcolor, font = font).pack()

loadnamelist = Listbox(loadframe, selectmode = BROWSE, selectbackground = highlightcolor, height = 5, bg = bgcolor, fg = textcolor, font = font)
update_loadnamelist()
loadnamelist.pack(fill = BOTH, expand = 1, padx = 5)

buttonframe = Frame(loadframe, bg = bgcolor)
buttonframe.pack(fill = X)

Button(loadframe, text = 'Load', command = load, bg = bgcolor, fg = textcolor, font = font).pack(side = LEFT, expand = 1)
Button(loadframe, text = 'Delete', command = delete, bg = bgcolor, fg = 'red', font = font).pack(side = RIGHT, expand = 1)

Frame(root, borderwidth = 1).pack(fill = X)

nameframe = Frame(root, bg = bgcolor)
nameframe.pack(fill = BOTH, expand = 1, padx = 5, pady = 5)

Label(nameframe, text = 'Set Player Name:', bg = bgcolor, fg = textcolor, font = font).pack()
namebox = Entry(nameframe, selectbackground = highlightcolor, bg = bgcolor, fg = textcolor, font = font)
get_playername()
namebox.pack(fill = X)

Button(nameframe, text = 'Set', command = set_playername, bg = bgcolor, fg = textcolor, font = font).pack(side = LEFT, expand = 1)

# =========================
# Run the Tkinter main loop
# =========================
root.mainloop()

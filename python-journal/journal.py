import tkinter as tk
import tkinter.ttk as ttk
import os
from tkinter import filedialog as fd

root = tk.Tk()
root.minsize(900, 500)
root.geometry("1400x900")
root.title("Notebook")
tk.Grid.rowconfigure(root, 0, weight = 1)
tk.Grid.columnconfigure(root, 0, weight = 1)

filename = ""
fileopened = ""
hiderotation = 0
filepaths = []
filepath = ""

s = ttk.Style()
s.theme_use("clam")
s.configure("TButton", relief = "flat")
s.configure("TRadiobutton", relief = "flat", font = ("System", 12))
s.configure("Vertical.TScrollbar", troughcolor = "#000", background = "#ffcc12")
s.map("TRadiobutton",
  background = [("!active", "#000"), ("active", "#000"), ("pressed", "#000")],
  foreground = [("!active", "#ffcc12"), ("active", "#ffdd23"), ("pressed", "#ffdd23")]
)
s.map("TButton",
  background = [("!active", "#000"), ("active", "#222"), ("pressed", "#222")],
  foreground = [("!active", "#ffcc12"), ("active", "#ffdd23"), ("pressed", "#ffdd23")]
)
s.map("Vertical.TScrollbar",
  background = [("pressed", "#ffcc12"), ("active", "#ffdd23")],
)

def openfile():
  global filename
  filename = fd.askopenfilename()
  if str(filename) == "()":
    return None
  filepaths.append(str(filename))
  fileopened = open(filename, "r")
  fileread = fileopened.read()
  basename = os.path.split(filename)[1]
  editor.delete("1.0", "end")
  editor.insert("1.0", fileread)
  fileopened.close()
  filesmenu.insert("end", basename)
  filesmenu.selection_set(0)
  filesmenu.activate(0)

def hide():
  global hiderotation
  if hiderotation % 2 == 0:
    divider.forget(menu)
  else:
    divider.add(menu)
    divider.paneconfigure(menu, minsize = 300, before = editor)
  hiderotation += 1

def savekey(event):
  global filename
  if not filename == "":
    filesaved = open(filename, "w+")
    filesaved.write(editor.get("1.0", "end"))
    filesaved.close()

def save():
  global filename
  if not filename == "":
    filesaved = open(filename, "w+")
    filesaved.write(editor.get("1.0", "end"))
    filesaved.close()

def new():

  def submit(event):
    global filename
    newname = newfileinput.get()
    filename = f"created/{newname}.txt"
    filepaths.append(str(filename))
    try:
      newfile = open(filename, "x")
    except FileExistsError:
      print(f"\"{str(filename)}\" already exists. Choose a different name.")
    else:
      newfile.close()
    fileopened = open(filename, "r")
    fileread = fileopened.read()
    fileopened.close()
    newfilename.destroy()

    editor.delete("1.0", "end")
    editor.insert("1.0", fileread)
    filesmenu.insert("end", f"{newname}.txt")
    filesmenu.selection_set(0)
    filesmenu.activate(0)
  
  newfilename = tk.Toplevel(root)
  newfilename.minsize(400, 200)
  newfilename.maxsize(400, 200)
  newfilename.title("Choose File Name")
  newfileprompt = tk.Label(newfilename, text = "Enter a name:")
  newfileinput = tk.Entry(newfilename, width = 16, background = "#ffdd23")
  newfileinput.bind("<Return>", submit)
  newfileprompt.place(relx = 0.5, rely = 0.43, anchor = "c")
  newfileinput.place(anchor = "c", relx = 0.5, rely = 0.57)
  newfileinput.focus_set()

def destroy(event):
  root.destroy()
  
def select(event):
  global filepath
  if str(filesmenu.curselection()) == "()":
    return None
  for item in filesmenu.curselection():
    filepath = filepaths[item]
  fileopened = open(filepath, "r")
  fileread = fileopened.read()
  editor.delete("1.0", "end")
  editor.insert("1.0", fileread)
  fileopened.close()

############
# GUI      #
############

menubar = tk.Menu(root, background = "#ffcc12", activebackground = "#ffdd23")
menubar.add_command(label = " < ", font = ("System", 12), command = hide)
menubar.add_command(label = " New ", font = ("System", 12), command = new)
menubar.add_command(label = " Open ", font = ("System", 12), command = openfile)
menubar.add_command(label = " Save ", font = ("System", 12), command = save)
root.config(menu = menubar)

divider = tk.PanedWindow(root, orient = "horizontal", borderwidth = 0)
scroll = ttk.Scrollbar(root, orient = "vertical")#, bg = "#ffcc12", troughcolor = "#000", activebackground = "#ffdd23")
scroll.pack(side = "right", fill = "y")
editor = tk.Text(divider, yscrollcommand = scroll.set, bg = "#222", fg = "#fff", insertbackground = "#fff", font = ("Courier", 10), wrap = "none", highlightthickness = 0)
editor.grid(column = 1, row = 0, sticky = "nesw")
scroll.config(command = editor.yview)
menu = tk.Frame(divider, background = "#000", height = 900, width = 140)
menu.grid(column = 0, row = 0, rowspan = 3, sticky = "nesw")
fileslabel = tk.Label(menu, text = "FILES", font = ("Roboto", 14), bg = "#000", anchor = "w", fg = "#ffdd23")
fileslabel.pack(pady = 20, padx = 24)
filesmenu_border = tk.Frame(menu, bd = 0, background = "#222")
filesmenu_border.pack(fill = "both", expand = True)
filesmenu = tk.Listbox(
  filesmenu_border, bg = "#222", highlightthickness = 0, borderwidth = 0,
  selectbackground = "#333", fg = "#fff", font = ("Roboto", 12),
  selectforeground = "#fff", activestyle = "none", 
)
filesmenu.pack(padx = 10, pady = 5, fill = "both", expand = True)
filesmenu.bind("<<ListboxSelect>>", select)
divider.add(menu)
divider.paneconfigure(menu, minsize = 300)
divider.add(editor)
divider.pack(fill = "both", expand = 1)

root.bind("<Control-w>", destroy)
root.bind("<Control-s>", savekey)

root.mainloop()

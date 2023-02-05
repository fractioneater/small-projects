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
filename = "nothing"
fileopened = ""
hiderotation = 0
filepaths = []
filepath = "/home/fractioneater/notebook/--nothing.txt"
s = ttk.Style()
s.theme_use("clam")
s.configure("TButton", relief = "flat")
s.configure("TRadiobutton", relief = "flat", font = ("System", 18))
s.map("TRadiobutton",
  background = [("!active", "#000"), ("active", "#000"), ("pressed", "#000")],
  foreground = [("!active", "#ffcc12"), ("active", "#ffdd23"), ("pressed", "ffdd23")]
)
s.map("TButton",
  background = [("!active", "#000"), ("active", "#222"), ("pressed", "#222")],
  foreground = [("!active", "#ffcc12"), ("active", "#ffdd23"), ("pressed", "ffdd23")]
)

def openfile():
  global filename
  filename = fd.askopenfilename()
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
  filesaved = open(filename, "w+")
  filesaved.write(editor.get("1.0", "end"))
  filesaved.close()

def save():
  global filename
  filesaved = open(filename, "w+")
  filesaved.write(editor.get("1.0", "end"))
  filesaved.close()

def new():

  def submit(event):
    global filename
    newname = picker.get()
    filename = f"/home/fractioneater/notebook/{newname}.txt"
    filepaths.append(str(filename))
    newfile = open(filename, "x")
    newfile.close()
    fileopened = open(filename, "r")
    fileread = fileopened.read()
    fileopened.close()
    namepicker.destroy()
    editor.delete("1.0", "end")
    editor.insert("1.0", fileread)
    filesmenu.insert("end", f"{newname}.txt")
    filesmenu.selection_set(0)
    filesmenu.activate(0)
  
  namepicker = tk.Toplevel(root)
  namepicker.minsize(400, 200)
  namepicker.maxsize(400, 200)
  namepicker.title("Choose File Name")
  newfilelabel = tk.Label(namepicker, text = "Enter a name:")
  picker = tk.Entry(namepicker, width = 16, background = "#ffdd23")
  picker.bind("<Return>", submit)
  newfilelabel.place(relx = 0.5, rely = 0.43, anchor = "c")
  picker.place(anchor = "c", relx = 0.5, rely = 0.57)
  picker.focus_set()

def destroy(event):
  root.destroy()

menubar = tk.Menu(root, background = "#ffcc12", activebackground = "#ffdd23")
menubar.add_command(label = " < ", font = ("Courier", 20), command = hide)
menubar.add_command(label = " New ", font = ("Courier", 20), command = new)
menubar.add_command(label = " Open ", font = ("Courier", 20), command = openfile)
menubar.add_command(label = " Save ", font = ("Courier", 20), command = save)
root.config(menu = menubar)

def select(event):
  global filepath
  for item in filesmenu.curselection():
    filepath = filepaths[item]
  fileopened = open(filepath, "r")
  fileread = fileopened.read()
  editor.delete("1.0", "end")
  editor.insert("1.0", fileread)
  fileopened.close()

divider = tk.PanedWindow(root, orient = "horizontal")
scroll = tk.Scrollbar(root, bg = "#ffcc12", troughcolor = "#000", activebackground = "#ffdd23")
scroll.pack(side = "right", fill = "y")
editor = tk.Text(divider, yscrollcommand = scroll.set, bg = "#222", fg = "#fff", insertbackground = "#fff", font = ("Courier", 14), wrap = "none")
editor.grid(column = 1, row = 0, sticky = "nesw")
scroll.config(command = editor.yview)
menu = tk.Frame(divider, background = "#000", height = 900, width = 140)
menu.grid(column = 0, row = 0, rowspan = 3, sticky = "nesw")
fileslabel = tk.Label(menu, text = "FILES", font = ("Roboto", 24), bg = "#000", anchor = "w", fg = "#ffdd23")
fileslabel.pack(pady = 20, padx = 24)
filesmenu = tk.Listbox(
  menu, bg = "#222", highlightbackground = "#222",
  selectbackground = "#333", fg = "#fff", font = ("Symbol", 16),
  selectforeground = "#fff", activestyle = "none"
)
filesmenu.pack(fill = "both", expand = 1)
filesmenu.bind("<<ListboxSelect>>", select)
divider.add(menu)
divider.paneconfigure(menu, minsize = 300)
divider.add(editor)
divider.pack(fill = "both", expand = 1)
root.bind("<Control-w>", destroy)
root.bind("<Control-s>", savekey)

root.mainloop()

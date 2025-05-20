from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font
import webbrowser
import json
import os

# global constants
IS_BUILD = bool(False)                  # declare true while editing code, declare false when not changing code
IS_DEBUG = bool(False)                  # need to add debug features for this one
currentFilePath = None                  # keeps track of file path for memory on open/save logic
unsavedChanges = False                  # keeps track of any unsaved changes
helpurl = "https://www.youtube.com/watch?v=My0lzMuNcHI"

# important functions
def fileCheck(filename):
    return os.path.exists(os.path.join(os.getcwd(),filename))

def updateVersion(file_path="np_settings.json"):
    # load or initialize version data
    if not os.path.exists(file_path):
        versionData = {"major" : 1, "minor" : 0, "build" : 0}
    else:
        with open(file_path, "r") as json_file:
            versionData = json.load(json_file)

    #increment build number
    if IS_BUILD:
        versionData["build"] += 1

    #save updated version
    with open(file_path, "w") as json_file:
        json.dump(versionData, json_file, indent=4)

    #create version string
    versionString = f"v{versionData['major']}.{versionData['minor']} build {versionData['build']}"
    return versionString

def updateTitle():
    # creates an asterisk next to the filename in the title bar if unsaved changes exist
    base_name = currentFilePath if currentFilePath else "Untitled"
    dirty_marker = "*" if unsavedChanges else ""
    mainWindow.title(f"{dirty_marker}{os.path.basename(base_name)} - PyNote")

def on_edit(event=None):
    # checks to see if text has been edited to change unsavedChange flag to true
    global unsavedChanges
    if mainTextField.edit_modified():
        unsavedChanges = True
        updateTitle()
        # print("Text has been edited") # debug
        mainTextField.edit_modified(False)

def rcPopup(event):
    try:
        rcMenu.tk_popup(event.x_root, event.y_root)
    finally:
        rcMenu.grab_release()

def fileExit():
    # on exit, if unsaved changes prompts user to save, not save or cancel w/ messagebox
    global currentFilePath
    if unsavedChanges:
        if currentFilePath == None:
            currentFilePath = "Untitled"
        unsavedChangesWarning = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Do you want to save changes to %s?" % currentFilePath)
        if unsavedChangesWarning:
            print("Unsaved changes has been saved") # debug
            saveFile()
            mainWindow.destroy()
        elif unsavedChangesWarning is None:
            return
        else:
            mainWindow.destroy()
    else:
        mainWindow.destroy()

def newFile():
    # -=Need to fix=-
    #-----------------
    # :Text deletes if you cancel the "save as" function instead of remaining

    global currentFilePath
    global unsavedChanges

    if unsavedChanges:
        unsavedChangesWarning = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Do you want to save changes to %s?" % currentFilePath)
        if unsavedChangesWarning:
            print("Unsaved changes has been saved") # debug
            saveFile()
        elif unsavedChangesWarning is None:
            return

    currentFilePath = None
    unsavedChanges = False
    updateTitle()
    mainTextField.delete(1.0, END)

def openFile():
    # opens a file starting at data folder
    global currentFilePath
    # sets the context window to default to .txt or an option for all files
    filepath = filedialog.askopenfilename(
        title="Open file...",
        filetypes=[("Text Files","*.txt"),
                   ("All Files","*.*")])

    # if filepath is true, start the openFile process
    # global currentFilePath
    if filepath:
        try:
            with open(filepath, "r") as openFile:
                openFileData = openFile.read()
                currentFilePath = filepath
                print(f"currentFilePath: {currentFilePath}") # for debugging
                mainTextField.delete(1.0, END)
                mainTextField.insert(1.0, openFileData)
                mainTextField.edit_modified(False)
                openFile.close()
                updateTitle()

        except FileNotFoundError:
            print("File not found, it might have been moved or deleted.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    else:
        print("No file selected")

def saveFile():
    global currentFilePath
    global unsavedChanges
    print(f"currentFilePath: {currentFilePath}") # debug
    if currentFilePath:
        try:
            content = mainTextField.get(1.0, END)
            with open(currentFilePath, "w") as saveFile:
                saveFile.write(content)
                unsavedChanges = False
                saveFile.close()
                updateTitle()

        except Exception as e:
            print(f"Save file error: {e}")
    else:
        saveAsFile()

def saveAsFile():
    global currentFilePath
    global unsavedChanges
    if currentFilePath == None:
        currentFilePath = "Untitled"
    file = filedialog.asksaveasfile(defaultextension=".txt",
                                    filetypes=[
                                        ("Text File", "*.txt"),
                                        ("Python File", "*.py"),
                                        ("All Files","*.*")
                                    ])
    if file:
        try:
            fileText = str(mainTextField.get("1.0", END))
            file.write(fileText)
            currentFilePath = file.name
            print(f"currentFilePath: {currentFilePath}") # debug
            unsavedChanges = False
            updateTitle()
            file.close()

        except FileNotFoundError:
            print("File not found, it might have been moved or deleted.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def undoEdit():
    try:
        mainTextField.edit_undo()
    except TclError:
        pass

def cutEdit():
    copyEdit()
    try:
        mainTextField.delete(SEL_FIRST, SEL_LAST)
    except TclError:
        pass

def copyEdit():
    try:
        selected_text = mainTextField.get(SEL_FIRST, SEL_LAST)
        mainTextField.clipboard_clear()
        mainTextField.clipboard_append(selected_text)
    except TclError:
        pass

def pasteEdit():
    try:
        clippaste = mainWindow.clipboard_get()
        mainTextField.insert(INSERT, clippaste)
    except TclError:
        pass

def fontFormat():

    def fontChange(event):
        selected_font = fontListbox.get(fontListbox.curselection())
        currentFont.config(family=selected_font)

    def fontSizeChange(event):
        selected_fontSize = sizeListbox.get(sizeListbox.curselection())
        currentFont.config(size=selected_fontSize)

    def fontStyleChange(event):
        # there is probably an easier and faster way to handle this :)
        # changes font style based on selection

        selected_fontStyle = styleListbox.get(styleListbox.curselection())

        if selected_fontStyle == "Regular":
            currentFont.config(weight="normal", slant="roman",underline=False, overstrike=False)
        elif selected_fontStyle == "Bold":
            currentFont.config(weight="bold", slant="roman",underline=False,overstrike=False)
        elif selected_fontStyle == "Italic":
            currentFont.config(weight="normal", slant="italic",underline=False,overstrike=False)
        elif selected_fontStyle == "Bold/Italic":
            currentFont.config(weight="bold", slant="italic",underline=False,overstrike=False)
        elif selected_fontStyle == "Underline":
            currentFont.config(weight="normal", slant="italic", underline=True,overstrike=False)
        elif selected_fontStyle == "Strike":
            currentFont.config(weight="normal", slant="italic", underline=False,overstrike=True)
        else:
            print("How did you select something that's not in the box?")

    # messagebox.showerror(title="Under construction", message="Under Construction - For now") # debug
    fontWindow = Toplevel(mainWindow)
    fontWindow.title("Font")
    fontWindow.resizable(FALSE, FALSE)
    # Center the window on screen
    window_width = 400
    window_height = 400
    screen_width = fontWindow.winfo_screenwidth()
    screen_height = fontWindow.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    fontWindow.geometry(f"{window_width}x{window_height}+{x}+{y}")

    #label generation
    fontLabel = Label(fontWindow, text="Font:", font=("Segoe UI", 9))
    fontLabel.grid(row=0, column=0, padx=10, pady=10)

    sizeLabel = Label(fontWindow, text="Font Size:", font=("Segoe UI", 9))
    sizeLabel.grid(row=0, column=1)

    styleLabel = Label(fontWindow, text="Font Style:", font=("Segoe UI", 9))
    styleLabel.grid(row=0, column=2)

    # add listboxes
    fontListbox = Listbox(fontWindow, selectmode=SINGLE, width=30)
    fontListbox.grid(row=1, column=0)

    sizeListbox = Listbox(fontWindow, selectmode=SINGLE, width=10)
    sizeListbox.grid(row=1, column=1)

    styleListbox = Listbox(fontWindow, selectmode=SINGLE, width=30)
    styleListbox.grid(row=1, column=2)

    # add preview frame with sample text inside of the frame
    # need to fix somewhat, at larger fonts there is not enough space even with clipping
    previewFrame = LabelFrame(fontWindow, text="Sample",padx=10, pady=10,width=100,height=70)
    previewFrame.grid(row=4, column=0, columnspan=1,padx=10, pady=10, sticky="nsew")
    previewFrame.rowconfigure(0, weight=1)
    previewFrame.columnconfigure(0, weight=1)
    previewFrame.grid_propagate(False)

    # creates the sample text

    previewCanvas = Canvas(previewFrame,width=100,height=70)
    previewCanvas.grid(row=0, column=0, sticky="nsew")
    previewCanvas.create_text(
        60, 10,  # center coordinates
        text="AaBbYyZz",
        font=currentFont,
        anchor="center"
    )

    # add font families to fontListbox
    for f in font.families():
        fontListbox.insert(END, f)

    # add sizes to size listbox (can create more sizes if so desired)
    font_sizes = [8,10,12,14,16,18,20,36,48,72]
    for size in font_sizes:
        sizeListbox.insert(END, size)

    # add styles to styleBox
    font_styles = ["Regular","Bold","Italic","Bold/Italic","Underline", "Strike"]
    for style in font_styles:
        styleListbox.insert(END, style)

    # bind listboxes to keys
    fontListbox.bind("<ButtonRelease-1>", fontChange)
    sizeListbox.bind("<ButtonRelease-1>", fontSizeChange)
    styleListbox.bind("<ButtonRelease-1>", fontStyleChange)

def helpView():
    webbrowser.open(helpurl)

def about():
    # create a child window (top level) and disable all buttons at the top
    aboutWindow = Toplevel(mainWindow)
    aboutWindow.title("About")
    aboutWindow.overrideredirect(False) # make true to remove min/max/close buttons

    # Center the window on screen
    window_width = 400
    window_height = 250
    screen_width = aboutWindow.winfo_screenwidth()
    screen_height = aboutWindow.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    aboutWindow.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # bulk of about window text
    aboutPynote = """PyNote is a project notepad app coded entirely in Python utilizing TKinter to get back into programming with python. 
    \nThank you to Bro Code and chatGPT (lol) for helping me practice my programming skills and giving me the resources and tips to help build this tool!
    \n
    \n\n Created by Jake Evans"""

    # add content to actual window

    aboutWindowLabel = Label(aboutWindow,text=f"PyNote version {version}", font=("Arial",14,"bold"))
    aboutWindowLabel.pack(side=TOP,pady=10)
    aboutWindowText = Label(aboutWindow,text=aboutPynote,font=("Arial",10),wraplength=380, justify="center")
    aboutWindowText.pack(side=TOP)



    awButtonClose = Button(aboutWindow, text="OK",
                           height=1, width=2,
                           padx=20,
                           command=aboutWindow.destroy)
    awButtonClose.place(relx=0.95, rely=0.95, anchor="se")

# window create
mainWindow = Tk()
mainWindow.geometry("600x400")
version = updateVersion()
# mainWindow.title("PyNotes Version %s" % version) - legacy v0.3b22
mainWindow.title("Untitled - PyNote")

#########DEFAULT VALUES FOR WINDOW################
currentFont = font.Font(family="consolas", size=13)
if fileCheck("pynote_icon.ico"):
    print("icon exists")
    mainWindow.iconbitmap("pynote_icon.ico")
else:
    print("No pynote_icon.ico file found.")
    pass
##################################################

# buttons for no context menubar notepad -- legacy code (v0.1 build 85)
# fileOpenButton = Button(mainWindow, text="Open File", command=openFile)
# fileOpenButton.pack(anchor="nw")
# fileSaveButton = Button(mainWindow, text="Save", command=saveFile)
# fileSaveButton.place(x=62,y=0)
# fileSaveAsButton = Button(mainWindow, text="Save As...", command=saveAsFile)
# fileSaveAsButton.place(x=98,y=0)

# Right Click (rc) context menu generation
rcMenu = Menu(mainWindow, tearoff=0)
rcMenu.add_command(label="Undo", command=undoEdit)
rcMenu.add_separator()
rcMenu.add_command(label="Cut", command=cutEdit)
rcMenu.add_command(label="Copy", command=copyEdit)
rcMenu.add_command(label="Paste", command=pasteEdit)
rcMenu.bind("<Button-3>", rcPopup)

# menubar generation
menubar = Menu(mainWindow)
mainWindow.config(menu=menubar)

# file context menu in menu bar
fileMenu = Menu(menubar,tearoff=False)
menubar.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="New", command=newFile)
fileMenu.add_command(label="Open", command=openFile)
fileMenu.add_command(label="Save", command=saveFile)
fileMenu.add_command(label="Save As...", command=saveAsFile)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=fileExit)

# edit context menu in menu bar
editMenu = Menu(menubar,tearoff=False)
menubar.add_cascade(label="Edit", menu=editMenu)
editMenu.add_command(label="Undo", accelerator="Ctrl+Z", command=undoEdit)
editMenu.add_separator()
editMenu.add_command(label="Cut", accelerator="Ctrl+X", command=cutEdit)
editMenu.add_command(label="Copy", accelerator="Ctrl+C", command=copyEdit)
editMenu.add_command(label="Paste", accelerator="Ctrl+V", command=pasteEdit)

# format context menu in menu bar
formatMenu = Menu(menubar,tearoff=False)
menubar.add_cascade(label="Format", menu=formatMenu)
formatMenu.add_command(label="Font...", command=fontFormat)

# help context menu in menu bar
helpMenu = Menu(menubar,tearoff=False)
menubar.add_cascade(label="Help", menu=helpMenu)
helpMenu.add_command(label="View Help", command=helpView)
helpMenu.add_separator()
helpMenu.add_command(label="About PyNote", command=about)

# text window scrollbar
scrollbar = Scrollbar(mainWindow)
scrollbar.pack(side="right", fill="y")

# text window
mainTextField = Text(mainWindow, font=currentFont, wrap="word", undo=True, yscrollcommand=scrollbar.set)
mainTextField.pack(side="top", expand=True, fill="both")
mainTextField.bind("<<Modified>>", on_edit)
mainTextField.bind("<Control-z>", lambda e: undoEdit())
mainTextField.bind("<Button-3>", rcPopup)
mainWindow.protocol("WM_DELETE_WINDOW", fileExit)

# Status bar frame
status_frame = Frame(mainWindow, relief="sunken", bd=1)
status_frame.pack(side="bottom", fill="x")

# Label to hold line/column display
cursor_label = Label(status_frame, text="Ln 1, Col 1", anchor="e")
cursor_label.pack(side="right", padx=5)

# Function to update cursor position
def update_cursor_position(event=None):
    try:
        index = mainTextField.index("insert")
        line, col = map(int, index.split("."))
        cursor_label.config(text=f"Ln {line}, Col {col + 1}")
    except:
        cursor_label.config(text="Ln -, Col -")

# Bind typing and mouse release to update function
mainTextField.bind("<KeyRelease>", update_cursor_position)
mainTextField.bind("<ButtonRelease>", update_cursor_position)


# window loop
update_cursor_position()
mainWindow.mainloop()
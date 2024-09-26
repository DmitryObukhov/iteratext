import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
import yaml
import importlib.util
import platform
import re


def new_file(event=None):
    global file_path
    text_area.delete(1.0, tk.END)
    output_area.delete(1.0, tk.END)
    file_path = None
    # Clear last opened file record
    save_last_opened_file(None)

def open_file(event=None, path=None):
    global file_path
    if path:
        file_path = path
    else:
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
        )
    if file_path:
        text_area.delete(1.0, tk.END)
        try:
            with open(file_path, "r") as file:
                text_area.insert(tk.END, file.read())
            output_area.delete(1.0, tk.END)
            # Save the last opened file path
            save_last_opened_file(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
            file_path = None

def save_file(event=None):
    global file_path
    if file_path:
        try:
            with open(file_path, "w") as file:
                file.write(text_area.get(1.0, tk.END))
            # Save the last opened file path
            save_last_opened_file(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    else:
        save_as_file()

def save_as_file(event=None):
    global file_path
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "w") as file:
                file.write(text_area.get(1.0, tk.END))
            # Save the last opened file path
            save_last_opened_file(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

def exit_editor(event=None):
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def paste_text():
    # Save current state for undo
    save_undo_state()
    # Get content from right window
    try:
        # Try to get selected text from right window
        output_text = output_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        # No selection, get all text
        output_text = output_area.get(1.0, tk.END)
    # Paste into left window
    try:
        # If there is a selection in the left window, replace it
        sel_first = text_area.index(tk.SEL_FIRST)
        sel_last = text_area.index(tk.SEL_LAST)
        text_area.delete(sel_first, sel_last)
        text_area.insert(sel_first, output_text)
    except tk.TclError:
        # No selection in left window, replace entire content
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, output_text)

def append_text():
    # Save current state for undo
    save_undo_state()
    # Get content from right window
    try:
        # Try to get selected text from right window
        output_text = output_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        # No selection, get all text
        output_text = output_area.get(1.0, tk.END)
    # Append to left window
    text_area.insert(tk.END, output_text)

def insert_text():
    # Save current state for undo
    save_undo_state()
    # Get content from right window
    try:
        # Try to get selected text from right window
        insert_text = output_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        # No selection, get all text
        insert_text = output_area.get(1.0, tk.END)
    # Get the current cursor position in the left window
    cursor_position = text_area.index(tk.INSERT)
    # Insert text at cursor position
    text_area.insert(cursor_position, insert_text)

# Undo functionality
undo_stack = []

def save_undo_state():
    # Save the current state of the text_area before modifying it
    text_content = text_area.get(1.0, tk.END)
    undo_stack.append(text_content)
    # Limit the undo stack size if necessary
    if len(undo_stack) > 20:
        undo_stack.pop(0)

def undo_last_operation(event=None):
    if undo_stack:
        last_state = undo_stack.pop()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, last_state)
    else:
        messagebox.showinfo("Undo", "Nothing to undo.")

def save_last_opened_file(path):
    # Save the last opened file path to a file
    try:
        with open(last_file_path, 'w') as f:
            if path:
                f.write(path)
            else:
                f.write('')
    except Exception as e:
        print(f"Failed to save last opened file: {e}")

def load_last_opened_file():
    # Load the last opened file path from a file
    if os.path.exists(last_file_path):
        try:
            with open(last_file_path, 'r') as f:
                path = f.read().strip()
                if path:
                    return path
        except Exception as e:
            print(f"Failed to load last opened file: {e}")
    return None

def process_includes(obj, prompts_dir):
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = process_includes(value, prompts_dir)
    elif isinstance(obj, list):
        obj = [process_includes(item, prompts_dir) for item in obj]
    elif isinstance(obj, str):
        # Check for {INCLUDE: filename} pattern
        pattern = r'\{INCLUDE:\s*(.*?)\}'
        matches = re.findall(pattern, obj)
        for match in matches:
            include_file = os.path.join(prompts_dir, match)
            if os.path.exists(include_file):
                with open(include_file, 'r') as f:
                    included_content = f.read()
                # Replace the {INCLUDE: filename} with the content
                obj = obj.replace(f'{{INCLUDE: {match}}}', included_content)
            else:
                print(f"Included prompt file '{match}' not found.")
    return obj


# Initialize the main window
root = tk.Tk()
root.title("Text Processor Application")

# Open the application full screen at startup based on OS
current_os = platform.system()
if current_os == 'Windows':
    root.state('zoomed')  # Maximize window on Windows
elif current_os == 'Linux':
    root.attributes('-zoomed', True)  # Maximize window on Linux
elif current_os == 'Darwin':  # macOS
    root.attributes('-zoomed', True)  # Maximize window on macOS
else:
    # If OS is not identified, you can opt for fullscreen
    root.attributes('-fullscreen', True)

# Initialize file_path variable
file_path = None

# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to store the last opened file
last_file_path = os.path.join(script_dir, 'lastfile.txt')

# Create frames for layout
left_frame = tk.Frame(root)
middle_frame = tk.Frame(root)
right_frame = tk.Frame(root)

left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
middle_frame.pack(side=tk.LEFT, fill=tk.Y)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create Text widget in left_frame
text_area = tk.Text(left_frame, undo=True)
text_area.pack(fill=tk.BOTH, expand=True)

# Create Text widget in right_frame
output_area = tk.Text(right_frame, undo=True)
output_area.pack(fill=tk.BOTH, expand=True)

# Create a Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add menu items to File menu
file_menu.add_command(label="New", command=new_file, accelerator="Ctrl+N")
file_menu.add_command(label="Open...", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label="Save As...", command=save_as_file, accelerator="Ctrl+Shift+S")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_editor, accelerator="Ctrl+Q")

# Process command-line arguments to get config file
if len(sys.argv) > 1:
    config_file = sys.argv[1]
else:
    config_file = os.path.join(script_dir, 'config.yaml')

# Load configuration file
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
else:
    messagebox.showerror("Configuration Error", f"Configuration file '{config_file}' not found.")
    sys.exit(1)

# Extract global configuration
global_config = config.get('global', {})


# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Directory for prompt templates
prompts_dir = os.path.join(script_dir, 'prompts')

# Load configuration file
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
else:
    messagebox.showerror("Configuration Error", f"Configuration file '{config_file}' not found.")
    sys.exit(1)

# Process includes in the configuration
config = process_includes(config, prompts_dir)


api_key_file = global_config.get('OPEN_AI_API_KEY_FILE')
if api_key_file:
    # Expand user tilde (~) to full path
    api_key_file = os.path.expanduser(api_key_file)
    if os.path.exists(api_key_file):
        with open(api_key_file, 'r') as f:
            api_key = f.read().strip()
            global_config['OPEN_AI_API_KEY'] = api_key  # Add the API key to global_config
    else:
        messagebox.showerror("Configuration Error", f"API key file '{api_key_file}' not found.")
        sys.exit(1)
else:
    messagebox.showerror("Configuration Error", "OPEN_AI_API_KEY_FILE not specified in config.yaml.")
    sys.exit(1)

# Get operations from config
operations = config.get('operations', [])

# Plugins directory
plugins_dir = os.path.join(script_dir, 'plugins')

# Dictionary to hold plugin instances
plugin_instances = {}

# Load plugins at startup and create instances
for operation in operations:
    func_name = operation.get('function', '')
    if func_name not in plugin_instances:
        # Load the plugin module
        plugin_path = os.path.join(plugins_dir, f"{func_name}.py")
        if os.path.exists(plugin_path):
            spec = importlib.util.spec_from_file_location(func_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Get the class from the module
            plugin_class = getattr(module, func_name.capitalize(), None)
            if plugin_class:
                # Create an instance of the plugin class
                instance = plugin_class(global_config)
                plugin_instances[func_name] = instance
            else:
                print(f"Plugin class '{func_name.capitalize()}' not found in '{func_name}.py'.")
        else:
            print(f"Plugin '{func_name}' not found.")

# Create processing buttons dynamically
processing_buttons = []
button_width = 0  # To determine the maximum button width
for operation in operations:
    op_name = operation.get('name', 'Unnamed')
    func_name = operation.get('function', '')
    func_config = operation.get('parameters', {})

    plugin_instance = plugin_instances.get(func_name)
    if plugin_instance:
        # Define the processing function to be called when button is pressed
        def process_text(f=plugin_instance.process, fc=func_config):
            # Get text from left window
            try:
                # Try to get selected text from left window
                input_text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                # No selection, get all text
                input_text = text_area.get(1.0, tk.END)

            # Process the text
            processed_text = f(input_text, fc)
            output_area.delete(1.0, tk.END)
            output_area.insert(tk.END, processed_text)

        # Determine the width of the button text
        button_text_length = len(op_name)
        if button_text_length > button_width:
            button_width = button_text_length

        # Create the button
        button = tk.Button(middle_frame, text=op_name, command=process_text)
        processing_buttons.append(button)
    else:
        print(f"Plugin instance for '{func_name}' not available.")

# Now set all buttons to have the same width
for button in processing_buttons:
    button.config(width=button_width)
    button.pack(pady=5)

# Spacer to push buttons to bottom
tk.Label(middle_frame, text="").pack(expand=True)

# Create "Paste", "Append", and "Insert" buttons at the bottom
insert_button = tk.Button(middle_frame, text="Insert", command=insert_text, width=button_width)
insert_button.pack(side=tk.BOTTOM, pady=5)

paste_button = tk.Button(middle_frame, text="Paste", command=paste_text, width=button_width)
paste_button.pack(side=tk.BOTTOM, pady=5)

append_button = tk.Button(middle_frame, text="Append", command=append_text, width=button_width)
append_button.pack(side=tk.BOTTOM, pady=5)

# Bind Ctrl+Z to undo_last_operation
root.bind('<Control-z>', undo_last_operation)
root.bind('<Control-Z>', undo_last_operation)  # For macOS compatibility

# Add keybindings for editor operations
root.bind('<Control-n>', new_file)
root.bind('<Control-N>', new_file)  # For macOS
root.bind('<Control-o>', open_file)
root.bind('<Control-O>', open_file)  # For macOS
root.bind('<Control-s>', save_file)
root.bind('<Control-S>', save_file)  # For macOS
root.bind('<Control-Shift-s>', save_as_file)
root.bind('<Control-Shift-S>', save_as_file)  # For macOS
root.bind('<Control-q>', exit_editor)
root.bind('<Control-Q>', exit_editor)  # For macOS

# Load the last opened file at startup
last_opened_file = load_last_opened_file()
if last_opened_file:
    open_file(path=last_opened_file)

# Start the application
root.mainloop()

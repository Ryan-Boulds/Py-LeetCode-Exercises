import pyperclip
import re
import logging
import keyboard
import tkinter as tk
from tkinter import ttk

# Configure logging to file
logging.basicConfig(
    filename='survey.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CommandModifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Command Modifier")
        self.root.configure(bg='#f0f0f0')

        # Create main frame for notebook and terminal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill="both")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both")

        # Command Modifier tab
        self.command_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.command_frame, text="Command Modifier")

        # Set Coordinates tab
        self.set_coord_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.set_coord_frame, text="Set Coordinates")

        # Initialize modifier variables for Command Modifier
        self.pos_x_offset = tk.StringVar(value="0")
        self.pos_y_offset = tk.StringVar(value="0")
        self.pos_z_offset = tk.StringVar(value="0")
        self.target_x_offset = tk.StringVar(value="0")
        self.target_y_offset = tk.StringVar(value="0")
        self.target_z_offset = tk.StringVar(value="0")

        # Initialize set variables for Set Coordinates
        self.pos_x_set = tk.StringVar(value="0")
        self.pos_y_set = tk.StringVar(value="0")
        self.pos_z_set = tk.StringVar(value="0")
        self.target_x_set = tk.StringVar(value="0")
        self.target_y_set = tk.StringVar(value="0")
        self.target_z_set = tk.StringVar(value="0")

        # Create GUI elements
        self.create_gui()

        # Bind F12 key
        keyboard.add_hotkey('F12', self.on_f12_press)

        logging.info("Application started (F12 clipboard mode with GUI)")
        self.print_to_text("Application started. Copy a command, press F12 to process.\n")

    def create_gui(self):
        # Common method to create GUI for both tabs
        def create_modifier_gui(frame, pos_vars, target_vars, title_prefix):
            # Make columns resizable
            frame.columnconfigure(4, weight=1)

            # Header
            tk.Label(
                frame, text=f"{title_prefix} Modifier", font=("Arial", 16, "bold"),
                bg='#f0f0f0', fg='#333333'
            ).grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

            # Position Modifiers
            tk.Label(
                frame, text="Position Modifiers", font=("Arial", 12, "bold"),
                bg='#f0f0f0', fg='#333333'
            ).grid(row=1, column=0, columnspan=4, pady=5, sticky="w", padx=10)

            # Position X
            tk.Label(frame, text="X:", font=("Arial", 10), bg='#f0f0f0').grid(row=2, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=pos_vars[0], width=10, bg='#ffffff', font=("Arial", 10)).grid(row=2, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda: self.adjust_offset(pos_vars[0], 1), font=("Arial", 8), width=3).grid(row=2, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda: self.adjust_offset(pos_vars[0], -1), font=("Arial", 8), width=3).grid(row=2, column=3, padx=5, pady=5, sticky="w")

            # Position Y
            tk.Label(frame, text="Y:", font=("Arial", 10), bg='#f0f0f0').grid(row=3, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=pos_vars[1], width=10, bg='#ffffff', font=("Arial", 10)).grid(row=3, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda: self.adjust_offset(pos_vars[1], 1), font=("Arial", 8), width=3).grid(row=3, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda: self.adjust_offset(pos_vars[1], -1), font=("Arial", 8), width=3).grid(row=3, column=3, padx=5, pady=5, sticky="w")

            # Position Z
            tk.Label(frame, text="Z:", font=("Arial", 10), bg='#f0f0f0').grid(row=4, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=pos_vars[2], width=10, bg='#ffffff', font=("Arial", 10)).grid(row=4, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda: self.adjust_offset(pos_vars[2], 1), font=("Arial", 8), width=3).grid(row=4, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda: self.adjust_offset(pos_vars[2], -1), font=("Arial", 8), width=3).grid(row=4, column=3, padx=5, pady=5, sticky="w")

            # BeamTarget Modifiers
            tk.Label(
                frame, text="BeamTarget Modifiers (summon only)", font=("Arial", 12, "bold"),
                bg='#f0f0f0', fg='#333333'
            ).grid(row=5, column=0, columnspan=4, pady=5, sticky="w", padx=10)

            # BeamTarget X
            tk.Label(frame, text="X:", font=("Arial", 10), bg='#f0f0f0').grid(row=6, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=target_vars[0], width=10, bg='#ffffff', font=("Arial", 10)).grid(row=6, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda: self.adjust_offset(target_vars[0], 1), font=("Arial", 8), width=3).grid(row=6, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda: self.adjust_offset(target_vars[0], -1), font=("Arial", 8), width=3).grid(row=6, column=3, padx=5, pady=5, sticky="w")

            # BeamTarget Y
            tk.Label(frame, text="Y:", font=("Arial", 10), bg='#f0f0f0').grid(row=7, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=target_vars[1], width=10, bg='#ffffff', font=("Arial", 10)).grid(row=7, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda: self.adjust_offset(target_vars[1], 1), font=("Arial", 8), width=3).grid(row=7, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda: self.adjust_offset(target_vars[1], -1), font=("Arial", 8), width=3).grid(row=7, column=3, padx=5, pady=5, sticky="w")

            # BeamTarget Z
            tk.Label(frame, text="Z:", font=("Arial", 10), bg='#f0f0f0').grid(row=8, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=target_vars[2], width=10, bg='#ffffff', font=("Arial", 10)).grid(row=8, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda: self.adjust_offset(target_vars[2], 1), font=("Arial", 8), width=3).grid(row=8, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda: self.adjust_offset(target_vars[2], -1), font=("Arial", 8), width=3).grid(row=8, column=3, padx=5, pady=5, sticky="w")

        # Create GUI for Command Modifier
        create_modifier_gui(self.command_frame,
                            [self.pos_x_offset, self.pos_y_offset, self.pos_z_offset],
                            [self.target_x_offset, self.target_y_offset, self.target_z_offset],
                            "Command")

        # Create GUI for Set Coordinates
        create_modifier_gui(self.set_coord_frame,
                            [self.pos_x_set, self.pos_y_set, self.pos_z_set],
                            [self.target_x_set, self.target_y_set, self.target_z_set],
                            "Set")

        # Terminal Output (outside notebook)
        tk.Label(
            self.main_frame, text="Terminal Output", font=("Arial", 12, "bold"),
            bg='#f0f0f0', fg='#333333'
        ).pack(pady=5, fill="x", padx=10)

        self.terminal_text = tk.Text(
            self.main_frame, height=10, font=("Courier", 10), bg='#000000', fg='#ffffff',
            insertbackground='#ffffff', relief='flat', borderwidth=2, state='disabled',
            wrap='none'
        )
        self.terminal_text.pack(expand=True, fill="both", padx=10, pady=5)

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.terminal_text.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.terminal_text['yscrollcommand'] = v_scrollbar.set

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.terminal_text.xview)
        h_scrollbar.pack(fill="x")
        self.terminal_text['xscrollcommand'] = h_scrollbar.set

        # Configure text tags for syntax highlighting
        self.terminal_text.tag_configure("command", foreground="#ffffff")
        self.terminal_text.tag_configure("object", foreground="#55aaff")
        self.terminal_text.tag_configure("coord", foreground="#ba42ff")
        self.terminal_text.tag_configure("modified_coord", foreground="#00ff00")
        self.terminal_text.tag_configure("normal", foreground="#ffffff")

        # Instructions
        tk.Label(
            self.main_frame, text="Copy a command, press F12 to process. Close window to exit.",
            font=("Arial", 10), bg='#f0f0f0', fg='#555555'
        ).pack(pady=10, fill="x", padx=10)

    def print_to_text(self, message, tags="normal"):
        self.terminal_text.configure(state='normal')
        self.terminal_text.insert(tk.END, message + '\n', tags)
        self.terminal_text.configure(state='disabled')
        self.terminal_text.see(tk.END)

    def highlight_command(self, command, is_output=False, original_coords=None):
        # Patterns for highlighting
        command_pattern = r'^(summon|setblock|kill)\b'
        summon_object_pattern = r'(?<=summon\s)\w+\b'
        setblock_object_pattern = r'setblock\s+-?\d+\s+-?\d+\s+-?\d+\s+(minecraft:\w+|\w+)\b'
        coord_pattern = r'-?\d+\b'
        args_pattern = r'\{.*?\}\}?'
        beam_target_pattern = r'BeamTarget:\{.*?X:(-?\d+).*?Y:(-?\d+).*?Z:(-?\d+).*?\}'

        # Compile patterns
        command_re = re.compile(command_pattern)
        summon_object_re = re.compile(summon_object_pattern)
        setblock_object_re = re.compile(setblock_object_pattern)
        coord_re = re.compile(coord_pattern)
        args_re = re.compile(args_pattern)
        beam_target_re = re.compile(beam_target_pattern)

        # Extract coordinates for comparison
        modified_coords = []
        if is_output and original_coords:
            modified_coords = [int(x) for x in re.findall(coord_pattern, command) if x.lstrip('-').isdigit()]
            original_coords = original_coords[:len(modified_coords)]  # Ensure same length

        pos = 0
        self.terminal_text.configure(state='normal')
        while pos < len(command):
            # Check for command keyword
            command_match = command_re.match(command, pos)
            if command_match:
                start, end = command_match.span()
                self.terminal_text.insert(tk.END, command[start:end], "command")
                pos = end
                continue

            # Check for summon object
            summon_object_match = summon_object_re.search(command, pos)
            if summon_object_match and summon_object_match.start() == pos:
                start, end = summon_object_match.span()
                self.terminal_text.insert(tk.END, command[start:end], "object")
                pos = end
                continue

            # Check for setblock object
            setblock_object_match = setblock_object_re.search(command, pos)
            if setblock_object_match and setblock_object_match.start() <= pos < setblock_object_match.end():
                start, end = setblock_object_match.span(1)  # Capture group 1 (minecraft:stone or stone)
                if pos < start:
                    self.terminal_text.insert(tk.END, command[pos:start], "normal")
                    pos = start
                self.terminal_text.insert(tk.END, command[start:end], "object")
                pos = end
                continue

            # Check for coordinates
            coord_match = coord_re.search(command, pos)
            if coord_match and coord_match.start() == pos:
                start, end = coord_match.span()
                coord_value = int(command[start:end])
                if is_output and original_coords and modified_coords:
                    try:
                        coord_idx = modified_coords.index(coord_value)
                        if coord_idx < len(original_coords) and coord_value != original_coords[coord_idx]:
                            self.terminal_text.insert(tk.END, command[start:end], "modified_coord")
                        else:
                            self.terminal_text.insert(tk.END, command[start:end], "coord")
                    except ValueError:
                        self.terminal_text.insert(tk.END, command[start:end], "coord")
                else:
                    self.terminal_text.insert(tk.END, command[start:end], "coord")
                pos = end
                continue

            # Check for arguments (parse brackets and coordinates separately)
            args_match = args_re.search(command, pos)
            if args_match and args_match.start() == pos:
                start, end = args_match.span()
                arg_text = command[start:end]
                # Insert newline before arguments if not at start
                if pos > 0:
                    self.terminal_text.insert(tk.END, '\n', "normal")
                # Parse the full argument block
                self.terminal_text.insert(tk.END, arg_text[:1], "normal")  # Opening {
                current_pos = 1
                while current_pos < len(arg_text):
                    if arg_text[current_pos] in '}':
                        self.terminal_text.insert(tk.END, arg_text[current_pos], "normal")  # Closing }
                        current_pos += 1
                        continue
                    # Check for BeamTarget section or extract coordinates
                    beam_match = beam_target_re.search(arg_text, current_pos)
                    if beam_match:
                        beam_start, beam_end = beam_match.span()
                        # Output text before BeamTarget
                        self.terminal_text.insert(tk.END, arg_text[current_pos:beam_start], "normal")
                        current_pos = beam_start
                        # Handle BeamTarget coordinates
                        x_coord = int(beam_match.group(1))
                        y_coord = int(beam_match.group(2))
                        z_coord = int(beam_match.group(3))
                        self.terminal_text.insert(tk.END, "BeamTarget:{", "normal")
                        if is_output and original_coords and modified_coords:
                            try:
                                x_idx = modified_coords.index(x_coord)
                                if x_idx < len(original_coords) and x_coord != original_coords[x_idx]:
                                    self.terminal_text.insert(tk.END, "X:", "normal")
                                    self.terminal_text.insert(tk.END, str(x_coord), "modified_coord")
                                else:
                                    self.terminal_text.insert(tk.END, "X:", "normal")
                                    self.terminal_text.insert(tk.END, str(x_coord), "coord")
                            except ValueError:
                                self.terminal_text.insert(tk.END, "X:", "normal")
                                self.terminal_text.insert(tk.END, str(x_coord), "coord")
                            try:
                                y_idx = modified_coords.index(y_coord)
                                if y_idx < len(original_coords) and y_coord != original_coords[y_idx]:
                                    self.terminal_text.insert(tk.END, ",Y:", "normal")
                                    self.terminal_text.insert(tk.END, str(y_coord), "modified_coord")
                                else:
                                    self.terminal_text.insert(tk.END, ",Y:", "normal")
                                    self.terminal_text.insert(tk.END, str(y_coord), "coord")
                            except ValueError:
                                self.terminal_text.insert(tk.END, ",Y:", "normal")
                                self.terminal_text.insert(tk.END, str(y_coord), "coord")
                            try:
                                z_idx = modified_coords.index(z_coord)
                                if z_idx < len(original_coords) and z_coord != original_coords[z_idx]:
                                    self.terminal_text.insert(tk.END, ",Z:", "normal")
                                    self.terminal_text.insert(tk.END, str(z_coord), "modified_coord")
                                else:
                                    self.terminal_text.insert(tk.END, ",Z:", "normal")
                                    self.terminal_text.insert(tk.END, str(z_coord), "coord")
                            except ValueError:
                                self.terminal_text.insert(tk.END, ",Z:", "normal")
                                self.terminal_text.insert(tk.END, str(z_coord), "coord")
                        else:
                            self.terminal_text.insert(tk.END, "X:", "normal")
                            self.terminal_text.insert(tk.END, str(x_coord), "coord")
                            self.terminal_text.insert(tk.END, ",Y:", "normal")
                            self.terminal_text.insert(tk.END, str(y_coord), "coord")
                            self.terminal_text.insert(tk.END, ",Z:", "normal")
                            self.terminal_text.insert(tk.END, str(z_coord), "coord")
                        self.terminal_text.insert(tk.END, "}", "normal")
                        current_pos = beam_end
                    else:
                        # Handle malformed input by extracting coordinates
                        coord_match = coord_re.search(arg_text, current_pos)
                        if coord_match:
                            coord_start, coord_end = coord_match.span()
                            coord_value = int(arg_text[coord_start:coord_end])
                            # Assume order: X, Y, Z if BeamTarget is missing
                            if current_pos == arg_text.index("139184-89".partition("1")[0]) and "139184-89" in arg_text:
                                coords = re.findall(r'-?\d+', "139184-89")
                                if len(coords) >= 3:
                                    x_coord, y_coord, z_coord = map(int, coords[:3])
                                    self.terminal_text.insert(tk.END, "BeamTarget:{", "normal")
                                    if is_output and original_coords and modified_coords:
                                        try:
                                            x_idx = modified_coords.index(x_coord)
                                            if x_idx < len(original_coords) and x_coord != original_coords[x_idx]:
                                                self.terminal_text.insert(tk.END, "X:", "normal")
                                                self.terminal_text.insert(tk.END, str(x_coord), "modified_coord")
                                            else:
                                                self.terminal_text.insert(tk.END, "X:", "normal")
                                                self.terminal_text.insert(tk.END, str(x_coord), "coord")
                                        except ValueError:
                                            self.terminal_text.insert(tk.END, "X:", "normal")
                                            self.terminal_text.insert(tk.END, str(x_coord), "coord")
                                        try:
                                            y_idx = modified_coords.index(y_coord)
                                            if y_idx < len(original_coords) and y_coord != original_coords[y_idx]:
                                                self.terminal_text.insert(tk.END, ",Y:", "normal")
                                                self.terminal_text.insert(tk.END, str(y_coord), "modified_coord")
                                            else:
                                                self.terminal_text.insert(tk.END, ",Y:", "normal")
                                                self.terminal_text.insert(tk.END, str(y_coord), "coord")
                                        except ValueError:
                                            self.terminal_text.insert(tk.END, ",Y:", "normal")
                                            self.terminal_text.insert(tk.END, str(y_coord), "coord")
                                        try:
                                            z_idx = modified_coords.index(z_coord)
                                            if z_idx < len(original_coords) and z_coord != original_coords[z_idx]:
                                                self.terminal_text.insert(tk.END, ",Z:", "normal")
                                                self.terminal_text.insert(tk.END, str(z_coord), "modified_coord")
                                            else:
                                                self.terminal_text.insert(tk.END, ",Z:", "normal")
                                                self.terminal_text.insert(tk.END, str(z_coord), "coord")
                                        except ValueError:
                                            self.terminal_text.insert(tk.END, ",Z:", "normal")
                                            self.terminal_text.insert(tk.END, str(z_coord), "coord")
                                    else:
                                        self.terminal_text.insert(tk.END, "X:", "normal")
                                        self.terminal_text.insert(tk.END, str(x_coord), "coord")
                                        self.terminal_text.insert(tk.END, ",Y:", "normal")
                                        self.terminal_text.insert(tk.END, str(y_coord), "coord")
                                        self.terminal_text.insert(tk.END, ",Z:", "normal")
                                        self.terminal_text.insert(tk.END, str(z_coord), "coord")
                                    self.terminal_text.insert(tk.END, "}", "normal")
                                    current_pos = coord_end + len(coords[2])
                                else:
                                    self.terminal_text.insert(tk.END, arg_text[current_pos:coord_end], "normal")
                                    current_pos = coord_end
                            else:
                                self.terminal_text.insert(tk.END, arg_text[current_pos:coord_end], "normal")
                                current_pos = coord_end
                        else:
                            self.terminal_text.insert(tk.END, arg_text[current_pos], "normal")
                            current_pos += 1
                pos = end
                continue

            # Insert remaining characters
            self.terminal_text.insert(tk.END, command[pos], "normal")
            pos += 1

        self.terminal_text.configure(state='disabled')

    def adjust_offset(self, offset_var, change):
        try:
            current = int(offset_var.get())
            offset_var.set(str(current + change))
        except ValueError:
            offset_var.set("0")  # Reset to 0 if invalid input

    def get_offsets(self):
        try:
            pos_offsets = (
                int(self.pos_x_offset.get()),
                int(self.pos_y_offset.get()),
                int(self.pos_z_offset.get())
            )
            target_offsets = (
                int(self.target_x_offset.get()),
                int(self.target_y_offset.get()),
                int(self.target_z_offset.get())
            )
            return pos_offsets, target_offsets
        except ValueError:
            logging.warning("Invalid offset values entered, using 0")
            return (0, 0, 0), (0, 0, 0)

    def get_set_values(self):
        try:
            pos_set = (
                int(self.pos_x_set.get()),
                int(self.pos_y_set.get()),
                int(self.pos_z_set.get())
            )
            target_set = (
                int(self.target_x_set.get()),
                int(self.target_y_set.get()),
                int(self.target_z_set.get())
            )
            return pos_set, target_set
        except ValueError:
            logging.warning("Invalid set values entered, using 0")
            return (0, 0, 0), (0, 0, 0)

    def modify_coordinates(self, command, use_set=False):
        logging.debug(f"Modifying coordinates for command: {command}")
        if use_set:
            pos_values, target_values = self.get_set_values()
        else:
            pos_offsets, target_offsets = self.get_offsets()

        # Extract original coordinates for highlighting
        original_coords = [int(x) for x in re.findall(r'-?\d+\b', command) if x.lstrip('-').isdigit()]

        # Summon command (end_crystal with BeamTarget)
        summon_pattern = re.compile(r'(summon end_crystal\s+)(-?\d+)(\s+)(-?\d+)(\s+)(-?\d+)(.*?(?:BeamTarget:\{|\],\{).*?X:)(-?\d+)(.*?Y:)(-?\d+)(.*?Z:)(-?\d+)(.*?\}\})')
        summon_match = summon_pattern.search(command)
        if summon_match:
            logging.debug(f"Summon match groups: {summon_match.groups()}")
            x1 = pos_values[0] if use_set else int(summon_match.group(2)) + pos_offsets[0]
            y1 = pos_values[1] if use_set else int(summon_match.group(4)) + pos_offsets[1]
            z1 = pos_values[2] if use_set else int(summon_match.group(6)) + pos_offsets[2]
            x2 = target_values[0] if use_set else int(summon_match.group(8)) + target_offsets[0]
            y2 = target_values[1] if use_set else int(summon_match.group(10)) + target_offsets[1]
            z2 = target_values[2] if use_set else int(summon_match.group(12)) + target_offsets[2]
            result = f"{summon_match.group(1)}{x1}{summon_match.group(3)}{y1}{summon_match.group(5)}{z1}{summon_match.group(7)}{x2}{summon_match.group(9)}{y2}{summon_match.group(11)}{z2}{summon_match.group(13)}"
            logging.debug(f"Summon command modified: {result}")
            return result, original_coords

        # Handle malformed input (e.g., 139184-89) for summon
        coords_pattern = r'-?\d+(?:\s*-?\d+){2}'
        coords_match = re.search(coords_pattern, command)
        if coords_match and "summon" in command and not summon_match:
            logging.debug(f"Malformed summon input detected, extracting coordinates: {coords_match.group()}")
            coords = re.findall(r'-?\d+', coords_match.group())
            if len(coords) >= 3:
                x1, y1, z1 = map(int, coords[:3])
                x2, y2, z2 = target_values if use_set else (x1 + target_offsets[0], y1 + target_offsets[1], z1 + target_offsets[2])
                result = f"summon end_crystal {x1} {y1} {z1} {{ShowBottom:0b,Invulnerable:1b,Tags:[\"laser\"],BeamTarget:{{X:{x2},Y:{y2},Z:{z2}}}}}"
                original_coords = [x1, y1, z1]  # Assume initial coords for highlighting
                logging.debug(f"Reconstructed summon command: {result}")
                return result, original_coords

        # Setblock command
        setblock_pattern = re.compile(r'(setblock\s+)(-?\d+)(\s+)(-?\d+)(\s+)(-?\d+)(\s+(minecraft:\w+|\w+))')
        setblock_match = setblock_pattern.search(command)
        if setblock_match:
            logging.debug(f"Setblock match groups: {setblock_match.groups()}")
            x = pos_values[0] if use_set else int(setblock_match.group(2)) + pos_offsets[0]
            y = pos_values[1] if use_set else int(setblock_match.group(4)) + pos_offsets[1]
            z = pos_values[2] if use_set else int(setblock_match.group(6)) + pos_offsets[2]
            result = f"{setblock_match.group(1)}{x}{setblock_match.group(3)}{y}{setblock_match.group(5)}{z}{setblock_match.group(7)}"
            logging.debug(f"Setblock command modified: {result}")
            return result, original_coords

        # Kill command
        kill_pattern = re.compile(r'(kill @e\[[^]]*x=)(-?\d+)([^,]*,\s*y=)(-?\d+)([^,]*,\s*z=)(-?\d+)([^]]*\])')
        kill_match = kill_pattern.search(command)
        if kill_match:
            logging.debug(f"Kill match groups: {kill_match.groups()}")
            x = pos_values[0] if use_set else int(kill_match.group(2)) + pos_offsets[0]
            y = pos_values[1] if use_set else int(kill_match.group(4)) + pos_offsets[1]
            z = pos_values[2] if use_set else int(kill_match.group(6)) + pos_offsets[2]
            result = f"{kill_match.group(1)}{x}{kill_match.group(3)}{y}{kill_match.group(5)}{z}{kill_match.group(7)}"
            logging.debug(f"Kill command modified: {result}")
            return result, original_coords

        logging.debug("No coordinate modification applied")
        return command, original_coords

    def process_command(self, command):
        logging.debug("Processing command")
        try:
            warning = None
            if "BeamTarget],{" in command:
                warning = "Warning: 'BeamTarget],{' detected. Did you mean 'BeamTarget:{'? The command may not work in Minecraft."
                logging.warning(warning)

            # Determine which tab is active
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            use_set = current_tab == "Set Coordinates"
            modified_command, original_coords = self.modify_coordinates(command, use_set)
            logging.debug(f"Modified command: {modified_command}")

            self.print_to_text("", "normal")  # Blank line before block
            self.print_to_text("Input Command:", "normal")
            self.highlight_command(command, is_output=False)
            self.print_to_text("\nOutput Command:", "normal")  # New line before output
            self.highlight_command(modified_command, is_output=True, original_coords=original_coords)
            self.print_to_text("\nUse Ctrl+V to paste in Minecraft.", "normal")  # New line before paste instruction
            if warning:
                self.print_to_text(warning, "normal")
            self.print_to_text("", "normal")  # Blank line after block

            pyperclip.copy(modified_command)
            logging.debug("Clipboard updated with modified command")

        except Exception as e:
            logging.error(f"Error processing command: {str(e)}")
            self.print_to_text("", "normal")  # Blank line before error
            self.print_to_text("Input Command:", "normal")
            self.highlight_command(command, is_output=False)
            self.print_to_text("Error processing command: " + str(e), "normal")
            self.print_to_text("", "normal")  # Blank line after error

    def on_f12_press(self):
        logging.info("F12 pressed - capturing clipboard command")
        command = pyperclip.paste()
        if command.strip():
            self.process_command(command)
        else:
            self.print_to_text("", "normal")  # Blank line before empty clipboard
            self.print_to_text("Input Command:", "normal")
            self.print_to_text("Clipboard is empty or invalid. Copy a command before pressing F12.", "normal")
            self.print_to_text("", "normal")  # Blank line after empty clipboard

def main():
    root = tk.Tk()
    root.resizable(True, True)  # Allow resizing
    root.attributes('-topmost', True)  # Keep window on top
    root.columnconfigure(0, weight=1)  # Allow terminal to scale
    app = CommandModifierApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        app.print_to_text("", "normal")  # Blank line before exit
        app.print_to_text("Input Command:", "normal")
        app.print_to_text("Exiting program.", "normal")
        app.print_to_text("", "normal")  # Blank line after exit
    finally:
        logging.info("Application exiting")

if __name__ == "__main__":
    main()
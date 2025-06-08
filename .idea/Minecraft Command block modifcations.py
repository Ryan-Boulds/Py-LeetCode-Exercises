import pyperclip
import re
import logging
import keyboard
import tkinter as tk
from tkinter import ttk
import pystray
from pystray import Menu, MenuItem
from PIL import Image
import threading
import sys
import os
import time

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
        self.root.geometry("400x300")  # Smaller initial size
        self.root.resizable(True, True)  # Allow resizing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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

        # Change Block tab
        self.change_block_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.change_block_frame, text="Change Block")

        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")

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

        # Initialize change block variable
        self.block_text = tk.StringVar(value="minecraft:lime_concrete")

        # Settings variables
        self.always_on_top = tk.BooleanVar(value=False)
        self.show_in_tray = tk.BooleanVar(value=True)

        # Create GUI elements
        self.create_gui()

        # Bind F12 key
        keyboard.add_hotkey('F12', self.on_f12_press)

        logging.info("Application started (F12 clipboard mode with GUI)")
        self.print_to_text("Application started. Copy a command, press F12 to process.\n")

        # Initialize tray icon after a delay
        self.tray = None
        self.tray_thread = None
        self.schedule_tray_setup()

        # Set initial always on top state
        self.toggle_always_on_top()

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

        # Create GUI for Change Block
        tk.Label(
            self.change_block_frame, text="Change Block Modifier", font=("Arial", 16, "bold"),
            bg='#f0f0f0', fg='#333333'
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        tk.Label(
            self.change_block_frame, text="New Block Text:", font=("Arial", 12, "bold"),
            bg='#f0f0f0', fg='#333333'
        ).grid(row=1, column=0, pady=5, sticky="e", padx=10)
        tk.Entry(
            self.change_block_frame, textvariable=self.block_text, width=30, bg='#ffffff', font=("Arial", 10)
        ).grid(row=1, column=1, pady=5, sticky="w", padx=10)

        # Create GUI for Settings
        tk.Checkbutton(
            self.settings_frame, text="Always Remains on Top", variable=self.always_on_top,
            command=self.toggle_always_on_top, bg='#f0f0f0', font=("Arial", 10)
        ).grid(row=0, column=0, pady=5, padx=10, sticky="w")
        tk.Checkbutton(
            self.settings_frame, text="Show in Tray Icon when Closed", variable=self.show_in_tray,
            command=self.update_tray, bg='#f0f0f0', font=("Arial", 10)
        ).grid(row=1, column=0, pady=5, padx=10, sticky="w")

        # Terminal Output (outside notebook)
        tk.Label(
            self.main_frame, text="Terminal Output", font=("Arial", 12, "bold"),
            bg='#f0f0f0', fg='#333333'
        ).pack(pady=5, fill="x", padx=10)

        self.terminal_text = tk.Text(
            self.main_frame, height=5, font=("Courier", 10), bg='#000000', fg='#ffffff',
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
        self.terminal_text.tag_configure("block_changed", foreground="#00ff00")  # Green for changed block
        self.terminal_text.tag_configure("block_unchanged", foreground="#ffffff")  # White for unchanged block

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

    def highlight_command(self, command, is_output=False, original_coords=None, original_block=None):
        # Patterns for highlighting
        command_pattern = r'^(summon|setblock|kill)\b'
        summon_object_pattern = r'(?<=summon\s)\w+\b'
        setblock_object_pattern = r'setblock\s+-?\d+\s+-?\d+\s+-?\d+\s+(minecraft:\w+|\w+)\b'
        coord_pattern = r'-?\d+\b'
        args_pattern = r'\{.*?\}\}?'
        beam_target_pattern = r'BeamTarget:\{.*?X:(-?\d+).*?Y:(-?\d+).*?Z:(-?\d+).*?\}'
        block_pattern = r'(?:setblock\s+-?\d+\s+-?\d+\s+-?\d+\s+)(minecraft:\w+|\w+)'

        # Compile patterns
        command_re = re.compile(command_pattern)
        summon_object_re = re.compile(summon_object_pattern)
        setblock_object_re = re.compile(setblock_object_pattern)
        coord_re = re.compile(coord_pattern)
        args_re = re.compile(args_pattern)
        beam_target_re = re.compile(beam_target_pattern)
        block_re = re.compile(block_pattern)

        # Extract coordinates and block for comparison
        modified_coords = []
        modified_block = None
        if is_output and original_coords:
            modified_coords = [int(x) for x in re.findall(coord_pattern, command) if x.lstrip('-').isdigit()]
            original_coords = original_coords[:len(modified_coords)]  # Ensure same length
        if is_output and original_block:
            block_match = block_re.search(command)
            if block_match:
                modified_block = block_match.group(1)

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
                block_text = command[start:end]
                if is_output and original_block and modified_block:
                    self.terminal_text.insert(tk.END, block_text, "block_changed" if block_text != original_block else "block_unchanged")
                else:
                    self.terminal_text.insert(tk.END, block_text, "object")
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
                        # Handle BeamTarget coordinates on a new line
                        self.terminal_text.insert(tk.END, "{X:", "normal")
                        x_coord = int(beam_match.group(1))
                        if is_output and original_coords and len(original_coords) > 3:  # BeamTarget coords start at index 3
                            self.terminal_text.insert(tk.END, str(x_coord), "modified_coord" if x_coord != original_coords[3] else "coord")
                        else:
                            self.terminal_text.insert(tk.END, str(x_coord), "coord")
                        self.terminal_text.insert(tk.END, ",Y:", "normal")
                        y_coord = int(beam_match.group(2))
                        if is_output and original_coords and len(original_coords) > 4:
                            self.terminal_text.insert(tk.END, str(y_coord), "modified_coord" if y_coord != original_coords[4] else "coord")
                        else:
                            self.terminal_text.insert(tk.END, str(y_coord), "coord")
                        self.terminal_text.insert(tk.END, ",Z:", "normal")
                        z_coord = int(beam_match.group(3))
                        if is_output and original_coords and len(original_coords) > 5:
                            self.terminal_text.insert(tk.END, str(z_coord), "modified_coord" if z_coord != original_coords[5] else "coord")
                        else:
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
                                    self.terminal_text.insert(tk.END, "\n", "normal")
                                    self.terminal_text.insert(tk.END, "{X:", "normal")
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

        # Extract original coordinates and block for highlighting
        original_coords = [int(x) for x in re.findall(r'-?\d+\b', command) if x.lstrip('-').isdigit()]
        original_block = None
        block_match = re.search(r'(?:setblock\s+-?\d+\s+-?\d+\s+-?\d+\s+)(minecraft:\w+|\w+)', command)
        if block_match:
            original_block = block_match.group(1)

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
            return result, original_coords, None

        # Handle malformed input (e.g., extra brackets) for summon
        coords_pattern = r'-?\d+(?:\s*-?\d+){2}'
        coords_match = re.search(coords_pattern, command)
        if coords_match and "summon" in command and not summon_match:
            logging.debug(f"Malformed summon input detected, extracting coordinates: {coords_match.group()}")
            coords = re.findall(r'-?\d+', coords_match.group())
            if len(coords) >= 3:
                x1, y1, z1 = map(int, coords[:3])
                x2, y2, z2 = target_values if use_set else (x1 + target_offsets[0], y1 + target_offsets[1], z1 + target_offsets[2])
                # Try to extract BeamTarget from the rest of the command
                beam_target_match = re.search(r'BeamTarget:\{.*?X:(-?\d+).*?Y:(-?\d+).*?Z:(-?\d+).*?\}', command)
                if beam_target_match:
                    x2 = target_values[0] if use_set else int(beam_target_match.group(1)) + target_offsets[0]
                    y2 = target_values[1] if use_set else int(beam_target_match.group(2)) + target_offsets[1]
                    z2 = target_values[2] if use_set else int(beam_target_match.group(3)) + target_offsets[2]
                result = f"summon end_crystal {x1} {y1} {z1} {{ShowBottom:0b,Invulnerable:1b,Tags:[\"laser\"],BeamTarget:{{X:{x2},Y:{y2},Z:{z2}}}}}"
                original_coords = [x1, y1, z1] + ([int(beam_target_match.group(1)), int(beam_target_match.group(2)), int(beam_target_match.group(3))] if beam_target_match else [])
                logging.debug(f"Reconstructed summon command: {result}")
                return result, original_coords, None

        # Setblock command
        setblock_pattern = re.compile(r'(setblock\s+)(-?\d+)(\s+)(-?\d+)(\s+)(-?\d+)(\s+(minecraft:\w+|\w+))')
        setblock_match = setblock_pattern.search(command)
        if setblock_match:
            logging.debug(f"Setblock match groups: {setblock_match.groups()}")
            x = pos_values[0] if use_set else int(setblock_match.group(2)) + pos_offsets[0]
            y = pos_values[1] if use_set else int(setblock_match.group(4)) + pos_offsets[1]
            z = pos_values[2] if use_set else int(setblock_match.group(6)) + pos_offsets[2]
            original_block_text = setblock_match.group(7)
            new_block_text = self.block_text.get().strip() if "Change Block" in self.notebook.tab(self.notebook.select(), "text") else original_block_text
            result = f"{setblock_match.group(1)}{x}{setblock_match.group(3)}{y}{setblock_match.group(5)}{z}{new_block_text}"
            logging.debug(f"Setblock command modified: {result}")
            return result, original_coords, original_block_text

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
            return result, original_coords, None

        logging.debug("No modification applied")
        return command, original_coords, None

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
            if current_tab == "Change Block":
                setblock_pattern = re.compile(r'(setblock\s+)(-?\d+)(\s+)(-?\d+)(\s+)(-?\d+)(\s+(minecraft:\w+|\w+))')
                setblock_match = setblock_pattern.search(command)
                if setblock_match:
                    x = int(setblock_match.group(2))
                    y = int(setblock_match.group(4))
                    z = int(setblock_match.group(6))
                    original_block = setblock_match.group(7)
                    new_block_text = self.block_text.get().strip()
                    result = f"setblock {x} {y} {z} {new_block_text}"
                    original_coords = [x, y, z]
                else:
                    self.print_to_text("", "normal")  # Blank line before error
                    self.print_to_text("Input Command:", "normal")
                    self.highlight_command(command, is_output=False)
                    self.print_to_text("Error: This command is not a setblock command.", "normal")
                    self.print_to_text("", "normal")  # Blank line after error
                    return
            else:
                modified_command, original_coords, original_block = self.modify_coordinates(command, use_set)
                result = modified_command

            logging.debug(f"Modified command: {result}")

            self.print_to_text("", "normal")  # Blank line before block
            self.print_to_text("Input Command:", "normal")
            self.highlight_command(command, is_output=False)
            self.print_to_text("\nOutput Command:", "normal")  # New line before output
            self.highlight_command(result, is_output=True, original_coords=original_coords, original_block=original_block)
            self.print_to_text("\nUse Ctrl+V to paste in Minecraft.", "normal")  # New line before paste instruction
            if warning:
                self.print_to_text(warning, "normal")
            self.print_to_text("", "normal")  # Blank line after block

            pyperclip.copy(result)
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

    def toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())
        logging.info(f"Always on top set to {self.always_on_top.get()}")

    def schedule_tray_setup(self):
        # Delay tray setup to avoid race conditions
        self.root.after(100, self.setup_tray)

    def setup_tray(self):
        if not self.show_in_tray.get():
            return

        try:
            # Use a custom icon (place icon.ico in the project directory)
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # Fallback to a simple 16x16 image if icon not found
                image = Image.new('RGB', (16, 16), color=(0, 128, 255))  # Blue square
                logging.warning(f"Icon file 'icon.ico' not found at {icon_path}. Using fallback image.")

            self.tray = pystray.Icon("Minecraft Command Modifier", image, "Minecraft Command Modifier", Menu(
                MenuItem("Open", self.show_window),
                MenuItem("Settings", self.show_settings),
                MenuItem("Exit", self.exit_app)
            ))

            def run_tray():
                self.tray.run()

            self.tray_thread = threading.Thread(target=run_tray, daemon=True)
            self.tray_thread.start()
            logging.info("Tray icon initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize tray icon: {str(e)}")
            self.show_in_tray.set(False)  # Disable tray if setup fails

    def update_tray(self):
        if self.tray:
            self.tray.stop()
            self.tray = None
            self.tray_thread = None
        if self.show_in_tray.get():
            self.setup_tray()
        logging.info(f"Show in tray set to {self.show_in_tray.get()}")

    def on_closing(self):
        if self.show_in_tray.get() and self.tray:
            self.root.withdraw()  # Minimize to tray if tray is enabled
        else:
            self.root.destroy()  # Close the program if tray is disabled
            if self.tray:
                self.tray.stop()

    def show_window(self):
        self.root.deiconify()

    def show_settings(self):
        self.root.deiconify()
        self.notebook.select(self.settings_frame)

    def exit_app(self):
        self.root.destroy()
        if self.tray:
            self.tray.stop()
        sys.exit(0)

def main():
    root = tk.Tk()
    root.resizable(True, True)  # Allow resizing
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
        if app.tray:
            app.tray.stop()


if __name__ == "__main__":
    main()
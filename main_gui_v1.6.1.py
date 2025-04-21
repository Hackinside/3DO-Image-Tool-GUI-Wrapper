# -*- coding: utf-8 -*-
# GUI Version 1.6.1
import sys
import os
import subprocess
import platform
import shlex # For safer manual command splitting
import threading # Simple threading approach for subprocess
import traceback # For detailed error logging

# Import necessary modules from PySide6
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QLabel, QLineEdit, QFileDialog, QScrollArea, QStyleFactory,
    QGroupBox, QCheckBox, QComboBox, QTextEdit, QFormLayout, QSplitter,
    QMessageBox, QSizePolicy, QSpacerItem, QProgressBar, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QPixmap, QPalette, QColor, QDesktopServices, QFont
from PySide6.QtCore import Qt, QProcess, QTimer, QObject, Signal, QThread, QMetaObject, QUrl, Slot

# --- Configuration ---
TOOL_VERSION = "1.8.0" # Match the 3it version being wrapped
GUI_VERSION = "1.6.1" # Version of this GUI Wrapper
APP_TITLE = f'3it GUI Wrapper v{GUI_VERSION} (for 3it v{TOOL_VERSION})'

# Determine the base path for resources (like 3it.exe, banner)
if getattr(sys, 'frozen', False): BASE_PATH = sys._MEIPASS # type: ignore
else: BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Define expected locations and names
EXE_NAME = "3it.exe" if platform.system() == "Windows" else "3it"
BANNER_NAME = "3itBanner.png"

# Prioritize 'bin' subdirectory for the executable
THREE_IT_EXE_PATH = os.path.join(BASE_PATH, 'bin', EXE_NAME)
if not os.path.exists(THREE_IT_EXE_PATH):
    THREE_IT_EXE_PATH_ALT = os.path.join(BASE_PATH, EXE_NAME)
    if os.path.exists(THREE_IT_EXE_PATH_ALT): THREE_IT_EXE_PATH = THREE_IT_EXE_PATH_ALT

BANNER_PATH = os.path.join(BASE_PATH, BANNER_NAME)
IMG_VIEWER_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.imag', '.cel', '.banner']

# --- Stylesheets ---
LIGHT_STYLE = """
    QWidget { background-color: #e8e8e8; color: #000; } /* Slightly darker background */
    QGroupBox { background-color: #dddddd; border: 1px solid #b0b0b0; margin-top: 10px; padding: 5px; border-radius: 3px; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; background-color: #dddddd; border-radius: 3px;}
    QGroupBox[checkable="true"]::title { padding-left: 18px; }
    QGroupBox::indicator { width: 13px; height: 13px; }
    QPushButton { background-color: #d0d0d0; border: 1px solid #a0a0a0; padding: 4px 8px; border-radius: 3px; min-height: 18px;} /* Darker buttons */
    QPushButton:hover { background-color: #c0c0c0; }
    QPushButton:pressed { background-color: #b0b0b0; }
    QPushButton:disabled { background-color: #cccccc; color: #888888; border-color: #b0b0b0;}
    QLineEdit, QTextEdit, QListWidget, QComboBox { background-color: #fff; border: 1px solid #a0a0a0; color: #000; selection-background-color: #a8d8ff; selection-color: #000; border-radius: 3px; }
    QComboBox::drop-down { border: 1px solid #a0a0a0; border-left: none; background-color: #d0d0d0; }
    QComboBox::down-arrow { image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-down-arrow-16.png); }
    QScrollArea { border: none; background-color: transparent; }
    QSplitter::handle { background-color: #b8b8b8; } /* Lighter handle */
    QSplitter::handle:horizontal { width: 5px; }
    QSplitter::handle:vertical { height: 5px; }
    QProgressBar { border: 1px solid #a0a0a0; border-radius: 3px; text-align: center; background-color: #d8d8d8;}
    QProgressBar::chunk { background-color: #5a8eda; width: 10px; margin: 0.5px;} /* Slightly different blue */
    QLabel#image_display_label { background-color: #d8d8d8; border: 1px solid #b0b0b0; }
    QListWidget::item:selected { background-color: #a8d8ff; color: #000; }
    QMessageBox { background-color: #e8e8e8; }
    QMessageBox QLabel { color: #000; }
    QMessageBox QLabel a { color: #0000CC; text-decoration: underline; } /* Slightly darker blue */
    QMessageBox QLabel a:visited { color: #551A8B; }
"""

DARK_STYLE = """
    QWidget { background-color: #2e2e2e; color: #e0e0e0; }
    QGroupBox { background-color: #3c3c3c; border: 1px solid #555; margin-top: 10px; padding: 5px; border-radius: 3px; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; background-color: #3c3c3c; color: #e0e0e0; border-radius: 3px;}
    QGroupBox[checkable="true"]::title { padding-left: 18px; }
    QGroupBox::indicator { width: 13px; height: 13px; }
    QGroupBox::indicator:unchecked { image: url(:/qt-project.org/styles/commonstyle/images/checkbox_unchecked_dark.png); }
    QGroupBox::indicator:checked { image: url(:/qt-project.org/styles/commonstyle/images/checkbox_checked_dark.png); }
    QPushButton { background-color: #505050; border: 1px solid #666; padding: 4px 8px; border-radius: 3px; color: #e0e0e0; min-height: 18px;}
    QPushButton:hover { background-color: #606060; }
    QPushButton:pressed { background-color: #707070; }
    QPushButton:disabled { background-color: #404040; color: #808080; border-color: #555;}
    QLineEdit, QTextEdit, QListWidget, QComboBox { background-color: #383838; border: 1px solid #555; color: #e0e0e0; selection-background-color: #005a9e; selection-color: #ffffff; border-radius: 3px; }
    QComboBox { selection-background-color: #005a9e; }
    QComboBox::drop-down { border: 1px solid #555; border-left: none; background-color: #505050;}
    QComboBox::down-arrow { image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-down-arrow-dark-16.png); }
    QScrollArea { border: none; background-color: transparent; }
    QSplitter::handle { background-color: #4a4a4a; }
    QSplitter::handle:horizontal { width: 5px; }
    QSplitter::handle:vertical { height: 5px; }
    QProgressBar { border: 1px solid #555; border-radius: 3px; text-align: center; background-color: #404040; color: #e0e0e0; }
    QProgressBar::chunk { background-color: #4a7cc0; width: 10px; margin: 0.5px;}
    QLabel#image_display_label { background-color: #383838; border: 1px solid #555; }
    QListWidget::item:selected { background-color: #005a9e; color: #ffffff; }
    QTextEdit { selection-background-color: #005a9e; }
    QMessageBox { background-color: #2e2e2e; }
    QMessageBox QLabel { color: #e0e0e0; }
    QMessageBox QLabel a { color: #66b3ff; text-decoration: underline; } /* Brighter blue */
    QMessageBox QLabel a:visited { color: #ce9178; }
"""

# --- Worker --- (Identical to previous version)
class SubprocessWorker(QObject):
    finished = Signal(bool, str, str); progress = Signal(str)
    def __init__(self, command_list): super().__init__(); self.command_list = command_list
    def run(self):
        stdout_acc, stderr_acc, success = "", "", False
        try:
            self.progress.emit(f"Starting: {' '.join(self.command_list)}")
            if not os.path.exists(self.command_list[0]): raise FileNotFoundError(f"Executable not found: {self.command_list[0]}")
            creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            process = subprocess.Popen(self.command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False, creationflags=creationflags, encoding='utf-8', errors='replace')
            stdout_data, stderr_data = process.communicate()
            stdout_acc, stderr_acc = (stdout_data or ""), (stderr_data or "")
            success = (process.returncode == 0)
            self.progress.emit(f"Finished with code {process.returncode}")
        except FileNotFoundError as e: stderr_acc = f"[ERROR] {e}"; success = False
        except Exception as e: stderr_acc = f"[ERROR] Python exception:\n{traceback.format_exc()}"; success = False
        finally: self.finished.emit(success, stdout_acc, stderr_acc)

# --- Help Window --- (Identical to previous version, content updated via main window method)
class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("3it GUI - Command Help"); self.setGeometry(200, 200, 750, 550)
        layout = QVBoxLayout(self); self.help_text_edit = QTextEdit(); self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setFontFamily("Courier New"); self.help_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.help_text_edit.setPlainText(self.generate_full_help())
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); button_box.rejected.connect(self.reject)
        layout.addWidget(self.help_text_edit); layout.addWidget(button_box)
    def generate_full_help(self):
        help_content = "..." # Content generated dynamically using parent's method
        main_window_instance = self.parent()
        if main_window_instance and hasattr(main_window_instance, 'get_formatted_help'):
            help_content = main_window_instance._generate_full_help_text() # Use helper
        else: help_content = "[Error: Could not retrieve help content.]"
        return help_content


# --- Main GUI Window ---
class ThreeItMainWindow(QWidget):
    log_update_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.input_file_paths = []
        self.output_path_is_dir = False
        self.output_file_path = ""
        self.palette_file_path = ""
        self.current_output_dir = ""
        self.last_browse_location = os.path.expanduser("~")
        self.output_images = []
        self.current_image_index = -1
        self.option_widgets = {}
        self.worker_thread = None
        self.worker = None
        self.last_run_subcommand = ""
        self.help_window = None

        self.initUI()
        self._update_ui_for_subcommand(self.combo_subcommand.currentText())
        self._update_output_widgets_state() # Initial state based on input count (0)
        self.log_update_signal.connect(self.log_message)

    def initUI(self):
        main_h_layout = QHBoxLayout(self)
        main_h_layout.setSpacing(6); main_h_layout.setContentsMargins(8, 8, 8, 8)

        # --- Left Panel ---
        left_panel_widget = QWidget(); left_v_layout = QVBoxLayout(left_panel_widget)
        left_v_layout.setSpacing(8); left_v_layout.setContentsMargins(0, 0, 0, 0)

        # Banner
        self.banner_label = QLabel()
        if os.path.exists(BANNER_PATH):
            pixmap = QPixmap(BANNER_PATH); max_banner_width = 500
            if pixmap.width() > max_banner_width: pixmap = pixmap.scaledToWidth(max_banner_width, Qt.SmoothTransformation)
            self.banner_label.setPixmap(pixmap)
        else: self.banner_label.setText("3it GUI"); self.banner_label.setFont(QFont("Arial", 14, QFont.Bold)); self.banner_label.setFixedHeight(30)
        self.banner_label.setAlignment(Qt.AlignCenter); left_v_layout.addWidget(self.banner_label)

        # IO Group
        self.io_group = QGroupBox("Input / Output")
        io_layout = QFormLayout(self.io_group); io_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        input_widget_layout = QHBoxLayout()
        self.input_list_widget = QListWidget(); self.input_list_widget.setToolTip("Selected source files."); self.input_list_widget.setFixedHeight(70)
        input_buttons_layout = QVBoxLayout(); self.btn_browse_input = QPushButton("Browse..."); self.btn_clear_input = QPushButton("Clear") # Made buttons instance vars
        self.btn_browse_input.clicked.connect(self.browse_input_files); self.btn_clear_input.clicked.connect(self.clear_input_files)
        input_buttons_layout.addWidget(self.btn_browse_input); input_buttons_layout.addWidget(self.btn_clear_input); input_buttons_layout.addStretch()
        input_widget_layout.addWidget(self.input_list_widget, 1); input_widget_layout.addLayout(input_buttons_layout)
        io_layout.addRow("Input File(s):", input_widget_layout)
        # Output Section
        output_widget_layout = QHBoxLayout()
        self.output_label = QLabel("N/A"); self.output_label.setWordWrap(True); self.output_label.setToolTip("Destination.") # Tooltip updated dynamically
        self.btn_browse_output = QPushButton("Select..."); self.btn_browse_output.setToolTip("Select output file/directory.")
        self.btn_clear_output = QPushButton("Clear"); self.btn_browse_output.clicked.connect(self.browse_output_file); self.btn_clear_output.clicked.connect(self.clear_output_file)
        output_buttons_layout = QVBoxLayout(); output_buttons_layout.addWidget(self.btn_browse_output); output_buttons_layout.addWidget(self.btn_clear_output); output_buttons_layout.addStretch()
        output_widget_layout.addWidget(self.output_label, 1); output_widget_layout.addLayout(output_buttons_layout)
        self.output_row_label = QLabel("Output Path:"); io_layout.addRow(self.output_row_label, output_widget_layout)
        # List of widgets to disable/enable for output path control
        self.output_control_widgets = [self.output_row_label, self.output_label, self.btn_browse_output, self.btn_clear_output]
        left_v_layout.addWidget(self.io_group)

        # Action Group
        self.action_exec_group = QGroupBox("Action & Run")
        action_exec_layout = QVBoxLayout(self.action_exec_group)
        main_action_layout = QHBoxLayout(); main_action_layout.addWidget(QLabel("Action:"))
        self.combo_subcommand = QComboBox(); self.combo_subcommand.addItems(["to-cel", "to-banner", "to-imag", "to-lrform", "to-nfs-shpm", "to-bmp", "to-png", "to-jpg"])
        self.combo_subcommand.setToolTip("Select conversion action."); self.combo_subcommand.currentTextChanged.connect(self._update_ui_for_subcommand)
        main_action_layout.addWidget(self.combo_subcommand, 1); action_exec_layout.addLayout(main_action_layout)
        self.btn_run_action = QPushButton("Run Selected Action"); self.btn_run_action.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 5px; font-weight: bold; }")
        self.btn_run_action.setToolTip("Execute selected action."); self.btn_run_action.clicked.connect(self.run_action_confirmed) # Connect to confirmation step
        action_exec_layout.addWidget(self.btn_run_action)
        action_exec_layout.addSpacerItem(QSpacerItem(1, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        action_exec_layout.addWidget(QLabel("Quick Actions / Info:"))
        quick_actions_layout = QGridLayout()
        btn_info = QPushButton("Info"); btn_list_chunks = QPushButton("List Chunks"); btn_dpi = QPushButton("Dump PIXC")
        btn_help = QPushButton("Help"); btn_about = QPushButton("About") # Version button removed
        btn_info.setToolTip("Get info (-i)."); btn_list_chunks.setToolTip("List chunks."); btn_dpi.setToolTip("Dump instructions (dpi).")
        btn_help.setToolTip("Show help."); btn_about.setToolTip("Show credits.")
        btn_info.clicked.connect(lambda: self.run_action("info")); btn_list_chunks.clicked.connect(lambda: self.run_action("list-chunks"))
        btn_dpi.clicked.connect(lambda: self.run_action("dump-packed-instructions"))
        btn_help.clicked.connect(self.show_help_window); btn_about.clicked.connect(self.show_about_window)
        quick_actions_layout.addWidget(btn_info, 0, 0); quick_actions_layout.addWidget(btn_list_chunks, 0, 1)
        quick_actions_layout.addWidget(btn_dpi, 1, 0); quick_actions_layout.addWidget(btn_help, 1, 1) # Help moved up
        quick_actions_layout.addWidget(btn_about, 2, 0, 1, 2) # Span About
        action_exec_layout.addLayout(quick_actions_layout)
        action_exec_layout.addSpacerItem(QSpacerItem(1, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        action_exec_layout.addWidget(QLabel("Manual Command:"))
        self.manual_cmd_input = QLineEdit(); self.manual_cmd_input.setPlaceholderText("Arguments only")
        self.manual_cmd_input.setToolTip("Enter 3it args, excluding '3it.exe'. Use quotes for spaces.")
        btn_run_manual = QPushButton("Run Manual Command"); btn_run_manual.clicked.connect(self.run_manual_command)
        action_exec_layout.addWidget(self.manual_cmd_input); action_exec_layout.addWidget(btn_run_manual)
        self.progress_bar = QProgressBar(); self.progress_bar.setRange(0, 0); self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False); self.progress_bar.setFixedHeight(15)
        action_exec_layout.addWidget(self.progress_bar)
        left_v_layout.addWidget(self.action_exec_group)

        # Bottom Area: Log / Viewer
        bottom_area_layout = QHBoxLayout()
        log_group = QGroupBox("Execution Log"); log_layout = QVBoxLayout(log_group)
        self.log_area = QTextEdit(); self.log_area.setReadOnly(True); self.log_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_area.setFontFamily("Courier New"); self.log_area.setFontPointSize(9); self.log_area.setMinimumHeight(80)
        btn_clear_log = QPushButton("Clear Log"); btn_clear_log.setToolTip("Clear log."); btn_clear_log.clicked.connect(self.clear_log)
        log_button_layout = QHBoxLayout(); log_button_layout.addStretch(); log_button_layout.addWidget(btn_clear_log)
        log_layout.addWidget(self.log_area, 1); log_layout.addLayout(log_button_layout)
        bottom_area_layout.addWidget(log_group, 1) # Log takes expanding space

        viewer_group = QGroupBox("Output Preview"); viewer_layout = QVBoxLayout(viewer_group)
        self.image_display_label = QLabel("Preview Area"); self.image_display_label.setObjectName("image_display_label")
        self.image_display_label.setAlignment(Qt.AlignCenter); self.image_display_label.setMinimumSize(360, 300)
        self.image_filename_label = QLabel(""); self.image_filename_label.setAlignment(Qt.AlignCenter); self.image_filename_label.setToolTip("Filename.")
        viewer_controls_layout = QHBoxLayout()
        btn_prev_img = QPushButton("<<"); btn_next_img = QPushButton(">>"); btn_open_folder = QPushButton("Open Folder")
        btn_prev_img.setToolTip("Previous"); btn_next_img.setToolTip("Next"); btn_open_folder.setToolTip("Open folder.")
        btn_prev_img.setFixedWidth(35); btn_next_img.setFixedWidth(35)
        self.image_index_label = QLabel("0 / 0"); self.image_index_label.setAlignment(Qt.AlignCenter)
        btn_prev_img.clicked.connect(self.show_prev_image); btn_next_img.clicked.connect(self.show_next_image); btn_open_folder.clicked.connect(self.open_output_folder)
        viewer_controls_layout.addWidget(btn_prev_img); viewer_controls_layout.addWidget(self.image_index_label, 1); viewer_controls_layout.addWidget(btn_next_img); viewer_controls_layout.addStretch(); viewer_controls_layout.addWidget(btn_open_folder)
        viewer_layout.addWidget(self.image_display_label, 1); viewer_layout.addWidget(self.image_filename_label); viewer_layout.addLayout(viewer_controls_layout)
        self.viewer_widgets = [viewer_group, self.image_display_label, btn_prev_img, btn_next_img, btn_open_folder, self.image_index_label, self.image_filename_label]
        for w in self.viewer_widgets[2:]: w.setEnabled(False)
        bottom_area_layout.addWidget(viewer_group, 0)
        left_v_layout.addLayout(bottom_area_layout, 1)

        # --- Right Panel (Options) ---
        self.options_scroll_area = QScrollArea(); self.options_scroll_area.setWidgetResizable(True)
        self.options_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn); self.options_scroll_area.setFrameShape(QScrollArea.StyledPanel) # No border for cleaner look
        self.options_scroll_area.setMinimumWidth(800) # Ensure options have some minimum width
        self.options_container = QWidget(); self.options_container_layout = QVBoxLayout(self.options_container)
        self.options_container_layout.setContentsMargins(8, 8, 8, 8); self.options_container_layout.setSpacing(8) # Adjusted margins

        # Theme Selector moved to top of right panel
        theme_layout = QHBoxLayout(); theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox(); self.theme_combo.addItems(["Light", "Dark", "System Default"])
        self.theme_combo.setToolTip("Change GUI color theme."); self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo); theme_layout.addStretch()
        self.options_container_layout.addLayout(theme_layout)

        # Create and add option groups
        self._create_cel_options(); self._create_nfs_shpm_options(); self._create_generic_image_options()
        self.options_container_layout.addWidget(self.cel_options_group); self.options_container_layout.addWidget(self.nfs_shpm_options_group); self.options_container_layout.addWidget(self.generic_image_options_group)
        self.options_container_layout.addStretch(1); self.options_scroll_area.setWidget(self.options_container)

        # --- Splitter ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel_widget)
        splitter.addWidget(self.options_scroll_area)
        splitter.setSizes([600, 300]) # Initial size ratio
        splitter.setStretchFactor(0, 1) # Allow left panel to expand more initially if needed
        splitter.setStretchFactor(1, 0) # Options panel less eager to expand
        splitter.setCollapsible(0, False); splitter.setCollapsible(1, True)
        main_h_layout.addWidget(splitter)

        self.setLayout(main_h_layout)
        self.setWindowTitle(APP_TITLE); self.setGeometry(100, 100, 950, 700)
        self.change_theme("Light")

    # --- Helper methods to create option groups ---
    def _make_editable_combo(self, items, tooltip=""):
        combo = QComboBox(); combo.addItems(items); combo.setEditable(True)
        combo.setToolTip(tooltip + "\n(You can also type a custom value)")
        if combo.lineEdit(): combo.lineEdit().setPlaceholderText("<Select or type>"); combo.lineEdit().setClearButtonEnabled(True)
        return combo

    def _create_cel_options(self):
        self.cel_options_group = QGroupBox("to-cel: Options"); layout = QFormLayout(self.cel_options_group)
        layout.setLabelAlignment(Qt.AlignRight) # Align labels to the right
        layout.setContentsMargins(5, 10, 5, 5); layout.setSpacing(6)
        # Basic Group
        basic_cel_group = QGroupBox("Basic Properties"); basic_cel_layout = QFormLayout(basic_cel_group)
        self.option_widgets['cel_bpp'] = QComboBox(); self.option_widgets['cel_bpp'].addItems(["16", "8", "6", "4", "2", "1"]); self.option_widgets['cel_bpp'].setToolTip("Bits Per Pixel (-b)")
        basic_cel_layout.addRow("Bits Per Pixel:", self.option_widgets['cel_bpp'])
        self.option_widgets['cel_coded'] = QCheckBox("Store coded (paletted)"); self.option_widgets['cel_coded'].setToolTip("--coded")
        basic_cel_layout.addRow(self.option_widgets['cel_coded'])
        self.option_widgets['cel_lrform'] = QCheckBox("Store LRFORM"); self.option_widgets['cel_lrform'].setToolTip("--lrform")
        basic_cel_layout.addRow(self.option_widgets['cel_lrform'])
        self.option_widgets['cel_packed'] = QCheckBox("Pack pixel data"); self.option_widgets['cel_packed'].setToolTip("--packed")
        basic_cel_layout.addRow(self.option_widgets['cel_packed'])
        self.option_widgets['cel_transparent'] = self._make_editable_combo(["magenta", "black", "white", "red", "green", "blue", "cyan"], "Packed transparent color (--transparent)\nSpecify name or 0xRRGGBBAA hex.")
        basic_cel_layout.addRow("Transparent Color:", self.option_widgets['cel_transparent'])
        self.option_widgets['cel_rotation'] = QComboBox(); self.option_widgets['cel_rotation'].addItems(["0", "90", "180", "270"]); self.option_widgets['cel_rotation'].setToolTip("Rotation degrees (--rotation)")
        basic_cel_layout.addRow("Rotation:", self.option_widgets['cel_rotation'])
        layout.addRow(basic_cel_group)
        # Palette Group
        palette_group = QGroupBox("Palette"); palette_layout = QFormLayout(palette_group)
        pal_browse_layout = self._create_file_browse_row("Select Palette File", self.browse_palette_file, self.clear_palette_file)
        self.option_widgets['cel_palette_label'] = pal_browse_layout.findChild(QLabel)
        palette_layout.addRow("External Palette:", pal_browse_layout)
        self.option_widgets['cel_no_write_plut'] = QCheckBox("Do NOT write PLUT"); self.option_widgets['cel_no_write_plut'].setToolTip("Check for --write-plut=false.")
        palette_layout.addRow(self.option_widgets['cel_no_write_plut'])
        layout.addRow(palette_group)
        # Generation Group
        gen_group = QGroupBox("Generation Mode"); gen_layout = QFormLayout(gen_group)
        self.option_widgets['cel_generate_all'] = QCheckBox("Generate ALL permutations"); self.option_widgets['cel_generate_all'].setToolTip("--generate-all")
        self.option_widgets['cel_find_smallest'] = QComboBox(); self.option_widgets['cel_find_smallest'].addItems(["None", "regular", "rotation"]); self.option_widgets['cel_find_smallest'].setToolTip("Find smallest format (--find-smallest)")
        gen_layout.addRow(self.option_widgets['cel_generate_all']); gen_layout.addRow("Find Smallest:", self.option_widgets['cel_find_smallest'])
        self.option_widgets['cel_generate_all'].toggled.connect(self._update_cel_option_states)
        self.option_widgets['cel_find_smallest'].currentTextChanged.connect(self._update_cel_option_states)
        layout.addRow(gen_group)
        # Advanced Flags Group
        ccb_group = QGroupBox("Advanced CCB/PRE0 Flags"); ccb_group.setCheckable(True); ccb_group.setChecked(False)
        ccb_layout = QGridLayout(ccb_group)
        ccb_flags = ["skip", "last", "npabs", "spabs", "ppabs", "ldsize", "ldprs", "ldplut", "ccbpre", "yoxy", "acsc", "alsc", "acw", "accw", "twd", "lce", "ace", "maria", "pxor", "useav", "packed", "plutpos", "bgnd", "noblk"]
        pre0_flags = ["literal", "bgnd", "uncoded", "rep8"]
        row, col, max_cols = 0, 0, 3 # Adjusted max cols for potentially better fit
        for flag in ccb_flags: combo = QComboBox(); combo.addItems(["default", "set", "unset"]); combo.setToolTip(f"--ccb-{flag}"); self.option_widgets[f'cel_ccb_{flag}'] = combo; ccb_layout.addWidget(QLabel(f"{flag.upper()}:"), row, col*2); ccb_layout.addWidget(combo, row, col*2 + 1); col += 1;
        if col >= max_cols: col = 0; row += 1
        row += 1 if col != 0 else 0; col = 0
        if row > 0: hline = QFrame(); hline.setFrameShape(QFrame.Shape.HLine); hline.setFrameShadow(QFrame.Shadow.Sunken); ccb_layout.addWidget(hline, row, 0, 1, max_cols*2); row += 1
        for flag in pre0_flags: combo = QComboBox(); combo.addItems(["default", "set", "unset"]); combo.setToolTip(f"--pre0-{flag}"); self.option_widgets[f'cel_pre0_{flag}'] = combo; ccb_layout.addWidget(QLabel(f"{flag.upper()}:"), row, col*2); ccb_layout.addWidget(combo, row, col*2 + 1); col += 1;
        if col >= max_cols: col = 0; row += 1
        layout.addRow(ccb_group)
        # Common Group
        common_group = QGroupBox("Common"); common_layout = QFormLayout(common_group)
        self.option_widgets['cel_ignore_ext'] = QCheckBox("Ignore input with target ext"); self.option_widgets['cel_ignore_ext'].setToolTip("-i")
        common_layout.addRow(self.option_widgets['cel_ignore_ext']); layout.addRow(common_group)
        self.cel_options_group.hide()

    def _create_nfs_shpm_options(self):
        self.nfs_shpm_options_group = QGroupBox("to-nfs-shpm: Options"); layout = QFormLayout(self.nfs_shpm_options_group)
        layout.setLabelAlignment(Qt.AlignRight); layout.setContentsMargins(5, 10, 5, 5); layout.setSpacing(6)
        self.option_widgets['nfs_packed'] = QCheckBox("Pack pixel data"); self.option_widgets['nfs_packed'].setToolTip("--packed")
        layout.addRow(self.option_widgets['nfs_packed'])
        self.option_widgets['nfs_transparent'] = self._make_editable_combo(["magenta", "black", "white", "red", "green", "blue", "cyan"], "Packed transparent color (--transparent)\nSpecify name or 0xRRGGBBAA hex.")
        layout.addRow("Transparent Color:", self.option_widgets['nfs_transparent']); self.nfs_shpm_options_group.hide()

    def _create_generic_image_options(self):
        self.generic_image_options_group = QGroupBox("Common Options"); layout = QFormLayout(self.generic_image_options_group)
        layout.setLabelAlignment(Qt.AlignRight); layout.setContentsMargins(5, 10, 5, 5); layout.setSpacing(6)
        self.option_widgets['generic_ignore_ext'] = QCheckBox("Ignore input with target ext"); self.option_widgets['generic_ignore_ext'].setToolTip("-i")
        layout.addRow(self.option_widgets['generic_ignore_ext']); self.generic_image_options_group.hide()

    def _create_file_browse_row(self, label_text, browse_slot, clear_slot):
        layout = QHBoxLayout(); layout.setSpacing(4)
        label = QLabel("None"); label.setWordWrap(True); label.setToolTip(f"Path to {label_text}."); label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        btn_browse = QPushButton("..."); btn_browse.setToolTip(f"Select {label_text}"); btn_browse.setFixedWidth(35)
        btn_clear = QPushButton("X"); btn_clear.setToolTip(f"Clear {label_text}"); btn_clear.setFixedWidth(35)
        btn_browse.clicked.connect(browse_slot); btn_clear.clicked.connect(clear_slot)
        layout.addWidget(label, 1); layout.addWidget(btn_browse); layout.addWidget(btn_clear)
        layout.setStretchFactor(label, 1)
        return layout

    # --- UI Update Logic ---
    def _update_output_widgets_state(self):
        """Enable/disable output path widgets based on input file count."""
        num_inputs = len(self.input_file_paths)
        enabled = num_inputs <= 1 # Enable only if 0 or 1 input file
        for w in self.output_control_widgets:
             if w: w.setEnabled(enabled)
        if not enabled:
             self.output_label.setText("(Default: Input Dir)")
             self.output_label.setToolTip("Output path disabled for multiple inputs.\nFiles will be saved in their respective input directories.")
        else:
             self.update_output_label() # Restore normal label/tooltip if enabled

    def _update_ui_for_subcommand(self, subcommand):
        """Show/hide options, update output state based on selected subcommand."""
        self.cel_options_group.hide(); self.nfs_shpm_options_group.hide(); self.generic_image_options_group.hide()
        self._update_output_widgets_state() # Enable/disable output based on *current* input count

        options_group_visible = False
        if subcommand == "to-cel": self.cel_options_group.show(); self._update_cel_option_states(); options_group_visible = True
        elif subcommand == "to-nfs-shpm": self.nfs_shpm_options_group.show(); options_group_visible = True
        elif subcommand in ["to-banner", "to-imag", "to-lrform", "to-bmp", "to-png", "to-jpg"]: self.generic_image_options_group.show(); options_group_visible = True

        self.options_container.setVisible(options_group_visible)
        self.options_scroll_area.updateGeometry()


    def _update_cel_option_states(self):
        """Enable/disable CEL options based on generate/find modes."""
        if not self.cel_options_group.isVisible(): return
        opts = self.option_widgets
        is_gen_all_checked = opts['cel_generate_all'].isChecked()
        find_mode = opts['cel_find_smallest'].currentText()
        is_find_smallest_set = (find_mode != "None")
        basic_option_keys = ['cel_bpp', 'cel_coded', 'cel_lrform', 'cel_packed', 'cel_rotation', 'cel_transparent']
        sender = self.sender()
        if sender == opts['cel_generate_all'] and is_gen_all_checked and is_find_smallest_set:
            opts['cel_find_smallest'].setCurrentIndex(0); is_find_smallest_set = False
        elif sender == opts['cel_find_smallest'] and is_find_smallest_set and is_gen_all_checked:
            opts['cel_generate_all'].setChecked(False); is_gen_all_checked = False
        opts['cel_generate_all'].setEnabled(not is_find_smallest_set)
        opts['cel_find_smallest'].setEnabled(not is_gen_all_checked)
        should_disable_basic = is_gen_all_checked or is_find_smallest_set
        for key in basic_option_keys:
            if key in opts: opts[key].setEnabled(not should_disable_basic)

    def _generate_full_help_text(self):
        """Helper to assemble text for the help window."""
        help_content = "..." # Replaced with actual generation logic
        # (Identical content generation as before, just moved here)
        help_content = """
=========================
 3it GUI - Command Help
=========================

This GUI provides an interface for the 3it command-line tool.
Select an action, specify input/output files, configure options, and run.

-------------------------
 Available Actions & Help
-------------------------
"""
        commands = [
            "info", "to-cel", "to-banner", "to-imag", "to-lrform", "to-nfs-shpm",
            "to-bmp", "to-png", "to-jpg", "list-chunks", "dump-packed-instructions",
            "version" # Version kept for help text
        ]
        for cmd in commands:
             help_content += f"\n---------- {cmd} ----------\n"
             help_content += self.get_formatted_help(cmd) # Use existing getter
             help_content += "\n"

        help_content += """
-------------------------
 Output Path Templates
-------------------------
Many conversion commands support templates in the output path (-o).
Examples: {filename}.png, output/{dirpath}/{filename}_{index}.cel

Common Templates:
  {filepath}: Full original input filepath.
  {dirpath}: Parent path of {filepath}. "." if no parent.
  {filename}: Filename without dirpath or extension.
  {origext}: Original extension (including '.').
  {ext}: Standard extension for the target format (e.g., '.cel', '.png').
  {_name}: Internal name from source (if supported), prefixed with '_'. Empty otherwise.
  {index}: Index (0-based) if input has multiple images/frames.
  {_index}: Index prefixed with '_' if input has multiple images/frames. Empty otherwise.
  {w}: Output image width in pixels.
  {h}: Output image height in pixels.

See specific command help below for additional available templates
(like {bpp}, {coded}, {flags} for to-cel).

-------------------------
 Manual Command
-------------------------
Use the 'Manual Command' field to enter arguments directly as you would
on the command line, *excluding* the '3it.exe' executable name itself.
Arguments are space-separated. Use double quotes (" ") around paths or
arguments containing spaces.

Example: to-png "my image file.cel" "output/image name.png" -i

-------------------------
 Tips & Notes
-------------------------
* Hover over options in the GUI for tooltips explaining the corresponding flag.
* Use 'Clear Input'/'Clear Output' buttons to reset file selections.
* Use 'Clear Log' button to clear the execution log area.
* Check the 'Execution Log' for detailed output and errors from 3it.
* The 'Output Preview' previews common formats in the output folder.
* For 'to-cel', advanced flags are in a collapsible section.
* Operations run in the background; the GUI stays responsive.
* If multiple input files are selected, output path selection is disabled,
  and files will be saved in their respective input directories using
  default naming templates (this is 3it's default behavior).
* If a single input file is selected and no output path is specified,
  the output will be saved in the input directory with a default name/extension.
* Use the 'Theme' dropdown to switch visual styles.
* Use the splitter bar to resize the main panels.
"""
        return help_content.strip()


    def get_formatted_help(self, subcommand):
        """Retrieves help text for a specific subcommand."""
        # (Identical map content as before)
        help_map = {
             "info": """info: Prints info about the file(s)\nUsage: 3it info [filepaths...]\n\nPositionals:\n  filepaths   PATH:FILE ... REQUIRED: Path to file(s)""",
             "to-cel": """to-cel: Convert image to CEL\nUsage: 3it to-cel [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED: Path to image(s) or directory\n\nOptions: (Defaults in [])\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -b,--bpp BPP:{1,2,4,6,8,16} [16] Excludes: --generate-all, --find-smallest\n  --coded BOOLEAN [false] Excludes: --generate-all, --find-smallest\n  --lrform BOOLEAN [false] Excludes: --generate-all, --find-smallest\n  --packed BOOLEAN [false] Excludes: --generate-all, --find-smallest\n  --transparent COLOR [magenta]: {black,white,red,green,blue,magenta,cyan,0xRRGGBBAA}\n  -i,--ignore-target-ext BOOLEAN [false]\n  --external-palette PATH:FILE\n  --write-plut BOOLEAN [true] (Check GUI box for FALSE)\n  --rotation INT:{0,90,180,270} [0] Excludes: --generate-all, --find-smallest\n  --generate-all [false] Excludes: --bpp, --coded, --lrform, --packed, --find-smallest, --rotation\n  --find-smallest TEXT:{regular,rotation} Excludes: --bpp, --coded, --lrform, --packed, --generate-all, --rotation\n  --ccb-<flag> ENUM:{default,set,unset} [default] \n  --pre0-<flag> ENUM:{default,set,unset} [default]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}, {coded}, {packed}, {lrform}, {_lrform}, {bpp}, {flags}, {pixc}, {rotation}""",
             "to-banner": """to-banner: Convert image to banner\nUsage: 3it to-banner [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED\n\nOptions:\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -i,--ignore-target-ext BOOLEAN [false]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}, {bpp} (16)""",
             "to-imag": """to-imag: Convert image to IMAG\nUsage: 3it to-imag [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED\n\nOptions:\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -i,--ignore-target-ext BOOLEAN [false]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}""",
             "to-lrform": """to-lrform: Convert image to raw LRFORM\nUsage: 3it to-lrform [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED\n\nOptions:\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -i,--ignore-target-ext BOOLEAN [false]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}""",
             "to-nfs-shpm": """to-nfs-shpm: Convert image to NFS SHPM\nUsage: 3it to-nfs-shpm [OPTIONS] filepath...\n\nPositionals:\n  filepath   PATH:FILE ... REQUIRED\n\nOptions:\n  -o,--output-path PATH\n  --packed BOOLEAN [false]\n  --transparent COLOR [magenta]: {black,white,red,green,blue,magenta,cyan,0xRRGGBBAA}""",
             "to-bmp": """to-bmp: Convert image to BMP\nUsage: 3it to-bmp [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED\n\nOptions:\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -i,--ignore-target-ext BOOLEAN [false]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}""",
             "to-png": """to-png: Convert image to PNG\nUsage: 3it to-png [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED\n\nOptions:\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -i,--ignore-target-ext BOOLEAN [false]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}""",
             "to-jpg": """to-jpg: Convert image to JPG\nUsage: 3it to-jpg [OPTIONS] filepaths...\n\nPositionals:\n  filepaths   PATH:PATH(existing)... REQUIRED\n\nOptions:\n  -o,--output-path PATH [{filepath}{_index}{_name}{ext}]\n  -i,--ignore-target-ext BOOLEAN [false]\n\nOutput Templates: {filepath}, {dirpath}, {filename}, {origext}, {ext}, {_name}, {index}, {_index}, {w}, {h}""",
             "list-chunks": """list-chunks: List 3DO file chunks\nUsage: 3it list-chunks [filepaths...]\n\nPositionals:\n  filepaths   PATH:FILE ... REQUIRED""",
             "dump-packed-instructions": """dump-packed-instructions (dpi): Print packed CEL instructions\nUsage: 3it dump-packed-instructions filepath\n\nPositionals:\n  filepath   PATH:FILE REQUIRED""",
             "version": """version: Print 3it version\nUsage: 3it version""",
             "docs": """docs: Print links to relevant documentation\nUsage: 3it docs""",
        }
        if "dump-packed-instructions" in help_map: help_map["dpi"] = help_map["dump-packed-instructions"]
        return help_map.get(subcommand, f"Help for '{subcommand}' not available.")

    # --- File Handling Slots ---
    def browse_input_files(self):
        """Opens dialog to select multiple input files."""
        fnames, _ = QFileDialog.getOpenFileNames(self, 'Select Input File(s)', self.last_browse_location, 'All Files (*)')
        if fnames:
            self.last_browse_location = os.path.dirname(fnames[0])
            current_files = set(self.input_file_paths)
            new_files_to_add = [os.path.normpath(f) for f in fnames if os.path.normpath(f) not in current_files]
            if new_files_to_add:
                self.input_file_paths.extend(new_files_to_add)
                self.input_list_widget.addItems([os.path.basename(f) for f in new_files_to_add])
                for i in range(self.input_list_widget.count() - len(new_files_to_add), self.input_list_widget.count()):
                    self.input_list_widget.item(i).setToolTip(self.input_file_paths[i])
            self._update_output_widgets_state() # Update output enable state

    def clear_input_files(self):
        self.input_file_paths = []; self.input_list_widget.clear()
        self._update_output_widgets_state() # Update output enable state

    def browse_output_file(self):
        """Handles selecting the output path (file for single input, dir for multiple)."""
        start_dir = self.last_browse_location
        selected_path = None
        self.output_path_is_dir = False # Reset flag

        num_inputs = len(self.input_file_paths)

        # Output path selection is only enabled when num_inputs <= 1, so we only need getSaveFileName
        dialog_title = 'Select Output File or Directory'
        suggested_name = ""
        if num_inputs == 1:
            first_input = self.input_file_paths[0]
            base, input_ext = os.path.splitext(os.path.basename(first_input))
            subcommand = self.combo_subcommand.currentText()
            ext_map = {"to-cel": ".cel", "to-banner": ".bnr", "to-imag": ".imag", "to-lrform": ".lrform", "to-nfs-shpm": ".shpm", "to-bmp": ".bmp", "to-png": ".png", "to-jpg": ".jpg"}
            ext = ext_map.get(subcommand, input_ext if input_ext else ".out")
            suggested_name = base + ext
            start_dir = os.path.dirname(first_input)
        elif num_inputs == 0:
             start_dir = self.last_browse_location # Use last known location

        selected_path, _ = QFileDialog.getSaveFileName(
            self, dialog_title, os.path.join(start_dir, suggested_name), 'All Files (*)'
        )

        if selected_path:
            self.last_browse_location = os.path.dirname(selected_path) # Remember dir
            self.output_file_path = os.path.normpath(selected_path)
            # Determine if it's likely a directory after selection
            self.output_path_is_dir = os.path.isdir(self.output_file_path) or \
                                      (not os.path.exists(self.output_file_path) and not os.path.splitext(self.output_file_path)[1])
            self.current_output_dir = self.output_file_path if self.output_path_is_dir else os.path.dirname(self.output_file_path)
            self.update_output_label()
            self._clear_image_viewer()

    def clear_output_file(self):
        self.output_file_path = ""; self.output_path_is_dir = False
        self.current_output_dir = ""; self.update_output_label(); self._clear_image_viewer()

    def update_output_label(self):
        """Updates the output label text and tooltip based on current state."""
        num_inputs = len(self.input_file_paths)
        enabled = num_inputs <= 1

        if not enabled: # Explicitly handle disabled state first
            self.output_label.setText("(Default: Input Dir)")
            self.output_label.setToolTip("Output path disabled for multiple inputs.\nFiles saved in their respective input directories.")
        elif not self.output_file_path:
            self.output_label.setText("No path selected")
            self.output_label.setToolTip("Destination path/template.\nIf empty, output saved in input directory.")
        elif self.output_path_is_dir:
            self.output_label.setText(f"Folder: ...{os.path.sep}{os.path.basename(self.output_file_path)}")
            self.output_label.setToolTip(f"Output Directory: {self.output_file_path}\n(Using default filename templates)")
        else: # It's a file path
            self.output_label.setText(os.path.basename(self.output_file_path))
            self.output_label.setToolTip(f"Output File: {self.output_file_path}")

    def browse_palette_file(self):
        start_dir = self.last_browse_location
        if self.input_file_paths: start_dir = os.path.dirname(self.input_file_paths[0])
        fname, _ = QFileDialog.getOpenFileName(self, 'Select CEL Palette File', start_dir, 'CEL files (*.cel);;All Files (*)')
        if fname:
            self.last_browse_location = os.path.dirname(fname)
            self.palette_file_path = fname
            if 'cel_palette_label' in self.option_widgets:
                 label_widget = self.option_widgets['cel_palette_label']
                 if label_widget and isinstance(label_widget, QLabel): label_widget.setText(os.path.basename(fname)); label_widget.setToolTip(fname)

    def clear_palette_file(self):
        self.palette_file_path = ""
        if 'cel_palette_label' in self.option_widgets:
             label_widget = self.option_widgets['cel_palette_label']
             if label_widget and isinstance(label_widget, QLabel): label_widget.setText("None"); label_widget.setToolTip("Path to the palette file.")

    # --- Action Execution ---
    def set_running_state(self, running):
        """Enable/disable controls during execution."""
        self.progress_bar.setVisible(running)
        controls_to_toggle = [self.combo_subcommand, self.btn_run_action, self.manual_cmd_input, self.theme_combo]
        controls_to_toggle.extend(self.io_group.findChildren(QPushButton))
        controls_to_toggle.extend(self.action_exec_group.findChildren(QPushButton))

        # Options container contents
        for group_box in self.options_container.findChildren(QGroupBox):
             is_collapsible = group_box.isCheckable()
             can_interact_content = not is_collapsible or group_box.isChecked()
             for child_widget in group_box.findChildren(QWidget):
                 # Check widget exists and has setEnabled before calling
                 if child_widget and hasattr(child_widget, 'setEnabled') and not isinstance(child_widget, (QLabel, QGroupBox, QFrame)):
                     # Disable if running OR if parent group is collapsed (and checkable)
                     child_widget.setEnabled(not running and can_interact_content)
             if is_collapsible: group_box.setEnabled(not running) # Disable group checkbox itself

        # Main controls list
        for w in controls_to_toggle:
            if w and w != self.progress_bar: w.setEnabled(not running)

        # Re-apply output widget state after potentially being disabled above
        self._update_output_widgets_state()


    def _confirm_run_action(self, subcommand, command_args):
        """Shows confirmation dialog before running the action."""
        num_inputs = len(self.input_file_paths)
        input_desc = f"{num_inputs} file(s)" if num_inputs > 1 else os.path.basename(self.input_file_paths[0]) if num_inputs == 1 else "No files"

        output_desc = "N/A"
        needs_output = subcommand in ["to-cel", "to-banner", "to-imag", "to-lrform", "to-nfs-shpm", "to-bmp", "to-png", "to-jpg"]

        if needs_output:
             if num_inputs > 1:
                 output_desc = "Default (Input Directory for each file)"
             elif self.output_file_path:
                 if self.output_path_is_dir:
                     output_desc = f"Directory: {os.path.basename(self.output_file_path)}"
                 else:
                     output_desc = f"File: {os.path.basename(self.output_file_path)}"
             else: # Single input, no output path set
                 output_desc = "Default (Input Directory)"

        # Construct message (consider showing command preview?)
        msg = f"Confirm Action:\n\n" \
              f"  Action:  {subcommand}\n" \
              f"  Input:   {input_desc}\n" \
              f"  Output:  {output_desc}\n\n" \
              f"Proceed?"
              # f"\nCommand Preview:\n  {' '.join(command_args[1:])}" # Optional command preview

        reply = QMessageBox.question(self, 'Confirm Action', msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                                     QMessageBox.StandardButton.Yes)
        return reply == QMessageBox.StandardButton.Yes


    def run_action_confirmed(self):
         """Builds command, confirms, then executes."""
         subcommand = self.combo_subcommand.currentText()
         command_args = self.build_command_list(subcommand)
         if command_args:
             # Only confirm actions that modify/create files
             needs_confirmation = subcommand not in ["info", "list-chunks", "dump-packed-instructions", "version"]
             if needs_confirmation:
                 if self._confirm_run_action(subcommand, command_args):
                     self.execute_command_in_thread(command_args, subcommand)
             else: # Run info/list actions directly without confirmation
                  self.execute_command_in_thread(command_args, subcommand)


    def run_action(self, subcommand):
        """Builds command and executes directly (used for quick actions)."""
        command_args = self.build_command_list(subcommand)
        if command_args: self.execute_command_in_thread(command_args, subcommand)


    def run_manual_command(self):
        """Handles running the manually entered command text."""
        manual_args_str = self.manual_cmd_input.text().strip()
        if not manual_args_str: QMessageBox.warning(self, "Input Missing", "Manual command field is empty."); return
        try: manual_args_list = shlex.split(manual_args_str)
        except ValueError as e: QMessageBox.critical(self, "Parsing Error", f"Error parsing manual command:\n{e}\nCheck quotes."); return
        if not manual_args_list: QMessageBox.warning(self, "Input Missing", "No valid arguments found."); return
        command_args = [THREE_IT_EXE_PATH] + manual_args_list
        subcommand_guess = manual_args_list[0]
        # Maybe add confirmation for manual command too? Optional.
        # if self._confirm_run_action(f"Manual: {subcommand_guess}", command_args):
        self.execute_command_in_thread(command_args, f"Manual: {subcommand_guess}")


    def build_command_list(self, subcommand):
        """Builds the list of arguments for subprocess based on GUI state."""
        needs_input = subcommand != "version"
        requires_single_input = subcommand in ["dump-packed-instructions", "dpi"]
        if needs_input and not self.input_file_paths: QMessageBox.warning(self, "Input Missing", f"'{subcommand}' requires input file(s)."); return None
        if requires_single_input and len(self.input_file_paths) != 1: QMessageBox.warning(self, "Input Error", f"'{subcommand}' requires exactly one input file."); return None

        # Output path check is implicit now (either set for single, or omitted for multi/default)

        command = [THREE_IT_EXE_PATH]; actual_subcommand = "dump-packed-instructions" if subcommand == "dpi" else subcommand
        command.append(actual_subcommand)
        opts = self.option_widgets
        needs_output = actual_subcommand in ["to-cel", "to-banner", "to-imag", "to-lrform", "to-nfs-shpm", "to-bmp", "to-png", "to-jpg"]
        num_inputs = len(self.input_file_paths)

        if actual_subcommand == "to-cel":
            is_bpp_default = (opts['cel_bpp'].currentText() == "16"); is_coded_set = opts['cel_coded'].isChecked()
            is_lrform_set = opts['cel_lrform'].isChecked(); is_packed_set = opts['cel_packed'].isChecked()
            is_rotation_default = (opts['cel_rotation'].currentText() == "0")
            is_find_smallest_set = (opts['cel_find_smallest'].currentText() != "None")
            is_gen_all_checked_manually = opts['cel_generate_all'].isChecked()
            conflicting_basic_option_set = (not is_bpp_default or is_coded_set or is_lrform_set or
                                            is_packed_set or not is_rotation_default)

            force_gen_all = False
            if (num_inputs > 1 and not conflicting_basic_option_set and
                    not is_find_smallest_set and not is_gen_all_checked_manually):
                 force_gen_all = True; command.append("--generate-all")
                 # No need to log here, confirmation dialog explains output

            if not force_gen_all and not is_gen_all_checked_manually:
                 if is_find_smallest_set: command.extend(["--find-smallest", opts['cel_find_smallest'].currentText()])
                 else:
                     command.extend(["--bpp", opts['cel_bpp'].currentText()])
                     if is_coded_set: command.append("--coded")
                     if is_lrform_set: command.append("--lrform")
                     if is_packed_set: command.append("--packed")
                     trans_color = opts['cel_transparent'].currentText().strip()
                     if trans_color and trans_color.lower() != "magenta": command.extend(["--transparent", trans_color])
                     if not is_rotation_default: command.extend(["--rotation", opts['cel_rotation'].currentText()])
            elif is_gen_all_checked_manually and not force_gen_all: command.append("--generate-all")

            if self.palette_file_path: command.extend(["--external-palette", self.palette_file_path])
            if opts['cel_no_write_plut'].isChecked(): command.append("--write-plut=false")
            ccb_group = self.cel_options_group.findChild(QGroupBox, "Advanced CCB/PRE0 Flags")
            if ccb_group and ccb_group.isChecked():
                 for key, widget in opts.items():
                     if key.startswith("cel_ccb_") or key.startswith("cel_pre0_"):
                         if isinstance(widget, QComboBox): value = widget.currentText();
                         if value != "default": command.extend([f"--{key.replace('cel_', '').replace('_', '-')}", value])
            if opts['cel_ignore_ext'].isChecked(): command.append("-i")

        elif actual_subcommand == "to-nfs-shpm":
            if opts['nfs_packed'].isChecked(): command.append("--packed")
            trans_color = opts['nfs_transparent'].currentText().strip()
            if trans_color and trans_color.lower() != "magenta": command.extend(["--transparent", trans_color])

        elif actual_subcommand in ["to-banner", "to-imag", "to-lrform", "to-bmp", "to-png", "to-jpg"]:
             if 'generic_ignore_ext' in opts and opts['generic_ignore_ext'].isChecked(): command.append("-i")

        # --- Add Output Path and Input Files ---
        if needs_output and self.output_file_path and num_inputs == 1:
            # Only add -o for single file input *if* a path was provided
            # (If prompt was accepted for single file, output_file_path is dir, but we *omit* -o)
            if not self.output_path_is_dir: # Add -o only if it's a specific file
                 command.extend(["-o", self.output_file_path])
            # If output_path_is_dir is True (meaning user selected dir or accepted prompt for dir),
            # we still *omit* -o for single file input to let 3it use defaults in that dir.

        # Always add input files last
        if needs_input: command.extend(self.input_file_paths)
        return command

    def execute_command_in_thread(self, command_args, subcommand_name=""):
        """Runs the 3it command list in a separate QThread."""
        if not os.path.exists(THREE_IT_EXE_PATH): QMessageBox.critical(self, "Error", f"3it not found: {THREE_IT_EXE_PATH}"); return
        if self.worker_thread and self.worker_thread.isRunning(): QMessageBox.warning(self, "Busy", "Operation in progress."); return

        self.set_running_state(True)
        log_cmd_str = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in command_args])
        self.log_message(f"--- Starting: {subcommand_name} ---", prefix="[INFO]")
        self.log_message(f"[CMD] {log_cmd_str}", prefix="")
        QApplication.processEvents()

        self.worker_thread = QThread(self); self.worker = SubprocessWorker(command_args)
        self.worker.moveToThread(self.worker_thread); self.last_run_subcommand = subcommand_name
        self.worker.finished.connect(self.handle_process_finished)
        self.worker.progress.connect(lambda msg: self.log_update_signal.emit(f"{msg}"))
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(lambda: self.set_running_state(False))
        self.worker_thread.start()

    def log_message(self, message, prefix="[LOG]"):
        """Appends a message to the log area safely."""
        full_message = f"{prefix} {message}" if prefix else message
        if QThread.currentThread() != self.thread(): self.log_update_signal.emit(full_message); return
        self.log_area.append(full_message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    @Slot(bool, str, str)
    def handle_process_finished(self, success, stdout_data, stderr_data):
        """Slot called in the main thread when the worker finishes."""
        self.log_message("--- stdout ---", prefix=""); self.log_message(stdout_data.strip() or "(empty)", prefix="")
        self.log_message("\n--- stderr ---", prefix=""); self.log_message(stderr_data.strip() or "(empty)", prefix="")
        self.log_message(f"--- Execution {'Complete' if success else 'Failed'} ---", prefix="[INFO]")

        if success:
            is_visual_conversion = self.last_run_subcommand in ["to-cel", "to-banner", "to-imag", "to-lrform", "to-bmp", "to-png", "to-jpg"]
            # Use current_output_dir which is set based on output path or input path (if defaulted)
            if is_visual_conversion and self.current_output_dir:
                 self._update_image_viewer() # Update viewer based on confirmed output dir
        else: QMessageBox.warning(self, "Execution Failed", f"Action '{self.last_run_subcommand}' failed.\nCheck log.")
        self.worker_thread = None; self.worker = None

    # --- Image Viewer Logic ---
    def _update_image_viewer(self):
        self.output_images = []; self.current_image_index = -1
        for w in self.viewer_widgets[2:]: w.setEnabled(False)
        self.image_filename_label.setText(""); self.image_display_label.setText("Scanning..."); QApplication.processEvents()
        if not self.current_output_dir or not os.path.isdir(self.current_output_dir): self.image_display_label.setText("Output directory invalid."); self.image_filename_label.setText(""); return
        try:
            found_files = []
            for fname in os.listdir(self.current_output_dir):
                if any(fname.lower().endswith(ext) for ext in IMG_VIEWER_EXTENSIONS):
                    full_path = os.path.join(self.current_output_dir, fname)
                    if os.path.isfile(full_path): found_files.append(full_path)
            if found_files: found_files.sort(); self.output_images = found_files
            if self.output_images:
                self.current_image_index = 0; self._load_current_image()
                btn_prev, btn_next, btn_open = self.viewer_widgets[2], self.viewer_widgets[3], self.viewer_widgets[4]
                if btn_prev: btn_prev.setEnabled(self.current_image_index > 0)
                if btn_next: btn_next.setEnabled(self.current_image_index < len(self.output_images) - 1)
                if btn_open: btn_open.setEnabled(True)
            else:
                 self.image_display_label.setText("No compatible images found."); self.image_index_label.setText("0 / 0"); self.image_filename_label.setText("")
                 btn_open = self.viewer_widgets[4];
                 if btn_open: btn_open.setEnabled(True) # Keep open folder enabled
        except OSError as e: self.image_display_label.setText(f"Scan Error:\n{e}"); self.image_index_label.setText("0 / 0"); self.image_filename_label.setText("")
        except Exception as e: self.image_display_label.setText(f"Scan Error:\n{e}"); self.image_index_label.setText("0 / 0"); self.image_filename_label.setText(""); self.log_message(f"[ERROR] Viewer scan failed:\n{traceback.format_exc()}", prefix="")

    def _load_current_image(self):
        if not self.output_images or not (0 <= self.current_image_index < len(self.output_images)): self._clear_image_viewer(); return
        filepath = self.output_images[self.current_image_index]; basename = os.path.basename(filepath)
        pixmap = QPixmap(filepath)
        if pixmap.isNull(): self.image_display_label.setText(f"Cannot preview:\n{basename}"); self.image_display_label.setPixmap(QPixmap()); self.image_filename_label.setText(f"(Unsupported: {basename})")
        else: scaled_pixmap = pixmap.scaled(self.image_display_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation); self.image_display_label.setPixmap(scaled_pixmap); self.image_filename_label.setText(basename); self.image_filename_label.setToolTip(filepath)
        total = len(self.output_images); self.image_index_label.setText(f"{self.current_image_index + 1} / {total}")
        btn_prev, btn_next = self.viewer_widgets[2], self.viewer_widgets[3]
        if btn_prev: btn_prev.setEnabled(self.current_image_index > 0)
        if btn_next: btn_next.setEnabled(self.current_image_index < total - 1)

    def show_prev_image(self):
        if self.current_image_index > 0: self.current_image_index -= 1; self._load_current_image()
    def show_next_image(self):
        if self.current_image_index < len(self.output_images) - 1: self.current_image_index += 1; self._load_current_image()
    def open_output_folder(self, show_warning=True):
        dir_to_open = self.current_output_dir
        # Fallback needed if output path was a file for single input, use its dir
        if not dir_to_open and self.output_file_path and not self.output_path_is_dir: dir_to_open = os.path.dirname(self.output_file_path)
        if dir_to_open and os.path.isdir(dir_to_open):
            try: QDesktopServices.openUrl(QUrl.fromLocalFile(dir_to_open))
            except Exception as e:
                 if show_warning: QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")
        elif show_warning: QMessageBox.warning(self, "Not Found", "Output folder not set or invalid.")

    def _clear_image_viewer(self):
        self.image_display_label.setText("No preview"); self.image_display_label.setPixmap(QPixmap())
        self.image_index_label.setText("0 / 0"); self.image_filename_label.setText("")
        self.output_images = []; self.current_image_index = -1
        self.viewer_widgets[2].setEnabled(False); self.viewer_widgets[3].setEnabled(False) # Disable prev/next
        self.viewer_widgets[4].setEnabled(bool(self.current_output_dir and os.path.isdir(self.current_output_dir))) # Enable open based on dir

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.output_images and 0 <= self.current_image_index < len(self.output_images):
             current_pixmap = self.image_display_label.pixmap()
             if current_pixmap and not current_pixmap.isNull(): self._load_current_image()

    # --- Log Handling ---
    def clear_log(self): self.log_area.clear()

    # --- Help and About Windows ---
    def show_help_window(self):
        if self.help_window is None or not self.help_window.isVisible(): self.help_window = HelpWindow(self)
        self.help_window.show(); self.help_window.raise_(); self.help_window.activateWindow()

    def show_about_window(self):
        """Shows the About dialog box with updated credits and links."""
        about_text = f"""
        <h3>{APP_TITLE}</h3>
        <p>A graphical user interface for the <b>3it</b> command-line tool.</p>
        <hr>
        <p><b><u>3it Tool Credits:</u></b><br>
           Developed by: <b>Trapexit</b><br>
           Source Code: <a href='https://github.com/trapexit/3it'>github.com/trapexit/3it</a></p>
        <p><b><u>3DO Development Resources:</u></b><br>
           Website: <a href='https://3dodev.com'>3dodev.com</a><br>
           Docs: <a href='https://3dodev.com/documentation/file_formats'>File Formats</a> |
           <a href='https://3dodev.com/documentation/development/opera/pf25/ppgfldr/ggsfldr/gpgfldr/3gpg'>Graphics Guide</a> |
           <a href='https://3dodev.com/documentation/development/opera/pf25/ppgfldr/ggsfldr/gpgfldr/5gpg'>CEL Format</a> |
           <a href='https://3dodev.com/documentation/development/opera/pf25/ppgfldr/ggsfldr/gpgfldr/5gpgh'>More CEL</a> |
           <a href='https://3dodev.com/documentation/development/opera/pf25/ppgfldr/ggsfldr/gpgfldr/00gpg1'>Image Formats</a></p>
        <hr>
        <p><b><u>GUI Wrapper Credits:</u></b><br>
           Developed by: <b>Hakcinside</b><br>
           Source Code: <a href='https://github.com/Hackinside/3DO-Image-Tool-GUI-Wrapper'>github.com/Hackinside/3DO-Image-Tool-GUI-Wrapper</a></p>
        <p><i>GUI Version: {GUI_VERSION}</i></p>
        """
        msgBox = QMessageBox(self); msgBox.setWindowTitle(f"About {APP_TITLE}")
        msgBox.setTextFormat(Qt.RichText); msgBox.setTextInteractionFlags(Qt.TextBrowserInteraction | Qt.LinksAccessibleByMouse)
        msgBox.setText(about_text); msgBox.setIcon(QMessageBox.Information); msgBox.setStandardButtons(QMessageBox.Ok); msgBox.exec()

    # --- Theme Switching ---
    def change_theme(self, theme_name):
        app = QApplication.instance()
        if theme_name == "Dark": app.setStyleSheet(DARK_STYLE)
        elif theme_name == "Light": app.setStyleSheet(LIGHT_STYLE)
        else: app.setStyleSheet("") # Clear custom stylesheet

    # --- Window Close ---
    def closeEvent(self, event):
        if self.help_window and self.help_window.isVisible(): self.help_window.close()
        if self.worker_thread and self.worker_thread.isRunning():
            self.log_message("Stopping worker thread on close...", "[WARN]")
            self.worker_thread.quit()
            if not self.worker_thread.wait(1000): self.log_message("Worker thread timed out.", "[WARN]"); self.worker_thread.terminate(); self.worker_thread.wait()
            self.log_message("Worker thread stopped.", "[INFO]")
        super().closeEvent(event)

# --- Application Entry Point ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ThreeItMainWindow()
    mainWindow.show()
    sys.exit(app.exec())
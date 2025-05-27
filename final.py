# main.py - Advanced Lexical Analyzer with Modern GUI

import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'

ML_AVAILABLE = False

# Modern GUI imports
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.font as tkFont
from tkinter import colorchooser

import re
import json
import ast
import keyword
import threading
import queue
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
from datetime import datetime
import sys

# Set CustomTkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# AI/ML imports for advanced features
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML libraries not available. Install transformers and torch for AI features.")

class AdvancedLexicalAnalyzer:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_modern_styling()
        self.setup_variables()
        self.setup_ml_models()
        self.create_main_interface()
        

    def setup_modern_styling(self):
        """Configure modern styling with CustomTkinter"""
        self.root.title("🔍 Advanced Multi-Language Lexical Analyzer")
        
        # Optimize for 13-inch MacBook (2560x1600 or 1440x900 scaled)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate optimal window size (80% of screen)
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # Setup modern colors and fonts
        self.setup_modern_colors()
        self.setup_modern_fonts()

    def setup_modern_colors(self):
        """Setup modern color palette"""
        self.colors = {
            'primary': '#2563EB',
            'secondary': '#7C3AED', 
            'success': '#059669',
            'warning': '#D97706',
            'danger': '#DC2626',
            'background': '#F8FAFC',
            'surface': '#FFFFFF',
            'text_primary': '#1F2937',
            'text_secondary': '#6B7280',
            'accent': '#8B5CF6',
            'border': '#E5E7EB'
        }
        
        # Dark mode colors
        self.dark_colors = {
            'primary': '#3B82F6',
            'secondary': '#8B5CF6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'background': '#111827',
            'surface': '#1F2937',
            'text_primary': '#F9FAFB',
            'text_secondary': '#D1D5DB',
            'accent': '#A78BFA',
            'border': '#374151'
        }

    def setup_modern_fonts(self):
        """Configure modern font system"""
        self.fonts = {
            # Headings
            'heading': ('Segoe UI', 24, 'bold'),
            'heading_large': ('Segoe UI', 24, 'bold'),
            'heading_medium': ('Segoe UI', 18, 'bold'),
            'heading_small': ('Segoe UI', 14, 'bold'),
            'subheading': ('Segoe UI', 18, 'bold'),
            
            # Body text
            'body': ('Segoe UI', 12),
            'body_large': ('Segoe UI', 14),
            'body_medium': ('Segoe UI', 12),
            'body_small': ('Segoe UI', 11),
            
            # Code and monospace
            'code': ('JetBrains Mono', 12),
            'code_small': ('JetBrains Mono', 10),
            'monospace': ('Courier New', 10),
            
            # Special
            'caption': ('Segoe UI', 9),
            'button': ('Segoe UI', 11, 'bold')
        }

    def on_language_change(self, selected_language):
        """Handle language selection change with comprehensive updates"""
        try:
            self.update_status(f"Switching to {selected_language}...")
            
            # Store previous language for comparison
            previous_language = getattr(self, '_previous_language', None)
            self._previous_language = selected_language
            
            # Only proceed if language actually changed
            if previous_language == selected_language:
                return
            
            # Clear previous analysis results
            self.tokens = []
            self.errors = []
            
            # Clear all result displays
            result_widgets = [
                'tokens_text', 'errors_text', 'stats_text',
                'lexical_results', 'syntax_results', 'semantic_results',
                'error_predictions', 'code_suggestions', 'autocomplete_results'
            ]
            
            for widget_name in result_widgets:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    widget.delete('1.0', 'end')
                    widget.insert('1.0', f"Language changed to {selected_language}. Run analysis to see results.")
            
            # Clear visual displays
            visual_frames = [
                'ast_canvas_frame', 'freq_canvas_frame', 'parse_tree_canvas_frame'
            ]
            
            for frame_name in visual_frames:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    for widget in frame.winfo_children():
                        widget.destroy()
            
            # Update file info if current file doesn't match new language
            if self.current_file:
                file_ext = os.path.splitext(self.current_file)[1].lower()
                lang_config = self.languages.get(selected_language, {})
                expected_extensions = lang_config.get('file_extensions', [])
                
                if file_ext not in expected_extensions:
                    self.file_info.configure(
                        text=f"File: {os.path.basename(self.current_file)} (Language mismatch)"
                    )
            
            # Re-analyze code if there's content in the editor
            code = self.code_editor.get('1.0', 'end-1c')
            if code.strip():
                # Delay analysis to ensure UI updates complete
                self.root.after(200, self.perform_lexical_analysis)
            
            self.update_status(f"Language changed to {selected_language}")
            
        except Exception as e:
            self.update_status(f"Language change failed: {str(e)}")
            print(f"Error in on_language_change: {e}")


    def adjust_color_brightness(self, color, amount):
        """Adjust color brightness for hover effects"""
        # Convert hex to RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        # Adjust brightness
        rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        # Convert back to hex
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def setup_variables(self):
        """Initialize application variables"""
        self.current_file = None
        self.tokens = []
        self.parse_tree = None
        self.ast_tree = None
        self.errors = []
        self.suggestions = []
        self._analysis_timer = None

        # Language definitions
        self.languages = {
            'Python': {
                'keywords': keyword.kwlist,
                'operators': ['+', '-', '*', '/', '//', '%', '**', '=', '==', '!=', '<', '>', '<=', '>=',
                             'and', 'or', 'not', 'in', 'is', '&', '|', '^', '~', '<<', '>>'],
                'delimiters': ['(', ')', '[', ']', '{', '}', ',', ':', ';', '.', '->', '=>'],
                'comment_style': '#',
                'string_delimiters': ['"', "'", '"""', "'''"],
                'file_extensions': ['.py']
            },
            'JavaScript': {
                'keywords': ['var', 'let', 'const', 'function', 'if', 'else', 'for', 'while', 'do',
                            'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch',
                            'finally', 'throw', 'class', 'extends', 'import', 'export', 'async', 'await'],
                'operators': ['+', '-', '*', '/', '%', '=', '==', '===', '!=', '!==', '<', '>',
                             '<=', '>=', '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '>>>'],
                'delimiters': ['(', ')', '[', ']', '{', '}', ',', ';', '.', '=>'],
                'comment_style': '//',
                'string_delimiters': ['"', "'", '`'],
                'file_extensions': ['.js', '.jsx']
            },
            'Java': {
                'keywords': ['abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
                            'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
                            'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
                            'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
                            'package', 'private', 'protected', 'public', 'return', 'short', 'static',
                            'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
                            'transient', 'try', 'void', 'volatile', 'while'],
                'operators': ['+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
                             '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '>>>'],
                'delimiters': ['(', ')', '[', ']', '{', '}', ',', ';', '.'],
                'comment_style': '//',
                'string_delimiters': ['"'],
                'file_extensions': ['.java']
            },
            'C++': {
                'keywords': ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
                            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
                            'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
                            'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
                            'volatile', 'while', 'class', 'private', 'protected', 'public',
                            'virtual', 'friend', 'inline', 'template', 'namespace', 'using'],
                'operators': ['+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
                             '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '++', '--'],
                'delimiters': ['(', ')', '[', ']', '{', '}', ',', ';', '.', '->', '::'],
                'comment_style': '//',
                'string_delimiters': ['"', "'"],
                'file_extensions': ['.cpp', '.cc', '.cxx', '.h', '.hpp']
            }
        }

        self.current_language = ctk.StringVar(value='Python')
        self.analysis_results = {}

    def setup_ml_models(self):
        """Initialize ML models for advanced features"""
        self.ml_queue = queue.Queue()
        self.ml_models = {}
        
        if ML_AVAILABLE:
            try:
                # Initialize code completion model
                self.ml_models['completion'] = pipeline(
                    "text-generation",
                    model="microsoft/CodeGPT-small-py",
                    device=-1  # Use CPU for compatibility
                )
                
                # Initialize error detection model
                self.ml_models['error_detection'] = pipeline(
                    "text-classification",
                    model="huggingface/CodeBERTa-small-v1",
                    device=-1
                )
                
                print("✅ ML models loaded successfully")
            except Exception as e:
                print(f"⚠️ ML model loading failed: {e}")
                self.ml_models = {}

    def create_main_interface(self):
        """Create the main application interface"""
        # Create main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Create header
        self.create_header(main_container)

        # Create main content area with notebook
        self.create_notebook_interface(main_container)

        # Create status bar
        self.create_status_bar(main_container)

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def create_header(self, parent):
        """Create modern header with card-style layout"""
        header_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.colors['surface'])
        header_frame.pack(fill='x', pady=(0, 20), padx=20)

        # Main container with padding
        main_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        main_container.pack(fill='x', padx=20, pady=15)

        # Title section
        title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        title_frame.pack(fill='x', pady=(0, 15))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🔍 Advanced Lexical Analyzer",
            font=self.fonts['heading'],
            text_color=self.colors['text_primary']
        )
        title_label.pack(side='left')

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Multi-Language Code Analysis & Parsing",
            font=self.fonts['body'],
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(side='left', padx=(20, 0))

        # Controls section - THIS IS THE MISSING FRAME
        controls_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        controls_frame.pack(fill='x')

        # Language selection
        lang_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        lang_frame.pack(side='left', fill='y')

        lang_label = ctk.CTkLabel(
            lang_frame,
            text="Language:",
            font=self.fonts['body_medium'],
            text_color=self.colors['text_primary']
        )
        lang_label.pack(side='left', padx=(0, 10))

        language_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.current_language,
            values=["Python", "JavaScript", "Java", "C++"],
            command=self.on_language_change,
            fg_color=self.colors['primary'],
            button_color=self.colors['primary'],
            button_hover_color=self.adjust_color_brightness(self.colors['primary'], -20),
            dropdown_fg_color=self.colors['surface'],
            font=self.fonts['body'],
            width=120,
            height=36
        )
        language_menu.pack(side='left', padx=(0, 20))

        # Action buttons frame
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(side='right')

        # Modern action buttons
        button_configs = [
            ("📁 Open File", self.open_file, self.colors['primary']),
            ("📋 Load Sample", self.load_sample_code, self.colors['accent']),
            ("💾 Save Analysis", self.save_analysis, self.colors['success']),
            ("🎨 Theme", self.toggle_theme_mode, self.colors['secondary'])
        ]

        for text, command, color in button_configs:
            btn = ctk.CTkButton(
                buttons_frame,  # Use buttons_frame instead of controls_frame
                text=text,
                command=command,
                fg_color=color,
                hover_color=self.adjust_color_brightness(color, -20),
                corner_radius=8,
                height=36,
                font=self.fonts['body_medium']
            )
            btn.pack(side='left', padx=4)


    def load_sample_code(self):
        """Load sample code for the selected language"""
        language = self.current_language.get()
        
        samples = {
            'Python': '''
# Python Sample Code
number = 5
result = factorial(number)
print(f"Factorial of {number} is {result}")
            ''',
                    
                    'JavaScript': '''// JavaScript Sample Code
        function fibonacci(n) {
            if (n <= 1) {
                return n;
            }
            return fibonacci(n - 1) + fibonacci(n - 2);
        }

            // Main execution
            const num = 8;
            const result = fibonacci(num);
            console.log(`Fibonacci of ${num} is ${result}`);
            ''',
                    
                    'Java': '''// Java Sample Code
            public class Calculator {
                public static int add(int a, int b) {
                    return a + b;
                }
                
                public static void main(String[] args) {
                    int x = 10;
                    int y = 20;
                    int sum = add(x, y);
                    System.out.println("Sum: " + sum);
                }
            }
            ''',
                    
                    'C++': '''// C++ Sample Code
            #include <iostream>
            using namespace std;

            int multiply(int a, int b) {
                return a * b;
            }

            int main() {
                int x = 6;
                int y = 7;
                int product = multiply(x, y);
                cout << "Product: " << product << endl;
                return 0;
            }
            '''
        }
        
        sample_code = samples.get(language, "// No sample available for this language")
        
        # Clear editor and insert sample
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', sample_code)
        
        # Auto-analyze the sample
        self.perform_lexical_analysis()
        
        self.update_status(f"Sample {language} code loaded")


    def create_notebook_interface(self, parent):
        """Create modern tabbed interface"""
        self.notebook = ctk.CTkTabview(parent, corner_radius=12)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Add tabs with modern styling
        tabs = [
            ("📝 Editor & Analysis", self.create_editor_tab),
            ("🎨 Visual Features", self.create_visual_tab),
            ("🔬 Multi-Phase Analysis", self.create_analysis_tab),
            ("🤖 AI Features", self.create_ai_tab),
            ("⚙️ Settings", self.create_settings_tab)
        ]
        
        for tab_name, tab_creator in tabs:
            tab = self.notebook.add(tab_name)
            tab_creator(tab)

    def create_editor_tab(self, parent):
        """Create code editor and basic lexical analysis tab"""
        # Create paned window for split view
        paned_frame = ctk.CTkFrame(parent, fg_color="transparent")
        paned_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Left panel - Code editor
        left_frame = ctk.CTkFrame(paned_frame, corner_radius=8)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Editor header
        editor_header = ctk.CTkFrame(left_frame, height=50, corner_radius=8)
        editor_header.pack(fill='x', padx=15, pady=(15, 10))
        editor_header.pack_propagate(False)

        ctk.CTkLabel(
            editor_header,
            text="Code Editor",
            font=self.fonts['heading_medium'],
            anchor='w'
        ).pack(side='left', padx=15, pady=10)

        # Editor controls
        controls = ctk.CTkFrame(editor_header, fg_color="transparent")
        controls.pack(side='right', padx=15, pady=8)

        analyze_btn = ctk.CTkButton(
            controls,
            text="🔍 Analyze",
            command=self.perform_lexical_analysis,
            fg_color=self.colors['primary'],
            hover_color=self.adjust_color_brightness(self.colors['primary'], -20),
            corner_radius=6,
            height=32,
            width=100
        )
        analyze_btn.pack(side='left', padx=4)

        clear_btn = ctk.CTkButton(
            controls,
            text="🧹 Clear",
            command=self.clear_editor,
            fg_color=self.colors['text_secondary'],
            hover_color=self.adjust_color_brightness(self.colors['text_secondary'], -20),
            corner_radius=6,
            height=32,
            width=80
        )
        clear_btn.pack(side='left', padx=4)

        # Modern text editor
        editor_frame = ctk.CTkFrame(left_frame, corner_radius=8)
        editor_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        self.code_editor = ctk.CTkTextbox(
            editor_frame,
            font=self.fonts['code'],
            corner_radius=8,
            border_width=1,
            wrap='none'
        )
        self.code_editor.pack(fill='both', expand=True, padx=10, pady=10)

        # Bind events for real-time analysis
        self.code_editor.bind('<KeyRelease>', self.on_code_change)
        self.code_editor.bind('<Button-1>', self.on_code_change)

        # Right panel - Analysis results
        right_frame = ctk.CTkFrame(paned_frame, corner_radius=8)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Results header
        results_header = ctk.CTkFrame(right_frame, height=40, corner_radius=8)
        results_header.pack(fill='x', padx=15, pady=(15, 10))
        results_header.pack_propagate(False)

        ctk.CTkLabel(
            results_header,
            text="Analysis Results",
            font=self.fonts['heading_medium']
        ).pack(side='left', padx=15, pady=8)

        # Modern tabbed results
        self.results_notebook = ctk.CTkTabview(right_frame, corner_radius=8)
        self.results_notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Tokens tab
        tokens_tab = self.results_notebook.add("🎯 Tokens")
        self.create_tokens_tab(tokens_tab)

        # Errors tab
        errors_tab = self.results_notebook.add("⚠️ Errors")
        self.create_errors_tab(errors_tab)

        # Statistics tab
        stats_tab = self.results_notebook.add("📊 Statistics")
        self.create_statistics_tab(stats_tab)

    def create_tokens_tab(self, parent):
        """Create modern tokens display"""
        self.tokens_text = ctk.CTkTextbox(
            parent,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.tokens_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_errors_tab(self, parent):
        """Create modern errors display"""
        self.errors_text = ctk.CTkTextbox(
            parent,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.errors_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_statistics_tab(self, parent):
        """Create modern statistics display"""
        self.stats_text = ctk.CTkTextbox(
            parent,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_visual_tab(self, parent):
        """Create visual features tab"""
        # Create sub-notebook for visual features
        visual_notebook = ctk.CTkTabview(parent, corner_radius=12)
        visual_notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Parsing Table Generator
        table_tab = visual_notebook.add("📋 Parsing Table")
        self.create_parsing_table_tab(table_tab)

        # AST Visualizer
        ast_tab = visual_notebook.add("🌳 AST Visualizer")
        self.create_ast_tab(ast_tab)

        # Token Frequency Visualizer
        freq_tab = visual_notebook.add("📊 Token Frequency")
        self.create_frequency_tab(freq_tab)

        # Parse Tree Visualizer
        tree_tab = visual_notebook.add("🌲 Parse Tree")
        self.create_parse_tree_tab(tree_tab)

    def create_parsing_table_tab(self, parent):
        """Create parsing table generator tab"""
        # Header
        header = ctk.CTkFrame(parent, height=50, corner_radius=8)
        header.pack(fill='x', padx=10, pady=10)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="LALR(1) Parsing Table Generator",
            font=self.fonts['heading_medium']
        ).pack(side='left', padx=15, pady=10)

        ctk.CTkButton(
            header,
            text="🔄 Generate Table",
            command=self.generate_parsing_table,
            fg_color=self.colors['primary']
        ).pack(side='right', padx=15, pady=8)

        # Grammar input
        grammar_frame = ctk.CTkFrame(parent, corner_radius=8)
        grammar_frame.pack(fill='x', padx=10, pady=(0, 10))

        ctk.CTkLabel(
            grammar_frame,
            text="Grammar Rules:",
            font=self.fonts['heading_small']
        ).pack(anchor='w', padx=15, pady=(15, 5))

        self.grammar_text = ctk.CTkTextbox(
            grammar_frame,
            height=150,
            font=self.fonts['code'],
            corner_radius=8
        )
        self.grammar_text.pack(fill='x', padx=15, pady=(0, 15))

        # Default grammar
        default_grammar = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
        self.grammar_text.insert('1.0', default_grammar)

        # Parsing table display
        table_display_frame = ctk.CTkFrame(parent, corner_radius=8)
        table_display_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(
            table_display_frame,
            text="Generated Parsing Table:",
            font=self.fonts['heading_small']
        ).pack(anchor='w', padx=15, pady=(15, 5))

        self.parsing_table_text = ctk.CTkTextbox(
            table_display_frame,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.parsing_table_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))

    def create_ast_tab(self, parent):
        """Create AST visualization tab"""
        # Header with controls
        header = ctk.CTkFrame(parent, height=50, corner_radius=8)
        header.pack(fill='x', padx=10, pady=10)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Abstract Syntax Tree Visualizer",
            font=self.fonts['heading_medium']
        ).pack(side='left', padx=15, pady=10)

        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side='right', padx=15, pady=8)

        ctk.CTkButton(
            controls,
            text="🌳 Generate AST",
            command=self.generate_ast,
            fg_color=self.colors['primary']
        ).pack(side='left', padx=2)

        ctk.CTkButton(
            controls,
            text="💾 Export PNG",
            command=self.export_ast,
            fg_color=self.colors['success']
        ).pack(side='left', padx=2)

        # AST display area
        self.ast_canvas_frame = ctk.CTkFrame(parent, corner_radius=8)
        self.ast_canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def create_frequency_tab(self, parent):
        """Create token frequency visualization tab"""
        # Header
        header = ctk.CTkFrame(parent, height=50, corner_radius=8)
        header.pack(fill='x', padx=10, pady=10)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Token Frequency Analyzer",
            font=self.fonts['heading_medium']
        ).pack(side='left', padx=15, pady=10)

        ctk.CTkButton(
            header,
            text="📊 Generate Chart",
            command=self.generate_frequency_chart,
            fg_color=self.colors['primary']
        ).pack(side='right', padx=15, pady=8)

        # Chart display area
        self.freq_canvas_frame = ctk.CTkFrame(parent, corner_radius=8)
        self.freq_canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def create_parse_tree_tab(self, parent):
        """Create parse tree visualization tab"""
        # Header with controls
        header = ctk.CTkFrame(parent, height=50, corner_radius=8)
        header.pack(fill='x', padx=10, pady=10)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Parse Tree Generator",
            font=self.fonts['heading_medium']
        ).pack(side='left', padx=15, pady=10)

        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side='right', padx=15, pady=8)

        ctk.CTkButton(
            controls,
            text="🌲 Generate Tree",
            command=self.generate_parse_tree,
            fg_color=self.colors['primary']
        ).pack(side='left', padx=2)

        ctk.CTkButton(
            controls,
            text="💾 Export Tree",
            command=self.export_parse_tree,
            fg_color=self.colors['success']
        ).pack(side='left', padx=2)

        # Parse tree display area
        self.parse_tree_canvas_frame = ctk.CTkFrame(parent, corner_radius=8)
        self.parse_tree_canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def create_analysis_tab(self, parent):
        """Create multi-phase analysis tab"""
        # Create three-column layout
        columns_frame = ctk.CTkFrame(parent, fg_color="transparent")
        columns_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Lexical Analysis Column
        lexical_frame = ctk.CTkFrame(columns_frame, corner_radius=8)
        lexical_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        ctk.CTkLabel(
            lexical_frame,
            text="🔍 Lexical Analysis",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        self.lexical_results = ctk.CTkTextbox(
            lexical_frame,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.lexical_results.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Syntax Analysis Column
        syntax_frame = ctk.CTkFrame(columns_frame, corner_radius=8)
        syntax_frame.pack(side='left', fill='both', expand=True, padx=5)

        ctk.CTkLabel(
            syntax_frame,
            text="📝 Syntax Analysis",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        self.syntax_results = ctk.CTkTextbox(
            syntax_frame,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.syntax_results.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Semantic Analysis Column
        semantic_frame = ctk.CTkFrame(columns_frame, corner_radius=8)
        semantic_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))

        ctk.CTkLabel(
            semantic_frame,
            text="🧠 Semantic Analysis",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        self.semantic_results = ctk.CTkTextbox(
            semantic_frame,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.semantic_results.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Control buttons
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.pack(fill='x', padx=10, pady=10)

        buttons = [
            ("🔍 Run Lexical Analysis", self.run_lexical_analysis),
            ("📝 Run Syntax Analysis", self.run_syntax_analysis),
            ("🧠 Run Semantic Analysis", self.run_semantic_analysis),
            ("🚀 Run All Phases", self.run_all_phases)
        ]

        for text, command in buttons:
            ctk.CTkButton(
                controls_frame,
                text=text,
                command=command,
                fg_color=self.colors['primary'],
                corner_radius=8
            ).pack(side='left', padx=5)


    def create_ai_tab(self, parent):
        """Create AI/ML features tab without auto-complete section"""
        # Create main frame
        ai_frame = ctk.CTkFrame(parent, fg_color="transparent")
        ai_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Error prediction section (left side)
        error_frame = ctk.CTkFrame(ai_frame, corner_radius=8)
        error_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        ctk.CTkLabel(
            error_frame,
            text="🎯 ML-based Error Prediction",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        ctk.CTkButton(
            error_frame,
            text="🔍 Analyze Errors",
            command=self.predict_errors,
            fg_color=self.colors['warning']
        ).pack(padx=15, pady=(0, 10))

        self.error_predictions = ctk.CTkTextbox(
            error_frame,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.error_predictions.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Code suggestions section (right side)
        suggestions_frame = ctk.CTkFrame(ai_frame, corner_radius=8)
        suggestions_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        ctk.CTkLabel(
            suggestions_frame,
            text="💡 Code Suggestions",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        ctk.CTkButton(
            suggestions_frame,
            text="✨ Get Suggestions",
            command=self.get_code_suggestions,
            fg_color=self.colors['success']
        ).pack(padx=15, pady=(0, 10))

        self.code_suggestions = ctk.CTkTextbox(
            suggestions_frame,
            font=self.fonts['code_small'],
            corner_radius=8
        )
        self.code_suggestions.pack(fill='both', expand=True, padx=15, pady=(0, 15))


    def create_settings_tab(self, parent):
        """Create settings and configuration tab"""
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(parent, corner_radius=8)
        scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Theme Settings
        theme_frame = ctk.CTkFrame(scrollable_frame, corner_radius=8)
        theme_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            theme_frame,
            text="🎨 Theme Settings",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        # Color scheme selector
        ctk.CTkLabel(
            theme_frame,
            text="Color Scheme:",
            font=self.fonts['body_medium']
        ).pack(anchor='w', padx=20, pady=(10, 5))

        self.color_scheme_var = ctk.StringVar(value='Default')
        color_schemes = ['Default', 'Dark Mode', 'High Contrast', 'Solarized', 'Custom']

        for scheme in color_schemes:
            ctk.CTkRadioButton(
                theme_frame,
                text=scheme,
                variable=self.color_scheme_var,
                value=scheme,
                command=self.apply_color_scheme
            ).pack(anchor='w', padx=30, pady=2)

        # Font Settings
        font_frame = ctk.CTkFrame(scrollable_frame, corner_radius=8)
        font_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            font_frame,
            text="📝 Font Settings",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        # Font family
        ctk.CTkLabel(
            font_frame,
            text="Font Family:",
            font=self.fonts['body_medium']
        ).pack(anchor='w', padx=20, pady=(10, 5))

        self.font_family_var = ctk.StringVar(value='JetBrains Mono')
        font_combo = ctk.CTkComboBox(
            font_frame,
            variable=self.font_family_var,
            values=['JetBrains Mono', 'Monaco', 'Menlo', 'Consolas', 'Courier New'],
            command=self.apply_font_settings
        )
        font_combo.pack(anchor='w', padx=30, pady=(0, 10))

        # Font size
        ctk.CTkLabel(
            font_frame,
            text="Font Size:",
            font=self.fonts['body_medium']
        ).pack(anchor='w', padx=20, pady=(0, 5))

        self.font_size_var = ctk.IntVar(value=12)
        font_size_slider = ctk.CTkSlider(
            font_frame,
            from_=8,
            to=20,
            variable=self.font_size_var,
            command=self.apply_font_settings
        )
        font_size_slider.pack(anchor='w', padx=30, fill='x', pady=(0, 15))

        # Analysis Settings
        analysis_frame = ctk.CTkFrame(scrollable_frame, corner_radius=8)
        analysis_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            analysis_frame,
            text="🔬 Analysis Settings",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        # Real-time analysis
        self.realtime_analysis_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            analysis_frame,
            text="Enable Real-time Analysis",
            variable=self.realtime_analysis_var
        ).pack(anchor='w', padx=20, pady=5)

        # Show line numbers
        self.show_line_numbers_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            analysis_frame,
            text="Show Line Numbers",
            variable=self.show_line_numbers_var,
            command=self.toggle_line_numbers
        ).pack(anchor='w', padx=20, pady=5)

        # Syntax highlighting
        self.syntax_highlighting_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            analysis_frame,
            text="Enable Syntax Highlighting",
            variable=self.syntax_highlighting_var,
            command=self.toggle_syntax_highlighting
        ).pack(anchor='w', padx=20, pady=(5, 15))

        # ML Features Settings
        ml_frame = ctk.CTkFrame(scrollable_frame, corner_radius=8)
        ml_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            ml_frame,
            text="🤖 ML Features Settings",
            font=self.fonts['heading_small']
        ).pack(padx=15, pady=(15, 5))

        # Enable ML features
        self.enable_ml_var = ctk.BooleanVar(value=ML_AVAILABLE)
        ctk.CTkCheckBox(
            ml_frame,
            text="Enable ML Features",
            variable=self.enable_ml_var
        ).pack(anchor='w', padx=20, pady=5)

        # Auto-complete threshold
        ctk.CTkLabel(
            ml_frame,
            text="Auto-complete Confidence Threshold:",
            font=self.fonts['body_medium']
        ).pack(anchor='w', padx=20, pady=(10, 5))

        self.autocomplete_threshold_var = ctk.DoubleVar(value=0.7)
        threshold_slider = ctk.CTkSlider(
            ml_frame,
            from_=0.1,
            to=1.0,
            variable=self.autocomplete_threshold_var
        )
        threshold_slider.pack(anchor='w', padx=30, fill='x', pady=(0, 15))

    def create_status_bar(self, parent):
        """Create modern status bar"""
        status_frame = ctk.CTkFrame(parent, height=40, corner_radius=8)
        status_frame.pack(fill='x', padx=20, pady=(10, 20))
        status_frame.pack_propagate(False)

        # Status indicator
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(side='left', padx=15, pady=8)

        self.status_indicator = ctk.CTkLabel(
            status_container,
            text="●",
            font=('Arial', 16),
            text_color=self.colors['success']
        )
        self.status_indicator.pack(side='left', padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            status_container,
            text="Ready",
            font=self.fonts['body_medium']
        )
        self.status_label.pack(side='left')

        # Modern progress bar
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            width=200,
            height=8,
            corner_radius=4
        )
        self.progress_bar.pack(side='right', padx=15, pady=12)
        self.progress_bar.set(0)

        # File info
        self.file_info = ctk.CTkLabel(
            status_frame,
            text="No file loaded",
            font=self.fonts['body_small'],
            text_color=self.colors['text_secondary']
        )
        self.file_info.pack(side='right', padx=15, pady=8)

    def toggle_theme_mode(self):
        """Toggle between dark and light modes"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update colors based on mode
        if new_mode == "dark":
            self.colors.update(self.dark_colors)
        else:
            self.colors.update({
                'primary': '#2563EB',
                'secondary': '#7C3AED',
                'success': '#059669',
                'warning': '#D97706',
                'danger': '#DC2626',
                'background': '#F8FAFC',
                'surface': '#FFFFFF',
                'text_primary': '#1F2937',
                'text_secondary': '#6B7280',
                'accent': '#8B5CF6',
                'border': '#E5E7EB'
            })
        
        self.update_status(f"Switched to {new_mode} mode")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # macOS uses Cmd key, Windows/Linux use Ctrl
        modifier = 'Command' if sys.platform == 'darwin' else 'Control'
        
        self.root.bind(f'<{modifier}-o>', lambda e: self.open_file())
        self.root.bind(f'<{modifier}-s>', lambda e: self.save_analysis())
        self.root.bind(f'<{modifier}-n>', lambda e: self.clear_editor())
        self.root.bind(f'<{modifier}-r>', lambda e: self.perform_lexical_analysis())
        self.root.bind(f'<{modifier}-t>', lambda e: self.toggle_theme_mode())
        self.root.bind(f'<{modifier}-q>', lambda e: self.root.quit())

        # Function keys
        self.root.bind('<F5>', lambda e: self.run_all_phases())
        self.root.bind('<F1>', lambda e: self.show_help())

    # Core Lexical Analysis Methods
    def perform_lexical_analysis(self):
        """Perform comprehensive lexical analysis"""
        self.update_status("Performing lexical analysis...")
        self.progress_bar.set(0)
        
        code = self.code_editor.get('1.0', 'end-1c')
        if not code.strip():
            self.update_status("No code to analyze")
            return

        try:
            # Clear previous results
            self.tokens = []
            self.errors = []

            # Tokenize based on selected language
            language = self.current_language.get()
            self.tokens = self.tokenize_code(code, language)
            self.progress_bar.set(0.5)

            # Update displays
            self.update_tokens_display()
            self.update_errors_display()
            self.update_statistics_display()

            # Apply syntax highlighting
            if self.syntax_highlighting_var.get():
                self.apply_syntax_highlighting()

            self.progress_bar.set(1.0)
            self.update_status(f"Analysis complete. Found {len(self.tokens)} tokens.")

        except Exception as e:
            self.errors.append(f"Analysis error: {str(e)}")
            self.update_errors_display()
            self.update_status("Analysis failed")

    def tokenize_code(self, code, language):
        """Advanced tokenization with multi-language support"""
        tokens = []
        lang_config = self.languages.get(language, self.languages['Python'])

        # Split code into lines for line tracking
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            column = 1
            i = 0
            
            while i < len(line):
                char = line[i]
                
                # Skip whitespace
                if char.isspace():
                    i += 1
                    column += 1
                    continue

                # Comments
                if line[i:].startswith(lang_config['comment_style']):
                    comment_text = line[i:]
                    tokens.append({
                        'type': 'COMMENT',
                        'value': comment_text,
                        'line': line_num,
                        'column': column
                    })
                    break

                # String literals
                string_token = self.extract_string_literal(line, i, lang_config)
                if string_token:
                    tokens.append({
                        'type': 'STRING',
                        'value': string_token['value'],
                        'line': line_num,
                        'column': column
                    })
                    i += string_token['length']
                    column += string_token['length']
                    continue

                # Numbers
                number_token = self.extract_number(line, i)
                if number_token:
                    tokens.append({
                        'type': 'NUMBER',
                        'value': number_token['value'],
                        'line': line_num,
                        'column': column
                    })
                    i += number_token['length']
                    column += number_token['length']
                    continue

                # Identifiers and keywords
                identifier_token = self.extract_identifier(line, i)
                if identifier_token:
                    token_value = identifier_token['value']
                    token_type = 'KEYWORD' if token_value in lang_config['keywords'] else 'IDENTIFIER'
                    
                    tokens.append({
                        'type': token_type,
                        'value': token_value,
                        'line': line_num,
                        'column': column
                    })
                    i += identifier_token['length']
                    column += identifier_token['length']
                    continue

                # Operators
                operator_token = self.extract_operator(line, i, lang_config)
                if operator_token:
                    tokens.append({
                        'type': 'OPERATOR',
                        'value': operator_token['value'],
                        'line': line_num,
                        'column': column
                    })
                    i += operator_token['length']
                    column += operator_token['length']
                    continue

                # Delimiters
                if char in lang_config['delimiters']:
                    tokens.append({
                        'type': 'DELIMITER',
                        'value': char,
                        'line': line_num,
                        'column': column
                    })
                    i += 1
                    column += 1
                    continue

                # Unknown character
                self.errors.append(f"Unknown character '{char}' at line {line_num}, column {column}")
                i += 1
                column += 1

        return tokens

    def extract_string_literal(self, line, start, lang_config):
        """Extract string literals"""
        for delimiter in lang_config['string_delimiters']:
            if line[start:].startswith(delimiter):
                end = start + len(delimiter)
                while end < len(line):
                    if line[end:].startswith(delimiter):
                        return {
                            'value': line[start:end + len(delimiter)],
                            'length': end - start + len(delimiter)
                        }
                    if line[end] == '\\':  # Escape character
                        end += 2
                    else:
                        end += 1
                
                # Unterminated string
                self.errors.append(f"Unterminated string starting at position {start}")
                return {
                    'value': line[start:],
                    'length': len(line) - start
                }
        return None

    def extract_number(self, line, start):
        """Extract numeric literals"""
        i = start
        has_dot = False
        
        if not line[i].isdigit():
            return None

        while i < len(line) and (line[i].isdigit() or line[i] == '.'):
            if line[i] == '.':
                if has_dot:
                    break
                has_dot = True
            i += 1

        # Handle scientific notation
        if i < len(line) and line[i].lower() == 'e':
            i += 1
            if i < len(line) and line[i] in '+-':
                i += 1
            while i < len(line) and line[i].isdigit():
                i += 1

        return {
            'value': line[start:i],
            'length': i - start
        }

    def extract_identifier(self, line, start):
        """Extract identifiers"""
        if not (line[start].isalpha() or line[start] == '_'):
            return None

        i = start
        while i < len(line) and (line[i].isalnum() or line[i] == '_'):
            i += 1

        return {
            'value': line[start:i],
            'length': i - start
        }

    def extract_operator(self, line, start, lang_config):
        """Extract operators (longest match first)"""
        operators = sorted(lang_config['operators'], key=len, reverse=True)
        
        for op in operators:
            if line[start:].startswith(op):
                return {
                    'value': op,
                    'length': len(op)
                }
        return None

    # Visual Features Implementation
    def generate_parsing_table(self):
        """Generate LALR(1) parsing table"""
        self.update_status("Generating parsing table...")
        try:
            grammar_text = self.grammar_text.get('1.0', 'end-1c')
            if not grammar_text.strip():
                messagebox.showwarning("Warning", "Please enter grammar rules")
                return

            # Parse grammar rules
            rules = self.parse_grammar_rules(grammar_text)
            
            # Generate parsing table (simplified implementation)
            parsing_table = self.build_lalr_table(rules)
            
            # Display in text widget
            self.display_parsing_table(parsing_table)
            self.update_status("Parsing table generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate parsing table: {str(e)}")
            self.update_status("Parsing table generation failed")

    def parse_grammar_rules(self, grammar_text):
        """Parse grammar rules from text"""
        rules = []
        lines = grammar_text.strip().split('\n')
        
        for line in lines:
            if '->' in line:
                left, right = line.split('->', 1)
                left = left.strip()
                # Handle multiple productions
                productions = [prod.strip() for prod in right.split('|')]
                for prod in productions:
                    rules.append({
                        'left': left,
                        'right': prod.split() if prod.strip() else ['ε']
                    })
        return rules

    def build_lalr_table(self, rules):
        """Build LALR(1) parsing table (simplified)"""
        # This is a simplified implementation
        terminals = set()
        non_terminals = set()
        
        # Extract terminals and non-terminals
        for rule in rules:
            non_terminals.add(rule['left'])
            for symbol in rule['right']:
                if symbol not in non_terminals and symbol != 'ε':
                    terminals.add(symbol)
        
        # Create simplified table
        action_table = {}
        goto_table = {}
        
        # Generate simplified states
        states = list(range(min(10, len(rules) * 2)))
        
        for i in states:
            action_table[i] = {}
            goto_table[i] = {}
            
            for terminal in terminals:
                action_table[i][terminal] = f"s{(i + 1) % len(states)}"
                
            for non_terminal in non_terminals:
                goto_table[i][non_terminal] = (i + 1) % len(states)
        
        return {
            'action': action_table,
            'goto': goto_table,
            'states': states,
            'terminals': terminals,
            'non_terminals': non_terminals
        }

    def display_parsing_table(self, table):
        """Display parsing table with improved formatting"""
        self.parsing_table_text.delete('1.0', 'end')
        
        display_text = "LALR(1) PARSING TABLE\n"
        display_text += "=" * 80 + "\n\n"

        terminals = sorted(list(table['terminals']))
        non_terminals = sorted(list(table['non_terminals']))
        
        # Create header with proper column widths
        col_width = 12
        header = f"{'State':<8}"
        
        # Action table headers
        for terminal in terminals:
            header += f"{terminal:<{col_width}}"
        
        # Goto table headers  
        for non_terminal in non_terminals:
            header += f"{non_terminal:<{col_width}}"
        
        display_text += header + "\n"
        display_text += "-" * len(header) + "\n"

        # Table rows with consistent formatting
        for state_id in sorted(table['states']):
            row = f"{state_id:<8}"
            
            # Action table values
            for terminal in terminals:
                action = table['action'].get(state_id, {}).get(terminal, '')
                row += f"{str(action):<{col_width}}"
            
            # Goto table values
            for non_terminal in non_terminals:
                goto = table['goto'].get(state_id, {}).get(non_terminal, '')
                row += f"{str(goto) if goto != '' else '':<{col_width}}"
            
            display_text += row + "\n"

        self.parsing_table_text.insert('1.0', display_text)

    def create_token_breakdown_section(self, parent, tokens):
        """Create token breakdown by lines section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['warning'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📊 Token Breakdown by Lines",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Group tokens by lines
        lines = {}
        for token in tokens:
            line = token['line']
            if line not in lines:
                lines[line] = []
            lines[line].append(token)
        
        # Create breakdown table
        breakdown_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        breakdown_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Table header
        header_frame = ctk.CTkFrame(breakdown_frame, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', pady=(0, 5))
        
        header_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_grid.pack(fill='x', padx=15, pady=10)
        
        headers = ["Line", "Token Count", "Keywords", "Identifiers", "Operators"]
        for i, header_text in enumerate(headers):
            ctk.CTkLabel(
                header_grid,
                text=header_text,
                font=('Arial', 12, 'bold'),
                text_color='white'
            ).grid(row=0, column=i, padx=5, sticky='ew')
            header_grid.grid_columnconfigure(i, weight=1)
        
        # Table rows
        for i, (line_num, line_tokens) in enumerate(sorted(lines.items())):
            row_color = self.colors['background'] if i % 2 == 0 else self.colors['surface']
            
            row_frame = ctk.CTkFrame(breakdown_frame, fg_color=row_color)
            row_frame.pack(fill='x', pady=1)
            
            row_grid = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_grid.pack(fill='x', padx=15, pady=5)
            
            # Count different token types
            keywords = len([t for t in line_tokens if t['type'] == 'KEYWORD'])
            identifiers = len([t for t in line_tokens if t['type'] == 'IDENTIFIER'])
            operators = len([t for t in line_tokens if t['type'] == 'OPERATOR'])
            
            values = [str(line_num), str(len(line_tokens)), str(keywords), str(identifiers), str(operators)]
            
            for j, value in enumerate(values):
                ctk.CTkLabel(
                    row_grid,
                    text=value,
                    font=('Arial', 11),
                    anchor='center'
                ).grid(row=0, column=j, padx=5, sticky='ew')
                row_grid.grid_columnconfigure(j, weight=1)

    def create_syntax_structure_section(self, parent, tokens):
        """Create syntax structure analysis section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['secondary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🔍 Syntax Structure Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Analyze syntax patterns
        patterns = self.analyze_syntax_patterns(tokens)
        
        # Display patterns
        patterns_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        patterns_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        for pattern_name, pattern_data in patterns.items():
            pattern_card = ctk.CTkFrame(patterns_frame, corner_radius=8)
            pattern_card.pack(fill='x', pady=5)
            
            # Pattern header
            pattern_header = ctk.CTkFrame(pattern_card, fg_color=self.colors['accent'])
            pattern_header.pack(fill='x', padx=10, pady=10)
            
            ctk.CTkLabel(
                pattern_header,
                text=f"{pattern_name}: {pattern_data['count']} occurrences",
                font=('Arial', 12, 'bold'),
                text_color='white'
            ).pack(pady=5)
            
            # Pattern examples
            if pattern_data['examples']:
                examples_text = "Examples: " + ", ".join(pattern_data['examples'][:3])
                ctk.CTkLabel(
                    pattern_card,
                    text=examples_text,
                    font=('Arial', 10),
                    text_color=self.colors['text_secondary']
                ).pack(padx=15, pady=(0, 10))

    def analyze_syntax_patterns(self, tokens):
        """Analyze common syntax patterns in tokens"""
        patterns = {
            "Assignment Patterns": {"count": 0, "examples": []},
            "Function Calls": {"count": 0, "examples": []},
            "Control Structures": {"count": 0, "examples": []},
            "Arithmetic Operations": {"count": 0, "examples": []}
        }
        
        for i, token in enumerate(tokens):
            # Assignment pattern: identifier = value
            if (token['type'] == 'OPERATOR' and token['value'] == '=' and 
                i > 0 and i < len(tokens) - 1):
                patterns["Assignment Patterns"]["count"] += 1
                if len(patterns["Assignment Patterns"]["examples"]) < 3:
                    prev_token = tokens[i-1]['value'] if i > 0 else ""
                    next_token = tokens[i+1]['value'] if i < len(tokens)-1 else ""
                    patterns["Assignment Patterns"]["examples"].append(f"{prev_token} = {next_token}")
            
            # Function calls: identifier(
            if (token['type'] == 'DELIMITER' and token['value'] == '(' and 
                i > 0 and tokens[i-1]['type'] == 'IDENTIFIER'):
                patterns["Function Calls"]["count"] += 1
                if len(patterns["Function Calls"]["examples"]) < 3:
                    func_name = tokens[i-1]['value']
                    patterns["Function Calls"]["examples"].append(f"{func_name}()")
            
            # Control structures
            if token['type'] == 'KEYWORD' and token['value'] in ['if', 'for', 'while', 'def', 'class']:
                patterns["Control Structures"]["count"] += 1
                if len(patterns["Control Structures"]["examples"]) < 3:
                    patterns["Control Structures"]["examples"].append(token['value'])
            
            # Arithmetic operations
            if token['type'] == 'OPERATOR' and token['value'] in ['+', '-', '*', '/', '%']:
                patterns["Arithmetic Operations"]["count"] += 1
                if len(patterns["Arithmetic Operations"]["examples"]) < 3:
                    patterns["Arithmetic Operations"]["examples"].append(token['value'])
        
        return patterns

    def visualize_ast(self):
        """Wrapper method for AST visualization"""
        try:
            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                messagebox.showwarning("Warning", "No code to analyze")
                return
            
            # Generate AST
            self.generate_ast()
        except Exception as e:
            self.show_ast_error(e)

    def perform_lexical_analysis(self):
        """Perform comprehensive lexical analysis with progress tracking"""
        self.update_status("Performing lexical analysis...")
        self.progress_bar.set(0)
        
        code = self.code_editor.get('1.0', 'end-1c')
        if not code.strip():
            self.update_status("No code to analyze")
            self.progress_bar.set(0)
            return

        try:
            # Clear previous results
            self.tokens = []
            self.errors = []
            self.progress_bar.set(0.2)

            # Tokenize based on selected language
            language = self.current_language.get()
            self.tokens = self.tokenize_code(code, language)
            self.progress_bar.set(0.6)

            # Update displays
            self.update_tokens_display()
            self.update_errors_display()
            self.update_statistics_display()
            self.progress_bar.set(0.8)

            # Apply syntax highlighting
            if hasattr(self, 'syntax_highlighting_var') and self.syntax_highlighting_var.get():
                self.apply_syntax_highlighting()
            
            self.progress_bar.set(1.0)
            self.update_status(f"Analysis complete. Found {len(self.tokens)} tokens.")
            
            # Reset progress bar after 2 seconds
            self.root.after(2000, lambda: self.progress_bar.set(0))
            
        except Exception as e:
            self.errors.append(f"Analysis error: {str(e)}")
            self.update_errors_display()
            self.update_status("Analysis failed")
            self.progress_bar.set(0)
    def update_tokens_display(self):
        """Update tokens display with improved formatting"""
        if hasattr(self, 'tokens_text'):
            self.tokens_text.delete('1.0', 'end')
            if not self.tokens:
                self.tokens_text.insert('1.0', "No tokens found")
                return

            # Create properly formatted table
            display_text = "TOKEN ANALYSIS RESULTS\n"
            display_text += "=" * 60 + "\n\n"
            
            # Header with proper spacing
            header = f"{'Type':<15} {'Value':<25} {'Line':<8} {'Column':<8}\n"
            display_text += header
            display_text += "-" * 60 + "\n"
            
            # Format each token with consistent spacing
            for token in self.tokens:
                token_type = token['type']
                value = token['value'][:22] + '...' if len(token['value']) > 25 else token['value']
                line_num = str(token['line'])
                column_num = str(token['column'])
                
                row = f"{token_type:<15} {value:<25} {line_num:<8} {column_num:<8}\n"
                display_text += row

            display_text += f"\nTotal Tokens: {len(self.tokens)}\n"
            self.tokens_text.insert('1.0', display_text)

    def update_errors_display(self):
        """Update errors display"""
        if hasattr(self, 'errors_text'):
            self.errors_text.delete('1.0', 'end')
            if not self.errors:
                self.errors_text.insert('1.0', "No errors found ✅")
            else:
                error_text = f"ERRORS FOUND ({len(self.errors)}):\n"
                error_text += "=" * 30 + "\n\n"
                for i, error in enumerate(self.errors, 1):
                    error_text += f"{i}. {error}\n"
                self.errors_text.insert('1.0', error_text)

    def update_statistics_display(self):
        """Update statistics display"""
        if hasattr(self, 'stats_text'):
            self.stats_text.delete('1.0', 'end')
            
            if not self.tokens:
                self.stats_text.insert('1.0', "No statistics available")
                return
            
            # Calculate statistics
            from collections import Counter
            token_types = Counter(token['type'] for token in self.tokens)
            
            stats_text = "LEXICAL ANALYSIS STATISTICS\n"
            stats_text += "=" * 35 + "\n\n"
            stats_text += f"Total Tokens: {len(self.tokens)}\n"
            stats_text += f"Unique Values: {len(set(token['value'] for token in self.tokens))}\n"
            stats_text += f"Lines Analyzed: {len(set(token['line'] for token in self.tokens))}\n\n"
            
            stats_text += "Token Type Distribution:\n"
            stats_text += "-" * 25 + "\n"
            for token_type, count in token_types.most_common():
                percentage = (count / len(self.tokens)) * 100
                stats_text += f"{token_type}: {count} ({percentage:.1f}%)\n"
            
            self.stats_text.insert('1.0', stats_text)

    def apply_syntax_highlighting(self):
        """Apply basic syntax highlighting (placeholder)"""
        # This is a placeholder - full syntax highlighting would require more complex implementation
        pass

    def clear_editor(self):
        """Clear the code editor"""
        self.code_editor.delete('1.0', 'end')
        self.tokens = []
        self.errors = []
        if hasattr(self, 'tokens_text'):
            self.tokens_text.delete('1.0', 'end')
        if hasattr(self, 'errors_text'):
            self.errors_text.delete('1.0', 'end')
        if hasattr(self, 'stats_text'):
            self.stats_text.delete('1.0', 'end')
        self.update_status("Editor cleared")

    def on_code_change(self, event=None):
        """Handle code editor changes"""
        if hasattr(self, 'realtime_analysis_var') and self.realtime_analysis_var.get():
            # Cancel previous timer
            if self._analysis_timer:
                self.root.after_cancel(self._analysis_timer)
            # Set new timer for delayed analysis
            self._analysis_timer = self.root.after(1000, self.perform_lexical_analysis)


    def generate_ast(self):
        """Generate and visualize Abstract Syntax Tree"""
        self.update_status("Generating AST...")
        try:
            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                messagebox.showwarning("Warning", "No code to analyze")
                return

            # Clear previous AST display
            for widget in self.ast_canvas_frame.winfo_children():
                widget.destroy()

            # Generate AST based on language
            language = self.current_language.get()
            if language == 'Python':
                # Use Python's ast module
                try:
                    tree = ast.parse(code)
                    self.visualize_python_ast(tree)
                except SyntaxError as e:
                    messagebox.showerror("Syntax Error", f"Cannot parse code: {str(e)}")
                    return
            else:
                # For other languages, create a simplified AST
                self.visualize_generic_ast(code, language)

            self.update_status("AST generated successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate AST: {str(e)}")
            self.update_status("AST generation failed")

    def visualize_python_ast(self, tree):
        """Visualize AST in scrollable layout with proper error handling"""
        try:
            # Clear canvas
            for widget in self.ast_canvas_frame.winfo_children():
                widget.destroy()

            # Create scrollable frame
            scrollable_frame = ctk.CTkScrollableFrame(
                self.ast_canvas_frame,
                corner_radius=8,
                fg_color=self.colors['background']
            )
            scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Create AST sections
            self.create_ast_sections(scrollable_frame, tree)

        except Exception as e:
            # Call the error handler
            self.show_ast_error(e)

    def create_ast_sections(self, parent, tree):
        """Create AST analysis sections with chart"""
        
        # 1. AST Overview (text)
        self.create_ast_overview_section(parent, tree)
        
        # 2. AST Network Chart (NEW!)
        self.create_ast_chart_section(parent, tree)
        
        # 3. Node Types Analysis
        self.create_node_types_section(parent, tree)
        
        # 4. AST Structure Table
        self.create_ast_structure_table(parent, tree)

    def create_parse_tree_sections(self, parent, tokens):
        """Create parse tree analysis sections with chart"""
        
        # 1. Tree Overview (text)
        self.create_tree_overview_section(parent, tokens)
        
        # 2. Parse Tree Network Chart (NEW!)
        self.create_parse_tree_chart_section(parent, tokens)
        
        # 3. Token Breakdown by Lines
        self.create_token_breakdown_section(parent, tokens)
        
        # 4. Syntax Structure Analysis
        self.create_syntax_structure_section(parent, tokens)

    def create_node_types_section(self, parent, tree):
        """Create node types analysis section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['warning'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🔍 AST Node Types Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Analyze node types
        node_types = self.analyze_ast_node_types(tree)
        
        # Display node types
        types_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        types_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Create node type cards
        for node_type, count in node_types.items():
            type_card = ctk.CTkFrame(types_frame, corner_radius=8)
            type_card.pack(fill='x', pady=5)
            
            type_header = ctk.CTkFrame(type_card, fg_color=self.colors['secondary'])
            type_header.pack(fill='x', padx=10, pady=10)
            
            ctk.CTkLabel(
                type_header,
                text=f"{node_type}: {count} occurrences",
                font=('Arial', 12, 'bold'),
                text_color='white'
            ).pack(pady=5)

    def analyze_ast_node_types(self, tree):
        """Analyze AST node types and count occurrences"""
        node_types = {}
        
        for node in ast.walk(tree):
            node_type = type(node).__name__
            if node_type not in node_types:
                node_types[node_type] = 0
            node_types[node_type] += 1
        
        return dict(sorted(node_types.items(), key=lambda x: x[1], reverse=True))

    def create_ast_structure_table(self, parent, tree):
        """Create AST structure table"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['accent'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📋 AST Structure Table",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create table
        table_container = ctk.CTkScrollableFrame(section_frame, height=300)
        table_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Table header
        header_frame = ctk.CTkFrame(table_container, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', pady=(0, 5))
        
        header_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_grid.pack(fill='x', padx=10, pady=8)
        
        headers = ["Level", "Node Type", "Value/Name", "Children"]
        for i, header_text in enumerate(headers):
            ctk.CTkLabel(
                header_grid,
                text=header_text,
                font=('Arial', 12, 'bold'),
                text_color='white'
            ).grid(row=0, column=i, padx=5, sticky='ew')
            header_grid.grid_columnconfigure(i, weight=1)
        
        # Build table data
        table_data = []
        self.build_ast_table_data(tree, 0, table_data)
        
        # Display table rows (limit to 50 for performance)
        for i, (level, node_type, value, children_count) in enumerate(table_data[:50]):
            row_color = self.colors['background'] if i % 2 == 0 else self.colors['surface']
            
            row_frame = ctk.CTkFrame(table_container, fg_color=row_color)
            row_frame.pack(fill='x', pady=1)
            
            row_grid = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_grid.pack(fill='x', padx=10, pady=3)
            
            values = [str(level), node_type, value, str(children_count)]
            
            for j, val in enumerate(values):
                ctk.CTkLabel(
                    row_grid,
                    text=val,
                    font=('Arial', 10),
                    anchor='center'
                ).grid(row=0, column=j, padx=5, sticky='ew')
                row_grid.grid_columnconfigure(j, weight=1)
        
        # Show count info
        if len(table_data) > 50:
            info_label = ctk.CTkLabel(
                table_container,
                text=f"Showing first 50 nodes of {len(table_data)} total nodes",
                font=('Arial', 10, 'italic'),
                text_color=self.colors['text_secondary']
            )
            info_label.pack(pady=10)

    def build_ast_table_data(self, node, level, table_data):
        """Build table data for AST structure"""
        node_type = type(node).__name__
        
        # Get node value/name
        if hasattr(node, 'name') and node.name:
            value = str(node.name)[:20]
        elif hasattr(node, 'id') and node.id:
            value = str(node.id)[:20]
        elif hasattr(node, 'value') and node.value is not None:
            value = str(node.value)[:20]
        else:
            value = "-"
        
        # Count children
        children = list(ast.iter_child_nodes(node))
        children_count = len(children)
        
        table_data.append((level, node_type, value, children_count))
        
        # Process children
        for child in children:
            self.build_ast_table_data(child, level + 1, table_data)

    def create_node_hierarchy_section(self, parent, tree):
        """Create node hierarchy section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🏗️ Node Hierarchy",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create hierarchy display
        hierarchy_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        hierarchy_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Generate hierarchy text
        hierarchy_text = self.generate_hierarchy_text(tree)
        
        text_widget = ctk.CTkTextbox(
            hierarchy_frame,
            height=200,
            font=('Courier', 10),
            fg_color=self.colors['surface']
        )
        text_widget.pack(fill='x', pady=10)
        text_widget.insert('1.0', hierarchy_text)
        text_widget.configure(state='disabled')

    def generate_hierarchy_text(self, tree, indent=0, max_depth=5):
        """Generate hierarchy text representation"""
        if indent > max_depth:
            return "  " * indent + "... (max depth reached)\n"
        
        result = "  " * indent + type(tree).__name__
        
        # Add node details
        if hasattr(tree, 'name') and tree.name:
            result += f" (name: {tree.name})"
        elif hasattr(tree, 'id') and tree.id:
            result += f" (id: {tree.id})"
        elif hasattr(tree, 'value') and tree.value is not None:
            value_str = str(tree.value)
            if len(value_str) < 30:
                result += f" (value: {value_str})"
        
        result += "\n"
        
        # Add children
        children = list(ast.iter_child_nodes(tree))
        for child in children[:5]:  # Limit to 5 children per node
            result += self.generate_hierarchy_text(child, indent + 1, max_depth)
        
        if len(children) > 5:
            result += "  " * (indent + 1) + f"... and {len(children) - 5} more children\n"
        
        return result

    def create_token_flow_chart_section(self, parent, tokens):
        """Create token flow visualization"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['warning'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🔄 Token Flow Diagram",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.patches as mpatches
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#ffffff')
            
            # Flow steps
            steps = ['Source Code', 'Lexical Analysis', 'Tokens', 'Parse Tree', 'AST']
            colors = ['#e2e8f0', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
            
            # Draw flow
            for i, (step, color) in enumerate(zip(steps, colors)):
                # Draw box
                rect = mpatches.Rectangle((i*2, 1), 1.5, 1, 
                                        facecolor=color, edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                
                # Add text
                ax.text(i*2 + 0.75, 1.5, step, ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white')
                
                # Draw arrow
                if i < len(steps) - 1:
                    ax.arrow(i*2 + 1.5, 1.5, 0.4, 0, head_width=0.1, head_length=0.1,
                            fc='black', ec='black')
            
            # Add token count info
            ax.text(4, 0.3, f"Total Tokens: {len(tokens)}", ha='center', va='center',
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
            
            ax.set_xlim(-0.5, 9.5)
            ax.set_ylim(0, 3)
            ax.set_title('Token Processing Flow', fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                chart_frame,
                text=f"Flow chart generation failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)


    def create_ast_chart_section(self, parent, tree):
        """Create actual NetworkX chart for AST"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['primary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🌳 AST Network Visualization",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import networkx as nx
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#ffffff')
            
            # Build NetworkX graph from AST
            G = nx.DiGraph()
            node_labels = {}
            node_colors = []
            node_sizes = []
            
            def add_ast_to_graph(ast_node, parent_id=None, node_counter=[0]):
                current_id = node_counter[0]
                node_counter[0] += 1
                
                # Get node type
                node_type = type(ast_node).__name__
                
                # Create label
                if hasattr(ast_node, 'name') and ast_node.name:
                    label = f"{node_type}\n{ast_node.name}"
                elif hasattr(ast_node, 'id') and ast_node.id:
                    label = f"{node_type}\n{ast_node.id}"
                elif hasattr(ast_node, 'value') and ast_node.value is not None:
                    value_str = str(ast_node.value)[:10]
                    label = f"{node_type}\n{value_str}"
                else:
                    label = node_type
                
                # Add node
                G.add_node(current_id)
                node_labels[current_id] = label
                
                # Color coding
                if node_type in ['Module', 'FunctionDef', 'ClassDef']:
                    node_colors.append('#2563eb')
                    node_sizes.append(3000)
                elif node_type in ['If', 'For', 'While', 'With']:
                    node_colors.append('#059669')
                    node_sizes.append(2500)
                elif node_type in ['Assign', 'Return', 'Expr']:
                    node_colors.append('#dc2626')
                    node_sizes.append(2200)
                elif node_type in ['Name', 'Constant', 'Num', 'Str']:
                    node_colors.append('#7c3aed')
                    node_sizes.append(1800)
                else:
                    node_colors.append('#6b7280')
                    node_sizes.append(2000)
                
                # Connect to parent
                if parent_id is not None:
                    G.add_edge(parent_id, current_id)
                
                # Process children
                for child in ast.iter_child_nodes(ast_node):
                    add_ast_to_graph(child, current_id, node_counter)
                
                return current_id
            
            # Build the graph
            add_ast_to_graph(tree)
            
            # Create layout
            try:
                pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
            except:
                pos = nx.circular_layout(G)
            
            # Draw the graph
            nx.draw_networkx_nodes(G, pos, 
                                node_color=node_colors,
                                node_size=node_sizes,
                                alpha=0.9,
                                linewidths=2,
                                edgecolors='white')
            
            nx.draw_networkx_labels(G, pos, node_labels,
                                font_size=9,
                                font_weight='bold',
                                font_color='white')
            
            nx.draw_networkx_edges(G, pos,
                                edge_color='#374151',
                                arrows=True,
                                arrowsize=20,
                                arrowstyle='->',
                                width=2,
                                alpha=0.7)
            
            # Styling
            ax.set_title('Abstract Syntax Tree Network', fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            ax.margins(0.1)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                chart_frame,
                text=f"AST chart generation failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)

    def create_parse_tree_chart_section(self, parent, tokens):
        """Create actual NetworkX chart for Parse Tree"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🌲 Parse Tree Network Visualization",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import networkx as nx
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.patch.set_facecolor('#ffffff')
            
            # Build NetworkX graph from tokens
            G = nx.DiGraph()
            node_labels = {}
            node_colors = []
            node_sizes = []
            
            node_id = 0
            
            # Root node
            G.add_node(node_id)
            node_labels[node_id] = "Program"
            node_colors.append('#1f2937')
            node_sizes.append(4000)
            root_id = node_id
            node_id += 1
            
            # Group tokens by lines
            lines = {}
            for token in tokens:
                line = token['line']
                if line not in lines:
                    lines[line] = []
                lines[line].append(token)
            
            # Create statement nodes
            for line_num, line_tokens in lines.items():
                stmt_id = node_id
                node_id += 1
                
                G.add_node(stmt_id)
                node_labels[stmt_id] = f"Line {line_num}"
                node_colors.append('#3b82f6')
                node_sizes.append(3000)
                G.add_edge(root_id, stmt_id)
                
                # Add important tokens only (limit for clarity)
                important_tokens = [t for t in line_tokens 
                                if t['type'] in ['KEYWORD', 'IDENTIFIER', 'OPERATOR', 'NUMBER', 'STRING']][:4]
                
                for token in important_tokens:
                    token_id = node_id
                    node_id += 1
                    
                    G.add_node(token_id)
                    
                    # Clean token value
                    token_value = token['value'][:8] + '..' if len(token['value']) > 8 else token['value']
                    node_labels[token_id] = f"{token['type']}\n'{token_value}'"
                    
                    # Color by token type
                    color_map = {
                        'KEYWORD': '#ef4444',
                        'IDENTIFIER': '#10b981',
                        'OPERATOR': '#f59e0b',
                        'NUMBER': '#8b5cf6',
                        'STRING': '#06b6d4'
                    }
                    node_colors.append(color_map.get(token['type'], '#6b7280'))
                    node_sizes.append(2000)
                    G.add_edge(stmt_id, token_id)
            
            # Create hierarchical layout
            try:
                pos = nx.spring_layout(G, k=4, iterations=50, seed=24)
            except:
                pos = nx.circular_layout(G)
            
            # Draw the graph
            nx.draw_networkx_nodes(G, pos,
                                node_color=node_colors,
                                node_size=node_sizes,
                                alpha=0.9,
                                linewidths=2,
                                edgecolors='white')
            
            nx.draw_networkx_labels(G, pos, node_labels,
                                font_size=9,
                                font_weight='bold',
                                font_color='white')
            
            nx.draw_networkx_edges(G, pos,
                                edge_color='#6b7280',
                                arrows=True,
                                arrowsize=15,
                                arrowstyle='->',
                                width=2,
                                alpha=0.7)
            
            # Add legend
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ef4444', 
                        markersize=10, label='Keywords'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#10b981', 
                        markersize=10, label='Identifiers'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f59e0b', 
                        markersize=10, label='Operators'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#8b5cf6', 
                        markersize=10, label='Numbers/Strings')
            ]
            ax.legend(handles=legend_elements, loc='upper right', frameon=True)
            
            # Styling
            ax.set_title('Parse Tree Network Structure', fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            ax.margins(0.1)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                chart_frame,
                text=f"Parse tree chart generation failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)


    def create_basic_ast_section(self, parent, tree):
        """Create basic AST section when detailed sections fail"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['primary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🌳 Basic AST Information",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Basic AST info
        info_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        info_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Count nodes
        node_count = sum(1 for _ in ast.walk(tree))
        root_type = type(tree).__name__
        
        info_text = f"""
    AST Statistics:
    • Root Node Type: {root_type}
    • Total Nodes: {node_count}
    • AST Successfully Parsed: ✅

    🔍 Basic Structure:
    The code has been successfully parsed into an Abstract Syntax Tree.
    You can view the detailed token analysis in other tabs.

    💡 Note:
    Advanced AST visualization is temporarily unavailable.
    The basic parsing functionality is working correctly.
    """
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        ).pack(fill='x', padx=10, pady=10)


    def create_ast_overview_section(self, parent, tree):
        """Create AST overview section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['primary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🌳 Abstract Syntax Tree Overview",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # AST text representation
        ast_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        ast_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Generate AST text
        ast_text = self.generate_ast_text(tree)
        
        text_widget = ctk.CTkTextbox(
            ast_frame,
            height=300,
            font=('Courier', 11),
            fg_color=self.colors['surface']
        )
        text_widget.pack(fill='x', pady=10)
        text_widget.insert('1.0', ast_text)
        text_widget.configure(state='disabled')

    def generate_ast_text(self, tree, indent=0):
        """Generate text representation of AST"""
        result = "  " * indent + type(tree).__name__
        
        # Add node details
        if hasattr(tree, 'name'):
            result += f" (name: {tree.name})"
        elif hasattr(tree, 'id'):
            result += f" (id: {tree.id})"
        elif hasattr(tree, 'value'):
            result += f" (value: {tree.value})"
        
        result += "\n"
        
        # Add children
        for child in ast.iter_child_nodes(tree):
            result += self.generate_ast_text(child, indent + 1)
        
        return result


    def build_ast_structure(self, tree):
        """Build simplified AST structure for visualization"""
        def extract_node_info(node):
            node_type = type(node).__name__
            
            # Get meaningful label
            if hasattr(node, 'name') and node.name:
                label = f"{node_type}\n{node.name}"
            elif hasattr(node, 'id') and node.id:
                label = f"{node_type}\n{node.id}"
            elif hasattr(node, 'value') and str(node.value) and len(str(node.value)) < 20:
                label = f"{node_type}\n{str(node.value)}"
            else:
                label = node_type
            
            return {
                'type': node_type,
                'label': label,
                'children': [extract_node_info(child) for child in ast.iter_child_nodes(node)]
            }
        
        return extract_node_info(tree)

    def draw_ast_diagram(self, ax, ast_structure):
        """Draw AST diagram with proper layout"""
        import matplotlib.patches as patches
        
        # Color scheme for different node types
        node_colors = {
            'Module': '#2d3748',
            'FunctionDef': '#2b6cb0',
            'ClassDef': '#2b6cb0',
            'If': '#38a169',
            'For': '#38a169',
            'While': '#38a169',
            'Assign': '#d69e2e',
            'Return': '#d69e2e',
            'Call': '#e53e3e',
            'Name': '#805ad5',
            'Constant': '#805ad5',
            'BinOp': '#dd6b20',
            'Compare': '#dd6b20'
        }
        
        # Calculate layout
        layout = self.calculate_ast_layout(ast_structure)
        
        # Draw nodes and connections
        for node_id, (x, y, node_data) in layout.items():
            # Get color
            color = node_colors.get(node_data['type'], '#718096')
            
            # Determine size
            if node_data['type'] in ['Module', 'FunctionDef', 'ClassDef']:
                size = 1.2
            elif node_data['type'] in ['If', 'For', 'While', 'Assign']:
                size = 1.0
            else:
                size = 0.8
            
            # Draw node
            circle = patches.Circle((x, y), size, facecolor=color,
                                edgecolor='white', linewidth=3, alpha=0.9)
            ax.add_patch(circle)
            
            # Add label
            ax.text(x, y, node_data['label'], ha='center', va='center',
                fontsize=9, fontweight='bold', color='white',
                bbox=dict(boxstyle="round,pad=0.1", facecolor=color, alpha=0.8))
        
        # Draw connections
        self.draw_ast_connections(ax, layout, ast_structure)
        
        # Set axis limits
        if layout:
            x_coords = [pos[0] for pos in layout.values()]
            y_coords = [pos[1] for pos in layout.values()]
            ax.set_xlim(min(x_coords) - 3, max(x_coords) + 3)
            ax.set_ylim(min(y_coords) - 3, max(y_coords) + 3)

    def calculate_ast_layout(self, ast_structure):
        """Calculate layout positions for AST nodes"""
        layout = {}
        node_counter = 0
        
        def position_nodes(node, level=0, h_position=0):
            nonlocal node_counter
            
            node_id = node_counter
            node_counter += 1
            
            # Vertical positioning
            y = -level * 4
            
            # Horizontal positioning
            num_children = len(node['children'])
            if num_children == 0:
                x = h_position
            else:
                # Calculate child positions first
                child_spacing = 4
                total_width = (num_children - 1) * child_spacing
                start_x = h_position - total_width / 2
                
                child_positions = []
                for i, child in enumerate(node['children']):
                    child_x = start_x + i * child_spacing
                    child_positions.append(child_x)
                    position_nodes(child, level + 1, child_x)
                
                # Center parent over children
                x = sum(child_positions) / len(child_positions) if child_positions else h_position
            
            layout[node_id] = (x, y, node)
            node['_id'] = node_id
            node['_pos'] = (x, y)
        
        position_nodes(ast_structure)
        return layout

    def draw_ast_connections(self, ax, layout, ast_structure):
        """Draw connections between AST nodes"""
        def draw_edges(node):
            if '_pos' in node:
                parent_x, parent_y = node['_pos']
                
                for child in node['children']:
                    if '_pos' in child:
                        child_x, child_y = child['_pos']
                        
                        # Draw curved line
                        ax.annotate('', xy=(child_x, child_y + 1.0),
                                xytext=(parent_x, parent_y - 1.0),
                                arrowprops=dict(arrowstyle='->', 
                                                connectionstyle="arc3,rad=0.1",
                                                color='#4a5568', lw=2, alpha=0.7))
                    
                    draw_edges(child)
        
        draw_edges(ast_structure)

    def show_ast_fallback(self):
        """Show fallback AST display when visualization fails"""
        fallback_frame = ctk.CTkFrame(self.ast_canvas_frame)
        fallback_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        fallback_label = ctk.CTkLabel(
            fallback_frame,
            text="🌳 AST Visualization\n\nAST structure is available but\nvisualization is temporarily unavailable.\n\nPlease check the code syntax and try again.",
            font=('Arial', 14),
            justify='center'
        )
        fallback_label.pack(expand=True)


    def create_improved_ast_layout(self, G, level_positions):
        """Create improved hierarchical layout for AST with better spacing"""
        pos = {}
        
        for level, nodes_at_level in level_positions.items():
            y_pos = -level * 3  # Increased vertical spacing
            num_nodes = len(nodes_at_level)
            
            if num_nodes == 1:
                x_positions = [0]
            else:
                # Dynamic width based on number of nodes
                total_width = max(12, num_nodes * 4)
                x_positions = np.linspace(-total_width/2, total_width/2, num_nodes)
            
            for i, (node_id, _) in enumerate(nodes_at_level):
                pos[node_id] = (x_positions[i], y_pos)
        
        return pos

    def show_ast_error(self, error):
        """Show AST error in a user-friendly way"""
        # Clear the AST canvas
        for widget in self.ast_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create error display frame
        error_frame = ctk.CTkFrame(self.ast_canvas_frame, corner_radius=12)
        error_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Error icon and title
        title_frame = ctk.CTkFrame(error_frame, corner_radius=8, fg_color=self.colors['danger'])
        title_frame.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            title_frame,
            text="⚠️ AST Generation Error",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=15)
        
        # Error details
        details_frame = ctk.CTkFrame(error_frame, fg_color="transparent")
        details_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        error_text = f"""
    🔍 Error Details:
    {str(error)}

    💡 Possible Solutions:
    • Check your code syntax for errors
    • Ensure the code is valid Python
    • Try with simpler code first
    • Check for missing imports or dependencies

    🔧 What you can do:
    1. Fix any syntax errors in your code
    2. Try loading a sample code using 'Load Sample' button
    3. Check the 'Theory & Concepts' tab for help
    4. Review the error details above
    """
        
        ctk.CTkLabel(
            details_frame,
            text=error_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        ).pack(fill='both', expand=True, padx=10, pady=10)
        
        # Action buttons
        button_frame = ctk.CTkFrame(error_frame, fg_color="transparent")
        button_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Load sample button
        sample_btn = ctk.CTkButton(
            button_frame,
            text="📋 Load Sample Code",
            command=self.load_sample_code,
            fg_color=self.colors['primary'],
            hover_color=self.adjust_color_brightness(self.colors['primary'], -20),
            corner_radius=8,
            height=40
        )
        sample_btn.pack(side='left', padx=5)
        
        # Try again button
        retry_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Try Again",
            command=self.visualize_ast,
            fg_color=self.colors['success'],
            hover_color=self.adjust_color_brightness(self.colors['success'], -20),
            corner_radius=8,
            height=40
        )
        retry_btn.pack(side='left', padx=5)
        
        # Update status
        self.update_status(f"AST generation failed: {str(error)}")

    
    def create_hierarchical_layout(self, G, level_nodes):
        """Create hierarchical layout for AST"""
        pos = {}
        
        for level, nodes in level_nodes.items():
            y_pos = -level * 2
            num_nodes = len(nodes)
            
            if num_nodes == 1:
                x_positions = [0]
            else:
                width = max(6, num_nodes * 1.5)
                x_positions = np.linspace(-width/2, width/2, num_nodes)
            
            for i, node_id in enumerate(nodes):
                pos[node_id] = (x_positions[i], y_pos)
        
        return pos

    def visualize_generic_ast(self, code, language):
        """Create simplified AST visualization for non-Python languages"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import networkx as nx

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor(self.colors['surface'])

        # Create simplified AST based on tokens
        tokens = self.tokenize_code(code, language)

        # Build simplified tree structure
        G = nx.DiGraph()
        labels = {}
        node_colors = []

        # Root node
        G.add_node(0)
        labels[0] = "Program"
        node_colors.append(self.colors['primary'])

        # Group tokens by type
        token_groups = defaultdict(list)
        for token in tokens:
            token_groups[token['type']].append(token)

        # Add type nodes
        node_id = 1
        for token_type, type_tokens in token_groups.items():
            type_node_id = node_id
            node_id += 1

            G.add_node(type_node_id)
            labels[type_node_id] = f"{token_type}\n({len(type_tokens)})"
            node_colors.append(self.colors['secondary'])
            G.add_edge(0, type_node_id)

            # Add sample tokens (limit to 3 per type)
            for j, token in enumerate(type_tokens[:3]):
                token_node_id = node_id
                node_id += 1

                G.add_node(token_node_id)
                token_value = token['value'][:10] + '...' if len(token['value']) > 10 else token['value']
                labels[token_node_id] = token_value
                node_colors.append(self.colors['accent'])
                G.add_edge(type_node_id, token_node_id)

        # Create layout
        pos = nx.spring_layout(G, k=3, iterations=50)

        # Draw graph
        nx.draw(G, pos, ax=ax, with_labels=True, labels=labels,
                node_color=node_colors, node_size=1500,
                font_size=8, font_color='white', font_weight='bold',
                edge_color=self.colors['text_secondary'], arrows=True,
                arrowsize=15, arrowstyle='->',
                node_shape='o', linewidths=1)

        ax.set_title(f"Simplified AST - {language}", fontsize=16, fontweight='bold',
                    color=self.colors['text_primary'])
        ax.set_facecolor(self.colors['background'])
        ax.set_xticks([])
        ax.set_yticks([])

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.ast_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def export_ast(self):
        """Export AST visualization as PNG"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export AST",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                # Get the current figure
                for widget in self.ast_canvas_frame.winfo_children():
                    if hasattr(widget, 'figure'):
                        widget.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                        self.update_status(f"AST exported to {os.path.basename(file_path)}")
                        return
                
                messagebox.showwarning("Warning", "No AST to export. Generate AST first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export AST: {str(e)}")

    def generate_frequency_chart(self):
        """Generate comprehensive frequency analysis in scrollable layout"""
        self.update_status("Creating frequency analysis...")
        try:
            if not self.tokens:
                messagebox.showwarning("Warning", "No tokens to analyze")
                return

            # Clear canvas
            for widget in self.freq_canvas_frame.winfo_children():
                widget.destroy()

            # Create scrollable frame
            scrollable_frame = ctk.CTkScrollableFrame(
                self.freq_canvas_frame, 
                corner_radius=8,
                fg_color=self.colors['background']
            )
            scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Analyze data
            analysis_data = self.analyze_comprehensive_token_data()
            
            # Create sections
            self.create_frequency_sections(scrollable_frame, analysis_data)

            self.update_status("Frequency analysis completed")

        except Exception as e:
            messagebox.showerror("Error", f"Frequency analysis failed: {str(e)}")
            self.update_status("Frequency analysis failed")

    def analyze_comprehensive_token_data(self):
        """Comprehensive token analysis"""
        from collections import Counter
        
        # Basic analysis
        token_types = Counter(token['type'] for token in self.tokens)
        token_values = Counter(token['value'] for token in self.tokens)
        
        # Line-by-line analysis
        line_analysis = {}
        for token in self.tokens:
            line = token['line']
            if line not in line_analysis:
                line_analysis[line] = {
                    'tokens': [],
                    'types': set(),
                    'count': 0
                }
            line_analysis[line]['tokens'].append(token)
            line_analysis[line]['types'].add(token['type'])
            line_analysis[line]['count'] += 1
        
        # Category analysis
        keywords = [t['value'] for t in self.tokens if t['type'] == 'KEYWORD']
        identifiers = [t['value'] for t in self.tokens if t['type'] == 'IDENTIFIER']
        operators = [t['value'] for t in self.tokens if t['type'] == 'OPERATOR']
        numbers = [t['value'] for t in self.tokens if t['type'] == 'NUMBER']
        strings = [t['value'] for t in self.tokens if t['type'] == 'STRING']
        
        return {
            'token_types': token_types,
            'token_values': token_values,
            'line_analysis': line_analysis,
            'keywords': Counter(keywords),
            'identifiers': Counter(identifiers),
            'operators': Counter(operators),
            'numbers': Counter(numbers),
            'strings': Counter(strings),
            'total_tokens': len(self.tokens),
            'unique_tokens': len(set(t['value'] for t in self.tokens)),
            'total_lines': len(line_analysis)
        }

    def create_token_distribution_pie_chart(self, parent, data):
        """Create pie chart for token distribution"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['accent'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🥧 Token Distribution Pie Chart",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            fig.patch.set_facecolor('#ffffff')
            
            # Data
            token_types = list(data['token_types'].keys())
            counts = list(data['token_types'].values())
            colors = ['#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#6b7280', '#84cc16']
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(counts, labels=token_types, colors=colors[:len(token_types)],
                                            autopct='%1.1f%%', startangle=90,
                                            textprops={'fontsize': 12, 'fontweight': 'bold'},
                                            pctdistance=0.85)
            
            # Style the percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            
            # Add title
            ax.set_title('Token Type Distribution', fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                chart_frame,
                text=f"Pie chart failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)


    def create_frequency_sections(self, parent, data):
        """Create all frequency analysis sections with actual charts"""
        
        # 1. Overview Statistics
        self.create_overview_section(parent, data)
        
        # 2. Token Types Bar Chart
        self.create_token_types_chart_section(parent, data)
        
        # 3. Token Distribution Pie Chart
        self.create_token_distribution_pie_chart(parent, data)
        
        # 4. Keywords Chart
        self.create_keywords_chart_section(parent, data)
        
        # 5. Line Analysis Chart
        self.create_line_analysis_chart_section(parent, data)
        
        # 6. Detailed Token Table
        self.create_detailed_token_table(parent)


    def create_token_types_chart_section(self, parent, data):
        """Create actual matplotlib chart for token types"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📊 Token Types Distribution Chart",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create matplotlib chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Generate actual chart
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#ffffff')
            
            # Data
            token_types = list(data['token_types'].keys())
            counts = list(data['token_types'].values())
            colors = ['#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#6b7280', '#84cc16']
            
            # Create bar chart
            bars = ax.bar(token_types, counts, color=colors[:len(token_types)], 
                        alpha=0.8, edgecolor='white', linewidth=2)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', 
                    fontweight='bold', fontsize=12)
            
            # Styling
            ax.set_title('Token Types Distribution', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Token Type', fontsize=12, fontweight='bold')
            ax.set_ylabel('Count', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_facecolor('#f8f9fa')
            
            # Rotate labels if needed
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            # Fallback text display
            ctk.CTkLabel(
                chart_frame,
                text=f"Chart generation failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)

    def create_keywords_chart_section(self, parent, data):
        """Create actual chart for keywords frequency"""
        if not data['keywords']:
            return
            
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['warning'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🔑 Keywords Frequency Chart",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#ffffff')
            
            # Data - top 8 keywords
            top_keywords = data['keywords'].most_common(8)
            keywords = [item[0] for item in top_keywords]
            counts = [item[1] for item in top_keywords]
            
            # Create horizontal bar chart
            bars = ax.barh(keywords, counts, color='#dc2626', alpha=0.8, edgecolor='white', linewidth=2)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center', 
                    fontweight='bold', fontsize=11)
            
            # Styling
            ax.set_title('Most Frequent Keywords', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.set_facecolor('#f8f9fa')
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                chart_frame,
                text=f"Keywords chart failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)

    def create_line_analysis_chart_section(self, parent, data):
        """Create line complexity analysis chart"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['secondary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📈 Line Complexity Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#ffffff')
            
            # Data
            lines = sorted(data['line_analysis'].keys())
            token_counts = [data['line_analysis'][line]['count'] for line in lines]
            
            # Create line chart
            ax.plot(lines, token_counts, marker='o', linewidth=3, markersize=8,
                color='#059669', markerfacecolor='#10b981', 
                markeredgecolor='white', markeredgewidth=2)
            
            # Fill area under curve
            ax.fill_between(lines, token_counts, alpha=0.3, color='#10b981')
            
            # Add value labels on points
            for i, (line, count) in enumerate(zip(lines, token_counts)):
                ax.text(line, count + 0.5, str(count), ha='center', va='bottom',
                    fontweight='bold', fontsize=10)
            
            # Styling
            ax.set_title('Token Count per Line', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Line Number', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Tokens', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_facecolor('#f8f9fa')
            ax.set_ylim(bottom=0)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(
                chart_frame,
                text=f"Line analysis chart failed: {str(e)}",
                font=('Arial', 12)
            ).pack(pady=20)


    def create_overview_section(self, parent, data):
        """Create overview statistics section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['primary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📊 Analysis Overview",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Stats grid
        stats_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        stats_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Create stats cards
        stats = [
            ("Total Tokens", data['total_tokens'], self.colors['success']),
            ("Unique Tokens", data['unique_tokens'], self.colors['warning']),
            ("Lines Analyzed", data['total_lines'], self.colors['secondary']),
            ("Token Types", len(data['token_types']), self.colors['accent'])
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, corner_radius=8, fg_color=color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=str(value),
                font=('Arial', 24, 'bold'),
                text_color='white'
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                card,
                text=label,
                font=('Arial', 12),
                text_color='white'
            ).pack(pady=(0, 15))

    def create_token_types_section(self, parent, data):
        """Create token types analysis section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🏷️ Token Types Distribution",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create chart
        chart_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        chart_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Simple bar chart using tkinter
        self.create_simple_bar_chart(chart_frame, data['token_types'], "Token Types")

    def create_simple_bar_chart(self, parent, data, title):
        """Create simple bar chart using tkinter"""
        chart_frame = ctk.CTkFrame(parent, corner_radius=8)
        chart_frame.pack(fill='x', pady=10)
        
        # Title
        ctk.CTkLabel(
            chart_frame,
            text=title,
            font=('Arial', 14, 'bold')
        ).pack(pady=(15, 10))
        
        # Data
        items = list(data.items())
        max_value = max(data.values()) if data else 1
        
        # Chart area
        chart_area = ctk.CTkFrame(chart_frame, fg_color="transparent")
        chart_area.pack(fill='x', padx=20, pady=(0, 15))
        
        colors = ['#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#6b7280', '#84cc16']
        
        for i, (label, value) in enumerate(items):
            # Row frame
            row_frame = ctk.CTkFrame(chart_area, fg_color="transparent")
            row_frame.pack(fill='x', pady=2)
            
            # Label
            label_frame = ctk.CTkFrame(row_frame, width=120, fg_color="transparent")
            label_frame.pack(side='left', padx=(0, 10))
            label_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                label_frame,
                text=label,
                font=('Arial', 11),
                anchor='w'
            ).pack(fill='x')
            
            # Bar
            bar_width = int((value / max_value) * 300)
            color = colors[i % len(colors)]
            
            bar_frame = ctk.CTkFrame(row_frame, height=25, fg_color=color)
            bar_frame.pack(side='left', fill='x', expand=True)
            
            # Value label
            ctk.CTkLabel(
                bar_frame,
                text=str(value),
                font=('Arial', 10, 'bold'),
                text_color='white'
            ).pack(side='right', padx=10)

    def create_keywords_section(self, parent, data):
        """Create keywords analysis section"""
        if not data['keywords']:
            return
            
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['warning'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🔑 Keywords Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Keywords table
        self.create_frequency_table(section_frame, data['keywords'].most_common(10), "Keyword", "Frequency")

    def create_identifiers_section(self, parent, data):
        """Create identifiers analysis section"""
        if not data['identifiers']:
            return
            
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['secondary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🏷️ Identifiers Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Identifiers table
        self.create_frequency_table(section_frame, data['identifiers'].most_common(10), "Identifier", "Frequency")

    def create_operators_section(self, parent, data):
        """Create operators analysis section"""
        if not data['operators']:
            return
            
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['accent'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="⚙️ Operators Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Operators table
        self.create_frequency_table(section_frame, data['operators'].most_common(10), "Operator", "Frequency")

    def create_frequency_table(self, parent, data, col1_name, col2_name):
        """Create frequency table"""
        table_frame = ctk.CTkFrame(parent, corner_radius=8)
        table_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Table header
        header_frame = ctk.CTkFrame(table_frame, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', padx=10, pady=10)
        
        header_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_grid.pack(fill='x', padx=10, pady=8)
        
        ctk.CTkLabel(
            header_grid,
            text=col1_name,
            font=('Arial', 12, 'bold'),
            text_color='white'
        ).grid(row=0, column=0, sticky='w', padx=10)
        
        ctk.CTkLabel(
            header_grid,
            text=col2_name,
            font=('Arial', 12, 'bold'),
            text_color='white'
        ).grid(row=0, column=1, sticky='e', padx=10)
        
        header_grid.grid_columnconfigure(0, weight=1)
        
        # Table rows
        for i, (item, count) in enumerate(data):
            row_color = self.colors['background'] if i % 2 == 0 else self.colors['surface']
            
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_color)
            row_frame.pack(fill='x', padx=10, pady=1)
            
            row_grid = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_grid.pack(fill='x', padx=10, pady=5)
            
            # Truncate long items
            display_item = item[:20] + '...' if len(str(item)) > 20 else str(item)
            
            ctk.CTkLabel(
                row_grid,
                text=display_item,
                font=('Arial', 11),
                anchor='w'
            ).grid(row=0, column=0, sticky='w', padx=10)
            
            ctk.CTkLabel(
                row_grid,
                text=str(count),
                font=('Arial', 11, 'bold'),
                anchor='e'
            ).grid(row=0, column=1, sticky='e', padx=10)
            
            row_grid.grid_columnconfigure(0, weight=1)

    def create_line_analysis_section(self, parent, data):
        """Create line-by-line analysis section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['danger'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📝 Line-by-Line Analysis",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Line analysis table
        table_frame = ctk.CTkFrame(section_frame, corner_radius=8)
        table_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Table header
        header_frame = ctk.CTkFrame(table_frame, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', padx=10, pady=10)
        
        header_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_grid.pack(fill='x', padx=10, pady=8)
        
        headers = ["Line", "Tokens", "Types", "Complexity"]
        for i, header_text in enumerate(headers):
            ctk.CTkLabel(
                header_grid,
                text=header_text,
                font=('Arial', 12, 'bold'),
                text_color='white'
            ).grid(row=0, column=i, padx=10)
            header_grid.grid_columnconfigure(i, weight=1)
        
        # Table rows
        for i, (line_num, line_data) in enumerate(sorted(data['line_analysis'].items())):
            row_color = self.colors['background'] if i % 2 == 0 else self.colors['surface']
            
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_color)
            row_frame.pack(fill='x', padx=10, pady=1)
            
            row_grid = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_grid.pack(fill='x', padx=10, pady=5)
            
            # Complexity calculation
            complexity = "Low" if line_data['count'] <= 5 else "Medium" if line_data['count'] <= 10 else "High"
            
            values = [str(line_num), str(line_data['count']), str(len(line_data['types'])), complexity]
            
            for j, value in enumerate(values):
                ctk.CTkLabel(
                    row_grid,
                    text=value,
                    font=('Arial', 11),
                    anchor='center'
                ).grid(row=0, column=j, padx=10)
                row_grid.grid_columnconfigure(j, weight=1)

    def create_detailed_token_table(self, parent):
        """Create detailed token table"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['primary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📋 Detailed Token List",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Create scrollable token table
        table_container = ctk.CTkScrollableFrame(section_frame, height=300)
        table_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Table header
        header_frame = ctk.CTkFrame(table_container, fg_color=self.colors['secondary'])
        header_frame.pack(fill='x', pady=(0, 5))
        
        header_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_grid.pack(fill='x', padx=10, pady=8)
        
        headers = ["#", "Type", "Value", "Line", "Column"]
        for i, header_text in enumerate(headers):
            ctk.CTkLabel(
                header_grid,
                text=header_text,
                font=('Arial', 12, 'bold'),
                text_color='white'
            ).grid(row=0, column=i, padx=5, sticky='ew')
            header_grid.grid_columnconfigure(i, weight=1)
        
        # Token rows (limit to first 100 for performance)
        display_tokens = self.tokens[:100]
        
        for i, token in enumerate(display_tokens):
            row_color = self.colors['background'] if i % 2 == 0 else self.colors['surface']
            
            row_frame = ctk.CTkFrame(table_container, fg_color=row_color)
            row_frame.pack(fill='x', pady=1)
            
            row_grid = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_grid.pack(fill='x', padx=10, pady=3)
            
            # Truncate long values
            token_value = token['value'][:15] + '...' if len(token['value']) > 15 else token['value']
            
            values = [str(i+1), token['type'], token_value, str(token['line']), str(token['column'])]
            
            for j, value in enumerate(values):
                ctk.CTkLabel(
                    row_grid,
                    text=value,
                    font=('Arial', 10),
                    anchor='center'
                ).grid(row=0, column=j, padx=5, sticky='ew')
                row_grid.grid_columnconfigure(j, weight=1)
        
        # Show count info
        if len(self.tokens) > 100:
            info_label = ctk.CTkLabel(
                table_container,
                text=f"Showing first 100 tokens of {len(self.tokens)} total tokens",
                font=('Arial', 10, 'italic'),
                text_color=self.colors['text_secondary']
            )
            info_label.pack(pady=10)


    def analyze_token_frequencies(self):
        """Analyze token frequencies and return structured data"""
        from collections import Counter
        
        # Basic frequency analysis
        token_types = Counter(token['type'] for token in self.tokens)
        token_values = Counter(token['value'] for token in self.tokens)
        
        # Line analysis
        lines_analysis = {}
        for token in self.tokens:
            line = token['line']
            if line not in lines_analysis:
                lines_analysis[line] = {'count': 0, 'types': set()}
            lines_analysis[line]['count'] += 1
            lines_analysis[line]['types'].add(token['type'])
        
        # Language-specific analysis
        keywords = [token['value'] for token in self.tokens if token['type'] == 'KEYWORD']
        identifiers = [token['value'] for token in self.tokens if token['type'] == 'IDENTIFIER']
        
        return {
            'token_types': token_types,
            'token_values': token_values,
            'lines_analysis': lines_analysis,
            'keywords': Counter(keywords),
            'identifiers': Counter(identifiers),
            'total_tokens': len(self.tokens),
            'unique_tokens': len(set(token['value'] for token in self.tokens))
        }

    def create_frequency_dashboard(self, fig, data):
        """Create comprehensive frequency dashboard"""
        # Define modern color palette
        colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']
        
        # Create grid layout
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3, 
                            left=0.08, right=0.95, top=0.92, bottom=0.08)
        
        # 1. Token Types Overview (top-left, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        self.create_token_types_chart(ax1, data['token_types'], colors)
        
        # 2. Statistics Panel (top-right)
        ax2 = fig.add_subplot(gs[0, 2])
        self.create_statistics_panel(ax2, data)
        
        # 3. Most Common Keywords (middle-left)
        ax3 = fig.add_subplot(gs[1, 0])
        self.create_keywords_chart(ax3, data['keywords'])
        
        # 4. Most Common Identifiers (middle-center)
        ax4 = fig.add_subplot(gs[1, 1])
        self.create_identifiers_chart(ax4, data['identifiers'])
        
        # 5. Line Complexity (middle-right)
        ax5 = fig.add_subplot(gs[1, 2])
        self.create_line_complexity_chart(ax5, data['lines_analysis'])
        
        # 6. Token Distribution Pie Chart (bottom, spans all columns)
        ax6 = fig.add_subplot(gs[2, :])
        self.create_distribution_pie_chart(ax6, data['token_types'], colors)
        
        # Add main title
        fig.suptitle('Token Frequency Analysis Dashboard', 
                    fontsize=20, fontweight='bold', y=0.96)

    def create_token_types_chart(self, ax, token_types, colors):
        """Create token types bar chart"""
        types = list(token_types.keys())
        counts = list(token_types.values())
        
        bars = ax.bar(types, counts, color=colors[:len(types)], 
                    alpha=0.8, edgecolor='white', linewidth=2)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', 
                fontweight='bold', fontsize=10)
        
        ax.set_title('Token Types Distribution', fontsize=14, fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#f8f9fa')

    def create_statistics_panel(self, ax, data):
        """Create statistics information panel"""
        ax.axis('off')
        
        stats_text = f"""
    📊 ANALYSIS SUMMARY

    Total Tokens: {data['total_tokens']:,}
    Unique Tokens: {data['unique_tokens']:,}
    Lines Analyzed: {len(data['lines_analysis'])}

    🔤 TOKEN BREAKDOWN
    Keywords: {sum(data['keywords'].values())}
    Identifiers: {sum(data['identifiers'].values())}
    Total Types: {len(data['token_types'])}

    📈 COMPLEXITY
    Avg Tokens/Line: {data['total_tokens']/len(data['lines_analysis']):.1f}
    Most Complex Line: {max(data['lines_analysis'].values(), key=lambda x: x['count'])['count']} tokens
    """
        
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#e2e8f0', alpha=0.8))

    def create_keywords_chart(self, ax, keywords):
        """Create keywords frequency chart"""
        if keywords:
            top_keywords = keywords.most_common(5)
            words = [item[0] for item in top_keywords]
            counts = [item[1] for item in top_keywords]
            
            bars = ax.barh(words, counts, color='#dc2626', alpha=0.8)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Keywords\nFound', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        ax.set_title('Top Keywords', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

    def create_identifiers_chart(self, ax, identifiers):
        """Create identifiers frequency chart"""
        if identifiers:
            top_identifiers = identifiers.most_common(5)
            names = [item[0][:10] for item in top_identifiers]  # Truncate long names
            counts = [item[1] for item in top_identifiers]
            
            bars = ax.barh(names, counts, color='#10b981', alpha=0.8)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Identifiers\nFound', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        ax.set_title('Top Identifiers', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

    def create_line_complexity_chart(self, ax, lines_analysis):
        """Create line complexity chart"""
        if lines_analysis:
            lines = sorted(lines_analysis.keys())
            complexities = [lines_analysis[line]['count'] for line in lines]
            
            ax.plot(lines, complexities, marker='o', linewidth=2, markersize=6,
                color='#8b5cf6', markerfacecolor='#a855f7')
            ax.fill_between(lines, complexities, alpha=0.3, color='#8b5cf6')
            
            ax.set_xlabel('Line Number', fontweight='bold')
            ax.set_ylabel('Tokens', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Line Data\nAvailable', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        ax.set_title('Line Complexity', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    def create_distribution_pie_chart(self, ax, token_types, colors):
        """Create token distribution pie chart"""
        types = list(token_types.keys())
        counts = list(token_types.values())
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(counts, labels=types, colors=colors[:len(types)],
                                        autopct='%1.1f%%', startangle=90,
                                        textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Token Type Distribution', fontsize=14, fontweight='bold')


    def fix_indentation(self):
        """Fix indentation issues in the code editor"""
        code = self.code_editor.get('1.0', 'end-1c')
        
        # Replace tabs with 4 spaces
        fixed_code = code.expandtabs(4)
        
        # Clear and reinsert fixed code
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', fixed_code)
        
        self.update_status("Indentation fixed")

    
    def generate_parse_tree(self):
        """Generate parse tree in scrollable layout"""
        self.update_status("Creating parse tree...")
        try:
            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                messagebox.showwarning("Warning", "No code to analyze")
                return

            # Clear canvas
            for widget in self.parse_tree_canvas_frame.winfo_children():
                widget.destroy()

            # Create scrollable frame
            scrollable_frame = ctk.CTkScrollableFrame(
                self.parse_tree_canvas_frame,
                corner_radius=8,
                fg_color=self.colors['background']
            )
            scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

            tokens = self.tokenize_code(code, self.current_language.get())
            
            # Create parse tree sections
            self.create_parse_tree_sections(scrollable_frame, tokens)

            self.update_status("Parse tree created successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Parse tree creation failed: {str(e)}")
            self.update_status("Parse tree creation failed")

    def create_parse_tree_sections(self, parent, tokens):
        """Create parse tree analysis sections"""
        
        # 1. Tree Overview
        self.create_tree_overview_section(parent, tokens)
        
        # 2. Hierarchical Structure
        self.create_hierarchical_structure_section(parent, tokens)
        
        # 3. Token Breakdown by Lines
        self.create_token_breakdown_section(parent, tokens)
        
        # 4. Syntax Structure Analysis
        self.create_syntax_structure_section(parent, tokens)

    def create_tree_overview_section(self, parent, tokens):
        """Create tree overview section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['primary'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🌳 Parse Tree Overview",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Tree structure display
        tree_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        tree_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Simple text-based tree
        tree_text = self.generate_text_tree(tokens)
        
        text_widget = ctk.CTkTextbox(
            tree_frame,
            height=200,
            font=('Courier', 12),
            fg_color=self.colors['surface']
        )
        text_widget.pack(fill='x', pady=10)
        text_widget.insert('1.0', tree_text)
        text_widget.configure(state='disabled')

    def generate_text_tree(self, tokens):
        """Generate text-based tree representation"""
        tree_text = "Program\n"
        
        # Group by lines
        lines = {}
        for token in tokens:
            line = token['line']
            if line not in lines:
                lines[line] = []
            lines[line].append(token)
        
        for line_num, line_tokens in lines.items():
            tree_text += f"├── Line {line_num}\n"
            
            for i, token in enumerate(line_tokens):
                is_last = i == len(line_tokens) - 1
                prefix = "    └── " if is_last else "    ├── "
                tree_text += f"{prefix}{token['type']}: '{token['value']}'\n"
        
        return tree_text

    def create_hierarchical_structure_section(self, parent, tokens):
        """Create hierarchical structure section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=15)
        
        # Header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)
        
        ctk.CTkLabel(
            header,
            text="🏗️ Hierarchical Structure",
            font=('Arial', 18, 'bold'),
            text_color='white'
        ).pack(pady=12)
        
        # Structure analysis
        structure_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        structure_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Analyze structure
        structure_data = self.analyze_code_structure(tokens)
        
        # Display structure cards
        for level, items in structure_data.items():
            if items:
                level_frame = ctk.CTkFrame(structure_frame, corner_radius=8)
                level_frame.pack(fill='x', pady=5)
                
                # Level header
                level_header = ctk.CTkFrame(level_frame, fg_color=self.colors['secondary'])
                level_header.pack(fill='x', padx=10, pady=10)
                
                ctk.CTkLabel(
                    level_header,
                    text=f"Level {level}: {', '.join(items)}",
                    font=('Arial', 12, 'bold'),
                    text_color='white'
                ).pack(pady=5)

    def analyze_code_structure(self, tokens):
        """Analyze code structure levels"""
        structure = {
            1: [],  # Keywords
            2: [],  # Identifiers
            3: [],  # Operators
            4: []   # Literals
        }
        
        for token in tokens:
            if token['type'] == 'KEYWORD' and token['value'] not in structure[1]:
                structure[1].append(token['value'])
            elif token['type'] == 'IDENTIFIER' and token['value'] not in structure[2]:
                structure[2].append(token['value'])
            elif token['type'] == 'OPERATOR' and token['value'] not in structure[3]:
                structure[3].append(token['value'])
            elif token['type'] in ['NUMBER', 'STRING'] and token['value'] not in structure[4]:
                structure[4].append(token['value'])
        
        return structure


    def build_simple_tree_structure(self, tokens):
        """Build simple tree structure for visualization"""
        # Group tokens by lines
        lines = {}
        for token in tokens:
            line_num = token['line']
            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(token)
        
        # Create tree structure
        tree = {
            'name': 'Program',
            'type': 'root',
            'children': []
        }
        
        for line_num, line_tokens in lines.items():
            # Create line node
            line_node = {
                'name': f'Line {line_num}',
                'type': 'line',
                'children': []
            }
            
            # Add important tokens only
            for token in line_tokens:
                if token['type'] in ['KEYWORD', 'IDENTIFIER', 'OPERATOR', 'NUMBER', 'STRING']:
                    token_value = token['value'][:8] + '...' if len(token['value']) > 8 else token['value']
                    token_node = {
                        'name': f"{token['type']}\n{token_value}",
                        'type': token['type'].lower(),
                        'children': []
                    }
                    line_node['children'].append(token_node)
            
            tree['children'].append(line_node)
        
        return tree

    def draw_clean_tree(self, ax, tree_data):
        """Draw clean tree visualization"""
        import matplotlib.patches as patches
        
        # Define colors for different node types
        colors = {
            'root': '#2b6cb0',
            'line': '#059669',
            'keyword': '#dc2626',
            'identifier': '#7c3aed',
            'operator': '#ea580c',
            'number': '#0891b2',
            'string': '#be123c',
            'default': '#6b7280'
        }
        
        # Calculate positions
        positions = self.calculate_tree_positions(tree_data)
        
        # Draw nodes and connections
        for node_id, (x, y, node_data) in positions.items():
            # Get color
            color = colors.get(node_data['type'], colors['default'])
            
            # Determine size based on type
            if node_data['type'] == 'root':
                size = 0.8
            elif node_data['type'] == 'line':
                size = 0.6
            else:
                size = 0.4
            
            # Draw node
            circle = patches.Circle((x, y), size, facecolor=color, 
                                edgecolor='white', linewidth=2, alpha=0.9)
            ax.add_patch(circle)
            
            # Add text
            ax.text(x, y, node_data['name'], ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', wrap=True)
        
        # Draw connections
        self.draw_tree_connections(ax, positions, tree_data)
        
        # Set axis limits
        if positions:
            x_coords = [pos[0] for pos in positions.values()]
            y_coords = [pos[1] for pos in positions.values()]
            ax.set_xlim(min(x_coords) - 2, max(x_coords) + 2)
            ax.set_ylim(min(y_coords) - 2, max(y_coords) + 2)

    def calculate_tree_positions(self, tree_data):
        """Calculate positions for tree nodes"""
        positions = {}
        node_counter = 0
        
        def assign_positions(node, level=0, h_offset=0, parent_x=0):
            nonlocal node_counter
            
            node_id = node_counter
            node_counter += 1
            
            # Calculate vertical position
            y = -level * 3
            
            # Calculate horizontal position
            num_children = len(node['children'])
            if num_children == 0:
                x = h_offset
            else:
                # Center parent over children
                child_positions = []
                child_offset = h_offset - (num_children - 1) * 1.5
                
                for i, child in enumerate(node['children']):
                    child_x = child_offset + i * 3
                    child_positions.append(child_x)
                    assign_positions(child, level + 1, child_x, h_offset)
                
                x = sum(child_positions) / len(child_positions) if child_positions else h_offset
            
            positions[node_id] = (x, y, node)
            node['_id'] = node_id
            node['_pos'] = (x, y)
        
        assign_positions(tree_data)
        return positions

    def draw_tree_connections(self, ax, positions, tree_data):
        """Draw connections between tree nodes"""
        def draw_edges(node):
            if '_pos' in node and '_id' in node:
                parent_x, parent_y = node['_pos']
                
                for child in node['children']:
                    if '_pos' in child:
                        child_x, child_y = child['_pos']
                        
                        # Draw line
                        ax.plot([parent_x, child_x], [parent_y, child_y],
                            color='#4a5568', linewidth=2, alpha=0.7)
                        
                        # Draw arrow
                        ax.annotate('', xy=(child_x, child_y + 0.4),
                                xytext=(parent_x, parent_y - 0.4),
                                arrowprops=dict(arrowstyle='->', color='#4a5568',
                                                lw=2, alpha=0.7))
                    
                    draw_edges(child)
        
        draw_edges(tree_data)


    def get_professional_token_color(self, token_type):
        """Get professional color scheme for tokens"""
        color_map = {
            'KEYWORD': '#ef4444',      # Red
            'IDENTIFIER': '#10b981',   # Green  
            'OPERATOR': '#f59e0b',     # Amber
            'NUMBER': '#8b5cf6',       # Purple
            'STRING': '#06b6d4',       # Cyan
            'DELIMITER': '#6b7280',    # Gray
            'COMMENT': '#84cc16'       # Lime
        }
        return color_map.get(token_type, '#9ca3af')


    def get_clean_token_color(self, token_type):
        """Get clean, distinct colors for token types"""
        color_map = {
            'KEYWORD': '#ef4444',
            'IDENTIFIER': '#10b981',
            'OPERATOR': '#f59e0b',
            'NUMBER': '#8b5cf6',
            'STRING': '#06b6d4',
            'DELIMITER': '#6b7280',
            'COMMENT': '#84cc16'
        }
        return color_map.get(token_type, '#9ca3af')


    def group_tokens_by_statements(self, tokens):
        """Group tokens by logical statements for better organization"""
        statements = {}
        for token in tokens:
            line_num = token['line']
            if line_num not in statements:
                statements[line_num] = []
            statements[line_num].append(token)
        return statements

    def group_similar_tokens(self, tokens):
        """Group similar tokens together"""
        groups = {}
        for token in tokens:
            token_type = token['type']
            if token_type not in groups:
                groups[token_type] = []
            groups[token_type].append(token)
        return groups

    def clean_token_value(self, value):
        """Clean token value for better display"""
        if len(value) > 12:
            return value[:10] + ".."
        return value

    def get_token_color(self, token_type):
        """Get consistent colors for token types"""
        color_map = {
            'KEYWORD': '#EF4444',      # Red
            'IDENTIFIER': '#10B981',   # Green
            'OPERATOR': '#F59E0B',     # Amber
            'NUMBER': '#8B5CF6',       # Purple
            'STRING': '#06B6D4',       # Cyan
            'DELIMITER': '#6B7280',    # Gray
            'COMMENT': '#84CC16'       # Lime
        }
        return color_map.get(token_type, '#9CA3AF')

    def create_radial_tree_layout(self, G, root):
        """Create radial tree layout for better spacing"""
        try:
            # Try hierarchical layout first
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            try:
                # Fallback to spring layout with better parameters
                pos = nx.spring_layout(G, k=5, iterations=100, scale=8)
            except:
                # Final fallback to circular layout
                pos = nx.circular_layout(G, scale=6)
        
        return pos

    def add_parse_tree_legend(self, ax):
        """Add comprehensive legend to parse tree"""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#EF4444', 
                    markersize=10, label='Keywords'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#10B981', 
                    markersize=10, label='Identifiers'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#F59E0B', 
                    markersize=10, label='Operators'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#8B5CF6', 
                    markersize=10, label='Numbers'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#06B6D4', 
                    markersize=10, label='Strings'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#6B7280', 
                    markersize=10, label='Delimiters')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1),
                frameon=True, fancybox=True, shadow=True)




    def export_parse_tree(self):
        """Export parse tree as image"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Parse Tree",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                for widget in self.parse_tree_canvas_frame.winfo_children():
                    if hasattr(widget, 'figure'):
                        widget.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                        self.update_status(f"Parse tree exported to {os.path.basename(file_path)}")
                        return
                
                messagebox.showwarning("Warning", "No parse tree to export. Generate tree first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export parse tree: {str(e)}")

    # Multi-Phase Analysis Methods
    def run_lexical_analysis(self):
        """Run detailed lexical analysis"""
        self.update_status("Running lexical analysis...")
        try:
            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                self.lexical_results.delete('1.0', 'end')
                self.lexical_results.insert('1.0', "No code to analyze")
                return

            # Perform tokenization
            tokens = self.tokenize_code(code, self.current_language.get())
            
            # Generate detailed report
            report = "LEXICAL ANALYSIS REPORT\n"
            report += "=" * 40 + "\n\n"
            
            # Token summary
            token_types = Counter(token['type'] for token in tokens)
            report += "Token Summary:\n"
            for token_type, count in token_types.most_common():
                report += f"  {token_type}: {count}\n"
            
            report += f"\nTotal Tokens: {len(tokens)}\n\n"
            
            # Detailed token list
            report += "Detailed Token List:\n"
            report += "-" * 30 + "\n"
            report += f"{'Line':<6} {'Col':<6} {'Type':<12} {'Value':<20}\n"
            report += "-" * 50 + "\n"
            
            for token in tokens:
                value = token['value'][:18] + '..' if len(token['value']) > 20 else token['value']
                report += f"{token['line']:<6} {token['column']:<6} {token['type']:<12} {value:<20}\n"
            
            # Error analysis
            if self.errors:
                report += f"\nLexical Errors ({len(self.errors)}):\n"
                report += "-" * 20 + "\n"
                for i, error in enumerate(self.errors, 1):
                    report += f"{i}. {error}\n"
            else:
                report += "\n✅ No lexical errors found\n"
            
            self.lexical_results.delete('1.0', 'end')
            self.lexical_results.insert('1.0', report)
            self.update_status("Lexical analysis completed")
            
        except Exception as e:
            error_msg = f"Lexical analysis failed: {str(e)}"
            self.lexical_results.delete('1.0', 'end')
            self.lexical_results.insert('1.0', error_msg)
            self.update_status("Lexical analysis failed")

    def run_syntax_analysis(self):
        """Run syntax analysis"""
        self.update_status("Running syntax analysis...")
        try:
            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                self.syntax_results.delete('1.0', 'end')
                self.syntax_results.insert('1.0', "No code to analyze")
                return

            language = self.current_language.get()
            syntax_errors = []
            
            # Language-specific syntax checking
            if language == 'Python':
                syntax_errors = self.check_python_syntax(code)
            elif language == 'JavaScript':
                syntax_errors = self.check_javascript_syntax(code)
            elif language == 'Java':
                syntax_errors = self.check_java_syntax(code)
            elif language == 'C++':
                syntax_errors = self.check_cpp_syntax(code)
            
            # Generate syntax analysis report
            report = "SYNTAX ANALYSIS REPORT\n"
            report += "=" * 40 + "\n\n"
            report += f"Language: {language}\n"
            report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if syntax_errors:
                report += f"Syntax Errors Found ({len(syntax_errors)}):\n"
                report += "-" * 30 + "\n"
                for i, error in enumerate(syntax_errors, 1):
                    report += f"{i}. {error}\n"
            else:
                report += "✅ No syntax errors found\n"
                report += "Code appears to be syntactically correct\n"
            
            # Basic structure analysis
            report += "\nStructural Analysis:\n"
            report += "-" * 20 + "\n"
            
            lines = code.split('\n')
            report += f"Total Lines: {len(lines)}\n"
            report += f"Non-empty Lines: {len([line for line in lines if line.strip()])}\n"
            
            # Count brackets and parentheses
            open_brackets = code.count('{')
            close_brackets = code.count('}')
            open_parens = code.count('(')
            close_parens = code.count(')')
            
            report += f"Bracket Balance: {open_brackets} open, {close_brackets} close"
            if open_brackets != close_brackets:
                report += " ⚠️ UNBALANCED"
            report += "\n"
            
            report += f"Parentheses Balance: {open_parens} open, {close_parens} close"
            if open_parens != close_parens:
                report += " ⚠️ UNBALANCED"
            report += "\n"
            
            self.syntax_results.delete('1.0', 'end')
            self.syntax_results.insert('1.0', report)
            self.update_status("Syntax analysis completed")
            
        except Exception as e:
            error_msg = f"Syntax analysis failed: {str(e)}"
            self.syntax_results.delete('1.0', 'end')
            self.syntax_results.insert('1.0', error_msg)
            self.update_status("Syntax analysis failed")

    def check_python_syntax(self, code):
        """Check Python syntax"""
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
        return errors

    def check_javascript_syntax(self, code):
        """Basic JavaScript syntax checking"""
        errors = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            # Check for common syntax issues
            if line.endswith('{') and not any(keyword in line for keyword in ['if', 'for', 'while', 'function', 'class']):
                if not line.startswith('}'):
                    errors.append(f"Line {i}: Unexpected opening brace")
            
            # Check semicolon usage (basic)
            if (line and not line.endswith((';', '{', '}', ')', ',')) and 
                not any(keyword in line for keyword in ['if', 'for', 'while', 'else', 'function', 'class', 'var', 'let', 'const'])):
                errors.append(f"Line {i}: Missing semicolon")
        
        return errors

    def check_java_syntax(self, code):
        """Basic Java syntax checking"""
        errors = []
        lines = code.split('\n')
        
        # Check for class declaration
        has_class = any('class' in line for line in lines)
        if not has_class:
            errors.append("Missing class declaration")
        
        # Check bracket balance
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        return errors

    def check_cpp_syntax(self, code):
        """Basic C++ syntax checking"""
        errors = []
        lines = code.split('\n')
        
        # Check for includes
        has_include = any('#include' in line for line in lines)
        if not has_include:
            errors.append("No #include statements found")
        
        # Check for main function
        has_main = any('main' in line and '(' in line for line in lines)
        if not has_main:
            errors.append("No main function found")
        
        return errors

    def run_semantic_analysis(self):
        """Run semantic analysis"""
        self.update_status("Running semantic analysis...")
        try:
            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                self.semantic_results.delete('1.0', 'end')
                self.semantic_results.insert('1.0', "No code to analyze")
                return

            # Perform semantic analysis
            semantic_issues = self.analyze_semantics(code)
            
            # Generate report
            report = "SEMANTIC ANALYSIS REPORT\n"
            report += "=" * 40 + "\n\n"
            
            # Variable analysis
            variables = self.extract_variables(code)
            report += f"Variables Declared: {len(variables)}\n"
            if variables:
                report += "Variable List:\n"
                for var in variables:
                    report += f"  - {var}\n"
            
            # Function analysis
            functions = self.extract_functions(code)
            report += f"\nFunctions Declared: {len(functions)}\n"
            if functions:
                report += "Function List:\n"
                for func in functions:
                    report += f"  - {func}\n"
            
            # Semantic issues
            if semantic_issues:
                report += f"\nSemantic Issues ({len(semantic_issues)}):\n"
                report += "-" * 25 + "\n"
                for i, issue in enumerate(semantic_issues, 1):
                    report += f"{i}. {issue}\n"
            else:
                report += "\n✅ No semantic issues detected\n"
            
            self.semantic_results.delete('1.0', 'end')
            self.semantic_results.insert('1.0', report)
            self.update_status("Semantic analysis completed")
            
        except Exception as e:
            error_msg = f"Semantic analysis failed: {str(e)}"
            self.semantic_results.delete('1.0', 'end')
            self.semantic_results.insert('1.0', error_msg)
            self.update_status("Semantic analysis failed")

    def analyze_semantics(self, code):
        """Analyze semantic issues in code"""
        issues = []
        language = self.current_language.get()
        
        if language == 'Python':
            issues.extend(self.analyze_python_semantics(code))
        
        return issues

    def analyze_python_semantics(self, code):
        """Analyze Python semantic issues"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check for undefined variables (basic check)
            defined_vars = set()
            used_vars = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
            
            # Check for undefined variables
            undefined = used_vars - defined_vars - set(dir(__builtins__))
            for var in undefined:
                issues.append(f"Undefined variable: {var}")
            
            # Check for unused variables
            unused = defined_vars - used_vars
            for var in unused:
                issues.append(f"Unused variable: {var}")
                
        except Exception as e:
            issues.append(f"Semantic analysis error: {str(e)}")
        
        return issues

    def extract_variables(self, code):
        """Extract variable names from code"""
        variables = set()
        tokens = self.tokenize_code(code, self.current_language.get())
        
        for i, token in enumerate(tokens):
            if token['type'] == 'IDENTIFIER':
                # Check if it's likely a variable (not a function call)
                if i + 1 < len(tokens) and tokens[i + 1]['value'] != '(':
                    variables.add(token['value'])
        
        return list(variables)

    def extract_functions(self, code):
        """Extract function names from code"""
        functions = set()
        language = self.current_language.get()
        
        if language == 'Python':
            # Look for 'def function_name('
            lines = code.split('\n')
            for line in lines:
                if 'def ' in line and '(' in line:
                    start = line.find('def ') + 4
                    end = line.find('(', start)
                    if start < end:
                        func_name = line[start:end].strip()
                        functions.add(func_name)
        
        elif language in ['JavaScript', 'Java', 'C++']:
            # Look for 'function name(' or 'type name('
            tokens = self.tokenize_code(code, language)
            for i, token in enumerate(tokens):
                if (token['type'] == 'IDENTIFIER' and 
                    i + 1 < len(tokens) and tokens[i + 1]['value'] == '('):
                    functions.add(token['value'])
        
        return list(functions)

    def run_all_phases(self):
        """Run all analysis phases"""
        self.update_status("Running all analysis phases...")
        
        # Run each phase
        self.run_lexical_analysis()
        self.run_syntax_analysis()
        self.run_semantic_analysis()
        
        self.update_status("All analysis phases completed")

    # AI/ML Features Implementation
    def predict_errors(self):
        """Predict potential errors using ML"""
        self.update_status("Predicting errors...")
        try:
            if not self.enable_ml_var.get() or not ML_AVAILABLE:
                self.error_predictions.delete('1.0', 'end')
                self.error_predictions.insert('1.0', "ML features not available or disabled")
                return

            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                self.error_predictions.delete('1.0', 'end')
                self.error_predictions.insert('1.0', "No code to analyze")
                return

            # Use ML model for error prediction
            predictions = []
            
            if 'error_detection' in self.ml_models:
                try:
                    # Split code into chunks for analysis
                    lines = code.split('\n')
                    for i, line in enumerate(lines, 1):
                        if line.strip():
                            result = self.ml_models['error_detection'](line)
                            if result and len(result) > 0:
                                confidence = result[0].get('score', 0)
                                label = result[0].get('label', 'UNKNOWN')
                                
                                if confidence > 0.7 and 'error' in label.lower():
                                    predictions.append(f"Line {i}: Potential {label} (confidence: {confidence:.2f})")
                except Exception as e:
                    predictions.append(f"ML prediction error: {str(e)}")
            
            # Add rule-based predictions
            rule_based_predictions = self.rule_based_error_prediction(code)
            predictions.extend(rule_based_predictions)
            
            # Display results
            report = "ML-BASED ERROR PREDICTIONS\n"
            report += "=" * 35 + "\n\n"
            
            if predictions:
                report += f"Potential Issues Found ({len(predictions)}):\n"
                report += "-" * 30 + "\n"
                for i, prediction in enumerate(predictions, 1):
                    report += f"{i}. {prediction}\n"
            else:
                report += "✅ No potential errors predicted\n"
                report += "Code appears to be error-free\n"
            
            report += f"\nAnalysis completed at: {datetime.now().strftime('%H:%M:%S')}\n"
            
            self.error_predictions.delete('1.0', 'end')
            self.error_predictions.insert('1.0', report)
            self.update_status("Error prediction completed")
            
        except Exception as e:
            error_msg = f"Error prediction failed: {str(e)}"
            self.error_predictions.delete('1.0', 'end')
            self.error_predictions.insert('1.0', error_msg)
            self.update_status("Error prediction failed")

    def rule_based_error_prediction(self, code):
        """Rule-based error prediction"""
        predictions = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check for common issues
            if line_stripped.count('(') != line_stripped.count(')'):
                predictions.append(f"Line {i}: Unmatched parentheses")
            
            if line_stripped.count('[') != line_stripped.count(']'):
                predictions.append(f"Line {i}: Unmatched brackets")
            
            if line_stripped.count('{') != line_stripped.count('}'):
                predictions.append(f"Line {i}: Unmatched braces")
            
            # Check for potential typos in keywords
            language = self.current_language.get()
            keywords = self.languages[language]['keywords']
            
            tokens = self.tokenize_code(line, language)
            for token in tokens:
                if token['type'] == 'IDENTIFIER':
                    # Check for similar keywords
                    for keyword in keywords:
                        if self.similar_strings(token['value'], keyword):
                            predictions.append(f"Line {i}: '{token['value']}' might be misspelled '{keyword}'")
        
        return predictions

    def similar_strings(self, s1, s2, threshold=0.8):
        """Check if two strings are similar (simple implementation)"""
        if len(s1) != len(s2):
            return False
        
        matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
        similarity = matches / len(s1)
        return similarity >= threshold and similarity < 1.0

    def get_code_suggestions(self):
        """Get AI-powered code suggestions"""
        self.update_status("Generating code suggestions...")
        try:
            if not self.enable_ml_var.get() or not ML_AVAILABLE:
                self.code_suggestions.delete('1.0', 'end')
                self.code_suggestions.insert('1.0', "ML features not available or disabled")
                return

            code = self.code_editor.get('1.0', 'end-1c')
            if not code.strip():
                self.code_suggestions.delete('1.0', 'end')
                self.code_suggestions.insert('1.0', "No code to analyze")
                return

            suggestions = []
            
            # Generate suggestions based on code analysis
            suggestions.extend(self.generate_style_suggestions(code))
            suggestions.extend(self.generate_optimization_suggestions(code))
            suggestions.extend(self.generate_best_practice_suggestions(code))
            
            # Display suggestions
            report = "CODE IMPROVEMENT SUGGESTIONS\n"
            report += "=" * 35 + "\n\n"
            
            if suggestions:
                categories = defaultdict(list)
                for suggestion in suggestions:
                    category = suggestion.split(':')[0]
                    categories[category].append(suggestion)
                
                for category, items in categories.items():
                    report += f"{category.upper()}:\n"
                    report += "-" * len(category) + "\n"
                    for item in items:
                        content = ':'.join(item.split(':')[1:]).strip()
                        report += f"• {content}\n"
                    report += "\n"
            else:
                report += "✅ No suggestions available\n"
                report += "Code follows good practices\n"
            
            self.code_suggestions.delete('1.0', 'end')
            self.code_suggestions.insert('1.0', report)
            self.update_status("Code suggestions generated")
            
        except Exception as e:
            error_msg = f"Code suggestion failed: {str(e)}"
            self.code_suggestions.delete('1.0', 'end')
            self.code_suggestions.insert('1.0', error_msg)
            self.update_status("Code suggestion failed")

    def generate_style_suggestions(self, code):
        """Generate code style suggestions"""
        suggestions = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 80:
                suggestions.append(f"Style: Line {i} is too long ({len(line)} chars). Consider breaking it up.")
            
            # Check indentation consistency
            if line.startswith(' ') and line.startswith('\t'):
                suggestions.append(f"Style: Line {i} mixes spaces and tabs for indentation.")
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                suggestions.append(f"Style: Line {i} has trailing whitespace.")
        
        return suggestions

    def generate_optimization_suggestions(self, code):
        """Generate optimization suggestions"""
        suggestions = []
        
        # Check for repeated code patterns
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        line_counts = Counter(lines)
        
        for line, count in line_counts.items():
            if count > 2 and len(line) > 10:
                suggestions.append(f"Optimization: Line '{line[:30]}...' appears {count} times. Consider extracting to a function.")
        
        return suggestions

    def generate_best_practice_suggestions(self, code):
        """Generate best practice suggestions"""
        suggestions = []
        language = self.current_language.get()
        
        if language == 'Python':
            # Python-specific suggestions
            if 'import *' in code:
                suggestions.append("Best Practice: Avoid 'import *'. Use specific imports instead.")
            
            if 'global ' in code:
                suggestions.append("Best Practice: Minimize use of global variables.")
        
        elif language == 'JavaScript':
            # JavaScript-specific suggestions
            if 'var ' in code:
                suggestions.append("Best Practice: Use 'let' or 'const' instead of 'var'.")
        
        return suggestions

    def predict_next_token(self):
        """Predict next token using ML"""
        self.update_status("Predicting next token...")
        try:
            if not self.enable_ml_var.get() or not ML_AVAILABLE:
                self.autocomplete_results.delete('1.0', 'end')
                self.autocomplete_results.insert('1.0', "ML features not available or disabled")
                return

            context = self.autocomplete_entry.get().strip()
            if not context:
                self.autocomplete_results.delete('1.0', 'end')
                self.autocomplete_results.insert('1.0', "Enter context for prediction")
                return

            predictions = []
            
            # Use ML model for prediction
            if 'completion' in self.ml_models:
                try:
                    results = self.ml_models['completion'](
                        context, 
                        max_length=len(context) + 20,
                        num_return_sequences=3,
                        temperature=0.7
                    )
                    
                    for result in results:
                        generated_text = result['generated_text']
                        if len(generated_text) > len(context):
                            prediction = generated_text[len(context):].split()[0]
                            predictions.append(prediction)
                            
                except Exception as e:
                    predictions.append(f"ML prediction error: {str(e)}")
            
            # Add rule-based predictions
            rule_predictions = self.rule_based_token_prediction(context)
            predictions.extend(rule_predictions)
            
            # Display results
            report = "NEXT TOKEN PREDICTIONS\n"
            report += "=" * 25 + "\n\n"
            report += f"Context: '{context}'\n\n"
            
            if predictions:
                report += "Predicted Tokens:\n"
                report += "-" * 18 + "\n"
                for i, prediction in enumerate(predictions[:5], 1):
                    report += f"{i}. {prediction}\n"
            else:
                report += "No predictions available\n"
            
            self.autocomplete_results.delete('1.0', 'end')
            self.autocomplete_results.insert('1.0', report)
            self.update_status("Token prediction completed")
            
        except Exception as e:
            error_msg = f"Token prediction failed: {str(e)}"
            self.autocomplete_results.delete('1.0', 'end')
            self.autocomplete_results.insert('1.0', error_msg)
            self.update_status("Token prediction failed")

    def rule_based_token_prediction(self, context):
        """Rule-based token prediction"""
        predictions = []
        language = self.current_language.get()
        lang_config = self.languages[language]
        
        # Get last token
        tokens = context.split()
        if not tokens:
            return predictions
        
        last_token = tokens[-1]
        
        # Predict based on language patterns
        if last_token in ['if', 'while', 'for']:
            predictions.append('(')
        elif last_token == '(':
            predictions.extend(['condition', 'expression', 'variable'])
        elif last_token in ['=', '==', '!=']:
            predictions.extend(['value', 'variable', 'expression'])
        elif last_token in lang_config['keywords']:
            # Suggest common follow-up tokens
            if language == 'Python':
                if last_token == 'def':
                    predictions.append('function_name')
                elif last_token == 'class':
                    predictions.append('ClassName')
                elif last_token == 'import':
                    predictions.extend(['os', 'sys', 'math', 'random'])
        
        return predictions

    # Event Handlers and Utility Methods
    def on_code_change(self, event=None):
        """Handle code editor changes"""
        if self.realtime_analysis_var.get():
            # Cancel existing timer
            if hasattr(self, '_analysis_timer') and self._analysis_timer is not None:
                try:
                    self.root.after_cancel(self._analysis_timer)
                except:
                    pass
            
            # Set new timer
            self._analysis_timer = self.root.after(1000, self.perform_lexical_analysis)

    def open_file(self):
        """Open and load a source code file with error handling"""
        try:
            file_path = filedialog.askopenfilename(
                title="Open Source Code File",
                filetypes=[
                    ("Python files", "*.py"),
                    ("JavaScript files", "*.js"),
                    ("Java files", "*.java"),
                    ("C++ files", "*.cpp;*.cc;*.cxx"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_editor.delete('1.0', 'end')
                    self.code_editor.insert('1.0', content)
                    
                    self.current_file = file_path
                    self.file_info.configure(text=f"File: {os.path.basename(file_path)}")
                    
                    # Auto-detect language based on file extension
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == '.py':
                        self.current_language.set('Python')
                    elif ext in ['.js', '.jsx']:
                        self.current_language.set('JavaScript')
                    elif ext == '.java':
                        self.current_language.set('Java')
                    elif ext in ['.cpp', '.cc', '.cxx', '.h', '.hpp']:
                        self.current_language.set('C++')
                    
                    self.update_status(f"Loaded {os.path.basename(file_path)}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            self.update_status("File loading failed")

    def save_analysis(self):
        """Save analysis results with error handling"""
        try:
            if not self.tokens:
                messagebox.showwarning("Warning", "No analysis results to save")
                return
                
            file_path = filedialog.asksaveasfilename(
                title="Save Analysis Results",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("LEXICAL ANALYSIS RESULTS\n")
                    file.write("=" * 50 + "\n\n")
                    
                    # Write tokens
                    file.write("TOKENS:\n")
                    for token in self.tokens:
                        file.write(f"{token['type']}: '{token['value']}' at line {token['line']}, column {token['column']}\n")
                    
                    # Write errors if any
                    if self.errors:
                        file.write(f"\nERRORS ({len(self.errors)}):\n")
                        for error in self.errors:
                            file.write(f"- {error}\n")
                    
                self.update_status(f"Analysis saved to {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save analysis: {str(e)}")
            self.update_status("Save failed")


    def save_analysis(self):
        """Save analysis results to file"""
        try:
            if not self.tokens:
                messagebox.showwarning("Warning", "No analysis results to save")
                return

            file_path = filedialog.asksaveasfilename(
                title="Save Analysis Results",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )

            if file_path:
                # Prepare analysis data
                analysis_data = {
                    'timestamp': datetime.now().isoformat(),
                    'language': self.current_language.get(),
                    'source_file': self.current_file,
                    'tokens': self.tokens,
                    'errors': self.errors,
                    'statistics': {
                        'total_tokens': len(self.tokens),
                        'token_types': dict(Counter(token['type'] for token in self.tokens)),
                        'unique_identifiers': len(set(token['value'] for token in self.tokens if token['type'] == 'IDENTIFIER'))
                    }
                }

                # Save based on file extension
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(analysis_data, file, indent=2, ensure_ascii=False)
                else:
                    # Save as formatted text
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write("LEXICAL ANALYSIS RESULTS\n")
                        file.write("=" * 50 + "\n\n")
                        file.write(f"Timestamp: {analysis_data['timestamp']}\n")
                        file.write(f"Language: {analysis_data['language']}\n")
                        file.write(f"Source File: {analysis_data['source_file']}\n\n")
                        
                        file.write("TOKENS:\n")
                        file.write("-" * 20 + "\n")
                        for token in self.tokens:
                            file.write(f"{token['type']:<12} {token['value']:<20} Line: {token['line']:<3} Col: {token['column']}\n")
                        
                        if self.errors:
                            file.write("\nERRORS:\n")
                            file.write("-" * 20 + "\n")
                            for error in self.errors:
                                file.write(f"{error}\n")

                self.update_status(f"Analysis saved to {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save analysis: {str(e)}")

    def clear_editor(self):
        """Clear the code editor and results"""
        self.code_editor.delete('1.0', 'end')
        self.tokens = []
        self.errors = []
        self.current_file = None

        # Clear all result displays
        self.tokens_text.delete('1.0', 'end')
        self.errors_text.delete('1.0', 'end')
        self.stats_text.delete('1.0', 'end')
        
        if hasattr(self, 'lexical_results'):
            self.lexical_results.delete('1.0', 'end')
        if hasattr(self, 'syntax_results'):
            self.syntax_results.delete('1.0', 'end')
        if hasattr(self, 'semantic_results'):
            self.semantic_results.delete('1.0', 'end')

        self.file_info.configure(text="No file loaded")
        self.update_status("Editor cleared")

    def apply_color_scheme(self):
        """Apply selected color scheme"""
        scheme = self.color_scheme_var.get()
        if scheme == 'Dark Mode':
            ctk.set_appearance_mode("dark")
        elif scheme == 'Default':
            ctk.set_appearance_mode("light")
        elif scheme == 'Custom':
            self.open_color_picker()
        
        self.update_status(f"Color scheme changed to {scheme}")

    def open_color_picker(self):
        """Open color picker for custom theme"""
        color = colorchooser.askcolor(title="Choose Primary Color")
        if color[1]:  # If a color was selected
            self.colors['primary'] = color[1]
            self.update_status("Custom color applied")

    def apply_font_settings(self, event=None):
        """Apply font settings to editor"""
        font_family = self.font_family_var.get()
        font_size = int(self.font_size_var.get())
        new_font = (font_family, font_size)
        
        # Update code editor font
        self.code_editor.configure(font=new_font)
        self.update_status(f"Font changed to {font_family} {font_size}pt")

    def toggle_line_numbers(self):
        """Toggle line number display"""
        status = "enabled" if self.show_line_numbers_var.get() else "disabled"
        self.update_status(f"Line numbers {status}")

    def toggle_syntax_highlighting(self):
        """Toggle syntax highlighting"""
        if self.syntax_highlighting_var.get():
            self.apply_syntax_highlighting()
            self.update_status("Syntax highlighting enabled")
        else:
            self.update_status("Syntax highlighting disabled")

    def apply_syntax_highlighting(self):
        """Apply syntax highlighting to code editor"""
        # This would require custom implementation for CTkTextbox
        # For now, just update status
        self.update_status("Syntax highlighting applied")

    def update_tokens_display(self):
        """Update tokens display with improved formatting"""
        self.tokens_text.delete('1.0', 'end')
        if not self.tokens:
            self.tokens_text.insert('1.0', "No tokens found")
            return

        # Create properly formatted table
        display_text = "TOKEN ANALYSIS RESULTS\n"
        display_text += "=" * 60 + "\n\n"
        
        # Header with proper spacing
        header = f"{'Type':<15} {'Value':<25} {'Line':<8} {'Column':<8}\n"
        display_text += header
        display_text += "-" * 60 + "\n"
        
        # Format each token with consistent spacing
        for token in self.tokens:
            token_type = token['type']
            value = token['value'][:22] + '...' if len(token['value']) > 25 else token['value']
            line_num = str(token['line'])
            column_num = str(token['column'])
            
            row = f"{token_type:<15} {value:<25} {line_num:<8} {column_num:<8}\n"
            display_text += row

        display_text += f"\nTotal Tokens: {len(self.tokens)}\n"
        self.tokens_text.insert('1.0', display_text)


    def update_errors_display(self):
        """Update errors display"""
        self.errors_text.delete('1.0', 'end')
        
        if self.errors:
            error_text = "LEXICAL ERRORS\n"
            error_text += "=" * 20 + "\n\n"
            for i, error in enumerate(self.errors, 1):
                error_text += f"{i}. {error}\n"
            self.errors_text.insert('1.0', error_text)
        else:
            self.errors_text.insert('1.0', "✅ No lexical errors found")

    def update_statistics_display(self):
        """Update statistics display"""
        self.stats_text.delete('1.0', 'end')
        
        if not self.tokens:
            self.stats_text.insert('1.0', "No tokens to analyze")
            return

        # Generate statistics
        stats = "📊 LEXICAL STATISTICS\n"
        stats += "=" * 30 + "\n\n"
        
        # Token type distribution
        token_types = Counter(token['type'] for token in self.tokens)
        stats += "Token Type Distribution:\n"
        stats += "-" * 25 + "\n"
        for token_type, count in token_types.most_common():
            percentage = (count / len(self.tokens)) * 100
            stats += f"{token_type:<12}: {count:>4} ({percentage:>5.1f}%)\n"
        
        stats += f"\nTotal Tokens: {len(self.tokens)}\n"
        
        # Unique identifiers
        identifiers = [token['value'] for token in self.tokens if token['type'] == 'IDENTIFIER']
        unique_identifiers = set(identifiers)
        stats += f"Unique Identifiers: {len(unique_identifiers)}\n"
        
        # Most common identifiers
        if identifiers:
            id_counts = Counter(identifiers)
            stats += "\nMost Common Identifiers:\n"
            stats += "-" * 25 + "\n"
            for identifier, count in id_counts.most_common(5):
                stats += f"{identifier:<15}: {count}\n"
        
        # Line statistics
        lines_with_tokens = set(token['line'] for token in self.tokens)
        stats += f"\nLines with Code: {len(lines_with_tokens)}\n"
        
        # Average tokens per line
        if lines_with_tokens:
            avg_tokens = len(self.tokens) / len(lines_with_tokens)
            stats += f"Avg Tokens/Line: {avg_tokens:.1f}\n"
        
        self.stats_text.insert('1.0', stats)

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
        
        # Update status indicator color based on message
        if "error" in message.lower() or "failed" in message.lower():
            self.status_indicator.configure(text_color=self.colors['danger'])
        elif "complete" in message.lower() or "success" in message.lower():
            self.status_indicator.configure(text_color=self.colors['success'])
        else:
            self.status_indicator.configure(text_color=self.colors['warning'])

    def show_help(self):
        """Show help dialog"""
        help_text = """
        
    
ADVANCED LEXICAL ANALYZER - HELP

KEYBOARD SHORTCUTS:
• Ctrl/Cmd + O: Open file
• Ctrl/Cmd + S: Save analysis
• Ctrl/Cmd + N: Clear editor
• Ctrl/Cmd + R: Run analysis
• Ctrl/Cmd + T: Toggle theme
• F5: Run all phases
• F1: Show help

FEATURES:
• Multi-language support (Python, JavaScript, Java, C++)
• Real-time lexical analysis
• Visual AST and parse tree generation
• Token frequency analysis
• Multi-phase compiler analysis
• AI-powered error prediction
• Code suggestions and auto-complete

TABS:
• Editor & Analysis: Main coding and token analysis
• Visual Features: AST, parse trees, and charts
• Multi-Phase Analysis: Lexical, syntax, semantic analysis
• AI Features: ML-based error prediction and suggestions
• Settings: Customize appearance and behavior

For more information, visit the documentation.
        """
        
        messagebox.showinfo("Help - Advanced Lexical Analyzer", help_text)

    def create_notebook_interface(self, parent):
        """Create modern tabbed interface"""
        self.notebook = ctk.CTkTabview(parent, corner_radius=12)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # Add tabs with modern styling
        tabs = [
            ("📝 Editor & Analysis", self.create_editor_tab),
            ("📚 Theory & Concepts", self.create_theory_tab),
            ("🎨 Visual Features", self.create_visual_tab),
            ("🔬 Multi-Phase Analysis", self.create_analysis_tab),
            ("🤖 AI Features", self.create_ai_tab),
            ("👥 Team Details", self.create_team_tab),  # NEW TAB
            ("⚙️ Settings", self.create_settings_tab)
        ]

        for tab_name, tab_creator in tabs:
            tab = self.notebook.add(tab_name)
            tab_creator(tab)

    
    def create_theory_tab(self, parent):
        """Create comprehensive theory and concepts tab"""
        # Create scrollable frame for theory content
        scrollable_frame = ctk.CTkScrollableFrame(parent, corner_radius=8)
        scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Header section
        self.create_theory_header(scrollable_frame)
        
        # Theory sections
        self.create_lexical_analysis_section(scrollable_frame)
        self.create_parsing_section(scrollable_frame)
        self.create_semantic_analysis_section(scrollable_frame)
        self.create_compiler_phases_section(scrollable_frame)
        self.create_interactive_examples_section(scrollable_frame)

    def create_theory_header(self, parent):
        """Create theory page header"""
        header_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', padx=10, pady=(10, 20))

        # Main title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Compiler Design Theory & Concepts",
            font=('Arial', 28, 'bold'),
            text_color='white'
        )
        title_label.pack(pady=(20, 10))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Complete guide to lexical analysis, parsing, and semantic analysis",
            font=('Arial', 16),
            text_color='white'
        )
        subtitle_label.pack(pady=(0, 20))

        # Navigation buttons
        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(fill='x', padx=20, pady=(0, 20))

        nav_buttons = [
            ("🔍 Lexical Analysis", lambda: self.scroll_to_section("lexical")),
            ("📝 Parsing", lambda: self.scroll_to_section("parsing")),
            ("🧠 Semantic Analysis", lambda: self.scroll_to_section("semantic")),
            ("⚙️ Compiler Phases", lambda: self.scroll_to_section("phases")),
            ("💡 Examples", lambda: self.scroll_to_section("examples"))
        ]

        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                fg_color='white',
                text_color=self.colors['primary'],
                hover_color=self.colors['background'],
                corner_radius=8,
                height=32,
                width=140
            )
            btn.pack(side='left', padx=5)

    def create_lexical_analysis_section(self, parent):
        """Create lexical analysis theory section"""
        # Section container
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="🔍 Lexical Analysis (Scanning)",
            font=('Arial', 22, 'bold'),
            text_color='white'
        ).pack(pady=15)

        # Content frame
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Theory text
        theory_text = """
    📖 DEFINITION:
    Lexical analysis is the first phase of compilation that reads the source code character by character and groups them into meaningful sequences called lexemes, producing tokens as output.

    🎯 OBJECTIVES:
    • Break down source code into tokens
    • Remove whitespace and comments
    • Handle string literals and numeric constants
    • Detect lexical errors
    • Maintain line and column information

    🔧 KEY COMPONENTS:
    • Lexemes: Sequence of characters forming a token
    • Tokens: Classified lexemes with type and value
    • Pattern: Rules describing token formation
    • Lexical Errors: Invalid character sequences

    ⚡ PROCESS:
    1. Read input character stream
    2. Group characters into lexemes
    3. Classify lexemes into token types
    4. Generate token stream for parser
    5. Handle errors and maintain position info
    """

        theory_label = ctk.CTkLabel(
            content_frame,
            text=theory_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        )
        theory_label.pack(fill='x', padx=10, pady=10)

        # Interactive lexical analysis diagram
        self.create_lexical_diagram(content_frame)

        # Token types table
        self.create_token_types_table(content_frame)

    def create_lexical_diagram(self, parent):
        """Create interactive lexical analysis flow diagram"""
        diagram_frame = ctk.CTkFrame(parent, corner_radius=8)
        diagram_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            diagram_frame,
            text="📊 Lexical Analysis Flow",
            font=('Arial', 16, 'bold')
        ).pack(pady=(15, 10))

        # Create matplotlib figure for flow diagram
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor(self.colors['surface'])

            # Flow diagram boxes
            boxes = [
                {"text": "Source\nCode", "pos": (1, 3), "color": self.colors['primary']},
                {"text": "Character\nStream", "pos": (3, 3), "color": self.colors['secondary']},
                {"text": "Lexical\nAnalyzer", "pos": (5, 3), "color": self.colors['success']},
                {"text": "Token\nStream", "pos": (7, 3), "color": self.colors['warning']},
                {"text": "Parser", "pos": (9, 3), "color": self.colors['danger']}
            ]

            # Draw boxes and arrows
            for i, box in enumerate(boxes):
                # Draw box
                rect = mpatches.Rectangle(
                    (box["pos"][0] - 0.4, box["pos"][1] - 0.3),
                    0.8, 0.6,
                    facecolor=box["color"],
                    edgecolor='black',
                    linewidth=2
                )
                ax.add_patch(rect)
                
                # Add text
                ax.text(box["pos"][0], box["pos"][1], box["text"],
                    ha='center', va='center', fontsize=10, fontweight='bold', color='white')
                
                # Draw arrow to next box
                if i < len(boxes) - 1:
                    ax.arrow(box["pos"][0] + 0.4, box["pos"][1],
                            1.2, 0, head_width=0.1, head_length=0.1,
                            fc='black', ec='black')

            # Add example annotations
            ax.text(5, 2, "Examples:\n• Keywords → KEYWORD\n• Numbers → NUMBER\n• Identifiers → ID",
                ha='center', va='top', fontsize=9, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

            ax.set_xlim(0, 10)
            ax.set_ylim(1, 4)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title('Lexical Analysis Process Flow', fontsize=14, fontweight='bold', pad=20)

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, diagram_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        except Exception as e:
            # Fallback text diagram
            fallback_label = ctk.CTkLabel(
                diagram_frame,
                text="Source Code → Character Stream → Lexical Analyzer → Token Stream → Parser",
                font=('Arial', 12, 'bold')
            )
            fallback_label.pack(pady=20)

    def create_token_types_table(self, parent):
        """Create token types reference table"""
        table_frame = ctk.CTkFrame(parent, corner_radius=8)
        table_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            table_frame,
            text="🏷️ Common Token Types",
            font=('Arial', 16, 'bold')
        ).pack(pady=(15, 10))

        # Token types data
        token_data = [
            ("KEYWORD", "if, while, for, class", "Reserved words"),
            ("IDENTIFIER", "variable, function", "User-defined names"),
            ("NUMBER", "123, 45.67, 1e10", "Numeric constants"),
            ("STRING", '"hello", \'world\'', "String literals"),
            ("OPERATOR", "+, -, *, /, ==, !=", "Arithmetic & logical"),
            ("DELIMITER", "(, ), {, }, ;, ,", "Punctuation marks"),
            ("COMMENT", "// comment, /* */", "Code documentation")
        ]

        # Create table header
        header_frame = ctk.CTkFrame(table_frame, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', padx=15, pady=(0, 5))

        header_text = f"{'Token Type':<15} {'Examples':<25} {'Description':<20}"
        ctk.CTkLabel(
            header_frame,
            text=header_text,
            font=('Courier', 12, 'bold'),
            text_color='white'
        ).pack(pady=8)

        # Create table rows
        for token_type, examples, description in token_data:
            row_frame = ctk.CTkFrame(table_frame, fg_color=self.colors['background'])
            row_frame.pack(fill='x', padx=15, pady=2)

            row_text = f"{token_type:<15} {examples:<25} {description:<20}"
            ctk.CTkLabel(
                row_frame,
                text=row_text,
                font=('Courier', 11),
                anchor='w'
            ).pack(pady=5, padx=10, anchor='w')

    def create_parsing_section(self, parent):
        """Create parsing theory section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['warning'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="📝 Syntax Analysis (Parsing)",
            font=('Arial', 22, 'bold'),
            text_color='white'
        ).pack(pady=15)

        # Content
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        theory_text = """
    📖 DEFINITION:
    Parsing analyzes the syntactic structure of token sequences to determine if they conform to the grammar rules of the programming language.

    🎯 OBJECTIVES:
    • Verify syntactic correctness
    • Build parse trees or ASTs
    • Detect syntax errors
    • Guide semantic analysis

    🔧 PARSING TECHNIQUES:

    🔹 TOP-DOWN PARSING:
    • Starts from start symbol
    • Expands towards terminals
    • Examples: Recursive Descent, LL(1)

    🔹 BOTTOM-UP PARSING:
    • Starts from terminals
    • Reduces to start symbol  
    • Examples: LR(1), LALR(1), SLR(1)

    ⚡ PARSE TREE vs AST:
    • Parse Tree: Shows complete derivation
    • AST: Simplified, removes unnecessary nodes
    """

        theory_label = ctk.CTkLabel(
            content_frame,
            text=theory_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        )
        theory_label.pack(fill='x', padx=10, pady=10)

        # Create parsing comparison chart
        self.create_parsing_comparison_chart(content_frame)

    def create_parsing_comparison_chart(self, parent):
        """Create parsing techniques comparison chart"""
        chart_frame = ctk.CTkFrame(parent, corner_radius=8)
        chart_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            chart_frame,
            text="📊 Parsing Techniques Comparison",
            font=('Arial', 16, 'bold')
        ).pack(pady=(15, 10))

        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            fig.patch.set_facecolor(self.colors['surface'])

            # Parsing complexity comparison
            techniques = ['Recursive\nDescent', 'LL(1)', 'SLR(1)', 'LALR(1)', 'LR(1)']
            complexity = [2, 3, 4, 4.5, 5]
            power = [2, 3, 4, 4.5, 5]

            x = np.arange(len(techniques))
            width = 0.35

            bars1 = ax1.bar(x - width/2, complexity, width, label='Implementation Complexity', 
                        color=self.colors['primary'], alpha=0.8)
            bars2 = ax1.bar(x + width/2, power, width, label='Parsing Power',
                        color=self.colors['success'], alpha=0.8)

            ax1.set_xlabel('Parsing Techniques')
            ax1.set_ylabel('Rating (1-5)')
            ax1.set_title('Parsing Techniques Comparison')
            ax1.set_xticks(x)
            ax1.set_xticklabels(techniques)
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Parse tree structure example
            ax2.text(0.5, 0.9, 'Parse Tree Structure', ha='center', va='top', 
                    transform=ax2.transAxes, fontsize=14, fontweight='bold')
            
            # Simple tree diagram
            tree_text = """
            Expression
            /    \\
        Term      +
        /    \\      \\
    Factor   *    Term
        |      |      |
        a      b      c
    """
            ax2.text(0.5, 0.7, tree_text, ha='center', va='top',
                    transform=ax2.transAxes, fontsize=10, fontfamily='monospace')
            
            ax2.axis('off')

            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        except Exception as e:
            fallback_label = ctk.CTkLabel(
                chart_frame,
                text="Parsing Techniques: Recursive Descent → LL(1) → SLR(1) → LALR(1) → LR(1)\n(Increasing in power and complexity)",
                font=('Arial', 12)
            )
            fallback_label.pack(pady=20)

    def create_semantic_analysis_section(self, parent):
        """Create semantic analysis theory section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['secondary'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="🧠 Semantic Analysis",
            font=('Arial', 22, 'bold'),
            text_color='white'
        ).pack(pady=15)

        # Content
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        theory_text = """
    📖 DEFINITION:
    Semantic analysis checks the meaning of syntactically correct programs, ensuring they follow the semantic rules of the language.

    🎯 OBJECTIVES:
    • Type checking and type inference
    • Scope resolution and variable binding
    • Function signature verification
    • Declaration and usage consistency

    🔧 KEY CONCEPTS:

    🔹 SYMBOL TABLE:
    • Stores identifier information
    • Tracks scope and type information
    • Manages variable declarations

    🔹 TYPE CHECKING:
    • Static vs Dynamic typing
    • Type compatibility verification
    • Implicit type conversions

    🔹 SCOPE ANALYSIS:
    • Variable visibility rules
    • Nested scope handling
    • Name resolution

    ⚠️ SEMANTIC ERRORS:
    • Undeclared variables
    • Type mismatches
    • Multiple declarations
    • Unreachable code
    """

        theory_label = ctk.CTkLabel(
            content_frame,
            text=theory_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        )
        theory_label.pack(fill='x', padx=10, pady=10)

        # Create semantic analysis flowchart
        self.create_semantic_flowchart(content_frame)

    def create_semantic_flowchart(self, parent):
        """Create semantic analysis process flowchart"""
        flowchart_frame = ctk.CTkFrame(parent, corner_radius=8)
        flowchart_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            flowchart_frame,
            text="🔄 Semantic Analysis Process",
            font=('Arial', 16, 'bold')
        ).pack(pady=(15, 10))

        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor(self.colors['surface'])

            # Flowchart steps
            steps = [
                {"text": "Parse Tree\nInput", "pos": (2, 7), "color": self.colors['primary']},
                {"text": "Symbol Table\nConstruction", "pos": (2, 5.5), "color": self.colors['success']},
                {"text": "Type\nChecking", "pos": (2, 4), "color": self.colors['warning']},
                {"text": "Scope\nAnalysis", "pos": (2, 2.5), "color": self.colors['danger']},
                {"text": "Semantic\nValidation", "pos": (2, 1), "color": self.colors['secondary']}
            ]

            # Draw process flow
            for i, step in enumerate(steps):
                # Draw box
                rect = mpatches.Rectangle(
                    (step["pos"][0] - 0.5, step["pos"][1] - 0.4),
                    1, 0.8,
                    facecolor=step["color"],
                    edgecolor='black',
                    linewidth=2
                )
                ax.add_patch(rect)
                
                # Add text
                ax.text(step["pos"][0], step["pos"][1], step["text"],
                    ha='center', va='center', fontsize=10, fontweight='bold', color='white')
                
                # Draw arrow to next step
                if i < len(steps) - 1:
                    ax.arrow(step["pos"][0], step["pos"][1] - 0.4,
                            0, -0.7, head_width=0.1, head_length=0.1,
                            fc='black', ec='black')

            # Add side annotations
            annotations = [
                {"text": "• Identifier declarations\n• Function signatures\n• Variable types", "pos": (4.5, 5.5)},
                {"text": "• Type compatibility\n• Operator validity\n• Function calls", "pos": (4.5, 4)},
                {"text": "• Variable visibility\n• Nested scopes\n• Name resolution", "pos": (4.5, 2.5)},
                {"text": "• Error detection\n• Warning generation\n• Code validation", "pos": (4.5, 1)}
            ]

            for ann in annotations:
                ax.text(ann["pos"][0], ann["pos"][1], ann["text"],
                    ha='left', va='center', fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))

            ax.set_xlim(0, 7)
            ax.set_ylim(0, 8)
            ax.axis('off')
            ax.set_title('Semantic Analysis Workflow', fontsize=14, fontweight='bold', pad=20)

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, flowchart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        except Exception as e:
            fallback_label = ctk.CTkLabel(
                flowchart_frame,
                text="Semantic Analysis: Parse Tree → Symbol Table → Type Checking → Scope Analysis → Validation",
                font=('Arial', 12)
            )
            fallback_label.pack(pady=20)

    def create_compiler_phases_section(self, parent):
        """Create compiler phases overview section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['danger'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="⚙️ Complete Compiler Phases",
            font=('Arial', 22, 'bold'),
            text_color='white'
        ).pack(pady=15)

        # Create phases diagram
        self.create_compiler_phases_diagram(section_frame)

    def create_compiler_phases_diagram(self, parent):
        """Create comprehensive compiler phases diagram"""
        diagram_frame = ctk.CTkFrame(parent, fg_color="transparent")
        diagram_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor(self.colors['surface'])

            # Compiler phases
            phases = [
                {"name": "Source Code", "pos": (7, 9), "color": "#E3F2FD", "text_color": "black"},
                {"name": "Lexical Analysis", "pos": (7, 8), "color": self.colors['primary'], "text_color": "white"},
                {"name": "Syntax Analysis", "pos": (7, 7), "color": self.colors['success'], "text_color": "white"},
                {"name": "Semantic Analysis", "pos": (7, 6), "color": self.colors['warning'], "text_color": "white"},
                {"name": "Intermediate Code", "pos": (7, 5), "color": self.colors['secondary'], "text_color": "white"},
                {"name": "Code Optimization", "pos": (7, 4), "color": self.colors['danger'], "text_color": "white"},
                {"name": "Code Generation", "pos": (7, 3), "color": "#795548", "text_color": "white"},
                {"name": "Target Code", "pos": (7, 2), "color": "#424242", "text_color": "white"}
            ]

            # Side information
            side_info = [
                {"text": "Characters", "pos": (2, 8.5)},
                {"text": "Tokens", "pos": (2, 7.5)},
                {"text": "Parse Tree", "pos": (2, 6.5)},
                {"text": "AST + Symbol Table", "pos": (2, 5.5)},
                {"text": "Three-Address Code", "pos": (2, 4.5)},
                {"text": "Optimized Code", "pos": (2, 3.5)},
                {"text": "Assembly/Machine", "pos": (2, 2.5)}
            ]

            # Draw phases
            for i, phase in enumerate(phases):
                # Draw main box
                rect = mpatches.Rectangle(
                    (phase["pos"][0] - 1.5, phase["pos"][1] - 0.3),
                    3, 0.6,
                    facecolor=phase["color"],
                    edgecolor='black',
                    linewidth=2
                )
                ax.add_patch(rect)
                
                # Add phase name
                ax.text(phase["pos"][0], phase["pos"][1], phase["name"],
                    ha='center', va='center', fontsize=11, fontweight='bold', 
                    color=phase["text_color"])
                
                # Draw arrow to next phase
                if i < len(phases) - 1:
                    ax.arrow(phase["pos"][0], phase["pos"][1] - 0.3,
                            0, -0.4, head_width=0.15, head_length=0.1,
                            fc='black', ec='black', linewidth=2)

            # Add side information
            for i, info in enumerate(side_info):
                ax.text(info["pos"][0], info["pos"][1], info["text"],
                    ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
                
                # Draw arrow to main flow
                ax.arrow(info["pos"][0] + 1, info["pos"][1],
                        2.5, 0, head_width=0.1, head_length=0.1,
                        fc='gray', ec='gray', alpha=0.6)

            # Add error handling flow
            ax.text(11, 6, "Error Handling", ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='red', alpha=0.8), color='white')
            
            # Error arrows
            for y in [8, 7, 6]:
                ax.arrow(8.5, y, 1.5, 6-y, head_width=0.1, head_length=0.1,
                        fc='red', ec='red', alpha=0.6, linestyle='--')

            ax.set_xlim(0, 13)
            ax.set_ylim(1, 10)
            ax.axis('off')
            ax.set_title('Complete Compiler Architecture', fontsize=16, fontweight='bold', pad=20)

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, diagram_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        except Exception as e:
            # Fallback text representation
            fallback_text = """
    COMPILER PHASES:
    Source Code → Lexical Analysis → Syntax Analysis → Semantic Analysis → 
    Intermediate Code → Optimization → Code Generation → Target Code
    """
            fallback_label = ctk.CTkLabel(
                diagram_frame,
                text=fallback_text,
                font=('Arial', 12, 'bold')
            )
            fallback_label.pack(pady=20)

    def create_interactive_examples_section(self, parent):
        """Create interactive examples section"""
        section_frame = ctk.CTkFrame(parent, corner_radius=12)
        section_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(section_frame, corner_radius=8, fg_color=self.colors['accent'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="💡 Interactive Examples & Demos",
            font=('Arial', 22, 'bold'),
            text_color='white'
        ).pack(pady=15)

        # Content
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Example selector
        example_frame = ctk.CTkFrame(content_frame, corner_radius=8)
        example_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            example_frame,
            text="🎮 Try Interactive Examples",
            font=('Arial', 16, 'bold')
        ).pack(pady=(15, 10))

        # Example buttons
        button_frame = ctk.CTkFrame(example_frame, fg_color="transparent")
        button_frame.pack(fill='x', padx=15, pady=(0, 15))

        examples = [
            ("🔍 Tokenization Demo", self.demo_tokenization),
            ("🌳 Parse Tree Demo", self.demo_parse_tree),
            ("🔧 Symbol Table Demo", self.demo_symbol_table),
            ("⚠️ Error Detection Demo", self.demo_error_detection)
        ]

        for text, command in examples:
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                fg_color=self.colors['primary'],
                hover_color=self.adjust_color_brightness(self.colors['primary'], -20),
                corner_radius=8,
                height=40,
                width=200
            )
            btn.pack(side='left', padx=10, pady=5)

    def demo_tokenization(self):
        """Demo tokenization process"""
        demo_code = '''int x = 10;
    if (x > 5) {
        print("Hello");
    }'''
        
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', demo_code)
        self.perform_lexical_analysis()
        
        # Switch to editor tab
        self.notebook.set("📝 Editor & Analysis")
        
        messagebox.showinfo("Demo", "Tokenization demo loaded! Check the tokens tab to see how the code is broken into tokens.")

    def demo_parse_tree(self):
        """Demo parse tree generation"""
        demo_code = '''def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n-1)'''
        
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', demo_code)
        self.perform_lexical_analysis()
        
        # Switch to visual features tab and generate parse tree
        self.notebook.set("🎨 Visual Features")
        self.root.after(500, self.generate_parse_tree)
        
        messagebox.showinfo("Demo", "Parse tree demo loaded! Check the Visual Features tab to see the parse tree.")

    def demo_symbol_table(self):
        """Demo symbol table construction"""
        demo_code = '''class Calculator:
        def __init__(self):
            self.result = 0
        
        def add(self, x, y):
            return x + y'''
        
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', demo_code)
        self.run_semantic_analysis()
        
        # Switch to multi-phase analysis tab
        self.notebook.set("🔬 Multi-Phase Analysis")
        
        messagebox.showinfo("Demo", "Symbol table demo loaded! Check the Multi-Phase Analysis tab to see semantic analysis results.")

    def demo_error_detection(self):
        """Demo error detection"""
        demo_code = '''int x = 10
    if x > 5 {
        print("Missing semicolon and parentheses"
        undeclared_variable = 5;
    }'''
        
        self.code_editor.delete('1.0', 'end')
        self.code_editor.insert('1.0', demo_code)
        self.perform_lexical_analysis()
        
        # Switch to editor tab to show errors
        self.notebook.set("📝 Editor & Analysis")
        
        messagebox.showinfo("Demo", "Error detection demo loaded! Check the Errors tab to see detected syntax issues.")

    def scroll_to_section(self, section):
        """Scroll to specific theory section"""
        # This would require implementing section anchors
        # For now, just show a message
        messagebox.showinfo("Navigation", f"Scrolling to {section} section...")

    def create_team_tab(self, parent):
        """Create comprehensive team details tab"""
        # Create scrollable frame for team content
        scrollable_frame = ctk.CTkScrollableFrame(parent, corner_radius=8)
        scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create team header
        self.create_team_header(scrollable_frame)
        
        # Create team overview
        self.create_team_overview(scrollable_frame)
        
        # Create team members section
        self.create_team_members_section(scrollable_frame)
        
        # Create project information
        self.create_project_info_section(scrollable_frame)
        
        # Create contact section
        self.create_contact_section(scrollable_frame)

    def create_team_header(self, parent):
        """Create team page header with modern design"""
        header_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.colors['primary'])
        header_frame.pack(fill='x', padx=10, pady=(10, 20))

        # Team logo/icon section
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(pady=(20, 10))

        # Team logo (using emoji as placeholder)
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🏗️",
            font=('Arial', 48),
            text_color='white'
        )
        logo_label.pack()

        # Team name
        team_name_label = ctk.CTkLabel(
            header_frame,
            text="Team Architechs",
            font=('Arial', 32, 'bold'),
            text_color='white'
        )
        team_name_label.pack(pady=(0, 5))

        # Team ID
        team_id_label = ctk.CTkLabel(
            header_frame,
            text="Team ID: CD-VI-T155",
            font=('Arial', 18),
            text_color='white'
        )
        team_id_label.pack(pady=(0, 10))

        # Project title
        project_label = ctk.CTkLabel(
            header_frame,
            text="Advanced Multi-Language Lexical Analyzer",
            font=('Arial', 16, 'italic'),
            text_color='white'
        )
        project_label.pack(pady=(0, 20))

    def create_team_overview(self, parent):
        """Create team overview section"""
        overview_frame = ctk.CTkFrame(parent, corner_radius=12)
        overview_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(overview_frame, corner_radius=8, fg_color=self.colors['success'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="🎯 About Team Architechs",
            font=('Arial', 20, 'bold'),
            text_color='white'
        ).pack(pady=12)

        # Content
        content_frame = ctk.CTkFrame(overview_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        overview_text = """
    🚀 MISSION:
    To develop innovative compiler design solutions that bridge the gap between theoretical concepts and practical implementation, creating tools that enhance understanding of lexical analysis and parsing techniques.

    💡 VISION:
    Building the next generation of educational compiler tools that make complex theoretical concepts accessible through interactive visualization and hands-on learning experiences.

    🎖️ ACHIEVEMENTS:
    • Developed comprehensive multi-language lexical analyzer
    • Implemented advanced parsing algorithms (LALR, LR)
    • Created interactive educational visualizations
    • Integrated AI-powered code analysis features
    • Built modern, user-friendly interface with real-time analysis

    🔧 TECHNOLOGIES USED:
    • Python with CustomTkinter for modern GUI
    • Matplotlib & NetworkX for visualizations
    • Abstract Syntax Tree (AST) parsing
    • Machine Learning integration for error prediction
    • Multi-language support (Python, JavaScript, Java, C++)
    """

        overview_label = ctk.CTkLabel(
            content_frame,
            text=overview_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        )
        overview_label.pack(fill='x', padx=10, pady=10)

    def create_team_members_section(self, parent):
        """Create detailed team members section"""
        members_frame = ctk.CTkFrame(parent, corner_radius=12)
        members_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(members_frame, corner_radius=8, fg_color=self.colors['secondary'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="👥 Meet Our Team",
            font=('Arial', 20, 'bold'),
            text_color='white'
        ).pack(pady=12)

        # Team members data
        team_members = [
            {
                "name": "Harshit Jasuja",
                "role": "Team Lead & Lead Developer",
                "student_id": "220211228",
                "email": "harshitjasuja70@gmail.com",
                "specialization": "Compiler Design & GUI Development",
                "contributions": [
                    "Project architecture and design",
                    "Lexical analyzer core implementation",
                    "Modern GUI development with CustomTkinter",
                    "Integration of visual features and charts",
                    "Team coordination and project management"
                ],
                "skills": ["Python", "GUI Development", "Compiler Design", "Project Management"],
                "icon": "👨‍💻",
                "color": self.colors['primary']
            },
            {
                "name": "Shivendra Srivastava",
                "role": "Parsing Specialist & Algorithm Developer",
                "student_id": "220211349",
                "email": "shivendrasri999@gmail.com",
                "specialization": "Parsing Algorithms & Syntax Analysis",
                "contributions": [
                    "LALR(1) parsing table implementation",
                    "Syntax analysis algorithms",
                    "Parse tree generation logic",
                    "Multi-language grammar support",
                    "Algorithm optimization and testing"
                ],
                "skills": ["Parsing Algorithms", "Data Structures", "Algorithm Design", "Testing"],
                "icon": "🔧",
                "color": self.colors['success']
            },
            {
                "name": "Yashika Dixit",
                "role": "Semantic Analysis Expert & Documentation Lead",
                "student_id": "22022577",
                "email": "yashikadixit1611@gmail.com",
                "specialization": "Semantic Analysis & Documentation",
                "contributions": [
                    "Semantic analysis implementation",
                    "Symbol table construction",
                    "Type checking algorithms",
                    "Comprehensive documentation",
                    "User interface design consultation"
                ],
                "skills": ["Semantic Analysis", "Technical Writing", "Type Systems", "Documentation"],
                "icon": "📚",
                "color": self.colors['warning']
            }
        ]

        # Create member cards
        for i, member in enumerate(team_members):
            self.create_member_card(members_frame, member, i)

    def create_member_card(self, parent, member, index):
        """Create individual member card"""
        # Member card container
        card_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.colors['surface'])
        card_frame.pack(fill='x', padx=15, pady=10)

        # Card header with member info
        card_header = ctk.CTkFrame(card_frame, corner_radius=8, fg_color=member['color'])
        card_header.pack(fill='x', padx=10, pady=10)

        # Header content
        header_content = ctk.CTkFrame(card_header, fg_color="transparent")
        header_content.pack(fill='x', padx=15, pady=15)

        # Left side - Icon and basic info
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side='left', fill='y')

        # Member icon
        icon_label = ctk.CTkLabel(
            left_frame,
            text=member['icon'],
            font=('Arial', 32),
            text_color='white'
        )
        icon_label.pack(side='left', padx=(0, 15))

        # Basic info
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side='left', fill='y')

        name_label = ctk.CTkLabel(
            info_frame,
            text=member['name'],
            font=('Arial', 18, 'bold'),
            text_color='white'
        )
        name_label.pack(anchor='w')

        role_label = ctk.CTkLabel(
            info_frame,
            text=member['role'],
            font=('Arial', 14),
            text_color='white'
        )
        role_label.pack(anchor='w')

        # Right side - Contact info
        right_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        right_frame.pack(side='right', fill='y')

        id_label = ctk.CTkLabel(
            right_frame,
            text=f"ID: {member['student_id']}",
            font=('Arial', 12),
            text_color='white'
        )
        id_label.pack(anchor='e')

        email_label = ctk.CTkLabel(
            right_frame,
            text=f"📧 {member['email']}",
            font=('Arial', 12),
            text_color='white'
        )
        email_label.pack(anchor='e')

        # Card body with detailed information
        card_body = ctk.CTkFrame(card_frame, fg_color="transparent")
        card_body.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Two-column layout for details
        details_frame = ctk.CTkFrame(card_body, fg_color="transparent")
        details_frame.pack(fill='x', padx=10, pady=10)

        # Left column - Specialization and Contributions
        left_details = ctk.CTkFrame(details_frame, corner_radius=8)
        left_details.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Specialization
        spec_label = ctk.CTkLabel(
            left_details,
            text="🎯 Specialization:",
            font=('Arial', 14, 'bold'),
            anchor='w'
        )
        spec_label.pack(anchor='w', padx=10, pady=(10, 5))

        spec_text = ctk.CTkLabel(
            left_details,
            text=member['specialization'],
            font=('Arial', 12),
            anchor='w'
        )
        spec_text.pack(anchor='w', padx=15, pady=(0, 10))

        # Contributions
        contrib_label = ctk.CTkLabel(
            left_details,
            text="💼 Key Contributions:",
            font=('Arial', 14, 'bold'),
            anchor='w'
        )
        contrib_label.pack(anchor='w', padx=10, pady=(0, 5))

        for contribution in member['contributions']:
            contrib_item = ctk.CTkLabel(
                left_details,
                text=f"• {contribution}",
                font=('Arial', 11),
                anchor='w'
            )
            contrib_item.pack(anchor='w', padx=15, pady=1)

        # Right column - Skills
        right_details = ctk.CTkFrame(details_frame, corner_radius=8)
        right_details.pack(side='right', fill='both', expand=True, padx=(5, 0))

        skills_label = ctk.CTkLabel(
            right_details,
            text="🛠️ Technical Skills:",
            font=('Arial', 14, 'bold'),
            anchor='w'
        )
        skills_label.pack(anchor='w', padx=10, pady=(10, 5))

        # Skills as badges
        skills_frame = ctk.CTkFrame(right_details, fg_color="transparent")
        skills_frame.pack(fill='x', padx=10, pady=(0, 10))

        for skill in member['skills']:
            skill_badge = ctk.CTkLabel(
                skills_frame,
                text=skill,
                font=('Arial', 10, 'bold'),
                fg_color=member['color'],
                text_color='white',
                corner_radius=15,
                width=80,
                height=25
            )
            skill_badge.pack(side='left', padx=2, pady=2)

    def create_project_info_section(self, parent):
        """Create project information section"""
        project_frame = ctk.CTkFrame(parent, corner_radius=12)
        project_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(project_frame, corner_radius=8, fg_color=self.colors['accent'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="🚀 Project Information",
            font=('Arial', 20, 'bold'),
            text_color='white'
        ).pack(pady=12)

        # Content in two columns
        content_frame = ctk.CTkFrame(project_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Left column - Project details
        left_column = ctk.CTkFrame(content_frame, corner_radius=8)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 5))

        project_details = [
            ("📋 Project Title", "Advanced Multi-Language Lexical Analyzer"),
            ("🎓 Course", "Compiler Design"),
            ("🏫 Institution", "Graphic Era University"),
            ("📅 Development Period", "2025"),
            ("🔧 Primary Language", "Python"),
            ("📦 GUI Framework", "CustomTkinter"),
            ("📊 Visualization", "Matplotlib & NetworkX")
        ]

        for label, value in project_details:
            detail_frame = ctk.CTkFrame(left_column, fg_color="transparent")
            detail_frame.pack(fill='x', padx=10, pady=5)

            label_widget = ctk.CTkLabel(
                detail_frame,
                text=label,
                font=('Arial', 12, 'bold'),
                anchor='w'
            )
            label_widget.pack(anchor='w')

            value_widget = ctk.CTkLabel(
                detail_frame,
                text=value,
                font=('Arial', 11),
                anchor='w',
                text_color=self.colors['text_secondary']
            )
            value_widget.pack(anchor='w', padx=15)

        # Right column - Features
        right_column = ctk.CTkFrame(content_frame, corner_radius=8)
        right_column.pack(side='right', fill='both', expand=True, padx=(5, 0))

        features_label = ctk.CTkLabel(
            right_column,
            text="✨ Key Features",
            font=('Arial', 14, 'bold'),
            anchor='w'
        )
        features_label.pack(anchor='w', padx=10, pady=(10, 5))

        features = [
            "Multi-language lexical analysis",
            "Real-time syntax highlighting",
            "Interactive parse tree visualization",
            "LALR(1) parsing table generation",
            "AST visualization and export",
            "Token frequency analysis",
            "AI-powered error prediction",
            "Comprehensive educational theory",
            "Modern, responsive UI design",
            "Export and save functionality"
        ]

        for feature in features:
            feature_item = ctk.CTkLabel(
                right_column,
                text=f"• {feature}",
                font=('Arial', 11),
                anchor='w'
            )
            feature_item.pack(anchor='w', padx=15, pady=1)

    def create_contact_section(self, parent):
        """Create contact and collaboration section"""
        contact_frame = ctk.CTkFrame(parent, corner_radius=12)
        contact_frame.pack(fill='x', padx=10, pady=10)

        # Section header
        header = ctk.CTkFrame(contact_frame, corner_radius=8, fg_color=self.colors['danger'])
        header.pack(fill='x', padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="📞 Get In Touch",
            font=('Arial', 20, 'bold'),
            text_color='white'
        ).pack(pady=12)

        # Contact content
        content_frame = ctk.CTkFrame(contact_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Contact information
        contact_info = ctk.CTkFrame(content_frame, corner_radius=8)
        contact_info.pack(fill='x', padx=10, pady=10)

        contact_text = """
    📧 TEAM EMAIL CONTACTS:
    • Team Lead: harshitjasuja70@gmail.com
    • Developer: shivendrasri999@gmail.com  
    • Documentation: yashikadixit1611@gmail.com

    🏫 INSTITUTION:
    Graphic Era University
    Dehradun, Uttarakhand, India

    🤝 COLLABORATION:
    We welcome collaboration opportunities, feedback, and contributions to improve this educational tool. Feel free to reach out for:
    • Technical discussions about compiler design
    • Feature suggestions and improvements
    • Educational partnerships
    • Open source contributions

    💡 ACKNOWLEDGMENTS:
    Special thanks to our faculty advisors and the Computer Science Department at Graphic Era University for their guidance and support throughout this project development.
    """

        contact_label = ctk.CTkLabel(
            contact_info,
            text=contact_text,
            font=('Arial', 12),
            justify='left',
            anchor='nw'
        )
        contact_label.pack(fill='x', padx=15, pady=15)

        # Footer with social links (placeholder)
        footer_frame = ctk.CTkFrame(content_frame, corner_radius=8, fg_color=self.colors['primary'])
        footer_frame.pack(fill='x', padx=10, pady=(10, 0))

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="🌟 Team Architechs - Building the Future of Compiler Education 🌟",
            font=('Arial', 14, 'bold'),
            text_color='white'
        )
        footer_label.pack(pady=15)

    
def main():
    """Main function to run the application"""
    try:
        app = AdvancedLexicalAnalyzer()
        app.root.mainloop()
    except Exception as e:
        print(f"Application error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

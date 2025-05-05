#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application class for IVAS-IFM.

This module contains the main application class that handles the UI and application flow.
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any, Optional

from config.settings import APP_CONFIG, MESSAGES, PLATFORM_CONFIGS
from components.ui_components import (
    StyledButton, 
    SearchBar,
    StatusBar,
    VideoResultFrame,
    PlatformSelector,
    ProgressIndicator
)

logger = logging.getLogger(__name__)


class App:
    """Main application class for IVAS-IFM."""
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.setup_window()
        self.create_variables()
        self.create_widgets()
        self.layout_widgets()
        self.bind_events()
        logger.info("Application initialized")
        
    def setup_window(self):
        """Configure the main window properties."""
        self.root.title(APP_CONFIG['ui']['title'])
        self.root.geometry(f"{APP_CONFIG['ui']['width']}x{APP_CONFIG['ui']['height']}")
        
        # Try to set icon if it exists
        icon_path = APP_CONFIG['ui']['icon']
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            
        # Configure the style
        self.style = ttk.Style()
        self.style.theme_use(APP_CONFIG['ui']['theme'])
        
        # Configure UI scaling for high DPI displays
        self.root.tk.call('tk', 'scaling', 1.5)
        
    def create_variables(self):
        """Create tkinter variables for the application."""
        self.search_query = tk.StringVar()
        self.status_message = tk.StringVar(value=MESSAGES['welcome'])
        self.selected_platforms = {
            platform: tk.BooleanVar(value=True) 
            for platform in PLATFORM_CONFIGS.keys()
        }
        self.is_searching = tk.BooleanVar(value=False)
        self.search_results: Dict[str, List[Dict[str, Any]]] = {}
        
    def create_widgets(self):
        """Create the UI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Top panel with search and filters
        self.top_panel = ttk.Frame(self.main_frame)
        self.search_bar = SearchBar(
            self.top_panel, 
            variable=self.search_query, 
            width=40, 
            placeholder=MESSAGES['search_prompt']
        )
        
        self.platform_selector = PlatformSelector(
            self.top_panel, 
            platforms=list(PLATFORM_CONFIGS.keys()),
            variables=self.selected_platforms
        )
        
        self.search_button = StyledButton(
            self.top_panel, 
            text="Search",
            command=self.perform_search
        )
        
        # Results area
        self.results_frame = ttk.Frame(self.main_frame)
        self.results_notebook = ttk.Notebook(self.results_frame)
        
        # All results tab
        self.all_results_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.all_results_tab, text="All Results")
        
        # Platform-specific tabs
        self.platform_tabs = {}
        for platform in PLATFORM_CONFIGS.keys():
            tab = ttk.Frame(self.results_notebook)
            self.platform_tabs[platform] = tab
            self.results_notebook.add(tab, text=platform.capitalize())
        
        # Progress indicator
        self.progress = ProgressIndicator(self.main_frame)
        
        # Status bar
        self.status_bar = StatusBar(self.root, textvariable=self.status_message)
        
    def layout_widgets(self):
        """Arrange the widgets in the window."""
        # Layout main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Layout top panel
        self.top_panel.pack(fill=tk.X, expand=False, pady=(0, 10))
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.platform_selector.pack(side=tk.LEFT, padx=(0, 10))
        self.search_button.pack(side=tk.LEFT)
        
        # Layout results area
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Layout progress indicator
        self.progress.pack(fill=tk.X, expand=False, pady=(10, 0))
        
        # Layout status bar
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def bind_events(self):
        """Bind events to callbacks."""
        self.search_bar.bind("<Return>", lambda event: self.perform_search())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def perform_search(self):
        """Search for videos based on the query and selected platforms."""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showinfo("Search", "Please enter a search query")
            return
            
        # Get selected platforms
        selected_platforms = [
            platform for platform, var in self.selected_platforms.items() 
            if var.get()
        ]
        
        if not selected_platforms:
            messagebox.showinfo("Search", "Please select at least one platform")
            return
            
        self.status_message.set(f"Searching for: {query}")
        self.is_searching.set(True)
        self.progress.start()
        
        # TODO: Implement actual search using the VCA module
        # For now, we'll just simulate a search
        self.search_results = {
            platform: self._simulate_search_results(platform, query)
            for platform in selected_platforms
        }
        
        self.update_results_display()
        self.progress.stop()
        self.is_searching.set(False)
        self.status_message.set(f"Found {self._count_total_results()} results for: {query}")
        
    def update_results_display(self):
        """Update the results display with current search results."""
        # Clear existing results
        for widget in self.all_results_tab.winfo_children():
            widget.destroy()
            
        for platform, tab in self.platform_tabs.items():
            for widget in tab.winfo_children():
                widget.destroy()
        
        # Display new results
        all_results_canvas = tk.Canvas(self.all_results_tab)
        all_results_scrollbar = ttk.Scrollbar(
            self.all_results_tab, 
            orient=tk.VERTICAL, 
            command=all_results_canvas.yview
        )
        all_results_frame = ttk.Frame(all_results_canvas)
        
        all_results_canvas.configure(yscrollcommand=all_results_scrollbar.set)
        all_results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        all_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        all_results_canvas.create_window(
            (0, 0), 
            window=all_results_frame, 
            anchor=tk.NW, 
            tags="all_results_frame"
        )
        
        row = 0
        # Add results to the all results tab and platform-specific tabs
        for platform, results in self.search_results.items():
            platform_tab = self.platform_tabs[platform]
            platform_canvas = tk.Canvas(platform_tab)
            platform_scrollbar = ttk.Scrollbar(
                platform_tab, 
                orient=tk.VERTICAL, 
                command=platform_canvas.yview
            )
            platform_frame = ttk.Frame(platform_canvas)
            
            platform_canvas.configure(yscrollcommand=platform_scrollbar.set)
            platform_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            platform_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            platform_canvas.create_window(
                (0, 0), 
                window=platform_frame, 
                anchor=tk.NW, 
                tags=f"{platform}_frame"
            )
            
            platform_row = 0
            for result in results:
                # Add to all results tab
                result_frame = VideoResultFrame(
                    all_results_frame, 
                    video_data=result,
                    platform=platform,
                    download_callback=lambda url=result['url']: self.download_video(url)
                )
                result_frame.grid(row=row, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
                row += 1
                
                # Add to platform-specific tab
                platform_result_frame = VideoResultFrame(
                    platform_frame, 
                    video_data=result,
                    platform=platform,
                    download_callback=lambda url=result['url']: self.download_video(url)
                )
                platform_result_frame.grid(
                    row=platform_row, 
                    column=0, 
                    sticky=tk.W+tk.E, 
                    padx=5, 
                    pady=5
                )
                platform_row += 1
            
            # Configure platform canvas scrolling
            platform_frame.update_idletasks()
            platform_canvas.config(
                scrollregion=platform_canvas.bbox("all"),
                width=APP_CONFIG['ui']['width'] - 50
            )
            
            # Bind mouse wheel to scroll
            platform_canvas.bind_all(
                "<MouseWheel>", 
                lambda event, canvas=platform_canvas: self._on_mousewheel(event, canvas)
            )
        
        # Configure all results canvas scrolling
        all_results_frame.update_idletasks()
        all_results_canvas.config(
            scrollregion=all_results_canvas.bbox("all"),
            width=APP_CONFIG['ui']['width'] - 50
        )
        
        # Bind mouse wheel to scroll
        all_results_canvas.bind_all(
            "<MouseWheel>", 
            lambda event, canvas=all_results_canvas: self._on_mousewheel(event, canvas)
        )
    
    def _on_mousewheel(self, event, canvas):
        """Handle mousewheel scrolling."""
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def download_video(self, url: str):
        """Download a video from the given URL."""
        # TODO: Implement actual download using the VCA module
        # For now, just show a message
        output_dir = filedialog.askdirectory(title="Select download location")
        if not output_dir:
            return
            
        self.status_message.set(f"Downloading video from: {url}")
        self.progress.start()
        
        # Simulate download
        import time
        time.sleep(2)
        
        self.progress.stop()
        self.status_message.set(
            MESSAGES['download_success'].format(path=os.path.join(output_dir, "video.mp4"))
        )
        messagebox.showinfo(
            "Download Complete",
            f"Video downloaded to: {os.path.join(output_dir, 'video.mp4')}"
        )
    
    def _simulate_search_results(self, platform: str, query: str) -> List[Dict[str, Any]]:
        """Simulate search results for demo purposes."""
        # This is just for demonstration
        results = []
        for i in range(1, 6):
            results.append({
                'title': f"{query} - Result {i} from {platform}",
                'url': f"https://{platform}.com/video/{i}",
                'author': f"Author {i}",
                'views': i * 1000,
                'duration': f"{i}:00",
                'published': f"2025-05-0{i}",
                'thumbnail': None,  # We don't have actual thumbnails
                'description': f"This is a sample description for {query} result {i} from {platform}."
            })
        return results
    
    def _count_total_results(self) -> int:
        """Count the total number of results across all platforms."""
        return sum(len(results) for results in self.search_results.values())
    
    def on_close(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            
    def run(self):
        """Run the application main loop."""
        self.root.mainloop() 
 
 
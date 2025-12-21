# workers/builder/dynamic_gui_create_web_link.py

import tkinter as tk
from tkinter import ttk
import webbrowser

class WebLinkCreatorMixin:
    def _create_web_link(self, parent_frame, label, config, path):
        """Creates a web link widget."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        url = config.get("url", "#")
        link_label = ttk.Label(
            frame, 
            text=label, 
            foreground="blue", 
            cursor="hand2"
        )
        link_label.pack(side=tk.LEFT)
        
        def _open_url(event):
            webbrowser.open_new(url)

        link_label.bind("<Button-1>", _open_url)

        self.topic_widgets[path] = {"widget": link_label}

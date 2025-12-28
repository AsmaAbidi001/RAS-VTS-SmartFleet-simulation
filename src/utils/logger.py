"""
Logging utilities
"""

import json
import logging
import tkinter as tk
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

class SimulationLogger:
    """Main simulation logger"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.events: List[Dict] = []
        self.gui_logger = None
        
        # Setup file logging
        log_file = config['logging']['log_file']
        self.setup_file_logging(log_file)
        
        # Setup GUI logging if enabled
        if config['simulation']['use_gui']:
            self.gui_logger = GUILogger(self.events)
    
    def setup_file_logging(self, log_file: str):
        """Setup file-based logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file.replace('.json', '.log')),
                logging.StreamHandler()
            ]
        )
    
    def log_event(self, timestamp: float, event_type: str, data: Dict[str, Any]):
        """
        Log a simulation event
        
        Args:
            timestamp: Simulation timestamp
            event_type: Type of event
            data: Event data
        """
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'data': self._clean_data(data)
        }
        
        self.events.append(event)
        
        # Log to console
        if event_type == 'error':
            logging.error(f"[t={timestamp:.1f}] {data.get('error', 'Unknown error')}")
        elif event_type == 'task_completed':
            logging.info(f"[t={timestamp:.1f}] Task {data.get('task_id')} completed")
        
        # Update GUI if available
        if self.gui_logger:
            self.gui_logger.handle(event)
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data for JSON serialization"""
        if not isinstance(data, dict):
            return str(data)
        
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                cleaned[key] = self._clean_data(value) if isinstance(value, dict) else value
            elif isinstance(value, float) and (value == float('inf') or value > 1e9):
                cleaned[key] = 9999999999.0
            elif value is None:
                cleaned[key] = ''
            else:
                cleaned[key] = value
        
        return cleaned
    
    def save_logs(self):
        """Save all logs to file"""
        log_file = self.config['logging']['log_file']
        with open(log_file, 'w') as f:
            json.dump(self.events, f, indent=2)
        
        logging.info(f"Saved {len(self.events)} events to {log_file}")
    
    def poll_gui(self):
        """Poll GUI for updates"""
        if self.gui_logger:
            self.gui_logger.poll()

def setup_logging(config: Dict[str, Any]) -> SimulationLogger:
    """
    Setup logging system
    
    Args:
        config: Configuration dictionary
        
    Returns:
        SimulationLogger instance
    """
    return SimulationLogger(config)

class GUILogger:
    """GUI-based logging interface"""
    
    def __init__(self, log_buffer: List[Dict]):
        self.log_buffer = log_buffer
        self.root = tk.Tk()
        self.root.title("DCCBBA-SUMO Live Log")
        self.root.geometry("1200x700")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Top frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Label(top_frame, text="DCCBBA-SUMO Simulation Log", 
                font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Filter frame
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.filter_vars = {}
        for event_type in ['INFO', 'WARNING', 'ERROR', 'TASK', 'COMM']:
            var = tk.BooleanVar(value=True)
            tk.Checkbutton(filter_frame, text=event_type, variable=var).pack(side=tk.LEFT, padx=5)
            self.filter_vars[event_type] = var
        
        # Log display
        log_frame = tk.Frame(self.root)
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, yscrollcommand=scrollbar.set,
                               bg='#1e1e1e', fg='white', font=("Courier", 10))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Configure tags for coloring
        self.log_text.tag_config('INFO', foreground='#00ff00')
        self.log_text.tag_config('WARNING', foreground='#ffff00')
        self.log_text.tag_config('ERROR', foreground='#ff0000')
        self.log_text.tag_config('TASK', foreground='#00ffff')
        self.log_text.tag_config('COMM', foreground='#ff00ff')
    
    def handle(self, event: Dict[str, Any]):
        """
        Handle a new log event
        
        Args:
            event: Log event dictionary
        """
        event_type = event.get('type', 'INFO').upper()
        timestamp = event.get('timestamp', 0)
        data = event.get('data', {})
        
        # Check filter
        if not self.filter_vars.get(event_type, tk.BooleanVar(value=True)).get():
            return
        
        # Format message
        message = f"[{timestamp:.1f}] [{event_type}] {data}\n"
        
        # Add to text widget with appropriate tag
        self.log_text.insert(tk.END, message, (event_type,))
        self.log_text.see(tk.END)
    
    def poll(self):
        """Poll for GUI updates"""
        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            pass
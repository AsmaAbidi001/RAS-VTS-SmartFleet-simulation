"""
Configuration management utilities
"""

import yaml
import os
from typing import Dict, Any

DEFAULT_CONFIG = {
    'simulation': {
        'step_length': 1,
        'duration': None,
        'random_seed': 42,
        'use_gui': True,
        'gui_delay': 50
    },
    'sumo': {
        'binary': 'sumo-gui',
        'config': 'sumo_configs/simulation.sumocfg',
        'net_file': 'sumo_configs/network.net.xml',
        'gui_settings': 'sumo_configs/viewsettings.xml'
    },
    'network': {
        'warehouse_edge': 'edge_warehouse',
        'communication_range': 600.0,
        'stall_speed_threshold': 0.2,
        'stall_ticks_threshold': 10
    },
    'vehicles': {
        'num_vehicles': 3,
        'default_capacity': 10.0,
        'default_battery': 100.0,
        'follow_agent_id': 'vehicle_B',
        'colors': [
            [0, 0, 255, 255],
            [255, 0, 0, 255],
            [0, 255, 0, 255]
        ]
    },
    'tasks': {
        'generate_random': True,
        'sod_tasks': 5,
        'mid_tasks': 20,
        'sod_deadline_range': [1800, 2000],
        'mid_deadline_offset_range': [4000, 4200]
    },
    'logging': {
        'log_file': 'simulation_log.json',
        'status_interval': 100,
        'battery_drain_per_status': 0.1
    }
}

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Merge with defaults for missing values
    merged_config = merge_dicts(DEFAULT_CONFIG, config)
    
    return merged_config

def save_config(config_path: str, config: Dict[str, Any]) -> None:
    """
    Save configuration to YAML file
    
    Args:
        config_path: Path to save configuration
        config: Configuration dictionary
    """
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def merge_dicts(default: Dict, override: Dict) -> Dict:
    """
    Recursively merge two dictionaries
    
    Args:
        default: Default dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = default.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def get_config_value(config: Dict[str, Any], key_path: str, default=None) -> Any:
    """
    Get configuration value using dot notation
    
    Args:
        config: Configuration dictionary
        key_path: Dot notation path (e.g., 'simulation.step_length')
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    
    return value if value is not None else default
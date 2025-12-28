"""
Main entry point for DCCBBA-SUMO Simulation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.simulation.sumo_interface import SumoSimulation
from src.agents.mesh_simulator import MeshSimulator
from src.utils.config import load_config
from src.utils.logger import setup_logging
from src.utils.metrics import PerformanceMetrics
import logging

logger = logging.getLogger(__name__)

def run_simulation(config_path="config.yaml"):
    """Main simulation runner"""
    
    # Load configuration
    config = load_config(config_path)
    
    # Setup logging
    setup_logging(config)
    
    logger.info("Starting DCCBBA-SUMO Simulation")
    
    # Initialize performance metrics
    metrics = PerformanceMetrics()
    
    try:
        # Initialize SUMO simulation
        sim = SumoSimulation(config)
        sim.initialize()
        
        # Run simulation
        sim.run()
        
        # Collect final metrics
        metrics.collect_final_metrics(sim)
        metrics.save_report()
        
        logger.info("Simulation completed successfully")
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise
    
    finally:
        sim.cleanup()

if __name__ == "__main__":
    run_simulation()
# RAS-VTS-SmartFleet-simulation
A comprehensive multi-agent simulation system for decentralized task allocation in urban environments using the Decentralized Consensus-Based Bundle Algorithm (DCCBBA) integrated with SUMO (Simulation of Urban MObility). This framework enables research into autonomous vehicle fleet coordination, intelligent routing, and decentralized decision-making algorithms.

# Features
Decentralized Task Allocation: Implementation of DCCBBA algorithm for distributed task assignment

SUMO Integration: Realistic urban traffic simulation with custom routing

Multi-Agent System: Configurable vehicle agents with varying capabilities

Real-time Visualization: GUI dashboard with live logs and performance metrics

Performance Analytics: Automated reporting and visualization of simulation results

Configurable Scenarios: YAML-based configuration for different simulation scenarios

Modular Architecture: Clean, extensible codebase with comprehensive documentation

# Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Simulation Controller                    │
├─────────────────────────────────────────────────────────────┤
│  Mesh Network  │  DCCBBA Algorithm  │  SUMO Interface       │
├─────────────────────────────────────────────────────────────┤
│  Vehicle Agents │  Warehouse        │  Visualization        │
├─────────────────────────────────────────────────────────────┤
│  Performance Metrics │  Configuration │  Logging System     │
└─────────────────────────────────────────────────────────────┘
```

# Prerequisites
- Python 3.7
- SUMO 1.14+ (Simulation of Urban MObility)
Basic understanding of multi-agent systems

# Installation
## Clone the repository
    git clone https://github.com/yourusername/dccbba-sumo-simulation.git
    cd dccbba-sumo-simulation

## Install dependencies
    pip install -r requirements.txt

## Install SUMO (platform-specific)

for exampe; for Ubintu
```bash
sudo apt-get install sumo sumo-tools
```

for Mac: 
```bash
brew install sumo
```

for Windows: Download from https://sumo.dlr.de/docs/Downloads.php

## Initialize configuration

```bash
python run_simulation.py init
```

## Run a basic simulation
python run_simulation.py run --num-vehicles 3 --duration 1000


# Algorithm: DCCBBA (Decentralized Consensus-Based Bundle Algorithm)
## How It Works:
DCCBBA is a decentralized, consensus-based algorithm for multi-agent task allocation that operates without a central coordinator. The algorithm follows these key phases:

### 1. Task Announcement Phase
Warehouse announces tasks to the network

Tasks include: pickup location, delivery location, weight, priority, and deadline

Tasks are broadcast through the mesh network

### 2. Forward Announcement Phase
Tasks propagate through agent ring topology

Each agent computes a bid based on:

- Distance Cost: Estimated travel distance to complete task
- Capacity Penalty: Current load vs. maximum capacity
- Priority Multiplier: Task importance weighting
- Time Window Penalty: Urgency based on deadline proximity
- Agents forward best bid encountered along the path

### 3. Winner Decision Phase
When task completes circuit, agent with lowest bid wins

Winner decision propagates back through communication path

Winner adds task to its bundle and updates its route

### 4. Execution Phase
Winners execute assigned tasks sequentially

Real-time route optimization based on current position

Continuous monitoring of task progress and deadlines


## Bid Calculation Formula
The bid for agent *i* for task *j* is calculated as:
```
Bid_ij = BaseDistance_ij × PriorityMultiplier_j × CapacityPenalty_i × TimePenalty_j
```
Where:

- `BaseDistance_ij`: Estimated travel distance from current position to warehouse to delivery and back

- `PriorityMultiplier_j`: Based on task weight/priority (0.5 for high, 1.0 for medium, 1.5 for low)

- `CapacityPenalty_i`: 1.0 + (current_load / capacity) × 2.0

- `TimePenalty_j`: Based on deadline urgency (1.0 normal, 1.5 urgent, 3.0 critical)

## Communication Protocol
The system uses a ring-based communication topology with three message types:

1. TASK_ANNOUNCEMENT: Initial task broadcast from warehouse

2. FORWARD_ANNOUNCEMENT: Task propagation with current best bid

3. WINNER_DECISION: Final allocation decision back-propagation



# Configuration
The simulation is configured via config.yaml:
### simulation:
```yaml
  step_length: 1          # Simulation step in seconds
  duration: null          # Duration in ticks (null = unlimited)
  random_seed: 42         # Random seed for reproducibility
  use_gui: true          # Enable/disable SUMO GUI
  gui_delay: 50          # GUI refresh delay in ms
```

### vehicles:

```yaml
  num_vehicles: 3        # Number of vehicles in simulation
  default_capacity: 10.0  # Default vehicle capacity
  default_battery: 100.0  # Default battery percentage
  colors:                # Vehicle colors for visualization
    - [0, 0, 255, 255]   # Blue
    - [255, 0, 0, 255]   # Red
    - [0, 255, 0, 255]   # Green
```

### tasks:

```
  generate_random: true   # Generate random tasks
  sod_tasks: 5           # Start-of-day tasks
  mid_tasks: 20          # Midday tasks
  priority_multipliers:  # Task priority settings
    high: 0.5
    normal: 1.0
    low: 1.5
```

# Performance Metrics
The system tracks comprehensive performance metrics:

## Key Metrics Collected
Task Completion Rate: Percentage of tasks completed successfully

Deadline Compliance: Tasks completed before/after deadline

Communication Overhead: Total messages exchanged

Total Distance Traveled: Aggregate distance by all vehicles

Vehicle Utilization: Individual vehicle efficiency metrics

Algorithm Convergence Time: Time to reach consensus

## Generated Reports
Task allocation distribution (pie/bar charts)

Deadline compliance timeline

Vehicle utilization statistics

Communication pattern analysis

Comprehensive summary report



# Usage Examples
## Basic Simulation
###  Run with default settings
python run_simulation.py run

### Run with 5 vehicles for 5000 ticks
python run_simulation.py run --num-vehicles 5 --duration 5000

### Run without GUI for faster execution
python run_simulation.py run --no-gui


## Configuration Management
### Validate configuration file
python run_simulation.py validate config.yaml

### Create new configuration
python run_simulation.py init --output my_config.yaml

### Show statistics from previous run
python run_simulation.py stats


## Advanced Usage
### Run with custom configuration
python run_simulation.py run --config custom_config.yaml

### Generate tasks only (no simulation)
python -c "from src.utils.tasks import generate_tasks; generate_tasks()"

### Test specific scenario
python -m pytest tests/test_dccbba.py -v



# Research Applications
This framework supports research in:

## Multi-Agent Systems
Decentralized coordination algorithms

Consensus protocols

Distributed optimization

## Autonomous Vehicles
Fleet management systems

Dynamic task allocation

Route optimization under constraints

## Urban Logistics
Last-mile delivery optimization

Emergency response coordination

Smart city infrastructure

## Algorithm Development
Comparative analysis of task allocation algorithms

Performance benchmarking

Scalability testing




# Extending the Framework

## Adding New Algorithms
Create a new class in src/routing/ inheriting from BaseAlgorithm

Implement required methods: compute_bid(), process_message()

Update configuration to select algorithm

Add corresponding tests in tests/




## Custom Vehicle Types

    from src.agents.vehicle_agent import VehicleAgent
    class DroneAgent(VehicleAgent):
        def __init__(self, agent_id, position, flight_range):
            super().__init__(agent_id, position)
            self.flight_range = flight_range
            self.airspace_constraints = []
    
        def compute_bid(self, task_info, network_info):
            # Custom bid calculation for aerial vehicles
            base_bid = super().compute_bid(task_info, network_info)
            return base_bid * self._calculate_airspace_penalty()

## Custom Scenarios
Create new SUMO network configuration

Define task generation patterns

Configure vehicle capabilities and constraints

Run comparative simulations

# Performance Optimization Tips
## For Faster Simulation
Set use_gui: false in configuration

Reduce gui_delay to minimum

Limit number of vehicles based on network size

Use smaller map areas for testing

## For Large-Scale Simulations
Implement spatial partitioning for communication

Use approximate distance calculations

Implement task batching

Enable parallel processing where possible

# Troubleshooting
## Common Issues
SUMO not found: Ensure SUMO is installed and in PATH

Memory issues with large networks: Reduce vehicle count or network size

GUI crashes: Try running with --no-gui flag

Slow simulation: Increase gui_delay or disable visualization

## Debugging Tips
bash

    # Enable verbose logging
    python run_simulation.py run --log-level DEBUG

    # Test SUMO connectivity
    python -c "import traci; print('SUMO available:', traci is not None)"

    # Check configuration
    python run_simulation.py validate

# Contributing
1.Fork the repository

2.Create a feature branch (git checkout -b feature/amazing-feature)

3.Commit changes (git commit -m 'Add amazing feature')

4.Push to branch (git push origin feature/amazing-feature)

5.Open a Pull Request

## Development Guidelines
Follow PEP 8 style guide

Write comprehensive docstrings

Include unit tests for new features

Update documentation accordingly

# References & Further Reading
## Academic Papers
- Choi, H.-L., Brunet, L., & How, J. P. (2009). Consensus-based decentralized auctions for robust task allocation. IEEE Transactions on Robotics

- Johnson, L. B., & Ponda, S. S. (2012). Decentralized task allocation for dynamic environments. AIAA Guidance, Navigation, and Control Conference

## Related Projects
SUMO Documentation

MATS: Multi-Agent Task Simulation

ROS2 Navigation Stack

Learning Resources
Multi-Robot Systems Course (MIT)

Decentralized AI Algorithms

## Learning Resources
Multi-Robot Systems Course (MIT)

Decentralized AI Algorithms



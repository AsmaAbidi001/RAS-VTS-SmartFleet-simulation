"""
SUMO simulation interface
"""

import os
import time
import random
from typing import Dict, List, Optional, Tuple
import json

try:
    import traci
    from sumolib import net
    SUMO_AVAILABLE = True
except ImportError:
    SUMO_AVAILABLE = False

class SumoSimulation:
    """Main SUMO simulation interface"""
    
    def __init__(self, config: Dict):
        """
        Initialize SUMO simulation
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.sumo_net = None
        self.traci_running = False
        self.simulation_time = 0
        
        # Simulation state
        self.edge_ids: List[str] = []
        self.valid_delivery_edges: List[str] = []
        self.vehicle_map: Dict[str, str] = {}  # agent_id -> sumo_vehicle_id
        
        # Visualization
        self.active_routes: Dict[str, List[str]] = {}
        self.visualization_ids: Dict[str, List[str]] = {}
    
    def initialize(self):
        """Initialize SUMO simulation"""
        if not SUMO_AVAILABLE:
            print("SUMO not available. Running in headless mode.")
            return
        
        try:
            # Build SUMO command
            cmd = self._build_sumo_command()
            
            # Start traci
            traci.start(cmd)
            self.traci_running = True
            
            # Load network
            net_file = self.config['sumo']['net_file']
            self.sumo_net = net.readNet(net_file)
            
            # Get edges
            self.edge_ids = [e.getID() for e in self.sumo_net.getEdges()]
            
            # Find valid delivery edges
            self._find_valid_delivery_edges()
            
            print(f"SUMO initialized with {len(self.edge_ids)} edges")
            
        except Exception as e:
            print(f"Error initializing SUMO: {e}")
            self.traci_running = False
    
    def _build_sumo_command(self) -> List[str]:
        """Build SUMO command list"""
        cmd = [
            self.config['sumo']['binary'],
            "-c", self.config['sumo']['config'],
            "--step-length", str(self.config['simulation']['step_length']),
            "--delay", str(self.config['simulation']['gui_delay'])
        ]
        
        # Add GUI settings if available
        gui_settings = self.config['sumo'].get('gui_settings')
        if gui_settings and os.path.exists(gui_settings):
            cmd.extend(["--gui-settings-file", gui_settings])
        
        # Disable warnings for cleaner output
        cmd.append("--no-warnings")
        
        return cmd
    
    def _find_valid_delivery_edges(self):
        """Find edges that can be reached from warehouse and back"""
        warehouse_edge = self.config['network']['warehouse_edge']
        
        if warehouse_edge not in self.edge_ids and self.edge_ids:
            # Use random edge as warehouse
            warehouse_edge = random.choice(self.edge_ids)
            self.config['network']['warehouse_edge'] = warehouse_edge
        
        self.valid_delivery_edges = []
        
        for edge_id in self.edge_ids:
            if edge_id == warehouse_edge:
                continue
            
            # Check if route exists both ways
            to_route = self._find_route(warehouse_edge, edge_id)
            from_route = self._find_route(edge_id, warehouse_edge)
            
            if to_route and from_route:
                self.valid_delivery_edges.append(edge_id)
        
        print(f"Found {len(self.valid_delivery_edges)} valid delivery edges")
    
    def _find_route(self, from_edge: str, to_edge: str) -> Optional[List[str]]:
        """Find route between two edges"""
        try:
            src = self.sumo_net.getEdge(from_edge)
            dst = self.sumo_net.getEdge(to_edge)
            path, _ = self.sumo_net.getShortestPath(src, dst)
            
            if path:
                return [e.getID() for e in path]
        except Exception:
            pass
        
        return None
    
    def run(self):
        """Run the main simulation loop"""
        if not self.traci_running:
            print("SUMO not running. Skipping simulation.")
            return
        
        duration = self.config['simulation']['duration']
        
        try:
            while True:
                # Simulation step
                traci.simulationStep()
                self.simulation_time = traci.simulation.getTime()
                
                # Update vehicle positions
                self._update_vehicle_positions()
                
                # Check simulation end
                if duration and self.simulation_time > duration:
                    break
                
                # Small delay for visualization
                if self.config['simulation']['use_gui']:
                    time.sleep(0.05)
                
        except Exception as e:
            print(f"Simulation error: {e}")
    
    def _update_vehicle_positions(self):
        """Update vehicle positions in the simulation"""
        if not self.traci_running:
            return
        
        # This would update agent positions based on SUMO vehicle positions
        for agent_id, vehicle_id in self.vehicle_map.items():
            try:
                x, y = traci.vehicle.getPosition(vehicle_id)
                # Update agent position here
            except Exception:
                pass
    
    def add_vehicle(self, agent_id: str, route_edges: List[str]):
        """
        Add a vehicle to SUMO
        
        Args:
            agent_id: Agent identifier
            route_edges: List of edge IDs for the route
        """
        if not self.traci_running:
            return
        
        try:
            vehicle_id = f"veh_{agent_id}"
            
            # Create route if it doesn't exist
            route_id = f"route_{agent_id}"
            traci.route.add(route_id, route_edges)
            
            # Add vehicle
            traci.vehicle.add(
                vehID=vehicle_id,
                routeID=route_id,
                typeID="vType",
                depart="now"
            )
            
            # Set color based on agent
            color = self._get_agent_color(agent_id)
            traci.vehicle.setColor(vehicle_id, color)
            
            # Store mapping
            self.vehicle_map[agent_id] = vehicle_id
            
            print(f"Added vehicle {vehicle_id} for agent {agent_id}")
            
        except Exception as e:
            print(f"Error adding vehicle {agent_id}: {e}")
    
    def _get_agent_color(self, agent_id: str) -> Tuple[int, int, int, int]:
        """Get color for an agent"""
        colors = self.config['vehicles']['colors']
        
        # Simple hash-based color assignment
        try:
            agent_num = int(''.join(filter(str.isdigit, agent_id))) - 1
            color = colors[agent_num % len(colors)]
        except:
            color = colors[0]
        
        return tuple(color)
    
    def update_vehicle_route(self, agent_id: str, route_edges: List[str]):
        """
        Update vehicle route
        
        Args:
            agent_id: Agent identifier
            route_edges: New route edges
        """
        if not self.traci_running:
            return
        
        vehicle_id = self.vehicle_map.get(agent_id)
        if not vehicle_id:
            return
        
        try:
            traci.vehicle.setRoute(vehicle_id, route_edges)
            self.active_routes[agent_id] = route_edges
            
            # Update visualization
            self._visualize_route(agent_id, route_edges)
            
        except Exception as e:
            print(f"Error updating route for {agent_id}: {e}")
    
    def _visualize_route(self, agent_id: str, route_edges: List[str]):
        """Visualize route in SUMO GUI"""
        if not self.traci_running:
            return
        
        # Clear previous visualization
        self._clear_visualization(agent_id)
        
        # Create polyline for route
        route_shape = []
        for edge_id in route_edges:
            try:
                edge = self.sumo_net.getEdge(edge_id)
                route_shape.extend(edge.getShape())
            except Exception:
                pass
        
        if not route_shape:
            return
        
        # Add polygon for route
        poly_id = f"route_{agent_id}_{int(self.simulation_time)}"
        color = self._get_agent_color(agent_id)
        
        try:
            traci.polygon.add(
                polygonID=poly_id,
                shape=route_shape,
                color=color,
                fill=False,
                layer=50
            )
            
            # Store for cleanup
            if agent_id not in self.visualization_ids:
                self.visualization_ids[agent_id] = []
            self.visualization_ids[agent_id].append(poly_id)
            
        except Exception as e:
            print(f"Error visualizing route: {e}")
    
    def _clear_visualization(self, agent_id: str):
        """Clear visualization for an agent"""
        if agent_id not in self.visualization_ids:
            return
        
        for vis_id in self.visualization_ids[agent_id]:
            try:
                traci.polygon.remove(vis_id)
            except Exception:
                pass
        
        self.visualization_ids[agent_id] = []
    
    def cleanup(self):
        """Cleanup simulation resources"""
        if self.traci_running:
            try:
                traci.close()
                self.traci_running = False
                print("SUMO simulation closed")
            except Exception as e:
                print(f"Error closing SUMO: {e}")
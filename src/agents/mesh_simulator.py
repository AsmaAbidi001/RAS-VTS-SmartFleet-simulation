"""
Mesh network simulator for vehicle communication
"""

import random
from typing import Dict, List, Tuple, Optional
from copy import deepcopy

class MeshSimulator:
    """Mesh network simulator for vehicle communication"""
    
    VERY_HIGH_BID = 9999999999.0
    
    def __init__(self, agents: Dict[str, 'VehicleAgent'], warehouse, 
                 comm_range: float = 600.0, seed: int = None):
        """
        Initialize mesh simulator
        
        Args:
            agents: Dictionary of vehicle agents
            warehouse: Warehouse instance
            comm_range: Communication range
            seed: Random seed
        """
        self.agents = agents
        self.warehouse = warehouse
        self.comm_range = comm_range
        self.message_queue: List[Tuple[str, Dict, int]] = []
        
        if seed is not None:
            random.seed(seed)
        
        # Create ring topology
        self.ring: List[str] = list(self.agents.keys())
        self.sod_assign_index = 0
    
    def send(self, sender_id: str, message: Dict, sim_time: int = None):
        """
        Send a message
        
        Args:
            sender_id: Sender agent ID
            message: Message to send
            sim_time: Simulation time
        """
        if not isinstance(message, dict) or "message_type" not in message:
            return
        
        self.message_queue.append((sender_id, deepcopy(message), sim_time))
    
    def deliver_messages(self, sim_time: int):
        """
        Deliver all queued messages
        
        Args:
            sim_time: Current simulation time
        """
        while self.message_queue:
            sender, msg, msg_time = self.message_queue.pop(0)
            current_time = msg_time if msg_time is not None else sim_time
            self._process_message(sender, msg, current_time)
    
    def _process_message(self, sender: str, msg: Dict, current_time: int):
        """Process a single message"""
        msg_type = msg.get("message_type")
        
        if msg_type == "TASK_ANNOUNCEMENT" and sender == "warehouse":
            self._handle_warehouse_announcement(msg, current_time)
        elif msg_type == "FORWARD_ANNOUNCEMENT":
            self._handle_forward_announcement(sender, msg, current_time)
        elif msg_type == "WINNER_DECISION":
            self._handle_winner_decision(msg)
    
    def _handle_warehouse_announcement(self, msg: Dict, current_time: int):
        """Handle task announcement from warehouse"""
        task_id = msg.get("task_id", "")
        
        # Check if it's a SOD (Start of Day) task
        if task_id.startswith("SOD-"):
            self._assign_sod_task(msg, current_time)
        else:
            self._forward_to_ring(msg, current_time)
    
    def _assign_sod_task(self, msg: Dict, current_time: int):
        """Assign SOD task using round-robin"""
        if not self.ring:
            return
        
        # Round-robin assignment
        winner = self.ring[self.sod_assign_index % len(self.ring)]
        self.sod_assign_index += 1
        
        # Create winner decision
        winner_msg = {
            "message_type": "WINNER_DECISION",
            "task_id": msg.get("task_id"),
            "winner": winner,
            "pickup": msg.get("pickup"),
            "delivery": msg.get("delivery"),
            "weight": msg.get("weight"),
            "best": {"bid": 0.0, "holder": winner}
        }
        
        # Send to winner
        if winner in self.agents:
            self.agents[winner].receive(winner_msg)
    
    def _forward_to_ring(self, msg: Dict, current_time: int):
        """Forward task announcement through the ring"""
        if not self.ring:
            return
        
        task_id = msg.get("task_id", "")
        pickup = msg.get("pickup", "")
        delivery = msg.get("delivery", "")
        weight = msg.get("weight", 0.0)
        
        # Start with warehouse
        path = ["warehouse"]
        
        # Find first agent in ring
        first_agent = self.ring[0]
        
        # Create forward message
        forward_msg = {
            "message_type": "FORWARD_ANNOUNCEMENT",
            "task_id": task_id,
            "pickup": pickup,
            "delivery": delivery,
            "weight": weight,
            "path": path + [first_agent],
            "best": {"bid": self.VERY_HIGH_BID, "holder": None}
        }
        
        # Send to first agent
        if first_agent in self.agents:
            self.agents[first_agent].receive(forward_msg)
    
    def _handle_forward_announcement(self, sender: str, msg: Dict, current_time: int):
        """Handle forward announcement"""
        path = msg.get("path", [])
        
        if not path:
            return
        
        # Find next agent in ring
        last_agent = path[-1]
        next_agent = self._find_next_in_ring(last_agent, path)
        
        if not next_agent:
            # End of ring - start backtrace
            self._start_backtrace(msg, current_time)
            return
        
        # Forward to next agent
        forward_msg = deepcopy(msg)
        forward_msg["path"] = path + [next_agent]
        
        if next_agent in self.agents:
            self.agents[next_agent].receive(forward_msg)
    
    def _find_next_in_ring(self, current: str, path: List[str]) -> Optional[str]:
        """Find next agent in ring that's not in path"""
        if current == "warehouse":
            # Start from beginning
            for agent in self.ring:
                if agent not in path:
                    return agent
            return None
        
        if current not in self.ring:
            return None
        
        # Find next in ring
        idx = self.ring.index(current)
        for offset in range(1, len(self.ring) + 1):
            next_idx = (idx + offset) % len(self.ring)
            candidate = self.ring[next_idx]
            if candidate not in path:
                return candidate
        
        return None
    
    def _start_backtrace(self, msg: Dict, current_time: int):
        """Start backtrace process to announce winner"""
        best = msg.get("best", {"bid": self.VERY_HIGH_BID, "holder": None})
        winner = best.get("holder")
        
        if not winner:
            # No winner found
            return
        
        path = msg.get("path", [])
        
        # Create backtrace path (reverse order)
        if winner in path:
            idx = path.index(winner)
            backtrace_path = list(reversed(path[idx:]))
        else:
            backtrace_path = [winner]
        
        # Create winner message
        winner_msg = {
            "message_type": "WINNER_DECISION",
            "task_id": msg.get("task_id"),
            "winner": winner,
            "pickup": msg.get("pickup"),
            "delivery": msg.get("delivery"),
            "weight": msg.get("weight"),
            "best": best,
            "backtrace_route": backtrace_path
        }
        
        # Send back through the path
        for i in range(len(backtrace_path) - 1):
            sender = backtrace_path[i]
            receiver = backtrace_path[i + 1]
            
            if receiver in self.agents:
                self.agents[receiver].receive(winner_msg)
    
    def _handle_winner_decision(self, msg: Dict):
        """Handle winner decision - deliver to winner"""
        winner = msg.get("winner", "")
        
        if winner in self.agents:
            self.agents[winner].receive(msg)
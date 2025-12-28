"""
Vehicle Agent implementation for DCCBBA algorithm
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Set
from copy import deepcopy

class VehicleAgent:
    """Vehicle agent for DCCBBA algorithm"""
    
    VERY_HIGH_BID = 9999999999.0
    
    def __init__(self, agent_id: str, position: Tuple[float, float], 
                 capacity: float = 10.0, battery: float = 100.0):
        """
        Initialize vehicle agent
        
        Args:
            agent_id: Unique agent identifier
            position: Initial (x, y) position
            capacity: Maximum load capacity
            battery: Initial battery percentage
        """
        self.id = agent_id
        self.position = {"x": float(position[0]), "y": float(position[1])}
        self.capacity = float(capacity)
        self.battery = float(battery)
        self.load = 0.0
        self.inbox: List[Dict] = []
        
        self.assigned_tasks: List[Tuple[str, str]] = []  # (task_id, delivery_edge)
        self.completed_tasks: int = 0
        self.current_route: Optional[List[str]] = None
        
        # Performance tracking
        self.total_distance = 0.0
        self.total_tasks = 0
    
    def get_position(self) -> Dict[str, float]:
        """Get current position"""
        return dict(self.position)
    
    def update_position(self, x: float, y: float):
        """Update agent position"""
        self.position["x"] = x
        self.position["y"] = y
    
    def receive(self, message: Dict):
        """
        Receive a message
        
        Args:
            message: Message dictionary
        """
        if isinstance(message, dict) and "message_type" in message:
            self.inbox.append(message)
    
    def has_capacity(self, task_weight: float) -> bool:
        """
        Check if agent has capacity for a task
        
        Args:
            task_weight: Weight of the task
            
        Returns:
            True if capacity is sufficient
        """
        return (self.load + task_weight) <= self.capacity
    
    def compute_bid(self, task_info: Dict, network_info: Dict) -> float:
        """
        Compute bid for a task using DCCBBA algorithm
        
        Args:
            task_info: Task information dictionary
            network_info: Network information dictionary
            
        Returns:
            Bid value (lower is better)
        """
        task_id = task_info.get("task_id", "")
        pickup = task_info.get("pickup", "")
        delivery = task_info.get("delivery", "")
        weight = float(task_info.get("weight", 0.0))
        
        # Check capacity
        if not self.has_capacity(weight):
            return self.VERY_HIGH_BID
        
        # Get current position
        current_edge = network_info.get("current_edge", "warehouse")
        
        # Calculate base distance cost
        base_cost = self._calculate_base_cost(current_edge, delivery, network_info)
        
        if base_cost >= self.VERY_HIGH_BID:
            return self.VERY_HIGH_BID
        
        # Apply priority multiplier
        priority_mult = self._calculate_priority_multiplier(weight)
        
        # Apply capacity penalty
        capacity_penalty = self._calculate_capacity_penalty()
        
        # Apply time window penalty
        time_penalty = self._calculate_time_penalty(task_info, base_cost, 
                                                   network_info.get("current_time", 0))
        
        # Final bid
        bid = base_cost * priority_mult * capacity_penalty * time_penalty
        
        return min(bid, self.VERY_HIGH_BID)
    
    def _calculate_base_cost(self, current_edge: str, delivery_edge: str, 
                           network_info: Dict) -> float:
        """Calculate base distance cost"""
        # This would use actual network routing
        # For now, return a simplified cost
        return 100.0  # Placeholder
    
    def _calculate_priority_multiplier(self, weight: float) -> float:
        """Calculate priority multiplier based on task weight"""
        if weight >= 5.0:
            return 0.5  # High priority
        elif weight >= 2.0:
            return 1.0  # Normal priority
        else:
            return 1.5  # Low priority
    
    def _calculate_capacity_penalty(self) -> float:
        """Calculate capacity penalty"""
        if self.capacity <= 0:
            return 1.0
        
        load_ratio = self.load / self.capacity
        return 1.0 + (load_ratio * 2.0)  # Base 1.0 + load-based penalty
    
    def _calculate_time_penalty(self, task_info: Dict, base_cost: float, 
                              current_time: float) -> float:
        """Calculate time window penalty"""
        deadline = task_info.get("due_by")
        if deadline is None:
            return 1.0
        
        travel_time_estimate = base_cost / 10.0  # Simplified
        estimated_completion = current_time + travel_time_estimate
        time_remaining = deadline - estimated_completion
        
        if time_remaining <= 0:
            return 3.0 * 2.0  # Critical
        elif time_remaining <= 100:
            return 3.0  # Critical
        elif time_remaining <= 300:
            return 1.5  # Urgent
        else:
            return 1.0  # Normal
    
    def process_messages(self, current_time: int, mesh):
        """
        Process incoming messages
        
        Args:
            current_time: Current simulation time
            mesh: Mesh simulator instance
        """
        while self.inbox:
            msg = self.inbox.pop(0)
            self._handle_message(msg, current_time, mesh)
    
    def _handle_message(self, msg: Dict, current_time: int, mesh):
        """Handle specific message types"""
        msg_type = msg.get("message_type")
        
        if msg_type == "TASK_ANNOUNCEMENT":
            self._handle_task_announcement(msg, current_time, mesh)
        elif msg_type == "FORWARD_ANNOUNCEMENT":
            self._handle_forward_announcement(msg, current_time, mesh)
        elif msg_type == "WINNER_DECISION":
            self._handle_winner_decision(msg)
    
    def _handle_task_announcement(self, msg: Dict, current_time: int, mesh):
        """Handle task announcement"""
        # Agents don't directly process task announcements in DCCBBA
        # They wait for forward announcements
        pass
    
    def _handle_forward_announcement(self, msg: Dict, current_time: int, mesh):
        """Handle forward announcement and compute bid"""
        task_id = msg.get("task_id", "")
        pickup = msg.get("pickup", "")
        delivery = msg.get("delivery", "")
        weight = float(msg.get("weight", 0.0))
        path = msg.get("path", [])
        
        # Compute bid
        bid = self.compute_bid({
            "task_id": task_id,
            "pickup": pickup,
            "delivery": delivery,
            "weight": weight
        }, {"current_time": current_time})
        
        # Update best bid if ours is better
        best = msg.get("best", {"bid": self.VERY_HIGH_BID, "holder": None})
        current_best = float(best.get("bid", self.VERY_HIGH_BID))
        
        if bid < current_best:
            best = {"bid": bid, "holder": self.id}
        
        # Forward to next agent
        if self.id not in path:
            path = path + [self.id]
        
        # Create forward message
        forward_msg = {
            "message_type": "FORWARD_ANNOUNCEMENT",
            "task_id": task_id,
            "pickup": pickup,
            "delivery": delivery,
            "weight": weight,
            "path": path,
            "best": best
        }
        
        mesh.send(self.id, forward_msg, sim_time=current_time)
    
    def _handle_winner_decision(self, msg: Dict):
        """Handle winner decision - assign task to this agent"""
        winner = msg.get("winner", "")
        task_id = msg.get("task_id", "")
        delivery = msg.get("delivery", "")
        
        if winner == self.id:
            # Add task to assigned tasks
            if not any(t[0] == task_id for t in self.assigned_tasks):
                self.assigned_tasks.append((task_id, delivery))
                print(f"[AGENT] {self.id} assigned task {task_id}")
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "id": self.id,
            "position": self.position,
            "battery": self.battery,
            "load": self.load,
            "capacity": self.capacity,
            "assigned_tasks": len(self.assigned_tasks),
            "completed_tasks": self.completed_tasks,
            "total_distance": self.total_distance
        }
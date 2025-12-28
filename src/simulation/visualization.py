"""
Visualization utilities for the simulation
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional

class SimulationVisualizer:
    """Visualization manager for simulation results"""
    
    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Output directory for visualizations
        """
        self.output_dir = output_dir
        import os
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_task_allocation(self, allocation_data: Dict[str, List[Dict]]):
        """
        Plot task allocation distribution
        
        Args:
            allocation_data: Task allocation data by agent
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        agents = list(allocation_data.keys())
        task_counts = [len(tasks) for tasks in allocation_data.values()]
        
        # Generate colors
        colors = plt.cm.tab10(np.linspace(0, 1, len(agents)))
        
        # Pie chart
        ax1.pie(task_counts, labels=agents, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Task Allocation Distribution')
        
        # Bar chart
        bars = ax2.bar(agents, task_counts, color=colors)
        ax2.set_title('Tasks per Vehicle')
        ax2.set_ylabel('Number of Tasks')
        ax2.set_xlabel('Vehicles')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/task_allocation.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_deadline_compliance(self, task_history: List[Dict]):
        """
        Plot deadline compliance
        
        Args:
            task_history: List of task completion records
        """
        if not task_history:
            return
        
        # Sort by completion time
        sorted_tasks = sorted(task_history, key=lambda x: x.get('completed_at', 0))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(1, len(sorted_tasks) + 1)
        deadlines = [t.get('due_by', 0) for t in sorted_tasks]
        completions = [t.get('completed_at', 0) for t in sorted_tasks]
        
        # Plot lines
        ax.plot(x, deadlines, 'b-', label='Deadline', linewidth=2, marker='o')
        ax.plot(x, completions, 'r-', label='Completed', linewidth=2, marker='s')
        
        # Fill between for on-time/late
        ax.fill_between(x, deadlines, completions,
                       where=[c <= d for c, d in zip(completions, deadlines)],
                       color='green', alpha=0.3, label='On Time')
        ax.fill_between(x, deadlines, completions,
                       where=[c > d for c, d in zip(completions, deadlines)],
                       color='red', alpha=0.3, label='Late')
        
        ax.set_xlabel('Task Index')
        ax.set_ylabel('Time (ticks)')
        ax.set_title('Deadline Compliance')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/deadline_compliance.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_vehicle_utilization(self, utilization_data: Dict[str, Dict]):
        """
        Plot vehicle utilization
        
        Args:
            utilization_data: Vehicle utilization data
        """
        if not utilization_data:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        agents = list(utilization_data.keys())
        
        # Plot 1: Distance traveled
        distances = [utilization_data[a].get('distance', 0) for a in agents]
        axes[0].bar(agents, distances, color='skyblue')
        axes[0].set_title('Distance Traveled')
        axes[0].set_ylabel('Distance')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Tasks completed
        tasks = [utilization_data[a].get('tasks_completed', 0) for a in agents]
        axes[1].bar(agents, tasks, color='lightgreen')
        axes[1].set_title('Tasks Completed')
        axes[1].set_ylabel('Number of Tasks')
        axes[1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Battery usage
        batteries = [utilization_data[a].get('battery_used', 0) for a in agents]
        axes[2].bar(agents, batteries, color='orange')
        axes[2].set_title('Battery Used')
        axes[2].set_ylabel('Battery %')
        axes[2].tick_params(axis='x', rotation=45)
        
        # Plot 4: Efficiency
        efficiencies = []
        for a in agents:
            dist = utilization_data[a].get('distance', 1)
            tasks_done = utilization_data[a].get('tasks_completed', 1)
            efficiencies.append(tasks_done / dist * 100 if dist > 0 else 0)
        
        axes[3].bar(agents, efficiencies, color='purple')
        axes[3].set_title('Efficiency (Tasks per Distance)')
        axes[3].set_ylabel('Efficiency Score')
        axes[3].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/vehicle_utilization.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def plot_communication_pattern(self, communication_log: List[Dict]):
        """
        Plot communication patterns
        
        Args:
            communication_log: List of communication events
        """
        if not communication_log:
            return
        
        # Extract data
        timestamps = []
        message_types = []
        senders = []
        receivers = []
        
        for event in communication_log:
            timestamps.append(event.get('timestamp', 0))
            message_types.append(event.get('type', 'unknown'))
            data = event.get('data', {})
            senders.append(data.get('sender', 'unknown'))
            receivers.append(data.get('receiver', 'unknown'))
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        # Plot 1: Messages over time
        axes[0].plot(timestamps, range(len(timestamps)), 'b-')
        axes[0].set_xlabel('Time')
        axes[0].set_ylabel('Cumulative Messages')
        axes[0].set_title('Communication Over Time')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Message type distribution
        type_counts = {}
        for msg_type in message_types:
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        axes[1].pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
        axes[1].set_title('Message Type Distribution')
        
        # Plot 3: Sender activity
        sender_counts = {}
        for sender in senders:
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        axes[2].bar(sender_counts.keys(), sender_counts.values())
        axes[2].set_title('Messages by Sender')
        axes[2].set_ylabel('Number of Messages')
        axes[2].tick_params(axis='x', rotation=45)
        
        # Plot 4: Communication network (simplified)
        unique_agents = set(senders + receivers)
        agent_indices = {agent: i for i, agent in enumerate(unique_agents)}
        
        comm_matrix = np.zeros((len(unique_agents), len(unique_agents)))
        
        for sender, receiver in zip(senders, receivers):
            if sender in agent_indices and receiver in agent_indices:
                i, j = agent_indices[sender], agent_indices[receiver]
                comm_matrix[i, j] += 1
        
        im = axes[3].imshow(comm_matrix, cmap='YlOrRd', aspect='auto')
        axes[3].set_title('Communication Matrix')
        axes[3].set_xlabel('Receiver')
        axes[3].set_ylabel('Sender')
        axes[3].set_xticks(range(len(unique_agents)))
        axes[3].set_yticks(range(len(unique_agents)))
        axes[3].set_xticklabels(list(unique_agents), rotation=45)
        axes[3].set_yticklabels(list(unique_agents))
        
        plt.colorbar(im, ax=axes[3])
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/communication_patterns.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def create_summary_report(self, metrics: Dict[str, Any]):
        """
        Create comprehensive summary report
        
        Args:
            metrics: All collected metrics
        """
        fig = plt.figure(figsize=(16, 12))
        
        # Overall metrics
        overall_text = f"""
        Simulation Summary
        ==================
        
        Total Tasks: {metrics.get('total_tasks', 0)}
        Completed: {metrics.get('completed_tasks', 0)}
        Deadline Hits: {metrics.get('deadline_hits', 0)}
        Deadline Misses: {metrics.get('deadline_misses', 0)}
        Success Rate: {metrics.get('success_rate', 0):.1f}%
        
        Total Distance: {metrics.get('total_distance', 0):.1f}
        Communication: {metrics.get('total_communication', 0)}
        
        Average Completion Time: {metrics.get('avg_completion_time', 0):.1f}
        Average Distance per Task: {metrics.get('avg_distance_per_task', 0):.1f}
        """
        
        plt.figtext(0.1, 0.95, overall_text, fontsize=12, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/summary_report.png', dpi=150, bbox_inches='tight')
        plt.close()
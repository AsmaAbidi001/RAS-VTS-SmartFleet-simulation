"""
Performance metrics and analysis utilities
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd
import os

class PerformanceMetrics:
    """Collect and analyze simulation performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'task_completion_times': [],
            'communication_overhead': 0,
            'total_distance': 0,
            'deadline_misses': 0,
            'deadline_hits': 0,
            'vehicle_utilization': {},
            'task_allocation': defaultdict(list)
        }
        
        self.start_time = datetime.now()
    
    def collect_final_metrics(self, simulation):
        """
        Collect final metrics from simulation
        
        Args:
            simulation: Simulation instance
        """
        # This would collect metrics from the completed simulation
        # For now, we'll implement basic metrics collection
        pass
    
    def record_task_completion(self, task_id: str, agent_id: str, 
                             assigned_at: float, completed_at: float,
                             deadline: float):
        """
        Record task completion metrics
        
        Args:
            task_id: Task identifier
            agent_id: Agent identifier
            assigned_at: Time task was assigned
            completed_at: Time task was completed
            deadline: Task deadline
        """
        duration = completed_at - assigned_at
        on_time = completed_at <= deadline
        
        self.metrics['task_completion_times'].append({
            'task_id': task_id,
            'agent_id': agent_id,
            'duration': duration,
            'on_time': on_time,
            'deadline': deadline,
            'completed_at': completed_at
        })
        
        if on_time:
            self.metrics['deadline_hits'] += 1
        else:
            self.metrics['deadline_misses'] += 1
    
    def record_communication(self, sender: str, receiver: str, message_size: int):
        """
        Record communication metrics
        
        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            message_size: Message size in bytes
        """
        self.metrics['communication_overhead'] += message_size
    
    def record_distance(self, agent_id: str, distance: float):
        """
        Record distance traveled
        
        Args:
            agent_id: Agent identifier
            distance: Distance traveled
        """
        if agent_id not in self.metrics['vehicle_utilization']:
            self.metrics['vehicle_utilization'][agent_id] = {
                'distance': 0,
                'tasks_completed': 0,
                'idle_time': 0
            }
        
        self.metrics['vehicle_utilization'][agent_id]['distance'] += distance
        self.metrics['total_distance'] += distance
    
    def record_task_allocation(self, task_id: str, agent_id: str, timestamp: float):
        """
        Record task allocation
        
        Args:
            task_id: Task identifier
            agent_id: Agent identifier
            timestamp: Allocation timestamp
        """
        self.metrics['task_allocation'][agent_id].append({
            'task_id': task_id,
            'timestamp': timestamp
        })
    
    def calculate_efficiency(self) -> Dict[str, float]:
        """
        Calculate efficiency metrics
        
        Returns:
            Dictionary of efficiency metrics
        """
        total_tasks = len(self.metrics['task_completion_times'])
        
        if total_tasks == 0:
            return {
                'deadline_success_rate': 0,
                'avg_completion_time': 0,
                'avg_communication_per_task': 0,
                'avg_distance_per_task': 0
            }
        
        # Deadline success rate
        success_rate = (self.metrics['deadline_hits'] / total_tasks) * 100
        
        # Average completion time
        avg_time = np.mean([t['duration'] for t in self.metrics['task_completion_times']])
        
        # Average communication per task
        avg_comm = self.metrics['communication_overhead'] / total_tasks
        
        # Average distance per task
        avg_dist = self.metrics['total_distance'] / total_tasks
        
        return {
            'deadline_success_rate': success_rate,
            'avg_completion_time': avg_time,
            'avg_communication_per_task': avg_comm,
            'avg_distance_per_task': avg_dist
        }
    
    def save_report(self, output_dir: str = "reports"):
        """
        Save metrics report
        
        Args:
            output_dir: Output directory for reports
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Calculate efficiency metrics
        efficiency = self.calculate_efficiency()
        
        # Save metrics to JSON
        report = {
            'summary': {
                'total_tasks': len(self.metrics['task_completion_times']),
                'deadline_hits': self.metrics['deadline_hits'],
                'deadline_misses': self.metrics['deadline_misses'],
                'total_communication': self.metrics['communication_overhead'],
                'total_distance': self.metrics['total_distance'],
                'simulation_duration': (datetime.now() - self.start_time).total_seconds()
            },
            'efficiency': efficiency,
            'vehicle_utilization': self.metrics['vehicle_utilization'],
            'task_allocation': dict(self.metrics['task_allocation'])
        }
        
        report_file = os.path.join(output_dir, f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate visualizations
        self.generate_visualizations(output_dir)
        
        print(f"Metrics report saved to {report_file}")
    
    def generate_visualizations(self, output_dir: str):
        """
        Generate visualization plots
        
        Args:
            output_dir: Output directory for plots
        """
        try:
            # Task completion timeline
            self.plot_task_completion_timeline(output_dir)
            
            # Deadline compliance
            self.plot_deadline_compliance(output_dir)
            
            # Vehicle utilization
            self.plot_vehicle_utilization(output_dir)
            
            # Task allocation distribution
            self.plot_task_allocation(output_dir)
            
        except Exception as e:
            print(f"Warning: Could not generate visualizations: {e}")
    
    def plot_task_completion_timeline(self, output_dir: str):
        """Plot task completion timeline"""
        if not self.metrics['task_completion_times']:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Group by agent
        agents = set(t['agent_id'] for t in self.metrics['task_completion_times'])
        colors = plt.cm.tab10(np.linspace(0, 1, len(agents)))
        
        for i, agent in enumerate(agents):
            agent_tasks = [t for t in self.metrics['task_completion_times'] if t['agent_id'] == agent]
            times = [t['completed_at'] for t in agent_tasks]
            tasks = list(range(1, len(times) + 1))
            
            ax.scatter(times, [i] * len(times), label=agent, color=colors[i], s=100)
        
        ax.set_xlabel('Time (ticks)')
        ax.set_ylabel('Vehicle')
        ax.set_yticks(range(len(agents)))
        ax.set_yticklabels(list(agents))
        ax.set_title('Task Completion Timeline')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'task_timeline.png'), dpi=150)
        plt.close()
    
    def plot_deadline_compliance(self, output_dir: str):
        """Plot deadline compliance"""
        if not self.metrics['task_completion_times']:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        tasks = sorted(self.metrics['task_completion_times'], key=lambda x: x['completed_at'])
        indices = range(1, len(tasks) + 1)
        deadlines = [t['deadline'] for t in tasks]
        completions = [t['completed_at'] for t in tasks]
        
        ax.plot(indices, deadlines, 'b-', label='Deadline', linewidth=2)
        ax.plot(indices, completions, 'r-', label='Completed', linewidth=2)
        
        # Fill area between lines
        ax.fill_between(indices, deadlines, completions, 
                       where=[c <= d for c, d in zip(completions, deadlines)],
                       color='green', alpha=0.3, label='On Time')
        ax.fill_between(indices, deadlines, completions,
                       where=[c > d for c, d in zip(completions, deadlines)],
                       color='red', alpha=0.3, label='Late')
        
        ax.set_xlabel('Task Index')
        ax.set_ylabel('Time (ticks)')
        ax.set_title('Deadline Compliance')
        ax.legend()
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'deadline_compliance.png'), dpi=150)
        plt.close()
    
    def plot_vehicle_utilization(self, output_dir: str):
        """Plot vehicle utilization"""
        if not self.metrics['vehicle_utilization']:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        agents = list(self.metrics['vehicle_utilization'].keys())
        distances = [self.metrics['vehicle_utilization'][a]['distance'] for a in agents]
        tasks = [self.metrics['vehicle_utilization'][a]['tasks_completed'] for a in agents]
        
        # Distance traveled
        bars1 = ax1.bar(agents, distances)
        ax1.set_title('Distance Traveled per Vehicle')
        ax1.set_ylabel('Distance')
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # Tasks completed
        bars2 = ax2.bar(agents, tasks)
        ax2.set_title('Tasks Completed per Vehicle')
        ax2.set_ylabel('Number of Tasks')
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'vehicle_utilization.png'), dpi=150)
        plt.close()
    
    def plot_task_allocation(self, output_dir: str):
        """Plot task allocation distribution"""
        if not self.metrics['task_allocation']:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        agents = list(self.metrics['task_allocation'].keys())
        task_counts = [len(self.metrics['task_allocation'][a]) for a in agents]
        
        # Pie chart
        ax1.pie(task_counts, labels=agents, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Task Allocation Distribution')
        
        # Bar chart
        bars = ax2.bar(agents, task_counts)
        ax2.set_title('Tasks per Vehicle')
        ax2.set_ylabel('Number of Tasks')
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'task_allocation.png'), dpi=150)
        plt.close()
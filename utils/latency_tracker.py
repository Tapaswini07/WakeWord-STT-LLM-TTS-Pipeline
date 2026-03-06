"""Latency tracking and measurement utilities."""

import time
from typing import Dict, List
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class LatencyMetric:
    """Stores latency metrics for a component."""
    component: str
    start_time: float
    end_time: float = 0.0
    duration: float = field(default=0.0, init=False)
    
    def __post_init__(self):
        if self.end_time > 0:
            self.duration = self.end_time - self.start_time


class LatencyTracker:
    """Tracks latency for various components of the voice assistant."""
    
    def __init__(self):
        self.metrics: Dict[str, List[LatencyMetric]] = defaultdict(list)
        self.active_timers: Dict[str, float] = {}
    
    def start(self, component: str) -> None:
        """Start timing a component."""
        self.active_timers[component] = time.time()
    
    def end(self, component: str) -> float:
        """End timing a component and return duration in ms."""
        if component not in self.active_timers:
            raise ValueError(f"Timer for {component} was never started")
        
        end_time = time.time()
        start_time = self.active_timers.pop(component)
        duration = end_time - start_time
        
        metric = LatencyMetric(
            component=component,
            start_time=start_time,
            end_time=end_time
        )
        self.metrics[component].append(metric)
        
        return duration * 1000  # Convert to milliseconds
    
    def get_stats(self, component: str) -> Dict:
        """Get statistics for a component."""
        if component not in self.metrics or not self.metrics[component]:
            return {}
        
        durations = [m.duration * 1000 for m in self.metrics[component]]
        
        return {
            'component': component,
            'count': len(durations),
            'avg_ms': sum(durations) / len(durations),
            'min_ms': min(durations),
            'max_ms': max(durations),
            'total_ms': sum(durations)
        }
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all components."""
        all_stats = {}
        for component in self.metrics:
            all_stats[component] = self.get_stats(component)
        return all_stats
    
    def print_report(self) -> None:
        """Print a formatted latency report."""
        print("\n" + "="*60)
        print("LATENCY REPORT")
        print("="*60)
        
        total_time = 0
        for component in sorted(self.metrics.keys()):
            stats = self.get_stats(component)
            if stats:
                print(f"\n{component}:")
                print(f"  Avg: {stats['avg_ms']:.2f}ms | "
                      f"Min: {stats['min_ms']:.2f}ms | "
                      f"Max: {stats['max_ms']:.2f}ms | "
                      f"Total: {stats['total_ms']:.2f}ms")
                total_time += stats['total_ms']
        
        print(f"\nTotal Processing Time: {total_time:.2f}ms")
        print("="*60 + "\n")
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.active_timers.clear()


# Global tracker instance
tracker = LatencyTracker()

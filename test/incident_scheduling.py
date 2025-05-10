"""
City Emergency Response Manager - Incident Scheduling Module
==========================================================
This module implements incident scheduling using Activity Selection and Knapsack algorithms,
along with incident sorting algorithms and logging capabilities.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import heapq
from dataclasses import dataclass, asdict
from enum import Enum


class IncidentType(Enum):
    FIRE = "Fire"
    MEDICAL = "Medical Emergency"
    TRAFFIC = "Traffic Accident"
    CRIME = "Criminal Activity"
    HAZMAT = "Hazardous Materials"
    NATURAL = "Natural Disaster"


class Priority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class Resource:
    type: str  # e.g., "Fire Truck", "Ambulance", "Police Car"
    quantity: int
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Resource quantity cannot be negative")


@dataclass
class Incident:
    id: str
    location: str
    time: datetime
    type: IncidentType
    priority: Priority
    required_resources: List[Resource]
    description: str
    estimated_duration: int  # in minutes
    assigned_resources: Optional[Dict[str, List[str]]] = None  # {resource_type: [resource_ids]}
    status: str = "PENDING"  # PENDING, ASSIGNED, IN_PROGRESS, COMPLETED
    completion_time: Optional[datetime] = None
    
    def to_dict(self):
        """Convert incident to dictionary for JSON serialization"""
        data = asdict(self)
        data['time'] = self.time.isoformat()
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        if self.completion_time:
            data['completion_time'] = self.completion_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create incident from dictionary"""
        data['time'] = datetime.fromisoformat(data['time'])
        data['type'] = IncidentType(data['type'])
        data['priority'] = Priority(data['priority'])
        if data.get('completion_time'):
            data['completion_time'] = datetime.fromisoformat(data['completion_time'])
        return cls(**data)


class IncidentScheduler:
    def __init__(self, log_file: str = "incident_log.json"):
        self.incidents = []
        self.log_file = log_file
        self.resource_inventory = {}  # {resource_type: [available_resource_ids]}
        self.load_incidents()
    
    def add_incident(self, incident: Incident):
        """Add a new incident to the scheduler"""
        self.incidents.append(incident)
        self.save_incidents()
        self.log_event(f"New incident added: {incident.id} at {incident.location}")
    
    def activity_selection_greedy(self, incidents: List[Incident]) -> List[Incident]:
        """
        Implements Activity Selection algorithm (greedy approach)
        Selects non-overlapping incidents based on their end times
        """
        if not incidents:
            return []
        
        sorted_incidents = sorted(incidents, 
                                  key=lambda x: x.time + timedelta(minutes=x.estimated_duration))
        
        selected = []
        last_end_time = None
        
        for incident in sorted_incidents:
            start_time = incident.time
            end_time = start_time + timedelta(minutes=incident.estimated_duration)
            
            if last_end_time is None or start_time >= last_end_time:
                selected.append(incident)
                last_end_time = end_time
        
        return selected
    
    def knapsack_incident_assignment(self, incidents: List[Incident], time_limit: int) -> List[Incident]:
        """
        Implements 0/1 Knapsack algorithm for incident assignment
        time_limit: maximum time available in minutes
        Returns: List of incidents that can be handled within time limit with maximum priority value
        """
        if not incidents or time_limit <= 0:
            return []
        
        n = len(incidents)
        dp = [[0 for _ in range(time_limit + 1)] for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            incident = incidents[i-1]
            duration = incident.estimated_duration
            priority_value = incident.priority.value
            
            for w in range(1, time_limit + 1):
                if duration <= w:
                    dp[i][w] = max(priority_value + dp[i-1][w-duration], dp[i-1][w])
                else:
                    dp[i][w] = dp[i-1][w]
        
        w = time_limit
        selected_incidents = []
        
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected_incidents.append(incidents[i-1])
                w -= incidents[i-1].estimated_duration
        
        return selected_incidents[::-1]
    
    def merge_sort_incidents(self, incidents: List[Incident], key_func) -> List[Incident]:
        """
        Merge Sort implementation for sorting incidents
        key_func: function to extract sorting key from incident
        """
        if len(incidents) <= 1:
            return incidents
        mid = len(incidents) // 2
        left = self.merge_sort_incidents(incidents[:mid], key_func)
        right = self.merge_sort_incidents(incidents[mid:], key_func)
        return self._merge(left, right, key_func)
    
    def _merge(self, left: List[Incident], right: List[Incident], key_func) -> List[Incident]:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if key_func(left[i]) <= key_func(right[j]):
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        result.extend(left[i:]); result.extend(right[j:])
        return result

    def quick_sort_incidents(self, incidents: List[Incident], key_func) -> List[Incident]:
        if len(incidents) <= 1:
            return incidents
        pivot = incidents[len(incidents) // 2]
        pivot_value = key_func(pivot)
        left = [x for x in incidents if key_func(x) < pivot_value]
        middle = [x for x in incidents if key_func(x) == pivot_value]
        right = [x for x in incidents if key_func(x) > pivot_value]
        return (self.quick_sort_incidents(left, key_func) + 
                middle + 
                self.quick_sort_incidents(right, key_func))

    def heap_sort_incidents(self, incidents: List[Incident], key_func) -> List[Incident]:
        if not incidents:
            return []
        heap = [(-key_func(incident), incident) for incident in incidents]
        heapq.heapify(heap)
        sorted_incidents = []
        while heap:
            _, incident = heapq.heappop(heap)
            sorted_incidents.append(incident)
        return sorted_incidents

    def sort_by_priority(self, algorithm: str = "merge") -> List[Incident]:
        if algorithm == "merge":
            return self.merge_sort_incidents(self.incidents, lambda x: -x.priority.value)
        elif algorithm == "quick":
            return self.quick_sort_incidents(self.incidents, lambda x: -x.priority.value)
        elif algorithm == "heap":
            return self.heap_sort_incidents(self.incidents, lambda x: x.priority.value)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def sort_by_time(self, algorithm: str = "merge") -> List[Incident]:
        if algorithm == "merge":
            return self.merge_sort_incidents(self.incidents, lambda x: x.time)
        elif algorithm == "quick":
            return self.quick_sort_incidents(self.incidents, lambda x: x.time)
        elif algorithm == "heap":
            return self.heap_sort_incidents(self.incidents, lambda x: x.time.timestamp())
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def sort_by_location(self, algorithm: str = "merge") -> List[Incident]:
        if algorithm == "merge":
            return self.merge_sort_incidents(self.incidents, lambda x: x.location)
        elif algorithm == "quick":
            return self.quick_sort_incidents(self.incidents, lambda x: x.location)
        elif algorithm == "heap":
            return self.heap_sort_incidents(self.incidents, lambda x: ord(x.location[0]) if x.location else 0)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def get_incidents_by_type(self, incident_type: IncidentType) -> List[Incident]:
        return [inc for inc in self.incidents if inc.type == incident_type]

    def get_incidents_by_status(self, status: str) -> List[Incident]:
        return [inc for inc in self.incidents if inc.status == status]

    def get_incidents_by_priority(self, priority: Priority) -> List[Incident]:
        return [inc for inc in self.incidents if inc.priority == priority]

    def get_pending_incidents(self) -> List[Incident]:
        pending = self.get_incidents_by_status("PENDING")
        return sorted(pending, key=lambda x: (-x.priority.value, x.time))

    def schedule_optimal_response(self, available_time: int) -> Dict[str, List[Incident]]:
        pending = self.get_pending_incidents()
        activity_selected = self.activity_selection_greedy(pending)
        knapsack_selected = self.knapsack_incident_assignment(pending, available_time)
        return {
            'activity_selection': activity_selected,
            'knapsack': knapsack_selected
        }

    def log_event(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open("incident_events.log", "a") as f:
            f.write(log_entry + "\n")

    def save_incidents(self):
        try:
            data = [incident.to_dict() for incident in self.incidents]
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.log_event(f"Error saving incidents: {str(e)}")

    def load_incidents(self):
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                self.incidents = [Incident.from_dict(item) for item in data]
        except FileNotFoundError:
            self.incidents = []
        except Exception as e:
            self.log_event(f"Error loading incidents: {str(e)}")
            self.incidents = []

    def generate_incident_report(self) -> Dict:
        total_incidents = len(self.incidents)
        if total_incidents == 0:
            return {"message": "No incidents to report"}
        status_counts = {}
        for incident in self.incidents:
            status_counts[incident.status] = status_counts.get(incident.status, 0) + 1
        type_counts = {}
        for incident in self.incidents:
            type_counts[incident.type.value] = type_counts.get(incident.type.value, 0) + 1
        priority_counts = {}
        for incident in self.incidents:
            priority_counts[incident.priority.value] = priority_counts.get(incident.priority.value, 0) + 1
        completed = [inc for inc in self.incidents if inc.status == "COMPLETED" and inc.completion_time]
        avg_response_time = 0
        if completed:
            total_time = sum((inc.completion_time - inc.time).total_seconds() / 60 for inc in completed)
            avg_response_time = total_time / len(completed)
        return {
            "total_incidents": total_incidents,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "priority_breakdown": priority_counts,
            "completed_incidents": len(completed),
            "average_response_time_minutes": round(avg_response_time, 2),
            "pending_incidents": len(self.get_pending_incidents())
        }
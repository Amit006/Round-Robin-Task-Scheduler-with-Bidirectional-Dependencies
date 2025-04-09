import threading
from collections import deque
from typing import Dict, List, Set

class Entity:
    def __init__(self, eid: str):
        self.id = eid
        self.execution_count = 0
        self.last_dependent_execution: Dict[str, int] = {}
        self.in_current_round = False

class Cin(Entity):
    def __init__(self, eid: str):
        super().__init__(eid)
        self.dependencies: List[str] = []
        self.reverse_dependencies: Set[str] = set()

class Din(Entity):
    def __init__(self, eid: str):
        super().__init__(eid)
        self.dependencies: List[str] = []
        self.reverse_dependencies: Set[str] = set()

class Scheduler:
    def __init__(self):
        self.cins: Dict[str, Cin] = {}
        self.dins: Dict[str, Din] = {}
        self.cin_queue = deque()
        self.din_queue = deque()
        self.lock = threading.Lock()
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def add_cin(self, cin_id: str, dependencies: List[str]):
        with self.lock:
            if cin_id in self.cins:
                return
            cin = Cin(cin_id)
            for din_id in dependencies:
                if din_id in self.dins:
                    cin.dependencies.append(din_id)
                    self.dins[din_id].reverse_dependencies.add(cin_id)
            self.cins[cin_id] = cin
            self.cin_queue.append(cin_id)

    def remove_cin(self, cin_id: str):
        with self.lock:
            if cin_id not in self.cins:
                return
            cin = self.cins.pop(cin_id)
            for din_id in cin.dependencies:
                if din_id in self.dins:
                    self.dins[din_id].reverse_dependencies.discard(cin_id)
            for din_id in cin.reverse_dependencies:
                if din_id in self.dins:
                    din = self.dins[din_id]
                    if cin_id in din.dependencies:
                        din.dependencies.remove(cin_id)
            self.cin_queue = deque([cid for cid in self.cin_queue if cid != cin_id])

    def add_din(self, din_id: str, dependencies: List[str]):
        with self.lock:
            if din_id in self.dins:
                return
            din = Din(din_id)
            for cin_id in dependencies:
                if cin_id in self.cins:
                    din.dependencies.append(cin_id)
                    self.cins[cin_id].reverse_dependencies.add(din_id)
            self.dins[din_id] = din
            self.din_queue.append(din_id)

    def remove_din(self, din_id: str):
        with self.lock:
            if din_id not in self.dins:
                return
            din = self.dins.pop(din_id)
            for cin_id in din.dependencies:
                if cin_id in self.cins:
                    self.cins[cin_id].reverse_dependencies.discard(din_id)
            for cin_id in din.reverse_dependencies:
                if cin_id in self.cins:
                    cin = self.cins[cin_id]
                    if din_id in cin.dependencies:
                        cin.dependencies.remove(din_id)
            self.din_queue = deque([did for did in self.din_queue if did != din_id])

    def _is_cin_eligible(self, cin: Cin) -> bool:
        for din_id in cin.dependencies:
            if self.dins[din_id].execution_count <= cin.last_dependent_execution.get(din_id, 0):
                return False
        return True

    def _is_din_eligible(self, din: Din) -> bool:
        for cin_id in din.dependencies:
            if self.cins[cin_id].execution_count <= din.last_dependent_execution.get(cin_id, 0):
                return False
        return True

    def _execute_cin(self, cin_id: str):
        cin = self.cins[cin_id]
        if not self._is_cin_eligible(cin) or cin.in_current_round:
            return False
        cin.in_current_round = True
        cin.execution_count += 1
        for din_id in cin.dependencies:
            cin.last_dependent_execution[din_id] = self.dins[din_id].execution_count
        print(f"Executed Cin {cin_id} (count: {cin.execution_count})")
        for din_id in cin.reverse_dependencies:
            din = self.dins[din_id]
            if self._is_din_eligible(din):
                self.din_queue.append(din_id)
        return True

    def _execute_din(self, din_id: str):
        din = self.dins[din_id]
        if not self._is_din_eligible(din) or din.in_current_round:
            return False
        din.in_current_round = True
        din.execution_count += 1
        for cin_id in din.dependencies:
            din.last_dependent_execution[cin_id] = self.cins[cin_id].execution_count
        print(f"Executed Din {din_id} (count: {din.execution_count})")
        for cin_id in din.reverse_dependencies:
            cin = self.cins[cin_id]
            if self._is_cin_eligible(cin):
                self.cin_queue.append(cin_id)
        return True

    def _reset_round_flags(self):
        for cin in self.cins.values():
            cin.in_current_round = False
        for din in self.dins.values():
            din.in_current_round = False

    def run_scheduler(self):
        while True:
            executed = False
            for _ in range(len(self.cin_queue)):
                cin_id = self.cin_queue.popleft()
                if self._execute_cin(cin_id):
                    executed = True
                    self.cin_queue.append(cin_id)
                    break
                self.cin_queue.append(cin_id)
            for _ in range(len(self.din_queue)):
                din_id = self.din_queue.popleft()
                if self._execute_din(din_id):
                    executed = True
                    self.din_queue.append(din_id)
                    break
                self.din_queue.append(din_id)
            if not executed:
                print("Deadlock detected. No entities could be executed.")
                break
            self._reset_round_flags()

# Example Usage
scheduler = Scheduler()
scheduler.add_cin("A", ["B"])
scheduler.add_din("B", ["A"])

# Let the scheduler run (in practice, this would run indefinitely)
import time
time.sleep(2)
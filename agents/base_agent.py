from abc import ABC, abstractmethod
import uuid

class BaseAgent(ABC):
    """
    Abstract base class for agents.
    All agents must implement the run() method.
    """
    def __init__(self, name='base_agent', id=None, properties={}, **kwargs):
        """
        The BaseAgent processes name, id and properties, other arguments are ignored and wait for the inheriting class to process.
        """
        self.name = name
        if id:
            self.id = id
        else:
            self.id = str(hex(uuid.uuid4().fields[0]))[2:]
        self._initialize(properties=properties)

    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)
    
    def _initialize_properties(self):
        self.properties = {}

    def _update_properties(self, properties=None):
        if properties is None:
            return
        # override
        for p in properties:
            self.properties[p] = properties[p]

    @abstractmethod
    def run(self, *args, **kwargs) -> dict:
        """
        Execute the agent's task.
        """
        pass
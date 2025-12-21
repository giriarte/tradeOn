import typing as t
from abc import ABC, abstractmethod

class Indicator(ABC):
    """
    Interface for a trading strategy, defining the required attributes and methods
    to be implemented by any concrete strategy (e.g., RSIStrategy, MACDStrategy).
    """
    
    # --- ATTRIBUTES (Class Variables or Properties for definition) ---
    name: str = ""
    params: t.Dict[str, t.Any] = {}

    def __init__(self, name: str, params: t.Dict[str, t.Any] = None):
        self.name = name
        self.params = params if params is not None else {}

    # --- ABSTRACT METHOD ---

    @abstractmethod
    def evaluate(self, data: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        """
        The core method to evaluate the strategy against the latest data and 
        return a trading signal (Position).
        
        Args:
            data: The current market data (e.g., a pandas DataFrame).
            params: Optional dictionary of parameters to override the default ones.
            
        Returns:
            signal (int): The generated trading signal (0=Hold, 1=Buy, 2=Sell).
        """
        raise NotImplementedError
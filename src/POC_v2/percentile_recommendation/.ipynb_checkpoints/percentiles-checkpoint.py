from commons.static_getters import StaticGetters

class Percentiles:
    _instance = None
    
    unique_demand = []
    green_percentiles_demand_costs = []
    
    peak_demand = []
    off_peak_demand = []
    blue_percentiles_demand_costs = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Percentiles, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

    def save_unique(self, unique, cost):
        self.unique_demand.append(unique)
        self.green_percentiles_demand_costs.append(cost)

    def save_demands(self, peak, off_peak, cost):
        self.peak_demand.append(peak)
        self.off_peak_demand.append(off_peak)
        self.blue_percentiles_demand_costs.append(cost)

    def get_green(self):
        return self.unique_demand, self.green_percentiles_demand_costs

    def get_blue(self):
        return self.peak_demand, self.off_peak_demand, self.blue_percentiles_demand_costs

    def clear(self):
        self.unique_demand.clear()
        self.green_percentiles_demand_costs.clear()
        self.peak_demand.clear()
        self.off_peak_demand.clear()
        self.blue_percentiles_demand_costs.clear()
        
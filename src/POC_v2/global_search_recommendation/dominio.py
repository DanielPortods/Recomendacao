from commons.Tariff import BlueTariff, GreenTariff, GREEN, BLUE
from commons.static_getters import StaticGetters
from pandas import DataFrame, to_numeric

class Dominio:
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Dominio, cls).__new__(cls)
        return cls._instance        
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.green = GreenTariff()
            self.blue = BlueTariff()

    def insert_new_history(self, history: DataFrame):
        self.hist = history.drop(columns=['year', 'month', 'contract_peak_demand_in_kw', 'contract_off_peak_demand_in_kw', 'cost_reais'])
        self.consumption_cost_on_blue = StaticGetters.get_comsuption_cost(self.hist, BlueTariff()).sum()
        self.consumption_cost_on_green = StaticGetters.get_comsuption_cost(self.hist, GreenTariff()).sum()

    def calc_exceeded_demand_values(self, tariff, contracted_demands, current) -> .0:
        if tariff == GREEN:
            if current:
                return (3 * (self.hist.peak_exceeded_in_kw + self.hist.off_peak_exceeded_in_kw)).sum()
            
            peak_exceeded = (self.hist.peak_measured_demand_in_kw - contracted_demands[0]).clip(0)
            off_peak_exceeded = (self.hist.off_peak_measured_demand_in_kw - contracted_demands[0]).clip(0)
            return (3 * (peak_exceeded + off_peak_exceeded)).sum()
        else:
            if current:
                return (3 * self.hist.peak_exceeded_in_kw).sum(), (3 * self.hist.off_peak_exceeded_in_kw).sum()
            
            peak_exceeded = (self.hist.peak_measured_demand_in_kw - contracted_demands[0]).clip(0)
            off_peak_exceeded = (self.hist.off_peak_measured_demand_in_kw - contracted_demands[1]).clip(0)
            return (3 * (peak_exceeded)).sum(), (3 * (off_peak_exceeded)).sum()

    def green_objective_func(self, x, current = False) -> .0:
        value = len(self.hist) * x[0] + self.calc_exceeded_demand_values(GREEN, x, current)
        return self.green.na_tusd_in_reais_per_kw * value + self.consumption_cost_on_green 

    def blue_objective_func(self, x, current = False) -> .0 :
        exceeded_values = self.calc_exceeded_demand_values(BLUE, x, current)
        value_i = len(self.hist) * x[0] + exceeded_values[0]
        value_ii = len(self.hist) * x[1] + exceeded_values[1]

        return (self.blue.peak_tusd_in_reais_per_kw * value_i) + \
               (self.blue.off_peak_tusd_in_reais_per_kw * value_ii) + self.consumption_cost_on_blue 
    
    def _exceeded_demand (self, meassured_demand: .0, contracted_demand: .0) :
        return max(.0, meassured_demand - contracted_demand)
    
    def green_objective_func_it(self, demands) -> .0 :
        demand_value = 0
        demand = round(demands[0])
        for bill in self.hist.values:
            demand_value += demand + 3 * (self._exceeded_demand(bill[2], demand) + \
                            self._exceeded_demand(bill[3], demand))

        return float(self.green.na_tusd_in_reais_per_kw) * demand_value + self.consumption_cost_on_green - demand

    def blue_objective_func_it(self, demands) -> .0 :
        peak_demand_value = 0
        off_peak_demand_value = 0
        peak_demand, off_peak_demand = round(demands[0]), round(demands[1])
        for bill in self.hist.values:
            peak_demand_value += peak_demand + 3 * self._exceeded_demand(bill[2], peak_demand)
            off_peak_demand_value += off_peak_demand + 3 * self._exceeded_demand(bill[3], off_peak_demand)

        return (float(self.blue.peak_tusd_in_reais_per_kw) * peak_demand_value) + \
               (float(self.blue.off_peak_tusd_in_reais_per_kw) * off_peak_demand_value) + self.consumption_cost_on_blue - \
               peak_demand - off_peak_demand
    
    def get_current_value(self, tariff, demand):
        if tariff == GREEN:
            return ['Atual', 'Verde', 0, 0, demand[0], round(self.green_objective_func_it(demand) + demand[0], 2), len(self.hist), '--']
        else:
            return ['Atual', 'Azul', demand[0], demand[1], 0, round(self.blue_objective_func_it(demand) + demand[0] + demand[1], 2), len(self.hist), '--']

    def save_pso_records(self, blue, green):
        self.pso_blue_record = blue
        self.pso_green_record = green

    def save_ga_records(self, blue, green):
        self.ga_blue_record = blue
        self.ga_green_record = green

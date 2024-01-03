from tariffs import BlueTariff, GreenTariff
from pandas import DataFrame

class Dominio:
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Dominio, cls).__new__(cls)
        return cls._instance        
    
    def __init__(self)  :
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.green = GreenTariff()
            self.blue = BlueTariff()

    def insert_new_history(self, history: DataFrame):
        self.hist = history[['peak_measured_demand_in_kw',
                             'off_peak_measured_demand_in_kw',
                             'contract_peak_demand_in_kw', 
                             'contract_off_peak_demand_in_kw']]\
                            .values.astype(float)

    def exceeded_demand (self, meassured_demand: .0, contracted_demand: .0) -> .0 :
        if meassured_demand <= contracted_demand :
            return 0
        else :
            return  meassured_demand - contracted_demand

    def green_objective_func(self, x) -> .0 :
        value = 0
        for i in self.hist:
            value += x[0] + 3 * (self.exceeded_demand(i[0], x[0]) + \
                                 self.exceeded_demand(i[1], x[0]))

        return self.green.na_tusd_in_reais_per_kw * value

    def blue_objective_func(self, x) -> .0 :
        value_i = 0
        value_ii = 0
        for i in self.hist:
            value_i += x[0] + 3 * self.exceeded_demand(i[0], x[0])
            value_ii += x[1] + 3 * self.exceeded_demand(i[1], x[1])

        return (self.blue.peak_tusd_in_reais_per_kw * value_i) + \
               (self.blue.off_peak_tusd_in_reais_per_kw * value_ii)

    def green_real_value(self) -> .0 :
        value = 0
        for i in self.hist:
            demand = i[3] if i[2] == 0 else i[2]
            value += demand + 3 * (self.exceeded_demand(i[0], demand) + self.exceeded_demand(i[1], demand))

        return self.green.na_tusd_in_reais_per_kw * value

    def blue_real_value(self) -> .0 :
        value_i = 0
        value_ii = 0
        for i in self.hist:
            value_i += i[2] + 3 * self.exceeded_demand(i[0], i[2])
            value_ii += i[3] + 3 * self.exceeded_demand(i[1], i[3])

        return (self.blue.peak_tusd_in_reais_per_kw * value_i) + (self.blue.off_peak_tusd_in_reais_per_kw * value_ii)

from tariffs import BlueTariff, GreenTariff
from pandas import DataFrame

class Dominio:        

    def __init__(self, history: DataFrame):
        self.hist = history[['peak_consumption_in_kwh','off_peak_consumption_in_kwh'
                             'peak_measured_demand_in_kw','off_peak_measured_demand_in_kw',
                             'contract_peak_demand_in_kw', 'contract_off_peak_demand_in_kw']].values.astype(float)

    def exceeded_demand (self, meassured_demand: .0, contracted_demand: .0) -> .0:
        if meassured_demand <= contracted_demand :
            return 0
        else :
            return  meassured_demand - contracted_demand

    def green_calc(self, x = None) -> .0:
        value = 0
        for i in self.hist:
            demand = x[0] if x != None else i[5]
            value += demand + 3 * (self.exceeded_demand(i[2], demand) +
                                   self.exceeded_demand(i[3], demand))

        return GreenTariff().na_tusd_in_reais_per_kw * value

    def blue_calc(self, x = None) -> .0:
        value_p, value_op = 0, 0
        for i in self.hist:
            demand_p, deman_op = (x[0], x[1]) if x != None else (i[4], i[5])
            value_p += demand_p + 3 * self.exceeded_demand(i[2], demand_p)
            value_op += deman_op + 3 * self.exceeded_demand(i[3], deman_op)

        return (BlueTariff().peak_tusd_in_reais_per_kw * value_p) + (BlueTariff().off_peak_tusd_in_reais_per_kw * value_op)
    
    def get_consumption_cost(self, tariff) -> .0:
        cost = 0
        for i in self.hist:
            cost += i[0] * (tariff.peak_tusd_in_reais_per_mwh + tariff.peak_te_in_reais_per_mwh)/1000 + \
                    i[1] * (tariff.off_peak_tusd_in_reais_per_mwh + tariff.off_peak_te_in_reais_per_mwh)/1000
        return cost
    
    def get_limits(self, tariff) -> list:
        p_lbound = self.hist['peak_measured_demand_in_kw'].min()
        o_lbound = self.hist['off_peak_measured_demand_in_kw'].min()
        p_ubound = self.hist['peak_measured_demand_in_kw'].max()
        o_ubound = self.hist['off_peak_measured_demand_in_kw'].max()
        if isinstance(tariff, GreenTariff):
            g_lb = min(p_lbound, o_lbound)
            g_ub = max(p_ubound, o_ubound)
            return [g_lb, g_ub]
        return[(p_lbound, p_ubound), (o_lbound, o_ubound)]

    
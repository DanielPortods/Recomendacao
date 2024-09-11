from pandas import DataFrame

from commons.headers import CONSUMPTION_HISTORY_HEADERS, CURRENT_CONTRACT_HEADERS, RECOMMENDATION_FRAME_HEADERS
from commons.Tariff import BlueTariff, GreenTariff, BLUE, GREEN

class StaticGetters:
    
    @staticmethod
    def get_comsuption_cost(history: DataFrame, tariff):
        return history.peak_consumption_in_kwh * float(tariff.peak_tusd_in_reais_per_mwh + tariff.peak_te_in_reais_per_mwh) / 1000 \
               + history.off_peak_consumption_in_kwh * float(tariff.off_peak_tusd_in_reais_per_mwh + tariff.off_peak_te_in_reais_per_mwh) / 1000
    
    @staticmethod
    def get_exceeded_demand_column(measured_demand, contracted_demand):
        return (measured_demand - contracted_demand).clip(0)
    
    @classmethod
    def get_demand_cost(cls, tariff, history: DataFrame, demand_values):        
        if tariff == GREEN:
            demand = demand_values[1]
            exceeded_val = (3 * (history.peak_exceeded_in_kw + history.off_peak_exceeded_in_kw)).sum()
            return (demand + exceeded_val) * GreenTariff().na_tusd_in_reais_per_kw
        elif tariff == BLUE:
            (peak_demand, off_peak_demand) = (demand_values[0], demand_values[1])
            value_peak = peak_demand + 3 * cls.get_exceeded_demand_column(history.peak_measured_demand_in_kw, peak_demand)
            value_off_peak = off_peak_demand + 3 * cls.get_exceeded_demand_column(history.off_peak_measured_demand_in_kw, off_peak_demand) # Checar a utilização da coluna de ultrapassagem
            return (BlueTariff().peak_tusd_in_reais_per_kw * value_peak) + (BlueTariff().off_peak_tusd_in_reais_per_kw * value_off_peak)
    
    """ @classmethod
    def get_demand_cost(cls, tariff history: DataFrame, demand_values):        
        if tariff.is_green():
            tariff = tariff.as_green_tariff()
            demand = demand_values[1]
            exceeded_sum = cls.get_exceeded_demand_column(history.peak_measured_demand_in_kw, demand) + \
                           cls.get_exceeded_demand_column(history.off_peak_measured_demand_in_kw, demand)   # Checar a utilização da coluna de ultrapassagem
            exceeded_val = exceeded_sum * 3
            return (demand + exceeded_val) * tariff.na_tusd_in_reais_per_kw
        elif tariff.is_blue():
            tariff = tariff.as_blue_tariff()
            (peak_demand, off_peak_demand) = (demand_values[0], demand_values[1])
            value_peak = peak_demand + 3 * cls.get_exceeded_demand_column(history.peak_measured_demand_in_kw, peak_demand)
            value_off_peak = off_peak_demand + 3 * cls.get_exceeded_demand_column(history.off_peak_measured_demand_in_kw, off_peak_demand) # Checar a utilização da coluna de ultrapassagem
            return (tariff.peak_tusd_in_reais_per_kw * value_peak) + (tariff.off_peak_tusd_in_reais_per_kw * value_off_peak)

    ## REFACTOR: tanto current quanto recommended possuem algumas colunas em comun, dá pra reutilizar melhor o código
    @classmethod
    def calculate_current_contract(cls, history: DataFrame, tariff):
        current_contract = DataFrame(columns=CURRENT_CONTRACT_HEADERS)
        current_contract.date = history.date
        current_contract.consumption_cost_in_reais = cls.get_comsuption_cost(history, tariff)
        demand_values = (history['contract_peak_demand_in_kw'], history['contract_off_peak_demand_in_kw'])
        current_contract.demand_cost_in_reais = cls.get_demand_cost(tariff, history, demand_values)
        current_contract.cost_in_reais = \
            current_contract.consumption_cost_in_reais + current_contract.demand_cost_in_reais

        current_contract.percentage_consumption = \
            current_contract.consumption_cost_in_reais / current_contract.cost_in_reais

        current_contract.percentage_demand = \
            current_contract.demand_cost_in_reais / current_contract.cost_in_reais
       
        return current_contract
    
    @classmethod
    def get_recommendation_frame(cls, history: DataFrame, values: tuple, tariff: ):
        recommendation_frame = DataFrame(columns=RECOMMENDATION_FRAME_HEADERS)
        recommendation_frame.date = history.date
        recommendation_frame.peak_demand_in_kw = values[0]
        recommendation_frame.off_peak_demand_in_kw = values[1]
        recommendation_frame.consumption_cost_in_reais = cls.get_comsuption_cost(history, tariff)
        recommendation_frame.demand_cost_in_reais = cls.get_demand_cost(tariff, history, values)

        recommendation_frame.contract_cost_in_reais = \
            recommendation_frame.consumption_cost_in_reais + recommendation_frame.demand_cost_in_reais

        recommendation_frame.percentage_consumption = \
            recommendation_frame.consumption_cost_in_reais / recommendation_frame.contract_cost_in_reais

        recommendation_frame.percentage_demand = \
            recommendation_frame.demand_cost_in_reais / recommendation_frame.contract_cost_in_reais
       
        return recommendation_frame """
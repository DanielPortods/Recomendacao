from typing import Literal
from pandas import DataFrame
from percentile_recommendation.green import GreenPercentileCalculator, GreenPercentileResult
from percentile_recommendation.blue import BluePercentileCalculator, BluePercentileResult
from commons.Tariff import BlueTariff, GreenTariff
import time

class ContractRecommendationResult:
    def __init__(self):
        self.tariff_flag = ''
        self.off_peak_demand_in_kw = .0
        self.peak_demand_in_kw = .0
        self.total = .0 
        self.unique_tariff = .0

class ContractRecommendationCalculator:
    HEADERS = ['date', 'peak_demand_in_kw', 'off_peak_demand_in_kw',
               'consumption_cost_in_reais', 'demand_cost_in_reais',
               'contract_cost_in_reais',
               'percentage_consumption', 'percentage_demand',
               'absolute_difference', 'percentage_difference']

    def __init__(
        self,
        consumption_history: DataFrame,
        blue_summary: BluePercentileResult,
        green_summary: GreenPercentileResult,
        current_tariff_flag: Literal['blue', 'green'],
        green_tariff: GreenTariff,
        blue_tariff: BlueTariff,
    ):
        self.green_tariff = green_tariff
        self.blue_tariff = blue_tariff
        self.consumption_history = consumption_history
        self.current_tariff_flag = current_tariff_flag
        self.blue_summary = blue_summary
        self.green_summary = green_summary

    def calculate(self):
        rec = ContractRecommendationResult()
        
        if self.blue_summary.total_total_cost_in_reais < self.green_summary.total_total_cost_in_reais:
            rec.tariff_flag = 'Azul'
            rec.off_peak_demand_in_kw = self.blue_summary.off_peak_demand_in_kw[0]
            rec.peak_demand_in_kw = self.blue_summary.peak_demand_in_kw[0]
            rec.total = self.blue_summary.total_total_cost_in_reais.sum()
        else:
            rec.tariff_flag = 'Verde'
            #rec.off_peak_demand_in_kw = self.green_summary.off_peak_demand_in_kw[0]
            #rec.peak_demand_in_kw = self.green_summary.off_peak_demand_in_kw[0]
            rec.unique_tariff = self.green_summary.off_peak_demand_in_kw[0]
            rec.total = self.green_summary.total_total_cost_in_reais.sum()
            
        return rec


class RecommendationResult:
    recommended_contract = ContractRecommendationResult
    ...

class RecommendationCalculator:
    def __init__(
        self,
        consumption_history: DataFrame,
        current_tariff_flag: str,
        blue_tariff: BlueTariff,
        green_tariff: GreenTariff,
        head_num: int
    ):
        self.current_tariff = current_tariff_flag
        self.blue_tariff = blue_tariff
        self.green_tariff = green_tariff
        self.consumption_history = consumption_history
        self.head_num = head_num

        self.blue_calculator = BluePercentileCalculator(consumption_history, blue_tariff)
        self.green_calculator = GreenPercentileCalculator(consumption_history, green_tariff)
        #display(consumption_history)

    def calculate(self, partial = False):
        '''Essa função ainda deve voltar um RecommendationResult, manipulando
        ou incluindo ContractRecommendationResult'''
        start_at = time.time()
        b_result = self.blue_calculator.calculate()
        g_result = self.green_calculator.calculate()

        if partial:
            return {'green':[g_result.summary.off_peak_demand_in_kw.loc[0], round(g_result.summary.total_total_cost_in_reais, 2)], 
                    'blue':[b_result.summary.peak_demand_in_kw.loc[0], b_result.summary.off_peak_demand_in_kw.loc[0], round(b_result.summary.total_total_cost_in_reais, 2)], 
                    'best':'green' if g_result.summary.total_total_cost_in_reais <= b_result.summary.total_total_cost_in_reais else 'blue'}

        rec_calculator = ContractRecommendationCalculator(
            self.consumption_history,
            b_result.summary,
            g_result.summary,
            self.current_tariff,
            self.green_tariff,
            self.blue_tariff,
        )
        
        
        rec = rec_calculator.calculate()
        end_at = time.time()
        
        return ['Percentil', rec.tariff_flag, round(rec.peak_demand_in_kw), round(rec.off_peak_demand_in_kw), \
                round(rec.unique_tariff), round(rec.total, 2), self.head_num, end_at - start_at]

from math import inf
from pandas import DataFrame
from numpy import ceil as roundup

from commons.Tariff import GreenTariff

from percentile_recommendation.percentiles import Percentiles

class GreenPercentileResult:
    def __init__(self, p: 'dict[str, DataFrame]', s: DataFrame):
        self.percentiles = p
        self.summary = s

class GreenPercentileCalculator():
    PERCENTILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98]
    PERCENTILE_HEADERS = ['off_peak_demand_in_kw',
                          'exceeded_peak_demand_in_kw', 'exceeded_off_peak_demand_in_kw',
                          'demand_total_cost_in_reais', 'total_in_reais']
    SUMMARY_HEADERS = ['consumption_cost_in_reais', 'demand_cost_in_reais',
                       'total_cost_in_reais',
                       'off_peak_demand_in_kw',
                       'exceeded_peak_demand_in_kw', 'exceeded_off_peak_demand_in_kw']

    def __init__(self, consumption_history: DataFrame, tariff: GreenTariff) -> None:
        self.consumption_history = consumption_history
        self.history_length = len(consumption_history.index)
        self.tariff = tariff

    def calculate(self) -> GreenPercentileResult:
        percentiles = self.__calculate_percentiles()
        summary = self.__calculate_summary(percentiles)
        return GreenPercentileResult(percentiles, summary)

    def __calculate_percentiles(self):
        percentiles: dict[str, DataFrame] = {}
        for p in self.PERCENTILES:
            p_str = str(p)
            percentiles[p_str] = DataFrame(columns=self.PERCENTILE_HEADERS)

            # Calcula percentil fora de pico
            off_peak_demand_in_kw = self \
                .consumption_history.off_peak_measured_demand_in_kw.quantile(p)
        
            percentiles[p_str].off_peak_demand_in_kw = [off_peak_demand_in_kw]*self.history_length

            # Ultrapassagem = max(0, demanda_medida - demanda_percentil)
            percentiles[p_str].exceeded_peak_demand_in_kw = \
                self.consumption_history.peak_measured_demand_in_kw - percentiles[p_str].off_peak_demand_in_kw
            percentiles[p_str].exceeded_peak_demand_in_kw = percentiles[p_str] \
                .exceeded_peak_demand_in_kw.clip(.0)

            # Ultrapassagem = max(0, demanda_medida - demanda_percentil)
            percentiles[p_str].exceeded_off_peak_demand_in_kw = \
                self.consumption_history.off_peak_measured_demand_in_kw \
                - percentiles[p_str].off_peak_demand_in_kw
            percentiles[p_str].exceeded_off_peak_demand_in_kw = percentiles[p_str]\
                .exceeded_off_peak_demand_in_kw.clip(.0)

            # Tem como colocar green_na_tusd_in_reais_per_kw em evidencia
            percentiles[p_str].demand_total_cost_in_reais = \
                self.tariff.na_tusd_in_reais_per_kw*percentiles[p_str].off_peak_demand_in_kw\
                + 3*self.tariff.na_tusd_in_reais_per_kw\
                * (percentiles[p_str].exceeded_peak_demand_in_kw+percentiles[p_str].exceeded_off_peak_demand_in_kw)

            # Calcular totais de valor
            percentiles[p_str].total_in_reais = percentiles[p_str].demand_total_cost_in_reais.sum()

            Percentiles().save_unique(off_peak_demand_in_kw, percentiles[p_str].demand_total_cost_in_reais.sum())
        return percentiles

    def __calculate_percentile(self, percentiles: 'dict[str, DataFrame]', p: float, p_str: str):
        column = 'off_peak_demand_in_kw'
        demand_percentile = self \
            .consumption_history[f'measured_{column}'].quantile(p)
        percentiles[p_str][column] = [demand_percentile]*self.history_length

    def __calculate_summary(self, percentiles: 'dict[str, DataFrame]'):
        summary = DataFrame(columns=self.SUMMARY_HEADERS)

        min_p_str, \
            smallest_total_demand_cost_in_reais = self.__find_percentile_with_smallest_total_demand(percentiles)

        SAFETY_MARGIN = 1.0
        # TODO: O ideal é que demand_[off_]peak_in_kw fosse apenas um valor no
        # "resumo" e não uma coluna inteira
        
        summary.smallest_total_demand_cost_in_reais = smallest_total_demand_cost_in_reais
        summary.off_peak_demand_in_kw = SAFETY_MARGIN * percentiles[min_p_str].off_peak_demand_in_kw
        summary.off_peak_demand_in_kw = summary.off_peak_demand_in_kw.apply(roundup)
        
        summary.exceeded_peak_demand_in_kw = (self.consumption_history.peak_measured_demand_in_kw - summary.off_peak_demand_in_kw).clip(.0)
        summary.exceeded_off_peak_demand_in_kw = self.consumption_history.off_peak_measured_demand_in_kw - summary.off_peak_demand_in_kw
        summary.exceeded_off_peak_demand_in_kw = summary.exceeded_off_peak_demand_in_kw.clip(.0)

        #summary.consumption_cost_in_reais = \
        #    self.consumption_history.peak_consumption_in_kwh * \
        #    (self.tariff.peak_tusd_in_reais_per_mwh+self.tariff.peak_te_in_reais_per_mwh)\
        #    / 1000\
        #    + self.consumption_history.off_peak_consumption_in_kwh * \
        #    (self.tariff.off_peak_tusd_in_reais_per_mwh+self.tariff.off_peak_te_in_reais_per_mwh)\
        #    / 1000

        # Calculate consumption cost in reais

        tp = self.tariff.peak_tusd_in_reais_per_mwh + self.tariff.peak_te_in_reais_per_mwh
        tp /= 1000
        peak_consumption_cost = self.consumption_history.peak_consumption_in_kwh * tp            

        top = self.tariff.off_peak_tusd_in_reais_per_mwh + self.tariff.off_peak_te_in_reais_per_mwh
        top /= 1000
        off_peak_consumption_cost = self.consumption_history.off_peak_consumption_in_kwh * top

        summary.consumption_cost_in_reais = peak_consumption_cost + off_peak_consumption_cost

        summary.demand_cost_in_reais = \
            self.tariff.na_tusd_in_reais_per_kw*summary.off_peak_demand_in_kw\
            + 3*self.tariff.na_tusd_in_reais_per_kw *\
            (summary.exceeded_off_peak_demand_in_kw + summary.exceeded_peak_demand_in_kw)

        summary.total_cost_in_reais = \
            summary.demand_cost_in_reais + summary.consumption_cost_in_reais

        summary.total_consumption_cost_in_reais = summary.consumption_cost_in_reais.sum()
        summary.total_demand_cost_in_reais = summary.demand_cost_in_reais.sum()
        summary.total_total_cost_in_reais = \
            summary.total_consumption_cost_in_reais + summary.total_demand_cost_in_reais

        return summary

    def __find_percentile_with_smallest_total_demand(self, percentiles: 'dict[str, DataFrame]') -> 'tuple[str, float]':
        smallest_total_demand_cost_in_reais = inf
        min_p_str = ''
        #tolerance = 0.01
        for p_str, percentile_frame in percentiles.items():
            if percentile_frame.total_in_reais[0] < smallest_total_demand_cost_in_reais:
                smallest_total_demand_cost_in_reais = percentile_frame.total_in_reais[0]
                min_p_str = p_str

            """ # Esse "hack" é pra dar o resultado igual ao da planilha. Não tenho certeza do "and"
            x = percentile_frame.total_in_reais[0]
            y = smallest_total_demand_cost_in_reais
            if x < (y + tolerance) and x < (y - tolerance):
                smallest_total_demand_cost_in_reais = percentile_frame.total_in_reais[0]
                min_p_str = p_str """
            
        return min_p_str, smallest_total_demand_cost_in_reais
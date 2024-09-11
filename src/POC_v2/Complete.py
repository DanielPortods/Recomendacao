from pandas import DataFrame
from global_search_recommendation.dominio import Dominio
import time

class CompleteCalculator:
    def __init__(self, head_num: int, history: DataFrame):
        self.history = history.head(head_num)
        self.head_num = head_num
        self.p_lbound = min(i for i in self.history['peak_measured_demand_in_kw'] if i > 0)
        self.o_lbound = min(i for i in self.history['off_peak_measured_demand_in_kw'] if i > 0)
        self.p_ubound = self.history['peak_measured_demand_in_kw'].max()
        self.o_ubound = self.history['off_peak_measured_demand_in_kw'].max()
        self.g_lb = min(self.p_lbound, self.o_lbound)
        self.g_ub = max(self.p_ubound, self.o_ubound)
        Dominio().insert_new_history(self.history)

    def run(self, save = False, partial = False):
        if save:
            self.green_pattern = [] #DataFrame(columns=['cost', 'unique_demand'])
            self.blue_pattern = [] #DataFrame(columns=['cost', 'peak_demand', 'off_peak_demand'])

        start_at = time.time()
        
        green_v = .0
        green_d = 0
        for v in range(int(round(self.g_lb)), int(round(self.g_ub))+1):
            value = Dominio().green_objective_func_it([v]) + v
            if value <= green_v or green_v == .0:
                green_v = value
                green_d = v
            if save:
                self.green_pattern.append([value, v])

        blue_v = .0
        blue_d = (0, 0)
        for v_i in range(int(round(self.p_lbound)), int(round(self.p_ubound))+1):
            for v_ii in range(int(self.o_lbound), int(self.o_ubound)+1):
                value = Dominio().blue_objective_func_it([v_i, v_ii]) + v_i + v_ii
                if value <= blue_v or blue_v == .0:
                    blue_v = value
                    blue_d = (v_i, v_ii)
                if save:
                    self.blue_pattern.append([value, v_i, v_ii])

        end_at = time.time()

        if partial:
            return {'green':[green_d, round(green_v, 2)], 'blue':[blue_d[0], blue_d[1], round(blue_v, 2)], 'best':'green' if green_v <= blue_v else 'blue', 'time':end_at - start_at}
        
        result = [0, 0, green_d, 'Verde', green_v] if green_v <= blue_v else [blue_d[0], blue_d[1], 0, 'Azul', blue_v]
        
        return  ['Completo', result[3], result[0], result[1], result[2], round(result[4], 2), self.head_num, end_at - start_at]
    
    def get_patterns(self, frame=False):
        if frame:
            return DataFrame(columns=['cost', 'unique_demand'], data=self.green_pattern), DataFrame(columns=['cost', 'peak_demand', 'off_peak_demand'], data=self.blue_pattern)
        
        return self.green_pattern, self.blue_pattern
        
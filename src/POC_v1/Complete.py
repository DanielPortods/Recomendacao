from pandas import DataFrame
from dominio import Dominio
import time

class CompleteCalculator:
    def __init__(self, head_num: int, history: DataFrame):
        self.history = history.head(head_num)
        self.head_num = head_num
        self.p_lbound = self.history['peak_measured_demand_in_kw'].min()
        self.o_lbound = self.history['off_peak_measured_demand_in_kw'].min()
        self.p_ubound = self.history['peak_measured_demand_in_kw'].max()
        self.o_ubound = self.history['off_peak_measured_demand_in_kw'].max()
        self.g_lb = min(self.p_lbound, self.o_lbound)
        self.g_ub = max(self.p_ubound, self.o_ubound)
        Dominio().insert_new_history(self.history)
    
    def _check_bounds(self, lb: .0, up: .0):
        return up > lb

    def run(self):
        start_at = time.time()
        
        green_v = .0
        green_d = 0
        for v in range(int(self.g_lb), int(self.g_ub)):
            value = Dominio().green_objective_func([v])
            if value < green_v or green_v == .0:
                green_v = value
                green_d = v

        blue_v = .0;
        blue_d = (0, 0)
        for v_i in range(int(self.p_lbound), int(self.p_ubound)):
            for v_ii in range(int(self.o_lbound), int(self.o_ubound)):
                value = Dominio().blue_objective_func([v_i, v_ii])
                if value < blue_v or blue_v == .0:
                    blue_v = value
                    blue_d = (v_i, v_ii)

        result = [0, 0, green_d, 'Verde', green_v] if green_v <= blue_v else [blue_d[0], blue_d[1], 0, 'Azul', blue_v]
        
        end_at = time.time()
        
        print(f'g: {green_v}, b: {blue_v}')
        
        return  ['Completo', result[3], round(result[0]), round(result[1]), round(result[2]), round(result[4], 2), self.head_num, end_at - start_at]
        
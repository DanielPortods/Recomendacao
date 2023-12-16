from sko.PSO import PSO
from sko.GA import GA
from pandas import DataFrame
from dominio import Dominio
import time

class BioInspiredRecomendation:
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

    def _skip(self, method, start):
        end_at = time.time()
        return [method, 'Skiped', '-', '-', '-', '-', self.head_num, end_at - start]
    
    def do_PSO(self):
        start_at = time.time()
        to_skip = [True, True]
        
        if self._check_bounds(lb=self.p_lbound, up=self.p_ubound) and self._check_bounds(lb=self.o_lbound, up=self.o_ubound):
            to_skip[0] = False
            blue = PSO(func=Dominio().blue_objective_func, n_dim=2, pop=200, max_iter=400, \
                       w=0.8, c1=0.6, c2=0.6, lb=[self.p_lbound, self.o_lbound], ub=[self.p_ubound, self.o_ubound])
            blue.run()
            
        if self._check_bounds(lb=self.g_lb, up=self.g_ub):
            to_skip[1] = False
            green = PSO(func=Dominio().green_objective_func, n_dim=1, pop=200, max_iter=400, \
                        w=0.8, c1=0.6, c2=0.6, lb=self.g_lb, ub=self.g_ub)
            green.run()
            
        if to_skip[0] and to_skip[1]:
            return self._skip('PSO', start_at)
        elif to_skip[0] or (green.gbest_y <= blue.gbest_y):
            end_at = time.time()
            return ['PSO', 'Verde', 0.0, 0.0, round(green.gbest_x[0], 2), round(green.gbest_y[0], 2), self.head_num, end_at - start_at]
        else:
            end_at = time.time()
            return ['PSO', 'Azul', round(blue.gbest_x[0], 2), round(blue.gbest_x[1], 2), 0.0, round(blue.gbest_y[0], 2), self.head_num, end_at - start_at]

    def do_GA(self):
        start_at = time.time()
        to_skip = [True, True]
        
        if self._check_bounds(lb=self.p_lbound, up=self.p_ubound) and self._check_bounds(lb=self.o_lbound, up=self.o_ubound):
            to_skip[0] = False
            blue_ga = GA(func=Dominio().blue_objective_func, n_dim=2, size_pop=100, max_iter=400, \
                         prob_mut=0.005, lb=[self.p_lbound, self.o_lbound], ub=[self.p_ubound, self.o_ubound], precision=1e-7)
            blue_ga_rec = blue_ga.run()

        if self._check_bounds(lb=self.g_lb, up=self.g_ub):
            to_skip[1] = False
            green_ga = GA(func=Dominio().green_objective_func, n_dim=1, size_pop=100, max_iter=400, \
                          prob_mut=0.005, lb=[self.g_lb], ub=[self.g_ub], precision=1e-7)
            green_ga_rec = green_ga.run()

        if to_skip[0] and to_skip[1]:
            return self._skip('GA', start_at)
        elif to_skip[0] or (green_ga_rec[1][0] <= blue_ga_rec[1][0]):
            end_at = time.time()
            return ['GA', 'Verde', 0.0, 0.0, round(green_ga_rec[0][0], 2), round(green_ga_rec[1][0], 2), self.head_num, end_at - start_at]
        else:
            end_at = time.time()
            return ['GA', 'Azul', round(blue_ga_rec[0][0], 2), round(blue_ga_rec[0][1], 2), 0.0, round(blue_ga_rec[1][0], 2), self.head_num, end_at - start_at]
        

            
        
    
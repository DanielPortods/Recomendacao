from sko.PSO import PSO
from sko.GA import GA
from pandas import DataFrame
from global_search_recommendation.dominio import Dominio
import time

class BioInspiredRecomendation:
    def __init__(self, head_num: int, history: DataFrame, num_pop = 40):
        self.history = history.head(head_num)
        self.head_num = head_num
        self.p_lbound = min(i for i in self.history['peak_measured_demand_in_kw'] if i > 0)
        self.o_lbound = min(i for i in self.history['off_peak_measured_demand_in_kw'] if i > 0)
        self.p_ubound = self.history['peak_measured_demand_in_kw'].max() + 1
        self.o_ubound = self.history['off_peak_measured_demand_in_kw'].max() + 1
        self.g_lb = min(self.p_lbound, self.o_lbound) 
        self.g_ub = max(self.p_ubound, self.o_ubound)
        self.num_pop = num_pop
        self.b_total_it = int((self.p_ubound - self.p_lbound) * (self.o_ubound - self.o_lbound)/self.num_pop)
        self.g_total_it = int((self.g_ub - self.g_lb)/self.num_pop)   
        Dominio().insert_new_history(self.history)
    
    def _check_bounds(self, lb: .0, up: .0):
        return up > lb

    def _skip(self, method, start):
        end_at = time.time()
        return [method, 'Skiped', '-', '-', '-', '-', self.head_num, end_at - start]
    
    def do_PSO(self, iterative = False, record = False, partial = False):
        start_at = time.time()
        to_skip = [True, True]
        
        if self._check_bounds(lb=self.p_lbound, up=self.p_ubound) \
           and self._check_bounds(lb=self.o_lbound, up=self.o_ubound):

            to_skip[0] = False
            blue = PSO(func=Dominio().blue_objective_func if not iterative else Dominio().blue_objective_func_it, n_dim=2, pop=self.num_pop, max_iter=100,
                       w=0.8, c1=0.6, c2=0.6, lb=[self.p_lbound, self.o_lbound], 
                       ub=[self.p_ubound, self.o_ubound])
            blue.record_mode = record
            blue.run(precision=1e-2)
            
        if self._check_bounds(lb=self.g_lb, up=self.g_ub):

            to_skip[1] = False
            green = PSO(func=Dominio().green_objective_func if not iterative else Dominio().green_objective_func_it, n_dim=1, pop=self.num_pop, max_iter=100, \
                        w=0.8, c1=0.6, c2=0.6, lb=self.g_lb, ub=self.g_ub)
            green.record_mode = record
            green.run(precision=1e-2)

        green_v = round(green.gbest_y[0] + green.gbest_x[0], 2) if green else None #
        blue_v = round(blue.gbest_y[0] + blue.gbest_x[0] + blue.gbest_x[1], 2) if blue else None  #

        if record:
            Dominio().save_pso_records(blue.record_value, green.record_value)

        if partial:
            end_at = time.time()
            return {'green':[round(green.gbest_x[0]), round(green_v, 2)], 
                    'blue':[round(blue.gbest_x[0]), round(blue.gbest_x[1]), round(blue_v, 2),], 
                    'best':'green' if green_v <= blue_v else 'blue',
                    'time':end_at - start_at}
              
        if to_skip[0] and to_skip[1]:
            return self._skip('PSO', start_at)
        elif to_skip[0] or (green_v <= blue_v):
            end_at = time.time()
            return ['PSO' if not iterative else 'PSO-it', 'Verde', 0, 0, round(green.gbest_x[0]), 
                    green_v, self.head_num, end_at - start_at]
        else:
            end_at = time.time()
            return ['PSO' if not iterative else 'PSO-it', 'Azul', round(blue.gbest_x[0]), 
                    round(blue.gbest_x[1]), 0, blue_v, self.head_num, end_at - start_at]

    def do_GA(self, iterative = False, record = False, partial = False):
        start_at = time.time()
        to_skip = [True, True]
        
        if self._check_bounds(lb=self.p_lbound, up=self.p_ubound) \
           and self._check_bounds(lb=self.o_lbound, up=self.o_ubound):
            
            to_skip[0] = False
            blue_ga = GA(func=Dominio().blue_objective_func if not iterative else Dominio().blue_objective_func_it, n_dim=2, size_pop=self.num_pop, max_iter=100,
                         prob_mut=0.005, lb=[self.p_lbound, self.o_lbound], ub=[self.p_ubound, self.o_ubound], early_stop=20, precision=[1,1])
            blue_ga_rec = blue_ga.run()

        if self._check_bounds(lb=self.g_lb, up=self.g_ub):
            to_skip[1] = False
            green_ga = GA(func=Dominio().green_objective_func if not iterative else Dominio().green_objective_func_it, n_dim=1, size_pop=self.num_pop, max_iter=100, \
                          prob_mut=0.005, lb=[self.g_lb], ub=[self.g_ub], early_stop=20, precision=1)
            green_ga_rec = green_ga.run()

        green_v = round(green_ga_rec[1][0] + green_ga_rec[0][0], 2) if green_ga else None
        blue_v = round(blue_ga_rec[1][0] + blue_ga_rec[0][0] + blue_ga_rec[0][1], 2) if blue_ga else None
        
        if record:
            Dominio().save_ga_records(blue_ga.generation_best_X, green_ga.generation_best_X)

        if partial:
            end_at = time.time()
            return {'green':[round(green_ga_rec[0][0]), round(green_v, 2)],
                    'blue':[round(blue_ga_rec[0][0]), round(blue_ga_rec[0][1]), round(blue_v, 2),],
                    'best':'green' if green_v <= blue_v else 'blue',
                    'time':end_at - start_at}

        if to_skip[0] and to_skip[1]:
            return self._skip('GA', start_at)
        elif to_skip[0] or (green_v <= blue_v):
            end_at = time.time()
            return ['GA' if not iterative else 'GA-it', 'Verde', 0, 0, round(green_ga_rec[0][0]), green_v, self.head_num, end_at - start_at]
        else:
            end_at = time.time()
            return ['GA' if not iterative else 'GA-it', 'Azul', round(blue_ga_rec[0][0]), round(blue_ga_rec[0][1]), 0, blue_v, self.head_num, end_at - start_at]
        

            
        
    
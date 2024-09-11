from glob import glob
import pandas as pd

class SheetsConversor:

    MONTHS = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
              "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    COLUMNS = ['year','month','peak_consumption_in_kwh','off_peak_consumption_in_kwh',
               'peak_measured_demand_in_kw','off_peak_measured_demand_in_kw',
               'contract_peak_demand_in_kw','contract_off_peak_demand_in_kw',"cost_reais", 
               'peak_exceeded_in_kw','off_peak_exceeded_in_kw', 'none']
    
    def __init__(self, sheets_dir) -> None:
        self.path = glob(f"{sheets_dir}/*.xls*")

    def convert(self, csv_save=False) -> dict:
        ucs = {}
        for sheet_path in self.path:
            print(f"Reading {sheet_path}...")
            sheet = pd.read_excel(sheet_path, sheet_name=None, 
                                  thousands='.', decimal=',', 
                                  names=self.COLUMNS, header=4)
            for uc in sheet:
                sheet[uc].drop(columns=['none'], inplace=True)
                sheet[uc].fillna(0, inplace=True)
                sheet[uc].month = sheet[uc].month.map(self.MONTHS)
                if csv_save:
                    ucs[sheet].to_csv(f"data/{sheet}.csv")
            ucs.update(sheet)
        print(f"Done! {len(ucs)} UCs conveted!")
        return ucs
    
    def get_uc_flags(self, ucs: dict) -> dict:
        flags = {}
        for uc in ucs:
            peak_demand = ucs[uc][self.COLUMNS[6]].eq(0).all()
            off_peak_demand = ucs[uc][self.COLUMNS[7]].eq(0).all()

            flag = ''            
            if peak_demand and not off_peak_demand:
                flag = 'Green'
            elif off_peak_demand and not peak_demand:
                flag = 'Green'
                ucs[uc][self.COLUMNS[7]] = ucs[uc][self.COLUMNS[6]]
            elif off_peak_demand and peak_demand: 
                flag = 'Blue'
            else:
                flag = 'Skip'
            
            flags.update({uc: flag})
        
        return flags
    
    def check_ucs(self, ucs: dict) -> None:
        for uc, plan in ucs.items():
            mes, cont = 0, 0
            for i in range(len(plan['month']+1)):
                if mes == 12 and cont == 78 and not plan['year'][i] - plan['year'][i-1] == 1:
                    print(f"uc {uc} problemática: descontinuidade anual")
                    break
                elif mes == 12 and not cont == 78:
                    print(f"uc {uc} problemática: descontinuidade mensal")
                    break
                elif mes == 12 and cont == 78:
                    mes, cont = 0, 0
                    break

            cont += plan['month'][i]
            mes += 1
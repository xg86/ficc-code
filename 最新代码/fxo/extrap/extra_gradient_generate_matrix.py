import numpy as np
import pandas as pd
from pandas import DataFrame


class FXOptionDeltaExtrapolator:
    def __init__(self, rr_values, bf_values):
        """
        Initialize the extrapolator with FX option Delta RR and BF values

        :param deltas: List of delta values [10, 25, 50]
        :param rr_values: Corresponding Risk Reversal (RR) values
        :param bf_values: Corresponding Butterfly (BF) values
        """
        # Convert to numpy arrays for robust handling
        #self.deltas = np.array(deltas)
        self.rr_values = np.array(rr_values)
        self.bf_values = np.array(bf_values)

    def extraploate_delta_rr_bf (self, atm: float, rr_25:float, rr_10:float, target_delta:float, isRR:bool, d_25:float = 25.0, d_10:int = 10.0):
        print(f"***************************************")
        ATMto25gradient = -1*rr_25 / (atm * 100.0 - d_25)
        print(f"ATMto25gradient: {ATMto25gradient:.6f}")

        extrap10Delta = ATMto25gradient * d_10 - ATMto25gradient * atm * 100.0
        print(f"extrap10Delta: {extrap10Delta:.6f}")

        grad25to10 = -1 * (rr_10 - rr_25) / (d_25 - d_10)
        print(f"grad25to10: {grad25to10:.6f}")

        extrap_target_delta = grad25to10 * target_delta + rr_25 - grad25to10 * d_25
        print(f"{target_delta:.6f}, extrap_target_delta: {extrap_target_delta:.6f}")

        error25to10 = (rr_10 - extrap10Delta) / (d_25 - d_10)
        print(f"error25to10: {error25to10:.6f}")

        if isRR:
            extrap_target_delta_Adj = extrap_target_delta + error25to10 * (d_10 - target_delta)
            print(f"extrap_target_delta_Adj RR: {extrap_target_delta_Adj:.6f}")
            return extrap_target_delta_Adj

        extrap_target_delta_Adj = extrap_target_delta + error25to10 * (d_10 - target_delta)
        if(extrap_target_delta_Adj < 0):
            return 0.0
        else:
            print(f"extrap_target_delta_Adj BF: {extrap_target_delta_Adj:.6f}")
            return  extrap_target_delta_Adj

def build_market_matrix(atm: float,rr_values:np.array, bf_values:np.array, tenor:str, delta_df: DataFrame, index:int):

    extrapolator = FXOptionDeltaExtrapolator(rr_values, bf_values)

    target_deltas = np.array([1, 5])

    # Weighted Interpolation for 5 Delta RR and BF
    for target_delta in target_deltas:
        rr_target = extrapolator.extraploate_delta_rr_bf(atm, rr_values[1], rr_values[0], target_delta, True)
        bf_target = extrapolator.extraploate_delta_rr_bf(atm, bf_values[1], bf_values[0], target_delta, False)

        print(f"{tenor} {target_delta} Delta RR:  {rr_target:.6f}")
        print(f"{tenor} {target_delta} Delta BF:  {bf_target:.6f}")
        delta_df.at[index, str(target_delta)+'P'] = (atm + bf_target - rr_target/2)/100
        delta_df.at[index, str(target_delta)+'C'] = (atm + bf_target + rr_target/2)/100
        delta_df.at[index, 'ATM'] = atm/100


if __name__ == "__main__":
    ''' POC Nanjing bank
    market_rr =[
             {
               "Tenors": "ON",
               "10RR": -0.05,
               "25RR": -0.05,
               "ATM": 4
             },
             {
               "Tenors": "1W",
               "10RR": -0.05,
               "25RR": -0.05,
               "ATM": 8.3
             },
             {
               "Tenors": "2W",
               "10RR": 0.05,
               "25RR": 0.075,
               "ATM": 8.1
             },
             {
               "Tenors": "3W",
               "10RR": 0.1,
               "25RR": 0.075,
               "ATM": 7.8
             },
             {
               "Tenors": "1M",
               "10RR": 0.15,
               "25RR": 0.08,
               "ATM": 7.05
             },
             {
               "Tenors": "2M",
               "10RR": 0.2,
               "25RR": 0.1,
               "ATM": 5.925
             },
             {
               "Tenors": "3M",
               "10RR": 0.4,
               "25RR": 0.2,
               "ATM": 5.8
             },
             {
               "Tenors": "6M",
               "10RR": 0.6,
               "25RR": 0.35,
               "ATM": 5.375
             },
             {
               "Tenors": "9M",
               "10RR": 0.8,
               "25RR": 0.4,
               "ATM": 5.2
             },
             {
               "Tenors": "1Y",
               "10RR": 1.1,
               "25RR": 0.55,
               "ATM": 5.125
             },
             {
               "Tenors": "18M",
               "10RR": 1.2,
               "25RR": 0.525,
               "ATM": 5.2
             },
             {
               "Tenors": "2Y",
               "10RR": 1.2,
               "25RR": 0.55,
               "ATM": 5.3
             },
             {
               "Tenors": "3Y",
               "10RR": 1.2,
               "25RR": 0.6,
               "ATM": 5.35
             }
        ]

    market_bf = [
                 {
                   "Tenors": "ON",
                   "ATM": 4,
                   "25BF": 0.23,
                   "10BF": 0.35
                 },
                 {
                   "Tenors": "1W",
                   "ATM": 8.3,
                   "25BF": 0.23,
                   "10BF": 0.35
                 },
                 {
                   "Tenors": "2W",
                   "ATM": 8.1,
                   "25BF": 0.23,
                   "10BF": 0.375
                 },
                 {
                   "Tenors": "3W",
                   "ATM": 7.8,
                   "25BF": 0.23,
                   "10BF": 0.4
                 },
                 {
                   "Tenors": "1M",
                   "ATM": 7.05,
                   "25BF": 0.24,
                   "10BF": 0.41
                 },
                 {
                   "Tenors": "2M",
                   "ATM": 5.925,
                   "25BF": 0.27,
                   "10BF": 0.475
                 },
                 {
                   "Tenors": "3M",
                   "ATM": 5.8,
                   "25BF": 0.275,
                   "10BF": 0.55
                 },
                 {
                   "Tenors": "6M",
                   "ATM": 5.375,
                   "25BF": 0.28,
                   "10BF": 0.58
                 },
                 {
                   "Tenors": "9M",
                   "ATM": 5.2,
                   "25BF": 0.2775,
                   "10BF": 0.68
                 },
                 {
                   "Tenors": "1Y",
                   "ATM": 5.125,
                   "25BF": 0.285,
                   "10BF": 0.75
                 },
                 {
                   "Tenors": "18M",
                   "ATM": 5.2,
                   "25BF": 0.29,
                   "10BF": 0.77
                 },
                 {
                   "Tenors": "2Y",
                   "ATM": 5.3,
                   "25BF": 0.3,
                   "10BF": 0.785
                 },
                 {
                   "Tenors": "3Y",
                   "ATM": 5.35,
                   "25BF": 0.3,
                   "10BF": 0.8
                 }
                ]
'''
market_rr = [
 {
   "Tenors": "1W",
   "10RR": 0.495,
   "25RR": 0.373,
   "ATM": 5.195
 },
 {
   "Tenors": "2W",
   "10RR": 0.535,
   "25RR": 0.365,
   "ATM": 5.293
 },
 {
   "Tenors": "3W",
   "10RR": 0.604,
   "25RR": 0.383,
   "ATM": 5.125
 },
 {
   "Tenors": "1M",
   "10RR": 0.505,
   "25RR": 0.475,
   "ATM": 4.815
 },
 {
   "Tenors": "2M",
   "10RR": 0.57,
   "25RR": 0.45,
   "ATM": 4.69
 },
 {
   "Tenors": "3M",
   "10RR": 0.595,
   "25RR": 0.453,
   "ATM": 4.658
 },
 {
   "Tenors": "4M",
   "10RR": 0.59,
   "25RR": 0.405,
   "ATM": 4.682
 },
 {
   "Tenors": "5M",
   "10RR": 0.651,
   "25RR": 0.367,
   "ATM": 4.689
 },
 {
   "Tenors": "6M",
   "10RR": 0.673,
   "25RR": 0.355,
   "ATM": 4.673
 },
 {
   "Tenors": "9M",
   "10RR": 0.727,
   "25RR": 0.342,
   "ATM": 4.722
 },
 {
   "Tenors": "1Y",
   "10RR": 0.788,
   "25RR": 0.353,
   "ATM": 4.77
 },
 {
   "Tenors": "18M",
   "10RR": 0.87,
   "25RR": 0.357,
   "ATM": 4.775
 },
 {
   "Tenors": "2Y",
   "10RR": 0.87,
   "25RR": 0.363,
   "ATM": 4.755
 },
 {
   "Tenors": "3Y",
   "10RR": 0.847,
   "25RR": 0.388,
   "ATM": 4.63
 }
]

market_bf =[
 {
   "Tenors": "1W",
   "ATM": 5.195,
   "25BF": 0.2375,
   "10BF": 0.4795
 },
 {
   "Tenors": "2W",
   "ATM": 5.293,
   "25BF": 0.2775,
   "10BF": 0.5445
 },
 {
   "Tenors": "3W",
   "ATM": 5.125,
   "25BF": 0.2175,
   "10BF": 0.515
 },
 {
   "Tenors": "1M",
   "ATM": 4.815,
   "25BF": 0.2255,
   "10BF": 0.4655
 },
 {
   "Tenors": "2M",
   "ATM": 4.69,
   "25BF": 0.225,
   "10BF": 0.475
 },
 {
   "Tenors": "3M",
   "ATM": 4.658,
   "25BF": 0.2295,
   "10BF": 0.4245
 },
 {
   "Tenors": "4M",
   "ATM": 4.682,
   "25BF": 0.2325,
   "10BF": 0.46
 },
 {
   "Tenors": "5M",
   "ATM": 4.689,
   "25BF": 0.2425,
   "10BF": 0.5485
 },
 {
   "Tenors": "6M",
   "ATM": 4.673,
   "25BF": 0.2625,
   "10BF": 0.5745
 },
 {
   "Tenors": "9M",
   "ATM": 4.722,
   "25BF": 0.263,
   "10BF": 0.6005
 },
 {
   "Tenors": "1Y",
   "ATM": 4.77,
   "25BF": 0.2775,
   "10BF": 0.62
 },
 {
   "Tenors": "18M",
   "ATM": 4.775,
   "25BF": 0.2725,
   "10BF": 0.575
 },
 {
   "Tenors": "2Y",
   "ATM": 4.755,
   "25BF": 0.2775,
   "10BF": 0.585
 },
 {
   "Tenors": "3Y",
   "ATM": 4.63,
   "25BF": 0.3,
   "10BF": 0.5925
 }
]
columns = ["Tenors", "1P", "5P", "10P", "15P", "20P", "25P", "30P", "35P", "40P", "45P","ATM",
                     "45C","40C", "35C", "30C", "25C", "20C", "15C", "10C", "5C", "1C"] # Create an empty DataFrame with the specified columns empty_df = pd.DataFrame(columns=columns)

matrix_df = pd.DataFrame(columns=columns)

matrix_df['Tenors'] = [ #"ON",
"1W",
"2W",
"3W",
"1M",
"2M",
"3M",
"4M",
"5M",
"6M",
"9M",
"1Y",
"18M",
"2Y",
"3Y"]

for rr, bf, index in zip(market_rr, market_bf, enumerate(matrix_df['Tenors'])):
    rr_vals= []
    rr_vals.append(rr['10RR'])
    rr_vals.append(rr['25RR'])

    bf_vals = []
    bf_vals.append(bf['10BF'])
    bf_vals.append(bf['25BF'])

    build_market_matrix(rr['ATM'], rr_vals, bf_vals, rr['Tenors'], matrix_df, index[0])
    print("$$$$$$$$$$$$$$$$$$$$$$$$")

print(matrix_df.to_string())
matrix_df.to_csv('extra_gradient_generate_matrix.csv', index=False)
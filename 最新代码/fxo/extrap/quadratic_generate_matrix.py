import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline
from numpy.polynomial.polynomial import Polynomial

class FXOptionQuadraticDeltaExtrapolator:
    def __init__(self, deltas, rr_values, bf_values):
        """
        Initialize the extrapolator with FX option Delta RR and BF values

        :param deltas: List of delta values [10, 25, 50]
        :param rr_values: Corresponding Risk Reversal (RR) values
        :param bf_values: Corresponding Butterfly (BF) values
        """
        # Convert to numpy arrays for robust handling
        self.deltas_values = np.array(deltas)
        self.vol_values = np.array(rr_values+bf_values)
        self.quadratic_interp = interp1d(self.deltas_values, self.vol_values, kind='quadratic', fill_value="extrapolate", assume_sorted=True)


    # Define the cubic extrapolators
    #def cubic_extrapolate_left(self, xval):
    #    return self.coeffs_left[0] + self.coeffs_left[1] * xval + self.coeffs_left[2] * xval ** 2

    #def cubic_extrapolate_right(self, xval):
    #    return self.coeffs_right[0] + self.coeffs_right[1] * xval + self.coeffs_right[2] * xval ** 2

    # Combined interpolator and extrapolator
    def cubic_interp_extrap(self, xval):
        return self.quadratic_interp(xval)


        '''
        if xval < self.deltas_values[0]:
            return self.cubic_extrapolate_left(xval)
        elif xval > self.deltas_values[-1]:
            return self.cubic_extrapolate_right(xval)
        else:
            return self.cubic_interp(xval)
        elif xval > 25 and xval < 50:
            return cubic_extrapolate_right(xval)
        elif xval > 50 and xval < 75:
            return cubic_extrapolate_left(xval)
        '''

def build_market_matrix(atm: float,rr_values:np.array, bf_values:np.array, tenor:str, delta_df: DataFrame, index:int):
    # Example usage with different delta values
    # Inputs: 10D RR, 25D RR, 50D RR

    deltas = np.array([10, 25, 75, 90])

    extrapolator = FXOptionQuadraticDeltaExtrapolator(deltas, rr_values, bf_values)

    # Linear Extrapolation for 5 Delta RR and BF
    '''
    rr_5d_linear, bf_5d_linear = extrapolator.linear_extrapolation(15)
    print("Linear Extrapolation:")
    print("5 Delta RR:", rr_5d_linear)
    print("5 Delta BF:", bf_5d_linear)
    '''
    target_deltas = np.array([5, 15, 20, 35, 65, 80, 85, 95])

    # Weighted Interpolation for 5 Delta RR and BF

    for target_delta in target_deltas:
        vol_val = extrapolator.cubic_interp_extrap(target_delta)

        print(f"{tenor} {target_delta} Delta RR:  {vol_val:.6f}")
        #print(f"{tenor} {target_delta} Delta BF:  {bf_val:.6f}")
        if target_delta < 50:
            delta_df.at[index, str(target_delta)+'RR'] = vol_val
        else:
            delta_df.at[index, str(100-target_delta) + 'BF'] = vol_val
        #delta_df.at[index, str(target_delta)+'C'] = (atm + bf_val + rr_val/2)/100
        delta_df.at[index, 'ATM'] = atm




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
#BBG RR
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
columns = ["Tenors", "1RR", "5RR", "10RR", "15RR", "20RR", "25RR", "30RR", "35RR", "40RR", "45RR","ATM",
                     "45BF","40BF", "35BF", "30BF", "25BF", "20BF", "15BF", "10BF", "5BF", "1BF"] # Create an empty DataFrame with the specified columns empty_df = pd.DataFrame(columns=columns)

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
    bf_vals.append(bf['25BF'])
    bf_vals.append(bf['10BF'])

    build_market_matrix(rr['ATM'], rr_vals, bf_vals, rr['Tenors'], matrix_df, index[0])
    print("$$$$$$$$$$$$$$$$$$$$$$$$")

print(matrix_df.to_string())
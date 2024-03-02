import uuid

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import statsmodels.tsa.stattools as tsa
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
from pandas import DataFrame
from sklearn import preprocessing
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import seaborn as sn
from datetime import datetime
import datetime as dt
from timeit import default_timer as timer
from dateutil.relativedelta import relativedelta

from mcpParamCurve import *

#start = '2022-01-4 00:00:00'
cutoff = '2023-11-1 00:00:00'
#bond_codes = ["210203.IB", "190215.IB", "210205.IB", "210210.IB", "220205.IB",
 #             "220210.IB", "220215.IB", "220220.IB", "230205.IB", "210220.IB"]
src_files = ['diff_gk.xlsx','diff_gz.xlsx','diff_nf.xlsx','diff_jc.xlsx']
#src_files = ['diff_nf.xlsx']

spread_file = 'E://meridian//债券//信号统计//NSS信号.xlsx'
spread_df = pd.read_excel(spread_file, sheet_name='bid-ask-spread')

def get_half_life2(z_array: pd.Series):
    z_lag = np.roll(z_array, 1)
    z_lag[0] = 0
    z_ret = z_array - z_lag
    z_ret[0] = 0
    # adds intercept terms to X variable for regression
    z_lag2 = sm.add_constant(z_lag)
    model = sm.OLS(z_ret, z_lag2)
    res = model.fit()
    halflife = -np.log(2) / res.params[1]
    #print('Halflife = ', halflife)
    return halflife
def get_half_life(data: pd.Series):
    if (len(data) < 2):
        return -1
    data_lag = data.shift(1)
    Y = data[1:] - data_lag[1:]
    X = sm.add_constant(data_lag[1:])  # Adds a column of ones to an array
    model = sm.OLS(Y, X)
    res = model.fit()
    np_log = -np.log(2)
    if(len(res.params) < 2):
        return -1
    res_params = res.params.iloc[1]
    param_1 = np_log / res_params
    halflife = round(param_1, 0)
    return halflife

def stationary_test(data2: pd.Series):
    # compute ADF test statistic
    adf_ = tsa.adfuller(data2,maxlag=1)
    #print('adf', adf_[0])
    #print('p-value', adf_[1])
    #print('T values', adf_[4])
    return adf_[1] < 0.1

def getYield(df1: DataFrame, col1: str, col2: str):
    if df1[col2] >= 1:
        return df1[col1]*100
def getPnl(df2: DataFrame, col1: str, col2: str, multiplier: int, isYield: bool):
    #if df['Buy'] == 1 and df['SellYield'] != None and df['BuyYield'] > 0 and df['SellYield'] > 0 :
    if df2['Sell'] == 1 and df2[col1] != None and df2[col1] > 0 and df2[col2] > 0:
        if isYield:
            return (df2[col1] - df2[col2]) * multiplier
        return (df2[col2] - df2[col1])* multiplier
#one buy one sell
def calculatePnl(df3: DataFrame):
    df3['BuyYield'] = df3.apply(getYield, args=('Yield', 'Buy'), axis=1)
    df3['SellYield'] = df3.apply(getYield, args=('Yield', 'Sell'), axis=1)
    #df['BuyDirtyPrice'] = df.apply(getYield, args=('ValuationDirtyPrice', 'Buy'), axis=1)
    #df['SellDirtyPrice'] = df.apply(getYield, args=('ValuationDirtyPrice', 'Sell'), axis=1)
   #if len(df[df['Sell'] == 1]) > 1:
   #     df['SellYield'].fillna(method='bfill', inplace=True)
    b_yield = -1
    b_yield_AbsDiffZero= -1
    for index, row in df3.iterrows():
        #print(row["Name"], row["Age"])
        if row['Buy'] == 1 and b_yield < 0:
            b_yield = row['BuyYield']
            b_yield_AbsDiffZero = row['AbsDiffZero']
        elif row['Sell'] == 1 and b_yield > 0:
            df3.at[index, 'BuyYield'] = b_yield
            df3.at[index, 'b_yield_AbsDiffZero'] = b_yield_AbsDiffZero
            b_yield = -1
            b_yield_AbsDiffZero = -1

    df3['PnLYield'] = df3.apply(getPnl, args=('BuyYield', 'SellYield', 100, True), axis=1)
    #df['PnLPrice'] = df.apply(getPnl, args=('BuyDirtyPrice', 'SellDirtyPrice', 100*1000, False), axis=1)
    return df3['PnLYield'].sum() #, df['PnLPrice'].sum()


def check_spread(spread_trades: pd.Series, spread_sigal: pd.Series, code: str, pnlY: float, left_year,
                 side: str, activeUnit: pd.Series, tradeTime: pd.Series,
                 yieldMkt: pd.Series, zSpread: float):
    code_df = spread_df[(spread_df.bond_code == code)]
    b_a_spread = 0
    if len(code_df) > 0 :
        b_a_spread = code_df['spread'].tolist()[0]
    min_val = spread_trades.min()
    for indx, val in spread_sigal.items():
        if val > min_val:
            #print("diff yield {0}, bid-ask spread {1} for code {2}".format (val, b_a_spread, code))
            print("%%%%%%%%%%%% {6} for-code {0} on {8} trade-yield {9} zSpread {10}, total-PnL {1}, diff-zero-abs-yield {2}, bid-ask-spread {3}, abs-spread {4}, activeUnit {7} left-year{5} "
                .format(code, pnlY, val, b_a_spread, val - b_a_spread, left_year, side, activeUnit[0],
                        tradeTime.max(), yieldMkt.max(), zSpread))
            return True
    return False
    pass  


def get_left_year(param: pd.Series):
    now = datetime.now()
    return relativedelta(param[0], now)
    pass

def cal_zspread(newdf: DataFrame, yield_str: str, date_str: str, maturityDate_col: str, coupon_col: str):
    return get_zspread(newdf[yield_str], newdf[date_str], newdf[maturityDate_col], newdf[coupon_col])

def get_rv_signal(src_file: str):
    print("starting reading ")
    request_file = 'D://git//strategy-repos-master//butterfly//nss-data//' + src_file
    src_df = pd.read_excel(request_file)
    #src_df = src_df.drop('Yld', axis=1)
    #src_df = src_df.drop('TradeTime', axis=1)
    #src_df = src_df.drop('Volume', axis=1)
    #src_df = src_df.drop('Coupon', axis=1)
    src_df = src_df.drop('StartDate', axis=1)
    #src_df = src_df.drop('MaturityDate', axis=1)
    src_df = src_df.drop('BondName', axis=1)
    src_df = src_df.drop('Frequency', axis=1)
    #src_df = src_df.drop('ActiveUnit', axis=1)
    src_df = src_df.drop('ValuationYield', axis=1)
    #df = df.drop('ValuationDirtyPrice', axis=1)
    src_df = src_df.drop('IsCurve', axis=1)
    codes = src_df.Code.unique()

    filename= str(uuid.uuid4().hex) + "_RV_YTM_"+ src_file
    writer = pd.ExcelWriter("D://git//strategy-repos-master//butterfly//nss-data-proc//"+filename)
    print("codes length ", len(codes))
    for code in codes:
        if (len(code) <= 9 and code.endswith('IB')):
            newdf = src_df[(src_df.Code == code)]
            #newdf['Date'] = pd.to_datetime(newdf['Date'])
            newdf.set_index('Date', inplace=True)

            #print("code is  ", code)
            newdf = newdf.tail(380)
            if (len(newdf) <= 100):
                continue
            #
            newdf=newdf.iloc[:-1, :]
            halflife_Zero = get_half_life(newdf["Yield"])
            #print('halflife_Zero = ', halflife_Zero)
            halflife_NssZero = get_half_life(newdf["NssYield"])
            #print('halflife_NssZero = ', halflife_NssZero)
            if(halflife_Zero > 0 and halflife_NssZero > 0 ):
                window_size = int(np.rint(halflife_Zero + halflife_NssZero)/2)
                newdf['AbsDiffZero'] = np.abs(newdf["NssYield"]-newdf["Yield"])*10000
                newdf['ave_'+str(window_size)] = newdf['AbsDiffZero'].rolling(window=int(window_size), center=False).mean()
                newdf['std_'+str(window_size)] = newdf['AbsDiffZero'].rolling(window=int(window_size), center=False).std(ddof=0)
                newdf['zscore_'+str(window_size)] = (newdf['AbsDiffZero'] - newdf['ave_'+str(window_size)])/newdf['std_'+str(window_size)]

                newdf['Buy'] = np.where(newdf['zscore_'+str(window_size)] >= 1, np.where(newdf['DiffZero'] <= 0, 1, 0), 0)
                newdf['Sell'] = np.where(newdf['zscore_'+str(window_size)] <= -1, np.where(newdf['AbsDiffZero'] <= 0.5, 1, 0), 0)
                if (src_file != 'diff_gz.xlsx'):
                    newdf['zSpread'] = newdf.apply(cal_zspread, args=('Yield', 'TradeTime', 'MaturityDate', 'Coupon'), axis=1)

                pnlY = calculatePnl(newdf)
                print(">>>>>>>>>>>> pnl yield %s, for code %s" % (pnlY, code))
                newdf.to_excel(writer, sheet_name=code)
                skip_df = newdf.loc[cutoff:]
                if (len(skip_df) <= 2):
                    continue
                tmp = newdf.tail(2)
                p_val = stationary_test(newdf['AbsDiffZero'])
                if (len(tmp[tmp['Buy'] == 1]) > 0 or len(tmp[tmp['Sell'] == 1]) > 0) and pnlY > 0 and p_val and code.startswith('2'):
                    tradedf = newdf[(newdf.PnLYield > 0)]
                    if (len(tradedf) <= 2):
                        continue
                    left_year = get_left_year(tmp['MaturityDate'])
                    if (src_file != 'diff_gz.xlsx'):
                        check_spread(tradedf['b_yield_AbsDiffZero'], tmp['AbsDiffZero'], code, pnlY, left_year, 'Buy' if len(tmp[tmp['Buy'] == 1]) > 0 else 'Sell',
                                 tmp['ActiveUnit'], tmp['TradeTime'], tmp['Yield'], tmp['zSpread'].max())
                    else:
                        check_spread(tradedf['b_yield_AbsDiffZero'], tmp['AbsDiffZero'], code, pnlY, left_year,
                                     'Buy' if len(tmp[tmp['Buy'] == 1]) > 0 else 'Sell',
                                     tmp['ActiveUnit'], tmp['TradeTime'], tmp['Yield'], -100)
                   #if len(tmp[tmp['Sell'] == 1]) > 0 :
                    #    print("############ Sell trading sigal for code is  ", code)
                    #print("done for code is  ", code)

    writer.close()
    print("ALl done ", src_file)

for src_file in src_files:
    get_rv_signal(src_file)

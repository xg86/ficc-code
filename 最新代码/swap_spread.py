from pandas import DataFrame
import uuid
from datetime import datetime
from mcp.enums import *
from mcp.tools import *
from dateutil.relativedelta import relativedelta
from AswSpread_cal import AswSpreadFsolve
import statsmodels.tsa.stattools as tsa
import statsmodels.api as sm
from mcpParamCurve import *
from scipy import stats

file_path= 'C://git//ficc-code//credit-curve//'
#src_files = ['corp-com-yields.xlsx']
#src_files = ['local_corp_asw.xlsx']

#local_gcb_static_file = 'c://meridian//债券//信号统计//value_counts.xlsx'
#static_df = pd.read_excel(local_gcb_static_file, sheet_name='value_counts')
#static_file = file_path + 'WIND_BOND.xlsx'
#static_df = pd.read_excel(static_file, sheet_name='Sheet1')


#three_mon_rel = relativedelta(months=3)



'''SHIBOR 3M'''
#shibor_3m_template_file='shibor-3m-template.xlsx'
shibor_3m_irs_data_file='shibor-3m-curve-data.xlsx'
fr007_irs_data_file='fr007-curve-data.xlsx'
#shibor_3m_rate_data_file='shibor-3m-rate.xlsx'

#curve_dict = {}
tenor_buckets = [relativedelta(years=1), relativedelta(years=2), relativedelta(years=3),
                 relativedelta(years=4), relativedelta(years=5)]

#df_swap_curve_data.to_excel(writer)
#writer.close()

curve_category = '00'

def get_years( delta: relativedelta):
    year = delta.years
    year_month = delta.months/12
    year_days = delta.days/365
    return year + year_month + year_days

def get_days( delta: relativedelta):
    days_month = delta.months*30
    return days_month + delta.days

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

def get_SwapSpread_shibor_3m():

    df_swap_curve_data = pd.read_excel(file_path + shibor_3m_irs_data_file)

    df_swap_curve_data['Date2'] = df_swap_curve_data['Date']
    df_swap_curve_data.set_index('Date', inplace=True)

    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_3M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_6Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_8Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_9Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_9M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_6M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_7Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('Shi3M_10Y.IB', axis=1)

    df_swap_curve_data = df_swap_curve_data.replace(0, np.nan)
    df_swap_curve_data.fillna(method='bfill', inplace=True)
    df_swap_curve_data.fillna(method='ffill', inplace=True)
    df_swap_curve_data['1Y'] = 0
    df_swap_curve_data['2Y'] = 0
    df_swap_curve_data['3Y'] = 0
    df_swap_curve_data['4Y'] = 0
    df_swap_curve_data['5Y'] = 0

    #today_str = '2024-09-13 00:00:00'
    #today = pd.to_datetime(today_str)

    filename = str(uuid.uuid4().hex) + "_shibor_3m_swap_spread" + ".xlsx"
    writer = pd.ExcelWriter("c://git//ficc-code//swap-spread-proc//" + filename)

    for index, row in df_swap_curve_data.iterrows():
        ref_date = row['Date2']
        tenors = list(map(lambda x: ref_date + x, tenor_buckets))
        nss_curve = get_gcb_pc_curve(pd.to_datetime(ref_date))
        yields = nss_curve.Ytm(pd.to_datetime(tenors))
        df_swap_curve_data.at[index, '1Y'] = yields[0]
        df_swap_curve_data.at[index, '2Y'] = yields[1]
        df_swap_curve_data.at[index, '3Y'] = yields[2]
        df_swap_curve_data.at[index, '4Y'] = yields[3]
        df_swap_curve_data.at[index, '5Y'] = yields[4]

    df_swap_curve_data['swap-spread-1Y'] = (df_swap_curve_data['Shi3M_1Y.IB'] - df_swap_curve_data['1Y']*100)*100
    df_swap_curve_data['swap-spread-2Y'] = (df_swap_curve_data['Shi3M_2Y.IB'] - df_swap_curve_data['2Y']*100)*100
    df_swap_curve_data['swap-spread-3Y'] = (df_swap_curve_data['Shi3M_3Y.IB'] - df_swap_curve_data['3Y']*100)*100
    df_swap_curve_data['swap-spread-4Y'] = (df_swap_curve_data['Shi3M_4Y.IB'] - df_swap_curve_data['4Y']*100)*100
    df_swap_curve_data['swap-spread-5Y'] = (df_swap_curve_data['Shi3M_5Y.IB'] - df_swap_curve_data['5Y']*100)*100

    get_signal(df_swap_curve_data, 'swap-spread-5Y')
    get_signal(df_swap_curve_data, 'swap-spread-4Y')
    get_signal(df_swap_curve_data, 'swap-spread-3Y')
    get_signal(df_swap_curve_data, 'swap-spread-2Y')
    get_signal(df_swap_curve_data, 'swap-spread-1Y')

    df_swap_curve_data.to_excel(writer)
    writer.close()
    print("ALl done " + shibor_3m_irs_data_file)

def get_SwapSpread_fr007():

    df_swap_curve_data = pd.read_excel(file_path + fr007_irs_data_file)

    df_swap_curve_data['Date2'] = df_swap_curve_data['Date']
    df_swap_curve_data.set_index('Date', inplace=True)

    df_swap_curve_data = df_swap_curve_data.drop('FR007_1W.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_2W.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_1M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_2M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_3M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_6M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_9M.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_6Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_7Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_8Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_9Y.IB', axis=1)
    df_swap_curve_data = df_swap_curve_data.drop('FR007_10Y.IB', axis=1)

    df_swap_curve_data = df_swap_curve_data.replace(0, np.nan)
    df_swap_curve_data.fillna(method='bfill', inplace=True)
    df_swap_curve_data.fillna(method='ffill', inplace=True)
    df_swap_curve_data['1Y'] = 0
    df_swap_curve_data['2Y'] = 0
    df_swap_curve_data['3Y'] = 0
    df_swap_curve_data['4Y'] = 0
    df_swap_curve_data['5Y'] = 0

    #today_str = '2024-09-13 00:00:00'
    #today = pd.to_datetime(today_str)

    filename = str(uuid.uuid4().hex) + "_fr007_swap_spread" + ".xlsx"
    writer = pd.ExcelWriter("c://git//ficc-code//swap-spread-proc//" + filename)

    for index, row in df_swap_curve_data.iterrows():
        ref_date = row['Date2']
        tenors = list(map(lambda x: ref_date + x, tenor_buckets))
        nss_curve = get_gcb_pc_curve(pd.to_datetime(ref_date))
        yields = nss_curve.Ytm(pd.to_datetime(tenors))
        df_swap_curve_data.at[index, '1Y'] = yields[0]
        df_swap_curve_data.at[index, '2Y'] = yields[1]
        df_swap_curve_data.at[index, '3Y'] = yields[2]
        df_swap_curve_data.at[index, '4Y'] = yields[3]
        df_swap_curve_data.at[index, '5Y'] = yields[4]

    df_swap_curve_data['swap-spread-1Y'] = (df_swap_curve_data['FR007_1Y.IB'] - df_swap_curve_data['1Y']*100)*100
    df_swap_curve_data['swap-spread-2Y'] = (df_swap_curve_data['FR007_2Y.IB'] - df_swap_curve_data['2Y']*100)*100
    df_swap_curve_data['swap-spread-3Y'] = (df_swap_curve_data['FR007_3Y.IB'] - df_swap_curve_data['3Y']*100)*100
    df_swap_curve_data['swap-spread-4Y'] = (df_swap_curve_data['FR007_4Y.IB'] - df_swap_curve_data['4Y']*100)*100
    df_swap_curve_data['swap-spread-5Y'] = (df_swap_curve_data['FR007_5Y.IB'] - df_swap_curve_data['5Y']*100)*100

    get_signal(df_swap_curve_data, 'swap-spread-5Y')
    get_signal(df_swap_curve_data, 'swap-spread-4Y')
    get_signal(df_swap_curve_data, 'swap-spread-3Y')
    get_signal(df_swap_curve_data, 'swap-spread-2Y')
    get_signal(df_swap_curve_data, 'swap-spread-1Y')

    df_swap_curve_data.to_excel(writer)
    writer.close()
    print("ALl done " + fr007_irs_data_file)

def get_signal(df_swap_curve_data: DataFrame, col_name: str):
    halflife_spread = get_half_life(df_swap_curve_data[col_name])
    if (halflife_spread > 2):
        window_size = int(np.rint(halflife_spread))
        df_swap_curve_data[col_name+'_ave_' + str(window_size)] = df_swap_curve_data[col_name].rolling(
            window=int(window_size), center=False).mean()
        df_swap_curve_data[col_name+'_std_' + str(window_size)] = df_swap_curve_data[col_name].rolling(
            window=int(window_size), center=False).std(ddof=0)
        df_swap_curve_data[col_name+'_zscore_' + str(window_size)] = (df_swap_curve_data[col_name] -
                                                                           df_swap_curve_data[
                                                                               col_name+'_ave_' + str(
                                                                                   window_size)]) / df_swap_curve_data[
                                                                              col_name+'_std_' + str(window_size)]
        df_swap_curve_data[col_name+'_Buy'] = np.where(
            df_swap_curve_data[col_name+'_zscore_' + str(window_size)] >= 1, 1, 0)
        df_swap_curve_data[col_name+'_Sell'] = np.where(
            df_swap_curve_data[col_name+'_zscore_' + str(window_size)] <= -1, 1, 0)
        df_swap_curve_data[col_name+'_percentile'] = df_swap_curve_data[col_name].rolling(
            window_size).apply(lambda x: stats.percentileofscore(x, x[-1]))


if __name__ == '__main__':
   get_SwapSpread_shibor_3m()
   get_SwapSpread_fr007()

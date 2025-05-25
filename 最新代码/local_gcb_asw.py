from pandas import DataFrame
import uuid
from datetime import datetime
from mcp.enums import *
from mcp.tools import *
from dateutil.relativedelta import relativedelta
from AswSpread_cal import AswSpreadFsolve
import statsmodels.tsa.stattools as tsa
import statsmodels.api as sm

src_files = ['local_gcb_asw.xlsx']
#src_files = ['local_corp_asw.xlsx']

local_gcb_static_file = 'c://meridian//债券//信号统计//value_counts.xlsx'
static_df = pd.read_excel(local_gcb_static_file, sheet_name='value_counts')

three_mon_rel = relativedelta(months=3)

file_path= 'c://git//ficc-code//nss-data-credit//'

fdr001_ois_template_file='fdr001-ois-template.xlsx'
fdr001_ois_irs_data_file='fdr001-ois-curve-data.xlsx'
fdr001_ois_rate_data_file='fdr001-ois-rate.xlsx'

df_ois_curve_template = pd.read_excel(file_path + fdr001_ois_template_file)
df_ois_curve_data = pd.read_excel(file_path + fdr001_ois_irs_data_file)
df_ois_rate_data = pd.read_excel(file_path + fdr001_ois_rate_data_file)

fdr001_ois_tenor_buckets = [relativedelta(days=1), relativedelta(months=1), relativedelta(months=3),
                           relativedelta(months=6), relativedelta(months=9), relativedelta(years=1),
                           relativedelta(years=2), relativedelta(years=3), relativedelta(years=4),
                           relativedelta(years=5), relativedelta(years=7), relativedelta(years=10)]

df_ois_curve_data.set_index('Date', inplace=True)
df_ois_rate_data.set_index('Date', inplace=True)

'''SHIBOR 3M'''
shibor_3m_template_file='shibor-3m-template.xlsx'
shibor_3m_irs_data_file='shibor-3m-curve-data.xlsx'
shibor_3m_rate_data_file='shibor-3m-rate.xlsx'

curve_dict = {}
shibor_3m_tenor_buckets = [relativedelta(months=3), relativedelta(months=6), relativedelta(months=9),
                           relativedelta(years=1), relativedelta(years=2), relativedelta(years=3),
                           relativedelta(years=4), relativedelta(years=5), relativedelta(years=7), relativedelta(years=10)]

df_swap_curve_template = pd.read_excel(file_path + shibor_3m_template_file)
df_swap_curve_data = pd.read_excel(file_path + shibor_3m_irs_data_file)
df_shibor_3m_data = pd.read_excel(file_path + shibor_3m_rate_data_file)

df_swap_curve_data.set_index('Date', inplace=True)
df_shibor_3m_data.set_index('Date', inplace=True)
#60 trading days
window_size = 60
df_shibor_3m_data['ave_'+str(window_size)] = df_shibor_3m_data['Shibor3M.IR'].rolling(window=int(window_size), center=False).mean()

df_swap_curve_data = df_swap_curve_data.drop('Shi3M_3M.IB', axis=1)
df_swap_curve_data = df_swap_curve_data.drop('Shi3M_6Y.IB', axis=1)
df_swap_curve_data = df_swap_curve_data.drop('Shi3M_8Y.IB', axis=1)
df_swap_curve_data = df_swap_curve_data.drop('Shi3M_9Y.IB', axis=1)
df_swap_curve_data = df_swap_curve_data.replace(0, np.nan)
df_swap_curve_data.fillna(method='bfill', inplace=True)
df_swap_curve_data.fillna(method='ffill', inplace=True)


def get_fdr001_ois_data(ref_date: datetime):
    df_ois_curve = df_ois_curve_template.copy(deep=True)
    df_ois_curve['SettlementDates'] = ref_date

    curve_data = df_ois_curve_data.loc[ref_date.strftime('%Y-%m-%d')]
    rate_data = df_ois_rate_data.loc[ref_date.strftime('%Y-%m-%d')]
    rate_array = np.array([rate_data['FDR001-D1']])
    # OIS swap yield upto 3Y
    yields_3y = curve_data.sort_values().array
    ois_yields_3y = np.concatenate((rate_array, yields_3y))

    shibor_3m_rate_data = df_shibor_3m_data.loc[ref_date.strftime('%Y-%m-%d')]
    shibor_3m_rate_ave_90 = shibor_3m_rate_data['ave_' + str(window_size)]

    shibor_3m_curve_data = df_swap_curve_data.loc[ref_date.strftime('%Y-%m-%d')]
    shibor_3m_curve_data_4y_10y = shibor_3m_curve_data[['Shi3M_4Y.IB', 'Shi3M_5Y.IB', 'Shi3M_7Y.IB', 'Shi3M_10Y.IB']].array

    ois_yields = np.concatenate((ois_yields_3y, shibor_3m_curve_data_4y_10y-shibor_3m_rate_ave_90+yields_3y[len(yields_3y)-1]))
    tenors = list(map(lambda x: ref_date + x, fdr001_ois_tenor_buckets))

    df_ois_curve['Coupons'] = pd.Series(ois_yields / 100)
    df_ois_curve['MaturityDates'] = pd.Series(tenors)
    return df_ois_curve

def get_shibor_3m_data(ref_date: datetime):
    df_swap_curve = df_swap_curve_template.copy(deep=True)
    df_swap_curve['SettlementDates'] = ref_date
    curve_data = df_swap_curve_data.loc[ref_date.strftime('%Y-%m-%d')]
    rate_data = df_shibor_3m_data.loc[ref_date.strftime('%Y-%m-%d')]
    depo_array = np.array([rate_data['Shibor3M.IR']])

    yields = curve_data.sort_values().array
    swap_yields = np.concatenate((depo_array, yields))

    tenors = list(map(lambda x: ref_date + x, shibor_3m_tenor_buckets))

    df_swap_curve['Coupons'] = pd.Series(swap_yields/100)
    df_swap_curve['MaturityDates'] = pd.Series(tenors)
    return df_swap_curve

def get_swap_curve(data_df: pd.DataFrame):

    mCalibrationSet = mcp.wrapper.McpCalibrationSet()
    calendar = McpCalendar()

    settlement_date = pd.to_datetime(data_df['SettlementDates'].head(1).values[0]).strftime('%Y-%m-%d')

    data_df['MaturityDates_str'] = pd.to_datetime(data_df['MaturityDates'])
    maturityDates_str = data_df['MaturityDates_str'].to_list()
    maturityDates_str_list = [date.strftime('%Y-%m-%d') for date in maturityDates_str]

    FixedFrequenciesList = data_df['Frequencies'].to_list()
    prices = data_df['Coupons'].to_list()
    BumpAmounts = data_df['BumpAmounts'].to_list()
    Buses = data_df['Buses'].to_list()

    args = [1,
            settlement_date,
            settlement_date,
            json.dumps(maturityDates_str_list),
            json.dumps(FixedFrequenciesList),
            json.dumps(prices),
            DayCounter.Act365Fixed,
            DayCounter.Act365Fixed,
            json.dumps(BumpAmounts),
            json.dumps(Buses),
            calendar.getHandler(),
            DateAdjusterRule.ModifiedFollowing]

    #print(f'swapCurveData args: {args}')

    swapCurveData = mcp.mcp.MVanillaSwapCurveData(*args)
    mCalibrationSet.addData(swapCurveData.getHandler())
    mCalibrationSet.addEnd()

    swap_curve_args = data_df.to_dict('list')
    swap_curve_args.update({
        "SettlementDate": settlement_date,
        "CalibrationSet": mCalibrationSet,
        # "DEPO": curveData,
        # "SWAP": swapCurveData,
        "InterpolatedVariable": InterpolatedVariable.CONTINUOUSRATES,
        "InterpolationMethod": InterpolationMethod.LINEARINTERPOLATION,
        "DayCounter": DayCounter.Act365Fixed
    })
    swap_curve = McpSwapCurve(swap_curve_args)
    return swap_curve

def get_years( delta: relativedelta):
    year = delta.years
    year_month = delta.months/12
    year_days = delta.days/365
    return year + year_month + year_days

def get_days( delta: relativedelta):
    days_month = delta.months*30
    return days_month + delta.days

def get_ois_curve (ref_date: datetime, category='ois'):
    key = category + ref_date.strftime('%Y-%m-%d')
    if key in curve_dict:
        return curve_dict[key]
    else:
        ois_curve = get_swap_curve(get_fdr001_ois_data(ref_date))
        curve_dict[key] = ois_curve
        return ois_curve
    return None

def get_shibor3m_curve (ref_date: datetime, category='shibor3m'):
    key = category + ref_date.strftime('%Y-%m-%d')
    if key in curve_dict:
        return curve_dict[key]
    else:
        shibor3m_curve = get_swap_curve(get_shibor_3m_data(ref_date))
        curve_dict[key] = shibor3m_curve
        return shibor3m_curve
    return None

def get_bond_pv_ois(
                ref_date: datetime,
                bond_mat_date: datetime,
                bond_coupon: float,
                freq: int = Frequency.Quarterly):
    frb = McpFixedRateBond({
        'ValuationDate': ref_date.strftime('%Y/%m/%d'),
        'MaturityDate': bond_mat_date.strftime('%Y/%m/%d'),
        'Coupon': bond_coupon,
        'Frequency': freq,
        'DayCounter': DayCounter.ActActXTR,
        #'Calendar': McpCalendar(),
        #'FaceValue': 100,
        #'IssueDate': '2020-05-12',
        #'prevCpnDate': '2022-05-13',
        #'lastCpnDate': '2023-11-13',
        #'firstCouponDate': '2020-11-13',
        #'dateAdjuster': 5,
        #'endToEnd': True,
        #'longStub': False,
       # 'endStub': False,
        #'applyDayCount': False
        })

    pay_dates = frb.PaymentDates()
    #print(pay_dates)

    cash_flows = frb.Payments()
    #TODO, count payment based on date
    cash_flows[0] = bond_coupon * 100 * get_days(relativedelta(pd.to_datetime(pay_dates[0]), pd.to_datetime(ref_date)))/365
    cash_flows[len(cash_flows)-1] = cash_flows[len(cash_flows)-1] - 100
    #print('cash_flows:', cash_flows)

    swap_ois_curve = get_ois_curve(ref_date)

    discount_factors = [swap_ois_curve.DiscountFactor(dt) for dt in pay_dates]
    #print('rates:', rates)
    #print('discount_factors:', discount_factors)
    pv_flows = np.multiply(cash_flows, discount_factors)
    #print('pv_flows:', pv_flows)
    return np.sum(pv_flows), frb

def get_asw_spread_valuation(bond_id: str, cur_date: datetime, mat_date: datetime, bond_coupon: float, corp_bond_flag: bool = True):
    #print('proc bond %s, mat_date: %s, cur_date: %s' %(bond_id, mat_date.strftime('%Y-%m-%d'),  cur_date.strftime('%Y-%m-%d')))
    pv_ois, frb = get_bond_pv_ois(cur_date, mat_date, bond_coupon)
    #print('bond %s, pv_ois: %s' %(bond_id, pv_ois))

    pay_dates = frb.PaymentDates()
    #print('pay_dates:', pay_dates)
    shibor3m_curve=get_shibor3m_curve(cur_date)
    #dates = ['2022/6/13', '2022/6/17', '2022/6/24', '2022/9/13', '2022/12/13', '2023/3/13', '2023/6/13', '2024/6/13',
    #         '2025/6/13', '2026/6/15', '2027/6/14', '2027/6/14']
    rates = [shibor3m_curve.ZeroRate(dt) for dt in pay_dates]
    #print('rates:', rates)

    fwd_rates = [shibor3m_curve.ForwardRate(dt,
                                            (pd.to_datetime(dt)+three_mon_rel).strftime('%Y/%m/%d'),
                                            DayCounter.Act365Fixed,
                                            False,
                                            Frequency.NoFrequency) for dt in pay_dates]
    #print('fwd_rates:', fwd_rates)

    discount_factors = [shibor3m_curve.DiscountFactor(dt) for dt in pay_dates]
    #print('shibor3m discount_factors:', discount_factors)

    year_counts = [0.25]*len(fwd_rates)
    #TODO change first rather last
    year_counts[0] = get_years(relativedelta(pd.to_datetime(pay_dates[0]), pd.to_datetime(cur_date)))

    #print('year_counts:', year_counts)
    aswSpreadFsolve =AswSpreadFsolve(pv_ois,discount_factors, year_counts, fwd_rates)
    aswSpread = aswSpreadFsolve.aswSpread_fsolve()*10000
    #print('bond %s, asw-spread: %s' %(bond_id, aswSpread))
    #print('bond %s, swap rate: %s' %(bond_id, rates[len(rates)-1]))
    estimate_yld = rates[len(rates)-1]*100 + aswSpread/100 if corp_bond_flag else rates[len(rates)-1]*100 - aswSpread/100
    #print('Date {5}, bond {0}, asw-spread-> yld: {1}, pv_ois: {2}, asw-spread: {3}, swap rate: {4}'.
    #      format(bond_id ,estimate_yld, pv_ois, aswSpread, rates[len(rates)-1]*100, cur_date.strftime('%Y-%m-%d')) )
    return aswSpread, estimate_yld

def cal_asw_spread(newdf: DataFrame, date_str: str, maturity_date: datetime, coupon: float, bond_code: str):
    return get_asw_spread_valuation(bond_code, newdf[date_str], maturity_date, coupon/100, False)

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

def getYield(df1: DataFrame, col1: str, col2: str):
    if df1[col2] >= 1:
        return df1[col1]

def getTradeYield(df: DataFrame, yieldStr: str, col2: str,  col3: str):
    #if df1[col2] >= 1:
    #    return df1[col1]
    for index, row in df.iterrows():
        #print(f'Index: {index}, ColumnA: {row["ColumnA"]}, ColumnB: {row["ColumnB"]}')
        if row[col2] > 0:
            index_of_buy_sell = index
            result = df[(df.index > index_of_buy_sell) & ((df['Volumn'] > 0) | (df['Tran'] > 0))]
            #print(index)
            #if index == pd.to_datetime('2023-11-20 00:00:00'):
            #    print(index)
            if len(result) > 0:
                df.at[index, col3] = result.head(1)[yieldStr].values.min()

def getPnl(df2: DataFrame, col1: str, col2: str, multiplier: int, isYield: bool):
    #if df['Buy'] == 1 and df['SellYield'] != None and df['BuyYield'] > 0 and df['SellYield'] > 0 :
    if df2['Sell'] == 1 and df2[col1] != None and df2[col1] > 0 and df2[col2] > 0:
        if isYield:
            return (df2[col1] - df2[col2]) * multiplier
        return (df2[col2] - df2[col1])* multiplier

def calculatePnl(df3: DataFrame):
    df3['BuyYield'] = df3.apply(getYield, args=('Yield', 'Buy'), axis=1, result_type='expand')
    df3['SellYield'] = df3.apply(getYield, args=('Yield', 'Sell'), axis=1, result_type='expand')
    #df['BuyDirtyPrice'] = df.apply(getYield, args=('ValuationDirtyPrice', 'Buy'), axis=1)
    #df['SellDirtyPrice'] = df.apply(getYield, args=('ValuationDirtyPrice', 'Sell'), axis=1)
   #if len(df[df['Sell'] == 1]) > 1:
   #     df['SellYield'].fillna(method='bfill', inplace=True)
    #df3['BuyYield'] = 0
    #df3['SellYield'] = 0
    #getTradeYield(df3,'Yield', 'Buy', 'BuyYield')
    #getTradeYield(df3, 'Yield', 'Sell', 'SellYield')
    b_yield = -1
    b_yield_aswSpread= -1
    for index, row in df3.iterrows():
        #print(row["Name"], row["Age"])
        if row['Buy'] == 1 and b_yield < 0:
            b_yield = row['BuyYield']
            b_yield_aswSpread = row['asw_Spread']
        elif row['Sell'] == 1 and b_yield > 0:
            df3.at[index, 'BuyYield'] = b_yield
            df3.at[index, 'b_yield_aswSpread'] = b_yield_aswSpread
            b_yield = -1
            b_yield_aswSpread = -1

    df3['PnLYield'] = df3.apply(getPnl, args=('BuyYield', 'SellYield', 100, True), axis=1)
    #df['PnLPrice'] = df.apply(getPnl, args=('BuyDirtyPrice', 'SellDirtyPrice', 100*1000, False), axis=1)
    return df3['PnLYield'].sum() #, df['PnLPrice'].sum()

def get_left_year(maturity_date: datetime):
    now = datetime.now()
    return relativedelta(maturity_date, now)
    pass


def stationary_test(data2: pd.Series):
    # compute ADF test statistic
    adf_ = tsa.adfuller(data2,maxlag=1)
    #print('adf', adf_[0])
    #print('p-value', adf_[1])
    #print('T values', adf_[4])
    return adf_[1] < 0.1

def check_spread(spread_trades: pd.Series, spread_sigal: pd.Series, code: str, pnlY: float, left_year, side: str, trades_time: pd.Series):
    #spread_df = static_df
    #code_df = spread_df[(spread_df.bond_id == code)]
    b_a_spread = 0
    #if len(code_df) > 0 :
    #    b_a_spread = code_df['spread'].tolist()[0]
    min_val = spread_trades.min()
    for indx, val in spread_sigal.items():
        if val > min_val:
            #print("diff yield {0}, bid-ask spread {1} for code {2}".format (val, b_a_spread, code))
            print("%%%%%%%%%%%% {5}  for code {0} on {7}, total PnL {1}, diff aswSpread {2}, bid-ask spread {3}, zs-b-a_sprd {6} left {4} "
                  .format(code, pnlY, val - min_val, b_a_spread, left_year, side, val - min_val - b_a_spread, trades_time.max()))
            return True
    return False
    pass

def get_rv_signal(src_file: str):
    print("starting reading ")
    #request_file = 'c://git//strategy-repos-master//butterfly//nss-data//' + src_file
    request_file = 'c://git//ficc-code//nss-data-credit//' + src_file
    src_df = pd.read_excel(request_file)
    codes = src_df.Code.unique()

    filename = str(uuid.uuid4().hex) + "local_gcb_asw_" + src_file
    writer = pd.ExcelWriter("c://git//ficc-code//nss-data-proc//" + filename)
    print("codes length ", len(codes))
    for code in codes:
        if (len(code) > 0):
            newdf = src_df[(src_df.Code == code)]
            newdf['TradeTime'] = pd.to_datetime(newdf['Date'])
            newdf.set_index('Date', inplace=True)
            print('bond code  = ', code)
            code_df = static_df[(static_df.bond_id == code)]
            maturityDates = code_df['maturityDate']
            maturity_date = pd.to_datetime(maturityDates.iloc[0])
            coupon = code_df['coupon'].iloc[0]
            freq = code_df['freq'].iloc[0]
            newdf[['asw_Spread', 'estimate_yld']] = newdf.apply(cal_asw_spread, args=('TradeTime', maturity_date, coupon, code),
                                           axis=1, result_type='expand')
            halflife_Yield = get_half_life(newdf["Yield"])
            # print('halflife_Zero = ', halflife_Zero)
            # halflife_NssZero = get_half_life(newdf["NssZero"])
            # print('halflife_NssZero = ', halflife_NssZero)
            if (halflife_Yield > 1):
                window_size = int(np.rint(halflife_Yield))
                # newdf['AbsDiffZero'] = np.abs(newdf["NssZero"]-newdf["Zero"])*10000
                newdf['ave_' + str(window_size)] = newdf['asw_Spread'].rolling(window=int(window_size),
                                                                            center=False).mean()
                newdf['std_' + str(window_size)] = newdf['asw_Spread'].rolling(window=int(window_size), center=False).std(
                    ddof=0)
                newdf['zscore_' + str(window_size)] = (newdf['asw_Spread'] - newdf['ave_' + str(window_size)]) / newdf[
                    'std_' + str(window_size)]

                newdf['Buy'] = np.where(newdf['zscore_' + str(window_size)] >= 1, 1, 0)
                newdf['Sell'] = np.where(newdf['zscore_' + str(window_size)] <= -1, 1, 0)

                pnlY = calculatePnl(newdf)
                print(">>>>>>>>>>>> pnl yield %s, for code %s" % (pnlY, code))

                tmp20 = newdf.tail(20)
                left_year = get_left_year(maturity_date)
                print("$$$$$$$$$ for code {0}, mat {4} min asw-spread {1}, Max asw-spread {2}, min-max spread {3}, left {5}"
                      .format(code, tmp20['asw_Spread'].min(), tmp20['asw_Spread'].max(),
                              tmp20['asw_Spread'].max() - tmp20['asw_Spread'].min(), maturity_date, left_year))
                newdf.to_excel(writer, sheet_name=code)
                tmp = newdf.tail(2)
                p_val = stationary_test(newdf['asw_Spread'])
                if (len(tmp[tmp['Buy'] == 1]) > 0 or len(tmp[tmp['Sell'] == 1]) > 0) and pnlY > 10 and p_val:
                    tradedf = newdf[(newdf.PnLYield > 0)]
                    if (len(tradedf) <= 2):
                        continue
                    check_spread(tradedf['b_yield_aswSpread'], tmp['asw_Spread'], code, pnlY, left_year,
                                 'Buy' if len(tmp[tmp['Buy'] == 1]) > 0 else 'Sell', tmp['TradeTime'])

                # if len(tmp[tmp['Sell'] == 1]) > 0 :
                #    print("############ Sell trading sigal for code is  ", code)
                # print("done for code is  ", code)

    writer.close()
    print("ALl done ", src_file)

if __name__ == '__main__':
    #get_fdr001_ois_curve(get_fdr001_ois_data())
    #22广东49
    bond_ids  = ['22华发集团MTN004', '21上海债11', '21广东103',  '20广东01',   '21浙江67',   '22北京06',   '22新疆10',   '22广东49']
    #cur_dates = ['2023-06-14',  '2023-07-14',   '2023-08-15', '2023-09-15', '2023-10-16','2023-11-15','2023-05-15',  '2023-04-17']
    cur_dates = ['2023-06-14',  '2023-06-14',   '2023-06-14', '2023-06-14', '2023-06-14', '2023-06-14', '2023-06-14',  '2023-06-14']
    mat_dates = ['2027-03-15', '2027-07-27',    '2026-11-19', '2027-01-20','2041-12-02','2025-01-20','2037-05-27',  '2027-08-05']
    bond_coupons = [0.0434,     0.0307,          0.0291,       0.033,       0.035,      0.0256,         0.033,      0.026 ]
    corp_bond_flags =[True, False, False, False, False, False, False, False]
    ''''
    for bond_id, cur_date, mat_date, bond_coupon, corp_bond_flag in zip(bond_ids, cur_dates, mat_dates, bond_coupons, corp_bond_flags):
        get_asw_spread_valuation( bond_id, pd.to_datetime(cur_date), pd.to_datetime(mat_date) , bond_coupon, corp_bond_flag)

    df_data = pd.read_excel(file_path + '华发.xlsx', sheet_name='Sheet1')
    for bond_id, cur_date, mat_date, bond_coupon in zip(df_data['id'], df_data['Date'], df_data['mat_dates'], df_data['coupon']):
        get_asw_spread_valuation(bond_id, pd.to_datetime(cur_date), pd.to_datetime(mat_date), bond_coupon/100, True)
 
    df_local_gcb_data = pd.read_excel(file_path + 'local_gcb-asw.xlsx', sheet_name='Sheet1')
    for bond_id, cur_date, mat_date, bond_coupon in zip(df_local_gcb_data['Code'], df_local_gcb_data['Date'],
                                                        df_local_gcb_data['maturityDate'],
                                                        df_local_gcb_data['coupon']):
        get_asw_spread_valuation(bond_id, pd.to_datetime(cur_date), pd.to_datetime(mat_date), bond_coupon / 100, False)
    '''
    for src_file in src_files:
        get_rv_signal(src_file)
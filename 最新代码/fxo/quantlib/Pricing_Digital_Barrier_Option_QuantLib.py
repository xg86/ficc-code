import QuantLib as ql

OVML = "OVML EURUSD DIKO 1.0000P B0.9500 01/13/23 N1M"

today = ql.Date(12, ql.October, 2022)
ql.Settings.instance().evaluationDate = today

# option specification
underlying = "EURUSD"
option_type = ql.Option.Put
strike = 1.0
barrier_type = ql.Barrier.DownOut
barrier = 0.95
payoff_amt = 1000000.0
trade_dt = ql.Date(12, 10, 2022)
settle_dt = ql.Date(14, 10, 2022)
expiry_dt = ql.Date(13, 1, 2023)
delivery_dt = ql.Date(17, 1, 2023)

# market data
spot = 0.9703
vol_atm = 12.48
vol_rr = -2.002
vol_bf = 0.400
vol_25d_put = vol_bf - vol_rr / 2 + vol_atm
vol_25d_call = vol_rr / 2 + vol_bf + vol_atm
eur_depo = 0.71764
usd_depo = 3.84558

# simple quotes
spot_quote = ql.SimpleQuote(spot)
vol_atm_quote = ql.SimpleQuote(vol_atm / 100)
vol_25d_put_quote = ql.SimpleQuote(vol_25d_put / 100)
vol_25d_call_quote = ql.SimpleQuote(vol_25d_call / 100)
eur_depo_quote = ql.SimpleQuote(eur_depo / 100)
usd_depo_quote = ql.SimpleQuote(usd_depo / 100)

# delta quotes
atmVol = ql.DeltaVolQuote(
    ql.QuoteHandle(vol_atm_quote),
    ql.DeltaVolQuote.Fwd,
    3.0,
    ql.DeltaVolQuote.AtmFwd,
)
vol25Put = ql.DeltaVolQuote(
    -0.25, ql.QuoteHandle(vol_25d_put_quote), 3.0, ql.DeltaVolQuote.Fwd
)
vol25Call = ql.DeltaVolQuote(
    0.25, ql.QuoteHandle(vol_25d_call_quote), 3.0, ql.DeltaVolQuote.Fwd
)

# term structures

domesticTS = ql.FlatForward(
    0, ql.UnitedStates(ql.UnitedStates.Settlement), ql.QuoteHandle(eur_depo_quote), ql.Actual360()
)
foreignTS = ql.FlatForward(
    0, ql.UnitedStates(ql.UnitedStates.Settlement), ql.QuoteHandle(usd_depo_quote), ql.Actual360()
)

'''
volTS = ql.BlackConstantVol(
    0, ql.UnitedStates(), ql.QuoteHandle(vol_atm_quote), ql.ActualActual()
)
'''
expanded_volTS = ql.BlackConstantVol(
    0, ql.UnitedStates(ql.UnitedStates.Settlement), ql.QuoteHandle(vol_atm_quote), ql.ActualActual(ql.ActualActual.Actual365)
)
#Give RuntimeError: non-plain payoff given
def vanna_volga_barrier_option():
    #RuntimeError: non-plain payoff given
    #payoff = ql.CashOrNothingPayoff(option_type, strike, payoff_amt)
    payoff = ql.AssetOrNothingPayoff(option_type, strike)
    exercise = ql.EuropeanExercise(expiry_dt)
    option = ql.BarrierOption(barrier_type, barrier, 0.0, payoff, exercise)
    engine = ql.VannaVolgaBarrierEngine(
        ql.DeltaVolQuoteHandle(atmVol),
        ql.DeltaVolQuoteHandle(vol25Put),
        ql.DeltaVolQuoteHandle(vol25Call),
        ql.QuoteHandle(spot_quote),
        ql.YieldTermStructureHandle(domesticTS),
        ql.YieldTermStructureHandle(foreignTS),
    )
    option.setPricingEngine(engine)
    return option
#[out] Premium:  74744.98133848533
def binomial_barrier_option():
    payoff = ql.CashOrNothingPayoff(option_type, strike, payoff_amt)
    exercise = ql.EuropeanExercise(expiry_dt)
    option = ql.BarrierOption(barrier_type, barrier, 0.0, payoff, exercise)
    process = ql.GarmanKohlagenProcess(
        ql.QuoteHandle(spot_quote),
        ql.YieldTermStructureHandle(foreignTS),
        ql.YieldTermStructureHandle(domesticTS),
        ql.BlackVolTermStructureHandle(expanded_volTS),
    )
    engine = ql.BinomialBarrierEngine(process, "crr", 200)
    option.setPricingEngine(engine)
    return option


def do_binomial_barrier_option():
    option = binomial_barrier_option()
    print("Premium: ", option.NPV())

def do_vanna_volga_barrier_option():
    option = vanna_volga_barrier_option()
    print("Premium: ", option.NPV())

''''
https://quant.stackexchange.com/questions/73488/pricing-a-digital-barrier-option-using-quantlib-in-python
'''
if __name__ == "__main__":
    do_binomial_barrier_option()
    do_vanna_volga_barrier_option()
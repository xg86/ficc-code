deltaFlys25=0.261/100
deltaFlys10=0.697/100
atm=5.088/100
'''
ATMto25gradient = deltaFlys25 / (atm * 100.0 - 25.0)
extrap10Delta = ATMto25gradient * 10.0 - ATMto25gradient * atm * 100.0
print(f"extrap10Delta Volatility : {extrap10Delta*100:.6f}")

grad25to10 = -(deltaFlys10 -deltaFlys25) / 15.0

extrap5Delta = grad25to10 * 5.0 + deltaFlys25 - grad25to10 * 25.0

extrap1Delta = grad25to10 * 1.0 + deltaFlys25 - grad25to10 * 25.0

error25to10 = (deltaFlys25 - extrap10Delta) / 15.0

deltaFlys05 = extrap5Delta + error25to10 * 5.0
print(f"deltaFlys05 Volatility : {deltaFlys05:.6f}")

deltaFlys01 = extrap1Delta + error25to10 * 9.0
print(f"deltaFlys01 Volatility : {deltaFlys01:.6f}")
'''
#Now
#BBG RR:









def extraploate_delta():
    ATMto25gradient = -m_deltaRiskReversals25 / (m_positiveDeltaNeutralPutDeltas * 100.0 - 25.0)
    print(f"ATMto25gradient: {ATMto25gradient:.6f}")
    extrap10Delta = ATMto25gradient * 10.0 - ATMto25gradient * m_positiveDeltaNeutralPutDeltas * 100.0
    print(f"extrap10Delta: {extrap10Delta:.6f}")
    grad25to10 = -(m_deltaRiskReversals10 - m_deltaRiskReversals25) / 15.0
    print(f"grad25to10: {grad25to10:.6f}")
    extrap5Delta = grad25to10 * 5.0 + m_deltaRiskReversals25 - grad25to10 * 25.0
    print(f"extrap5Delta: {extrap5Delta:.6f}")
    extrap1Delta = grad25to10 * 1.0 + m_deltaRiskReversals25 - grad25to10 * 25.0
    print(f"extrap1Delta: {extrap1Delta:.6f}")
    error25to10 = (m_deltaRiskReversals10 - extrap10Delta) / 15.0
    print(f"error25to10: {error25to10:.6f}")
    m_deltaRiskReversals05 = extrap5Delta + error25to10 * 5.0
    print(f"m_deltaRiskReversals05: {m_deltaRiskReversals05 :.6f}")
    m_deltaRiskReversals01 = extrap1Delta + error25to10 * 9.0
    print(f"m_deltaRiskReversals01: {m_deltaRiskReversals01 :.6f}")

def extraploate_delta_rr_bf (atm: float, rr_25:float, rr_10:float, target_delta:float, isRR:bool, d_25:float = 25.0, d_10:int = 10.0):
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

    if  isRR:
        extrap_target_delta_Adj = extrap_target_delta + error25to10 * (d_10 - target_delta)
        print(f"extrap_target_delta_Adj RR: {extrap_target_delta_Adj:.6f}")
        return extrap_target_delta_Adj

    extrap_target_delta_Adj = extrap_target_delta + error25to10 * (d_10 - target_delta)
    if(extrap_target_delta_Adj < 0):
        return 0.0
    else:
        print(f"extrap_target_delta_Adj BF: {extrap_target_delta_Adj:.6f}")
        return  extrap_target_delta_Adj

def extraploate_delta_pc (atm: float, vol_25:float, vol_10:float, target_delta:float, d_25:float = 25.0, d_10:int = 10.0):
    print(f"***************************************")
    ATMto25gradient = -1 * vol_25 / (atm * 100.0 - d_25)
    print(f"ATMto25gradient: {ATMto25gradient:.6f}")

    grad25to10 = -1 * (vol_10 - vol_25) / (d_25 - d_10)
    print(f"grad25to10: {grad25to10:.6f}")

    extrap10Delta = ATMto25gradient * d_10 - ATMto25gradient * atm * 100.0
    print(f"extrap10Delta: {extrap10Delta:.6f}")

    error25to10 = (vol_10 - extrap10Delta) / (d_25 - d_10)
    #errorAmtto25 = (rr_10 - extrap10Delta) / (50 - d_25)

    print(f"error25to10: {error25to10:.6f}")
    extrap_target_delta = vol_25 + grad25to10 * (d_25-target_delta)/100
    print(f"{target_delta:.6f}, extrap_target_delta: {extrap_target_delta:.6f}")
    extrap_target_delta_Adj = extrap_target_delta + error25to10 * (target_delta)/100
    print(f"extrap_target_delta_Adj: {extrap_target_delta_Adj:.6f}")

#BBG RR:
m_deltaRiskReversals25 = 0.353
m_deltaRiskReversals10 = 0.788
#ATM
m_positiveDeltaNeutralPutDeltas = 4.77

#extraploate_delta2(m_positiveDeltaNeutralPutDeltas, m_deltaRiskReversals25,m_deltaRiskReversals10, 5)
#extraploate_delta2(m_positiveDeltaNeutralPutDeltas, m_deltaRiskReversals25,m_deltaRiskReversals10, 1)
extraploate_delta_rr_bf(m_positiveDeltaNeutralPutDeltas, m_deltaRiskReversals25, m_deltaRiskReversals10, 5, True)
#extraploate_delta2(m_positiveDeltaNeutralPutDeltas, m_deltaRiskReversals25,m_deltaRiskReversals10, 20)
m_deltaBF25 = 0.2775
m_deltaBF10 = 0.62

print(f"m_deltaBF:#################### ")
#extraploate_delta2(m_positiveDeltaNeutralPutDeltas, m_deltaBF25,m_deltaBF10, 5)
#extraploate_delta2(m_positiveDeltaNeutralPutDeltas, m_deltaBF25,m_deltaBF10, 1)
extraploate_delta_rr_bf(m_positiveDeltaNeutralPutDeltas, m_deltaBF25, m_deltaBF10, 5, False)
#extraploate_delta2(m_positiveDeltaNeutralPutDeltas, m_deltaBF25,m_deltaBF10, 20)


atm=4.77
p_25=4.871
p_10=4.996
c_25=5.224
c_10=5.784
#extraploate_delta_pc(atm, p_25, p_10, 5)
#extraploate_delta_pc(atm, c_25, c_10, 5)

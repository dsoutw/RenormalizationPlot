import numpy as np

parameterMin=1
parameterMax=2
#1.784972834669053
# 11-renormalizable without interpolation
#parameterValue=1.7849728346094484
# //27-renormalizable with interpolation
# mechane precision 18-renormalizable
parameterValue=1.7849728359354726
# 7 period trippling renormalizable
# parameterValue=1.927038981795398
parameterZoom=2.0

figureSecondIterate=False
figureMultipleIterate=True
figureDiagonal=True
figureBeta0=True
figureSelfReturn=True
figureMaxLevels=5

precisionPeriodicA=1e-08
precisionPeriodicR=1e-06

interpolationEnabled=True
# unit second
interpolationThreshold=0.05
# precision of sampling points for the interpolation
interpolationPrecision=1e-04

# one-parameter unimodal map
def func(x, mu):
    x=np.float64(x)
    return np.float64(mu)*(np.float64(1.0)+x)*(np.float64(1.0)-x)-np.float64(1.0)
# critical point for the one-paraameter family
def func_c(mu):
    return 0
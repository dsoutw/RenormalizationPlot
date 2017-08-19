import numpy as np

parameterMin=1
parameterMax=2
#1.784972834669053
# 11-renormalizable without interpolation
#parameterValue=1.7849728346094484
# 27-renormalizable with interpolation
parameterValue=1.7849728359354726
parameterZoom=2.0

figureSecondIterate=True
figureMultipleIterate=False
figureDiagonal=False
figureBeta0=True
figureSelfReturn=True

# unit second
interpolationEnabled=True
interpolationThreshold=0.1
interpolationPrecision=0.001

# one-parameter unimodal map
def func(x, mu):
    return mu*(np.float64(1.0)+x)*(np.float64(1.0)-x)-np.float64(1.0)
# critical point
def func_c(mu):
    return 0
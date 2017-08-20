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

interpolationEnabled=True
# unit second
interpolationThreshold=0.1
# precision of sampling points for the interpolation
interpolationPrecision=0.001

# one-parameter unimodal map
def func(x, mu):
    return mu*(np.float64(1.0)+x)*(np.float64(1.0)-x)-np.float64(1.0)
# critical point for the one-paraameter family
def func_c(mu):
    return 0
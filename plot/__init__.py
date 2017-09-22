from plot.graphobject import GraphObject,Group
from plot.artist import ArtistBase
from plot.function import Function
from plot.contour import Contour
from plot.verticalline import VerticalLine
from plot.rectangle import Rectangle
from plot.ticks import Ticks
from plot.text import Text

import numpy as np
import matplotlib.patches as patches
import matplotlib.ticker as ticker
from PyQt5 import QtCore

def VetricalLineList(pointList,*args):
    return [VerticalLine(point, *args) for point in pointList]

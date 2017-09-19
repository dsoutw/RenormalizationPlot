from Plot.GraphObject import GraphObject,Group
from Plot.Artist import ArtistBase
from Plot.Function import Function
from Plot.Contour import Contour
from Plot.VerticalLine import VerticalLine
from Plot.Rectangle import Rectangle
from Plot.Ticks import Ticks
from Plot.Text import Text

import numpy as np
import matplotlib.patches as patches
import matplotlib.ticker as ticker
from PyQt5 import QtCore

def VetricalLineList(pointList,*args):
    return [VerticalLine(point, *args) for point in pointList]

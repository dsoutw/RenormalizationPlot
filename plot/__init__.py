'''
Renormalization Plot - plot/__init__.py
    Plotting package. A wrapper for matplotlib

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.
'''

from .graphobject import GraphObject
from .group import Group
from .artist import ArtistBase
from .function import Function
from .contour import Contour
from .verticalline import VerticalLine
from .rectangle import Rectangle
from .ticks import Ticks
from .text import Text

import numpy as np
import matplotlib.patches as patches
import matplotlib.ticker as ticker
from PyQt5 import QtCore

def VetricalLineList(pointList,*args):
    return [VerticalLine(point, *args) for point in pointList]

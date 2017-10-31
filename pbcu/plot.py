# (C) British Crown Copyright 2017, Met Office
#
# This code is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
"""
Simple plot functions for fast examination of 2d iris cubes.
"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import matplotlib.pyplot as plt

import iris
import iris.quickplot as qplt

def pplot(cb):
    
    # Draw the contour.
    qplt.pcolormesh(cb)

    # Add coastlines.
    plt.gca().coastlines('50m')

    # On screen
    plt.show()


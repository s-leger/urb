# -*- coding:utf-8 -*-

# #
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110- 1301, USA.
#
# 
# <pep8 compliant>

# Copyright (c) 2004-2011 Bruno Postle <bruno@postle.net>.

# ----------------------------------------------------------
# Author: Bruno Postle <bruno@postle.net>
# Python translation: Stephen Leger (s-leger)
#
# ----------------------------------------------------------

'''
Urb::Polygon - Class for maintaining polygon data

Some dodgy new Math::Polygon methods

This module contains some extra methods for L<Math::Polygon>, these methods are
not quite sane enough to be added to L<Math::Polygon> proper.
'''

from .math import distance_2d, scale_2d, points_2line, subtract_2d, add_2d, line_intersection
from ..math.polygon import Polygon as _polygon


class Polygon(_polygon):

    def __init__(self, points):
        _polygon.__init__(self, points)



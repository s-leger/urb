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

# This code is part of distribution Math-Polygon.  Meta-POD processed with
# OODoc into POD and HTML manual-pages.  See README.md
# Copyright Mark Overmeer.  Licensed under the same terms as Perl itself.


'''

This project is free software; you can redistribute it and/or modify it under the same terms as Perl itself.
See http://dev.perl.org/licenses/

Math::Polygon - Class for maintaining polygon data

'''

from .polygon.calc import (
    polygon_bbox,
    polygon_area,
    polygon_centroid,
    polygon_is_clockwise,
    polygon_perimeter,
    polygon_contains_point
)

class Polygon:

    def __init__(self, points):
        self._points = points
        self._clockwise = None
        self._bbox = None
        self._area = None
        self._centroid = None

    @property
    def order(self):
        return len(self._points) - 1

    @property
    def points(self):
        return self._points

    def point(self, index):
        order = self.order + 1
        try:
            iter(index)
            return [self._points[i] for i in index if i < order]
        except:
            pass
        if index < order:
            return self._points[index]
        return None

    @property
    def bbox(self):
        if self._bbox is None:
            self._bbox = polygon_bbox(self._points)
        return self._bbox

    @property
    def area(self):
        if self._area is None:
            self._area = polygon_area(self._points)
        return self._area\

    @property
    def centroid(self):
        if self._centroid is None:
            self._centroid = polygon_centroid(self._points)
        return self._centroid

    @property
    def isClockwise(self):
        if self._clockwise is None:
            self._clockwise = polygon_is_clockwise(self._points)
        return self._clockwise

    def clockwise(self):
        if not self.isClockwise:
            self._points = list(reversed(self._points))
            self._clockwise = True

    def counterClockwise(self):
        if self.isClockwise:
            self._points = list(reversed(self._points))
            self._clockwise = False

    @property
    def perimeter(self):
        return polygon_perimeter(self._points)

    def contains(self, point):
        return polygon_contains_point(point, self._points)
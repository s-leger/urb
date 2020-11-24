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
Urb::Boundary - A division within a quadrilateral space

Models a division within an Urb::Quad object and child quads that share this boundary

A boundary is a division of a quad or the edge of the root quad, it is always a
straight line.  It has various leafnode quads attached to it.  The boundary
object is a list of references to these leafnodes in no particular order.

'''


from math import pi
from .math import distance_2d, angle_2d


class Boundary(list):

    def __init__(self):
        list.__init__(self)


    def add_edges(self, quad, id_edge):
        '''Attach a quad to this boundary, indicate which edge of the quad (0,1,2 or 3) is attached:
        boundary->Add_Edge ($quad, 2);
        '''
        self.append({quad: quad, id_edge: id_edge})

    @property
    def _id(self):
        '''Query the Id of the quad of which this boundary is a division
        :return: boundary_id
        '''
        if len(self) < 1:
            return
        ed = self[0]
        return ed['quad'].boundary_id(ed['id_edge'])

    @property
    def length_total(self):
        '''Query the total length of this boundary
        :return: length_total
        '''
        quad_parent = self[0]['quad'].by_id(self._id)
        return distance_2d(quad_parent.coordinate_a, quad_parent.coordinate_b)

    @property
    def is_valid(self):
        '''Check some internal consistency
        :return: boolean validate_id
        '''
        _id = self._id
        for item in self:
            if _id != item['quad'].boundary_id(item['id_edge']):
                return False
        return True

    def _find_edges(self, quad_a, quad_b):
        edge_a, edge_b = None, None
        for item in self:
            if item['quad'] is quad_a:
                edge_a = item['id_edge']
            if item['quad'] is quad_b:
                edge_b = item['id_edge']
        return edge_a, edge_b

    def overlap(self, quad_a, quad_b):
        '''Given two quads, find out how much they overlap on this boundary, if at all
        :param quad_a:
        :param quad_b:
        :return: distance = boundary->Overlap (quad_a, quad_b)
        '''
        edge_a, edge_b = self._find_edges(quad_a, quad_b)
        if edge_a is None or edge_b is None:
            return 0.0

        if not self._id in {'a', 'b', 'c', 'd'}:
            return 0.0

        _id = self._id

        if quad_a.boundary_id(edge_a) != _id or \
                quad_b.boundary_id(edge_b) != _id:
            return 0.0

        length_a = quad_a.length(edge_a)
        length_b = quad_b.length(edge_b)
        ca0, ca1 = quad_a.coordinate(edge_a), quad_a.coordinate(edge_a + 1)
        cb0, cb1 = quad_b.coordinate(edge_b), quad_b.coordinate(edge_b + 1)

        d = max(
            distance_2d(ca0, cb0),
            distance_2d(ca0, cb1),
            distance_2d(ca1, cb0),
            distance_2d(ca1, cb1)
        )

        if d <= length_b:
            return length_a

        if d <= length_a:
            return length_b

        return length_a + length_b  - d

    def coordinates(self, quad_a, quad_b):
        '''Query coordinates of the segment shared by two overlapping quads
        :param quad_a:
        :param quad_b:
        :return: xy1 xy2 or None
        '''
        edge_a, edge_b = self._find_edges(quad_a, quad_b)
        if edge_a is None or edge_b is None:
            return
        _id = self._id
        if quad_a.boundary_id(edge_a) != _id or \
                quad_b.boundary_id(edge_b) != _id:
            return
        if self.overlap(quad_a, quad_b) <= 0:
            return
        length_a = quad_a.length(edge_a)
        length_b = quad_b.length(edge_b)
        ca0, ca1 = quad_a.coordinate(edge_a), quad_a.coordinate(edge_a + 1)
        cb0, cb1 = quad_b.coordinate(edge_b), quad_b.coordinate(edge_b + 1)

        length = distance_2d(ca0, cb0)
        ea, eb = edge_a + 1, edge_b + 1
        qa, qb = quad_a, quad_b

        d = distance_2d(ca0, cb1)
        if d > length:
            length = d
            ea, eb = edge_a + 1, edge_b

        d = distance_2d(ca1, cb0)
        if d > length:
            length = d
            ea, eb = edge_a, edge_b + 1

        d = distance_2d(ca1, cb1)
        if d > length:
            length = d
            ea, eb = edge_a, edge_b

        # edge_a is contained entirely within edge_b
        if length < length_b:
            ea, eb = edge_a, edge_a + 1
            qb = quad_a

        # edge_a is contained entirely within edge_a
        if length < length_a:
            ea, eb = edge_b, edge_b + 1
            qa = quad_b

        # otherwise edge_a and edge_b partially overlap so we want the two inner points
        c0, c1 = qa.coordiates(ea), qb.coordinates(eb)
        rad_quads = angle_2d(quad_a.centroid, quad_b.centroid)
        rad_edge = angle_2d(c1, c0)
        rad = rad_edge - rad_quads
        if rad > pi:
            return c0, c1
        else:
            return c1, c0

    def bearing(self, quad_a, quad_b):
        '''Query perpendicular bearing between centre quad and boundary with other quad,
        i.e. if this boundary is a wall, which direction does it face (east = 0.0, north = 1.57):
        :param quad_a:
        :param quad_b:
        :return: radians
        '''
        coor_a, coor_b = self.coordinates(quad_a, quad_b)
        centroid = quad_a.centroid
        angle_a = angle_2d(centroid, coor_a)
        angle_b = angle_2d(centroid, coor_b)

        angle = (angle_a - angle_b) % (2 * pi)
        # TODO: check for the % method
        angle_wall = angle_2d(coor_a, coor_b) % (2 * pi)
        if angle < pi / 2:
            angle_wall = angle_2d(coor_b, coor_a) % (2 * pi)
        return angle_wall

    def middle(self, quad_a, quad_b):
        '''Query the mid point of an edge half way up
        :param quad_a:
        :param quad_b:
        :return: tuple coor 3d
        '''
        coor_a, coor_b = self.coordinates(quad_a, quad_b)
        return 0.5 * (coor_a[0] + coor_b[0]), 0.5 * (coor_a[1] + coor_b[1]), quad_a.elevation + 0.5 * quad_a.height

    @property
    def pairs(self):
        '''Get a list of all pairs of quads that have a segment that is part of this boundary
        :return: list of pairs of quads
        '''
        if self._id is None or not not self._id in {'a', 'b', 'c', 'd'}:
            return []
        pairs = []
        for index_a, item_a in enumerate(self[:-1]):
            quad_a = item_a['quad']
            for item_b in self[index_a + 1:]:
                quad_b = item_b['quad']
                if self.overlap(quad_a, quad_b) > 0:
                    pairs.append([quad_a, quad_b])
        return pairs

    @property
    def pairs_by_length(self):
        '''Get a list of all pairs as with Pairs(), but sorted by length of shared segment
        :return: list of pairs of quads
        '''
        pairs = self.pairs
        pairs.sort(key=lambda x: self.overlap(x[0], x[1]))
        return pairs

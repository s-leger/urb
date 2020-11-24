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
Urb::Quad - Unit of architectural space

A fundamental unit of architectural space, four sided with straight edges. Can
be subdivided into two, forming a binary tree.

A quad has location in 2D space, it can be a child of another quad or be a root
of a binary tree, only leafnodes are actual spaces, branchnodes are containers.

A quad can have 0 or 2 children, it has type, rotation and division attributes
which define the geometry of children.

A Root quad can have another tree attached above or below.

Not to be confused with a 'quad tree', is related to a 'KD tree'.

'''

from math import pi, sin, cos, acos, atan2
from copy import deepcopy
from .math import (
    points_2line, subtract_2d, line_intersection, normalise_2d, triangle_area, is_between_2d,
    angle_2d, scale_2d, distance_2d
)
from .boundary import Boundary
from ..graph.graph import Graph



class Quad:

    def __init__(self, parent=None):
        self._parent = parent
        self._above = None
        self._below = None
        self.child = []
        # coords
        self.node = [None] * 4
        self._typ = None
        self.occlusion = None
        self.boundariees = None
        self._rotation = 0
        self._elevation = None
        self._height = None
        self.division = []

        # defaults ??
        self._perimeter = 0
        self.style = None
        self.wall_inner = False
        self.wall_outer = False

        # failure messages
        self._errors = []
        # ??
        self._id_cache = None

    @property
    def divided(self):
        return len(self.child) > 0 and len(self.division) > 0

    @property
    def serialized(self):
        '''Dereference and serialise a quad object suitable for transfer or persistent storage'''
        return

    @property
    def left(self):
        if self.divided:
            return self.child[0]
        return None

    @property
    def right(self):
        if self.divided:
            return self.child[1]
        return None

    @property
    def parent(self):
        return self._parent

    @property
    def r(self):
        return self.right

    @property
    def l(self):
        return self.left

    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root
        return self

    @property
    def above(self):
        if self._above is not None and self.parent is None:
            return self._above
        if self.root.above is None:
            return
        if self.root.above.by_id(self._id) is not None:
            return self.root.above.by_id(self._id)
        return

    @property
    def below(self):
        if self._below is not None and self.parent is None:
            return self._below
        if self.root.below is None:
            return
        if self.root.below.by_id(self._id) is not None:
            return self.root.below.by_id(self._id)
        return

    @property
    def below_more(self):
        '''
        There may not be a matching quad above or below, so retrieve the quad above or
        below the parent if necessary
        :return:
        '''
        if self.root.levels_below == 0:
            return None
        if self.below is not None:
            return self.below
        return self.parent.below_more

    @property
    def above_more(self):
        '''
        There may not be a matching quad above or below, so retrieve the quad above or
        below the parent if necessary
        :return:
        '''
        if self.root.levels_above == 0:
            return None
        if self.above is not None:
            return self.above
        return self.parent.above_more

    @property
    def below_leafs(self):
        '''
        # ??? not certain about logick here
        Get a list of all leafs below or above this one, note that a single leaf may be
        same size or larger than the current quad
        :return:
        '''
        return  [c.leafs for c in self.below_more]

    @property
    def above_leafs(self):
        '''
        Get a list of all leafs below or above this one, note that a single leaf may be
        same size or larger than the current quad
        :return:
        '''
        return [c.leafs for c in self.above_more]

    @property
    def below_children(self):
        '''
        # ??? not certain about logick here
        Get a list of all children below or above this one, note that a single child may be
        same size or larger than the current quad
        :return:
        '''
        return [c.children for c in self.below_more]

    @property
    def above_children(self):
        '''
        Get a list of all children below or above this one, note that a single child may be
        same size or larger than the current quad
        :return:
        '''
        return [c.children for c in self.above_more]

    @property
    def lowest(self):
        if self.below is None:
            return self
        return self.below.lowest

    @property
    def highest(self):
        if self.above is None:
            return self
        return self.above.highest

    def vertical_connection(self, other=None):
        if other is None:
            return
        if abs(self.level - other.level) != 1:
            return 0.0
        overlappers = self.below_children, self.above_children
        # ?? translate this
        # return 0.0 unless grep {$other} @overlappers;
        areas = [self.area, other.area]
        areas.sort()
        return areas

    def by_relative_id(self, _id=''):
        rel = list(filter(lambda x: x in {'l', 'r'}, index))
        lr = len(rel)
        if not self.divided and lr == 0:
            return None
        if lr == 0:
            return self
        if lr == 1:
            if rel[0] == 'l':
                return self.left
            elif rel[0] == 'r':
                return self.right
        if rel[0] == 'l':
            return self.left.by_relative_id("".join(rel[1:]))
        if rel[0] == 'r':
            return self.right.by_relative_id("".join(rel[1:]))

    def by_relative_level(self, _id):
        '''Access a level by name
        :param _id:
        :return:
        '''
        if _id < 0:
            return self.below.by_relative_level(_id + 1)
        else:
            return self.above.by_relative_level(_id - 1)

    def by_id(self, _id):
        return self.root.by_relative_id(_id)

    def by_level(self, _id):
        return self.lowest.by_relative_level(_id)

    def parents(self, parents):
        '''
        Get a list of parent quads, starting with the current parent all the way up to the root.
          @quad = $quad->Parents;
        :param parents:
        :return:
        '''
        if self.parent is None:
            return parents
        parents.append(self.parent)
        return self.parent.parents(parents)

    def levels_below(self, levels_below):
        '''
        Get a list of quads below or above this one
        :param levels_below:
        :return:
        '''
        if self.root.below is None:
            return levels_below
        levels_below.append(self.root.below)
        return self.root.below.levels_below(levels_below)

    def levels_above(self, levels_above):
        '''
        Get a list of quads below or above this one
        :param levels_above:
        :return:
        '''
        if self.root.above is None:
            return levels_above
        levels_above.append(self.root.above)
        return self.root.above.levels_above(levels_above)

    @property
    def leafs(self):
        '''
        Get a list of all leafnode quads, including self if necessary, i.e. not
        branches
        :return:
        '''
        if not self.divided:
            return self
        return self.left.leafs, self.right.leafs

    @property
    def branches(self):
        '''
        Get a list of all branchnode quads, including self if necessary, i.e. not
        leafs
        :return:
        '''
        if not self.divided and self.parent is None:
            return self
        if not self.divided:
            return []
        return self, self.left.branches, self.right.branches

    @property
    def children(self):
        '''
        Get a list of all child quads, both leafnode and branchnode, including self if
        necessary
        :return:
        '''
        if not self.divided:
            return self
        return self, self.left.children, self.right.children


    def __hash__(self):
        return hash(self.serialized)

    def deserialize(self, data):
        self._deserialize_recursive(data[0])

    def _deserialize_recursive(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def clean_cache(self):
        if self.parent is not None or self.below is not None:
            self.node = [None] * 4
            self._perimeter = None
            self._elevation = None

        self._id_cache = None
        if self.parent is None and self.above is not None:
            self.above.clean_cache()

        if not self.divided:
            return True

        self.left.clean_cache()
        self.right.clean_cache()

        if self.parent is not None:
            self._above = None

        return True

    def divide(self, ratios):
        if ratios is not None:
            self.division = ratios
        else:
            self.division = [0.5, 0.5]
        self.clean_cache()
        if self.left is not None:
            return

        self.child.append(Quad(self))
        self.child.append(Quad(self))
        return True

    def undivide(self):
        if not self.divided:
            return False
        self.left.undivide()
        self.right.undivide()
        if self.above is not None and self.above.divided:
            self.above.divide(self.division)

        del self.child[1]
        del self.child[0]
        self.child = []
        return True

    def add_above(self):
        if self.root.above is not None:
            return False
        self.root.above = Quad()
        self.root.above.below = self.root
        return True

    def del_above(self):
        if self.root.above is None:
            return False
        self.root.above.del_above()
        self.root.above.undivide()
        self.root.above = None
        return True

    def clone_above(self):
        root = self.root
        clone = root.clone()
        root.del_above()
        root._above = clone
        root.above._below = root
        root.clean_cache()
        return True

    def swap_above(self):
        if self.parent is not None:
            return
        if self.above is None:
            return False
        a = self.clone()
        a.del_above()
        b = self.above.clone()
        b.del_above()

        c = None
        if self.above.above is not None:
            c = self.above.above.clone()

        a._above = c
        a._below = b
        b._above = a
        b._below = self.below
        if c is not None:
            c._below = a

        keys = {'_below', 'node', '_perimeter', 'occlusion', '_elevation', 'style', 'wall_inner', 'wall_outer'}
        self.undivide()
        self.del_above()
        for k in keys:
            setattr(self, k, getattr(b, k))
        self.above._below = self
        if self.below is not None:
            self.below._above = self
        if self.divided:
            self.left._parent = self
            self.right._parent = self
        b.child = []
        b.parent = None
        b._above = None
        b._bleow = None
        self.clean_cache()
        return True

    def collapse(self, width):
        if not self.divided:
            return False
        if self.left.length_narrowest < width:
            tmp = self.right.clone()
            self.undivide()
            self.crossover(tmp)
            del tmp
            self.straighten_recursive()
            return True
        if self.right.length_narrowest < width:
            tmp = self.left.clone()
            self.undivide()
            self.crossover(tmp)
            del tmp
            self.straighten_recursive()
            return True
        return False

    def rotate(self):
        '''Rotate the quad anti-clockwise by a quarter turn, all children are moved along
        :return:
        '''
        self.rotation(self._rotation + 1)
        return True

    def unrotate(self):
        '''Rotate the quad clockwise by a quarter turn, all children are moved along
        :return:
        '''
        self.rotation(self._rotation - 1)
        return True

    def swap(self):
        if not self.divided:
            return False
        self.child[:] = [self.right, self.left]
        self.clean_cache()
        return True

    def crossover(self, alien):
        '''Swap everything except any parent and coordinates between any two quad objects:
        :param alien:
        :return:
        '''
        if alien is None:
            return False
        # can't do anything if one quad is a descendant of another
        for p in alien.parents:
            if p == self:
                return False
        for p in self.parents:
            if p == alien:
                return False

        _in = alien.clone()
        _out = self.clone()
        keys = {'_below', 'parent', 'node', '_perimeter', 'occlusion', '_elevation'}
        self.undivide()
        if self.parent is None:
           self.del_above()
        for k in keys:
            setattr(self, k, getattr(_in, k))
        if self.divided:
            self.left.parent = self
            self.right.parent = self
        if self.parent is None and self.below is not None:
            self.below._above = self
        if self.parent is None and self.above is not None:
            self.above._below = self

        alien.undivide()
        if alien.parent is None:
            alien.del_above()
        for k in keys:
            setattr(alien, k, getattr(_out, k))
        if alien.divided:
            alien.left.parent = alien
            alien.right.parent = alien
        if alien.parent is None and alien.below is not None:
            alien.below._above = alien
        if alien.parent is None and alien.above is not None:
            alien.above._below = alien

        _in.child = []
        _in._above = None
        _out.child = []
        _out._above = None

        self.clean_cache()
        alien.clean_cache()
        return True

    def _straighten(self, orientation):
        line1 = points_2line(
            self.coordinate_a,
            subtract_2d(self.coordinate_a, orientation)
        )
        line2 = points_2line(self.coordinate(2), self.coordinate(3))
        if line1['a'] == line2['a']:
            return False
        intersection = line_intersection(line1, line2)
        full = subtract_2d(self.coordinate(2), self.coordinate(3))
        partial = subtract_2d(intersection, self.coordinate(3))

        return full, partial

    def straghten(self):
        '''
        Align the division line of the current quad with the division line of the
        parent.  Depending on rotation this will be either parallel or perpendicular to
        the parent division line
        :return:
        '''
        if self.parent is not None or not self.divided:
            return False
        if self._rotation in {0, 2}:
            orientation = self.parent.orientation
        else:
            orientation = self.parent.orientation_perpendicular
        full, partial = self._straighten(orientation)
        if abs(full[0]) < abs(full[1]):
            division = partial[1] / full[1]
        else:
            division = partial[0] / full[0]
        if not (0 < division < 1):
            return False
        self.division[1] = division
        self.clean_cache()
        return True

    def straighten_recursive(self, reference=0):
        '''
        Apply Straighten() or Straighten_Root() to the current quad and all children:

          $quad->Straighten_Recursive ($reference);

        The parameter is '0, 1, 2 or 3' indicating which edge you would like the
        division of a root quad to use for alignment.

        Note if you want to guarantee to straighten the entire binary tree then you need to
        apply this to the Root() object:

        :return:
        '''
        for c in self.children:
            if c.parent is not None:
                c.straighten()
            else:
                c.straighten_root(reference)
                if c.above is not None:
                    c.above.straighten_recursive(reference)
        return True

    def straighten_root(self, reference=0):
        '''
        Align the division line of a root quad to one of the four outside edges:

          $quad->Straighten_Root ($reference);

        The parameter is '0, 1, 2 or 3' indicating which edge you would like the to use
        for alignment.  Note that depending on rotation this will be either parallel or
        perpendicular to the specified edge.
        :param reference:
        :return:
        '''
        if not self.divided or self.parent is not None:
            return False
        orientation = normalise_2d(
            subtract_2d(self.coordinate(reference), self.coordinate(1 + reference))
        )
        if reference in {0, 2}:
            # cross
            orientation = -orientation[1], orientation[0]

        full, partial = self._straighten(orientation)
        if full[0] == 0:
            division = partial[1] / full[1]
        else:
            division = partial[0] / full[0]
        if not (0 < division < 1):
            return False
        self.division[1] = division
        self.clean_cache()
        return True

    def shift(self, x, y, z=0):
        '''
        Shift the position of a quad by X, Y (and optionally Z)
        :param x:
        :param y:
        :param z:
        :return:
        '''
        root = self.root.lowest
        for node in root.node:
            node[0] += x
            node[1] += y
        root._elevation += z
        root.clean_cache()
        return True

    def clone(self):
        '''
        Create a duplicate of any quad creating a new binary tree, if this is not a root node
        then the quad is converted into a root.
        :return:
        '''
        coor = self.coordinate[:]
        new = deepcopy(self)
        if new.node[0] is None:
            new.node = coor
            new.rotation(0)
        if new.parent is not None:
            parent = new.parent
            if new == parent.left:
                parent.right.undivide()
            if new == parent.right:
                parent.left.undivide()
            parent.child = []
            lowest = parent.root.lowest
            lowest.del_above()
            lowest.undivide()
        elif new.below is not None:
            below = new.below
            below._above = None
            lowest = below.root.lowest
            lowest.del_above()
            lowest.undivide()

        new._parent = None
        new._below = None
        return new

    def fail_reset(self):
        self._errors.clear()

    def fail(self, msg):
        self._errors.append(msg)

    def failures(self):
        return self._errors

    def typ(self, typ=None):
        '''
        What is the 'type' of the quad (a string not a class name)
        NOTE type is a python reserved keyword
        :return:
        '''
        if typ is not None:
            self._typ = typ
        if self._typ is not None:
            return self._typ
        return ''

    @property
    def level(self):
        '''
        What is the level (0, 1, 2, ...)
        :return:
        '''
        levels_below = []
        return len(self.root.levels_below(levels_below))

    @property
    def perimeter(self):
        '''
        Access the Perimeter definition, this is stored in the lowest root, generally
        read-only
        :return:
        '''
        if self.root.below is None:
            return self.root._perimeter
        return self.root.below.perimeter

    @property
    def aspect(self):
        '''
        What is the aspect ratio of the quad:

          $ratio = $quad->Aspect;

        This is always greater than 1.0, 1.0 is equivalent to a 1:1 aspect ratio, 2.0
        is equal to 2:1 etc...
        :return:
        '''
        aspect = (self.length(0) + self.length(2)) / (self.length(1) + self.length(3))
        if 0 < aspect < 1:
            aspect = 1 / aspect
        return aspect

    def rotation(self, rotation=None):
        if rotation is not None:
            self._rotation = rotation % 4
            self.clean_cache()
        if self.below is not None:
            return self.below.rotation()
        return self._rotation

    @property
    def height(self):
        '''
        Query the height or elevation of this level
        :return:
        '''
        if self.root._height is not None:
            return self.root._height
        return 3.0

    @property
    def elevation(self):
        '''
        Query the height or elevation of this level
        :return:
        '''
        root = self.root
        if root.below is None:
            if root._elevation is not None:
                return root._elevation
            return 0.0
        return root.below.elevation + root.below.height

    @property
    def area(self):
        '''
        Query the area of a quad
        :return:
        '''
        return triangle_area(self.coordinate(0), self.coordinate(1), self.coordinate(2)) +\
            triangle_area(self.coordinate(0), self.coordinate(2), self.coordinate(3))

    @property
    def position(self):
        '''
        Query the position of the current quad (i.e. is it the left or right child):

          $id = $quad->Position;

        Answer is always 'l' or 'r', or '' for the root quad
        :return:
        '''
        if self.parent is None:
            return ''
        if self.parent.left == self:
            return 'l'
        if self.parent.right == self:
            return 'r'
        return None

    @property
    def _id(self):
        '''
        # NOTE: id is a reserved keyword in python
        Query the address of the current quad relative to the root:

          $string = $quad->Id;

        The root level quad is '', children of this are 'l' and 'r', children of 'r'
        are 'rl' and 'rr' etc...

        This string is usable as the parameter for By_Id().
        :return:
        '''
        if self.parent is None:
            return ''
        if self._id_cache is None:
            self._id_cache = self.parent._id + self.position
        return self._id_cache

    def corners_in_use(self, graph, neighbours):
        '''
        Given a list of neighbours, return the smallest set of corner ids that coincide
        with these neighbours, i.e. where we can't put a stair:

          @ids = $quad->Corners_In_Use ($graph, @neighbours);

        Note ids are always consecutive, but may be > 3

        :param graph:
        :param neighbours:
        :return:
        '''
        walls = [graph.get_edge_attribute(self, n, 'coordinates') for n in neighbours]
        corners = [self.coordinate(i) for i in range(3)]
        # try single corners
        for i in range(3):
            ok = True
            for wall in walls:
                if is_between_2d(corners[i], wall):
                    continue
                ok = False
            if ok:
                return i

        # try pairs of corners
        for i in range(3):
            ok = True
            for wall in walls:
                if is_between_2d(corners[i], wall):
                    continue
                if is_between_2d(corners[i + 1], wall):
                    continue
                if is_between_2d(wall[0], corners[i], corners[i + 1]):
                    continue
                if is_between_2d(wall[1], corners[i], corners[i + 1]):
                    continue
                ok = False
            if ok:
                return i, i + 1

        # try three corners
        for i in range(3):
            ok = True
            for wall in walls:
                if is_between_2d(corners[i], wall):
                    continue
                if is_between_2d(corners[i + 1], wall):
                    continue
                if is_between_2d(corners[i + 2], wall):
                    continue
                if is_between_2d(wall[0], corners[i], corners[i + 1]):
                    continue
                if is_between_2d(wall[1], corners[i], corners[i + 1]):
                    continue
                if is_between_2d(wall[0], corners[i + 1], corners[i + 2]):
                    continue
                if is_between_2d(wall[1], corners[i + 1], corners[i + 2]):
                    continue
                ok = False
            if ok:
                return i, i + 1, i + 2

        # then it must be all four corners
        return 0, 1, 2, 3

    def coordinate(self, index):
        '''
        Corner coordinates, number increments anti-clockwise. Number changes with
        rotation
        :param index:
        :return:
        '''
        if self.below:
            return self.below.coordinate(index)
        index = (index + self.rotation()) % 4
        if self.node[index] is not None:
            return self.node[index]

        # just return rotated coordinates if this is the root-level quad
        if self.parent is None:
            return self.node[index]

        res = 0
        # it isn't root level so get coordinates from parent
        if self.position == 'l':
            if index == 0:
                res = self.parent.coordinate(0)
            elif index == 1:
                res = self.parent.coordinate_a
            elif index == 2:
                res = self.parent.coordinate_b
            elif index == 3:
                res = self.parent.coordinate(3)
        if self.position == 'r':
            if index == 0:
                res = self.parent.coordinate_a
            elif index == 1:
                res = self.parent.coordinate(1)
            elif index == 2:
                res = self.parent.coordinate(2)
            elif index == 3:
                res = self.parent.coordinate_b

        self.node[index] = res
        return res

    def coordinate_offset(self, index, offset=None):
        '''
        The same, but offset by specified distance, positive is outside, negative is inside:

          $coor = $quad->Coordinate (2, $distance);

        When used without an offset, behaviour is identical to Coordinate():

          is_deeply ($quad->Coordinate (2), $quad->Coordinate_Offset (2));

        :param index:
        :param offset:
        :return:
        '''
        if offset is None:
            return self.coordinate(index)

        b_coor = self.coordinate(index)
        c_coor = self.coordinate(index + 1)
        theta2 = 0.5 * self.angle(index)
        angle_new = angle_2d(b_coor, c_coor) + theta2
        vector = scale_2d(offset / sin(theta2), [cos(angle_new), sin(angle_new)])
        return subtract_2d(b_coor, vector)

    @property
    def mini(self):
        '''
        Query bounding box:

          $coor = $quad->Min;
          $coor = $quad->Max;

        Used for determining bounding box for drawing operations, coordinate may be
        outside quad.
        :return:
        '''
        x, y = zip(*[self.coordinate(i) for i in range(4)])
        return min(x), min(y)

    @property
    def maxi(self):
        '''
        Query bounding box:

          $coor = $quad->Min;
          $coor = $quad->Max;

        Used for determining bounding box for drawing operations, coordinate may be
        outside quad.
        :return:
        '''
        x, y = zip(*[self.coordinate(i) for i in range(4)])
        return max(x), max(y)

    @property
    def coordinate_a(self):
        '''
        Query cooridinates of the ends of the division
        :return:
        '''
        if not self.divided:
            return
        if self.below is not None and self.below.divided:
            return self.below.coordinate_a
        tmp = self.division[0]
        x = self.coordinate(0)[0] * (1 - tmp) + \
            self.coordinate(1)[0] * tmp
        y = self.coordinate(0)[1] * (1 - tmp) + \
            self.coordinate(1)[1] * tmp
        return x, y

    @property
    def coordinate_b(self):
        '''
        Query cooridinates of the ends of the division
        :return:
        '''
        if not self.divided:
            return
        if self.below is not None and self.below.divided:
            return self.below.coordinate_b
        tmp = self.division[1]
        x = self.coordinate(3)[0] * (1 - tmp) + \
            self.coordinate(2)[0] * tmp
        y = self.coordinate(3)[1] * (1 - tmp) + \
            self.coordinate(2)[1] * tmp
        return x, y

    @property
    def centroid(self):
        '''
        Query the centroid of the quad
        :return:
        '''
        x, y = zip(*[self.coordinate(i) for i in range(4)])
        return 0.25 * sum(x), 0.25 * sum(y)

    @property
    def orientation(self):
        '''
        Get a normalised vector parallel to the current division
        :return:
        '''
        vector = subtract_2d(self.coordinate_b, self.coordinate_a)
        return normalise_2d(vector)

    @property
    def orientation_perpendicular(self):
        '''
        Get a normalised vector parallel to the current division
        :return:
        '''
        orientation = self.orientation
        return -orientation[1], orientation[0]

    def angle(self, index):
        '''
        Query the corner angles of the quad, angles are radians
        :return:
        '''
        a = self.length(index)
        b = self.length(index - 1)
        c = distance_2d(self.coordinate(index + 1), self.coordinate(index - 1))
        return acos((a**2 + b**2 - c**2) / (2 * a * b))

    def bearing(self, index):
        '''
        Query the bearing in radians perpendicular to an edge, i.e. 0.0 is due east 1.57 is due north.

          $radians = $quad->Bearing ($id);

        :return:
        '''
        x, y = subtract_2d(self.coordinate(index + 1), self.coordinate(index))
        return (atan2(y, x) - pi / 2) % (2 * pi)

    def middle(self, index):
        '''
        Query the mid point of an edge half way up
        :param index:
        :return:
        '''
        xa, ya = self.coordinate(index)
        xb, yb = self.coordinate(index + 1)
        return 0.5 * (xa + xb), 0.5 * (ya + yb), self.elevation + 0.5 * self.height

    def length(self, index=0):
        '''
        Query the edge lengths of a quad
        :param index:
        :return:
        '''
        return distance_2d(self.coordinate(index), self.coordinate(index + 1))

    @property
    def length_narrowest(self):
        '''
        Get the shortest of the four lengths
        :return:
        '''
        ids = self.by_length
        return self.length(ids[0])

    @property
    def by_length(self):
        '''
        Get all four lengths, shortest first
        :return:
        '''
        id_edges = [(i, self.length(i),) for i in range(4)]
        id_edges.sort(key=lambda x: x[1])
        return [index for (index, size) in id_edges]

    def boundary_id(self, index=0):
        '''
        Query the boundary id of the four edges:

          $string = $quad->Boundary_Id (0);
          $string = $quad->Boundary_Id (1);
          $string = $quad->Boundary_Id (2);
          $string = $quad->Boundary_Id (3);

        Note that this is equivalent to the Id of whichever quad provides the division
        that forms this boundary. If boundary is an outside boundary of the root quad
        then 'a, b, c or d' is returned.
        :param index:
        :return:
        '''
        index = (index + self.rotation()) % 4
        if self.parent is None:
            return 'abcd'[index]
        if self.position == 'l' and index == 1:
            return self.parent._id
        if self.position == 'r' and index == 3:
            return self.parent._id
        return self.parent.boundary_id(index)

    def by_area(self, ref=0.0001):
        '''
        Get a list of quads sorted by area nearest to a specified value, e.g. quads
        with an area most similar to 10.0:

          @list = $quad->By_Area (10.0);

        Each entry is [$ratio, $quad_ref]
        :param ref:
        :return:
        '''
        levels_above = [self.root]
        res = []
        for quad in [c.children for c in self.root.levels_above(levels_above)]:
            area = quad.area
            ratio = area / ref
            if ratio < 1:
                ratio = 1 / ratio
            res.append((ratio, quad))
        res.sort(key=lambda x: x[0])
        return res

    def calc_boundaries(self):
        '''
        Figure out all the boundaries:

          $hash = $quad->Calc_Boundaries;

        Returns a hash of L<Urb::Boundary> objects, keys are boundary Ids
        :return:
        '''
        boundaries = {branch._id: Boundary() for branch in self.branches}
        for _id in {'a', 'b', 'c', 'd'}:
            boundaries[_id] = Boundary()
        for quad in self.leafs:
            for edge in range(4):
                boundaries[quad.boundary_id(edge)].add_edge(quad, edge)
        self.boundaries = boundaries
        return boundaries

    def graph(self, threshold=0.001):
        '''
        Figure out topology of connections between quads, this is an undirected graph
        and completely different to the binary tree of the structure:

          $threshold = 1.25;
          $graph = $quad->Graph ($threshold);

        Returns a L<Graph> object representing the adjacentness of leafs.

        Note that this is currently very slow.
        :return:
        '''
        boundaries = self.calc_boundaries()
        # refverexed means vertex use reference to own objects
        # see https://metacpan.org/pod/distribution/Graph/lib/Graph.pod#refvertexed
        graph = Graph()
        for boundary_id, boundary in boundaries.items():
            for pair in boundary.pairs:
                overlap = boundary.overlap(pair)
                if overlap < threshold:
                    continue
                w0, w1 = [p.centroid for p in pair]
                c0, c1 = boundary.coordinates(pair)
                graph.add_edge(
                    pair,
                    {
                        'weight': distance_2d(w0, w1),
                        'coordinates': (c0, c1),
                        'width':overlap,
                        'label': ''
                    }
                )
        return graph

    def graph_clone(self, graph):
        # deep copy ??
        return graph.clone()

    def graph_sorted_apl(self, graph):
        return graph.sorted_apl()


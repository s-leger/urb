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
Urb::Math - Misc maths functions
NOTE: coords are returned as immutable tuple
'''


from math import pi, sqrt, atan2, sin, cos


def subtract_2d(a, b):
    '''vector_from_a_to_b = subtract_2d (b, a)'''
    return [a[0] - b[0], a[1] - b[1]]


def subtract_3d(a, b):
    '''vector_from_a_to_b = subtract_2d (b, a)'''
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def distance_2d(a, b):
    '''distance = distance_2d (coor_a, coor_b)'''
    if a is None or b is None:
        return 0
    return sqrt ((a[0] - b[0])**2 + (a[1] - b[1])**2)


def is_between_2d(point, points, points2=None):
    '''Is a point on a line between two other points'''
    if points2 is None:
        p0, p1 = points
    else:
        p0, p1 = points, points2
    length0 = distance_2d(p0, p1)
    length_a = distance_2d(p0, point)
    length_b = distance_2d(p1, point)
    return abs (length0 - length_a - length_b) < 0.000001


def angle_2d(a, b):
    '''radians = angle_2d (coor_a, coor_b)'''
    vec = subtract_2d(b, a)
    return atan2(vec[1], vec[0])


def add_2d(*args):
    '''$vector_sum = add_2d (a, b)
    vector_sum = add_2d (a, b, c, d)'''
    return sum([v[0] for v in args]), sum([v[1] for v in args])


def scale_2d(scale, vector):
    '''vector_scaled = scale_2d (3.2, [2.1,4.3]);
    vector_scaled = scale_2d ([2.1,4.3], 3.2);
    '''
    try:
        iter(scale)
        vector, scale = scale, vector
    except:
        pass
    return scale * vector[0], scale * vector[1]


def normalise_2d(vector):
    '''normal_vector = normalise_2d ([3,4])'''
    scalar = distance_2d ([0,0], vector)
    if scalar == 0:
        return 0, 1
    return vector[0] / scalar, vector[1] / scalar


def points_2line(coor_0, coor_1):
    '''line = points_2line ([1,2], [3,4])'''
    x, y = subtract_2d(coor_1, coor_0)
    if x == 0:
        x = 0.00000000001
    a = y / x
    b = coor_0[1] - (coor_0[0] * a)
    return {a: a, b: b}


def angle_2line(coor, angle_radians):
    '''line = angle_2line ($coor, $angle_radians)'''
    coor_0 = coor[:]
    coor_1 = coor[0] + cos(angle_radians), coor[1] + sin (angle_radians)
    return points_2line(coor_0, coor_1)


def perpendicular_line(line, coor):
    '''line = perpendicular_line (line, coor)'''
    a0 = line['a']
    if a0 == 0:
        a0 = 0.00000000001
    a = -1 / a0
    b = coor[1] - (coor[0] * a)
    return {a: a, b: b}


def line_intersection(line_0, line_1):
    '''coor = line_intersection (line_a, line_b)'''
    if line_0['a'] == line_1['a']:
        return
    x = (line_1['b'] - line_0['b']) / (line_0['a'] - line_1['a'])
    y = (line_0['a'] * x) + line_0['b']
    return [x, y]


def perpendicular_distance(line, coor):
    '''distance = perpendicular_distance (line, coor)'''
    perp_line = perpendicular_line(line, coor)
    intersection = line_intersection(line, perp_line)
    return distance_2d(coor, intersection)


def is_angle_between(angle, heading_a, heading_b):
    '''say 'nope!' unless is_angle_between (0.4, 0.1, 0.7)'''
    if angle > pi:
        angle -= 2 * pi
    angle_a = abs(heading_a - angle)
    if angle_a > pi:
        angle_a = 2 * pi - angle_a
    angle_b = abs(heading_b - angle)
    if angle_b > pi:
        angle_b = 2 * pi - angle_b
    angle_ab = abs(heading_a - heading_b)
    if angle_ab > pi:
        angle_ab = 2 * pi - angle_ab
    return (angle_a + angle_b - 0.000001 <= angle_ab)


def triangle_area(a, b, c):
    '''area = triangle_area ($coor_a, $coor_b, $coor_c)'''
    A = distance_2d(b, c)
    B = distance_2d(a, c)
    C = distance_2d(a, b)
    S = (A + B + C) / 2
    return sqrt(S * (S - A) * (S - B) * (S - C))


def gaussian(x, a_a, b_b, c):
    '''result = gaussian ($input_value, 1.0, $centre, $sigma)
    x = input value
    a_a = scale (usually 1.0)
    b_b = centre of peak
    c = sigma
    '''
    global e  # e = 2.718281828459045
    return a_a * (e **(0- ((x-b_b)**2/(2*c*c))))


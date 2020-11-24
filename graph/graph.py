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

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------

from ..pygraph.classes.graph import graph


class Graph(graph):
    def __init__(self, **kwargs):
        graph.__init__(self)

    def add_node(self, node, attrs=None):
        """
        Add given node to the graph.

        @attention: While nodes can be of any type, it's strongly recommended to use only
        numbers and single-line strings as node identifiers if you intend to use write().

        @type  node: node
        @param node: Node identifier.

        @type  attrs: list
        @param attrs: List of node attributes specified as (attribute, value) tuples.
        """
        if attrs is None:
            attrs = []
        if (not node in self.node_neighbors):
            self.node_neighbors[node] = set()
            self.node_attr[node] = attrs

    def add_vertex(self, node, attrs=None):
        self.add_node(node, attrs)

    def clone(self):
        # deep copy ??
        graph_out = Graph()
        for edge in self.node_neighbors.keys():
            graph_out.add_edge(edge, self.edge_properties[edge])
        return graph_out

    def average_path_length(self, node):
        others = self.neighbors(node)
        return sum([self.edge_properties[(node, other)]['weight'] for other in others]) / len(others)

    def sorted_apl(self, graph):
        apl = [(i, node) for i, node in enumerate(graph.nodes)]
        apl.sort(key=lambda x: self.average_path_length(x[1]))
        return [node for (i, node) in apl]

    def set_edge_properties(self, edge, properties ):
        self.edge_properties.setdefault( edge, {} ).update( properties )
        if edge[0] != edge[1]:
            self.edge_properties.setdefault((edge[1], edge[0]), {}).update( properties )

    def add_edge(self, edge, properties):
        """
        Add an edge to the graph connecting two nodes.

        An edge, here, is a pair of nodes like C{(n, m)}.

        @type  edge: tuple
        @param edge: Edge.

        @type  wt: number
        @param wt: Edge weight.

        @type  label: string
        @param label: Edge label.

        @type  attrs: tuple
        @param attrs: List of node attributes specified as (attribute, value) tuples.
        """
        u, v = edge
        # Implicit add nodes
        self.add_node(u)
        self.add_node(v)

        if (v not in self.node_neighbors[u] and u not in self.node_neighbors[v]):
            self.node_neighbors[u].add(v)
            if (u != v):
                self.node_neighbors[v].add(u)

            self.set_edge_properties((u, v), properties)

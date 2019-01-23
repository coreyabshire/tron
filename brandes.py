# brandes: An implementation of Brandes algorithm.
# Copyright (C) 2010 Corey Abshire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Since Python looks so much like pseudo-code, this is pretty much
# straight out of the paper titled "A Faster Algorithm for
# Betweenness Centrality", by Ulrik Brandes.

from collections import deque

def brandes(V, A):
    "Compute betweenness centrality in an unweighted graph."
    # Brandes algorithm
    # see http://www.cs.ucc.ie/~rb4/resources/Brandes.pdf
    C = dict((v,0) for v in V)
    for s in V:
        S = []
        P = dict((w,[]) for w in V)
        g = dict((t, 0) for t in V); g[s] = 1
        d = dict((t,-1) for t in V); d[s] = 0
        Q = deque([])
        Q.append(s)
        while Q:
            v = Q.popleft()
            S.append(v)
            for w in A[v]:
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    g[w] = g[w] + g[v]
                    P[w].append(v)
        e = dict((v, 0) for v in V)
        while S:
            w = S.pop()
            for v in P[w]:
                e[v] = e[v] + (g[v]/g[w]) * (1 + e[w])
            if w != s:
                C[w] = C[w] + e[w]
    return C


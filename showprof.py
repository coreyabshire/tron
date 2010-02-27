# showprof: A little utility to show a python cProfile file.
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

import sys, pstats

if len(sys.argv) < 2:
    print "usage: python showprof.py filename [lines]"
    quit()

p = pstats.Stats(sys.argv[1])

if len(sys.argv) > 2:
    limit = int(sys.argv[2])
else:
    limit = 40

p.strip_dirs().sort_stats('cumulative').print_stats(limit)

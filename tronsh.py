# tronsh: Startup script for interacting with the Tron routines.
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

import os, sys, time, logging, cProfile
import games, search, utils
import tron, tronutils, tronmoves
import aimatron, screen
import brandes, dijkstra
import MyTronBot

def load_map_dir(path):
    return dict((b,tronutils.read_board(b)) for b in tronutils.list_files(path))

logfile = 'log/online.log'
logging.basicConfig(filename=logfile, level=logging.DEBUG, filemode='w')

boards = load_map_dir('maps/')
cases = load_map_dir('cases/')

board = cases['cases/empty-room-002.txt']

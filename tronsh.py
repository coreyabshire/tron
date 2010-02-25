import os, sys, time, logging, cProfile
import games, search, utils
import tron, tronutils, tronmoves
import aimatron, screen
import brandes, dijkstra
import MyTronBot

boards = [tronutils.read_board(b) for b in tronutils.list_files('maps/')]
cases = [tronutils.read_board(b) for b in tronutils.list_files('cases/')]

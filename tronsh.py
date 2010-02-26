import os, sys, time, logging, cProfile
import games, search, utils
import tron, tronutils, tronmoves
import aimatron, screen
import brandes, dijkstra
import MyTronBot

def load_map_dir(path):
    return dict((b,tronutils.read_board(b)) for b in tronutils.list_files(path))

logging.basicConfig(filename='log/online.log', level=logging.DEBUG, filemode='w')

boards = load_map_dir('maps/')
cases = load_map_dir('cases/')

board = cases['cases/empty-room-002.txt']

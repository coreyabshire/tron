#!/usr/bin/python
# gauntlet: Runs a TronBot through a series of matches.
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

# The purpose of this script is to run MyTronBot through
# all the maps against some opponent. This will help me
# test to ensure that I have a winning strategy at least
# here before I upload and try to compete on the server.

import os, sys, subprocess
from tronutils import list_files

def make_command(mapfile, bot1, bot2):
    "Format a command to run a game in the engine for Popen."
    return ['java', '-jar', 'engine/Tron.jar', mapfile, bot1, bot2, '0', '1']

# Game results output as the last line of a game by the engine.
result_classification = {
    "Player One Wins!"            : "W",
    "Player Two Wins!"            : "L",
    "Both players crashed. Draw!" : "D",
    "Players collided. Draw!"     : "D" }

def classify_result(result):
    "Turn the result from the engine into (W)in, (L)ose, or (D)raw."
    if result in result_classification:
        return result_classification[result]
    else:
        return result

def play_game(mapfile, bot1, bot2):
    "Runs a single game and returns the result."
    command = make_command(mapfile, bot1, bot2)
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        result = line.strip()
    return classify_result(result)

def run_gauntlet(mapfiles, bot1, bot2):
    "Run the bots on all the specified mapfiles."
    summary = dict((c,0) for c in result_classification.values())
    for mapfile in mapfiles:
        result = play_game(mapfile, bot1, bot2)
        if result in summary:
            summary[result] += 1
        print mapfile, result
    print summary

if __name__ == '__main__':
    mapfiles = list_files(sys.argv[1])
    bot1 = sys.argv[2]
    bot2 = sys.argv[3]
    run_gauntlet(mapfiles, bot1, bot2)

#!/usr/bin/python

import re
import sys
from game import Game
from collections import defaultdict
import urllib

def game_iterator(handle, parse_moves=True):
    tag_pattern = re.compile(r'\[(\S*) "(.*)"\]')
    separate_moves_pattern = re.compile(r"""
                                        (?P<number>\d+)
                                        (?P<dots>\.+)
                                        \                       # There is a space here
                                        (?P<description>.+?)
                                        (?=(?:\ \d+\.+|$))
                                        """, re.VERBOSE)
    nag_pattern = re.compile(r'\$\d+(?: |$)')
    outcome_pattern = re.compile(r' (?:[012/]+-[012/]+|\*)')
    while True:
        line = handle.readline()
        if not line:
            break
        game = Game(parse_moves)
        tag_pattern_match = tag_pattern.match(line)
        while tag_pattern_match:
            tag_name, tag_value = tag_pattern_match.groups()
            game.info[tag_name] = tag_value
            line = handle.readline()
            tag_pattern_match = tag_pattern.match(line)
        # At this point, we have read the blank line separating tags from moves
        all_moves = []
        line = handle.readline()
        line = line.rstrip()
        while line:
            all_moves.append(line)
            line = handle.readline()
            line = line.rstrip()
        if parse_moves:
            all_moves = ' '.join(all_moves)
            all_moves = remove_comments(all_moves, '(', ')')
            all_moves = remove_comments(all_moves, '{', '}')
            all_moves = nag_pattern.sub('', all_moves)
            all_moves = outcome_pattern.sub('', all_moves)
            
            game.info['moves'] = separate_moves_pattern.findall(all_moves)
            for move_num, dots, move_pair in game.info['moves']:
                moves = move_pair.split(' ')
                if dots == '.':
                    game.move(moves[0], move_num, 'W')
                    if len(moves) == 2:
                        game.move(moves[1], move_num, 'B')
                elif dots == '...':
                    game.move(moves[0], move_num, 'B')
        yield game

def remove_comments(all_moves, start_char, end_char):
    all_moves_clean = all_moves
    while start_char in all_moves_clean:
        stack = []
        for i, char in enumerate(all_moves_clean):
            if char == start_char:
                stack.append(i)
            elif char == end_char:
                if len(stack) == 1:
                    var_start, var_end = (stack.pop(), i + 1)
                    break
                else:
                    stack.pop()
        all_moves_clean = all_moves_clean[:var_start] + all_moves_clean[var_end:].lstrip()
    return all_moves_clean

def position_distributions():
    pgn_file_name = "../data/Million_updated.pgn"
    #pgn_file_name = "../data/test.pgn"

    final_pos_dist = defaultdict(int)
    move_captureds = []
    
    for i, game in enumerate(game_iterator(open(pgn_file_name))):
        if i % 1000 == 0:
            print i
        if i > 10000:
            break
        piece = game.pieces['W']['Q'][0]
        final_pos_dist[piece.pos_hist[-1][0]] += 1
        move_captureds.append(piece.move_captured)

    for row in range(7, -1, -1):
        line = []
        for col in range(8):
            line.append('%d\t' % final_pos_dist[(row, col)])
        print ''.join(line)

def length_distribution():
    web_file = urllib.urlopen('http://slate.ices.utexas.edu/coursefiles/Million_updated.pgn')
    #pgn_file_name = "../data/Million_updated.pgn"
    lengths = defaultdict(int)
    for i, game in enumerate(game_iterator(web_file, parse_moves=False)):
    #for i, game in enumerate(game_iterator(open(pgn_file_name), parse_moves=False)):
        lengths[game.info['PlyCount']] += 1
        if i % 10000 == 9999:
            print i
    return lengths

if __name__ == "__main__":
    lengths = length_distribution()

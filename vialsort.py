#!/usr/bin/env python3

# Copyright (c) 2024 Ben Hottell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Provides an interactive interface for playing a vialsort puzzle.


import sys
import json


_ANSI_CLEAR = '\033[2J'

_ANSI_GO_HOME = '\033[H'

_ANSI_INVERT = '\033[7m'

# Black and white are intentionally ommitted as they would likely blend in too well with the terminal's background.

_ANSI_FG_COLORS = (
    '\033[31m',  # red
    '\033[32m',  # green
    '\033[33m',  # yellow
    '\033[34m',  # blue
    '\033[35m',  # magenta
    '\033[36m',  # cyan
    '\033[91m',  # bright red
    '\033[92m',  # bright green
    '\033[93m',  # bright yellow
    '\033[94m',  # bright blue
    '\033[95m',  # bright magenta
    '\033[96m',  # bright cyan
)

_ANSI_NORMAL = '\033[0m'

_SYMBOLS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


# An Action represents an atomic operation on the game board.
#
# The apply method should return False if the operation has no effect. In this case it will not be added to the history. It should return True otherwise.
#
# The undo method can assume that the board state is equivalent to the state that its apply method left it in. In other words, it does not need to have as stringent checks as the apply method.
#
# Using a C++ term, Actions are 'friends' of the Board. In other words, Actions can access private fields (fields starting with '_') of the Board.


class PourAction:

    def __init__(self, from_index, to_index):
        self._from_index = from_index
        self._to_index = to_index
        self._qty_moved = 0
        self._applied = False

    def apply(self, board):

        self._applied = True

        from_vial = board.vials[self._from_index]
        to_vial = board.vials[self._to_index]

        if len(from_vial) == 0:
            return False

        color = from_vial[-1]

        if len(to_vial) > 0 and to_vial[-1] != color:
            return False

        while len(from_vial) > 0 and from_vial[-1] == color and len(to_vial) < board.vial_size:
            to_vial.append(from_vial[-1])
            from_vial.pop()
            self._qty_moved = self._qty_moved + 1

        return self._qty_moved > 0

    def undo(self, board):

        if not self._applied:
            raise ValueError('Action not yet applied')

        from_vial = board.vials[self._from_index]
        to_vial = board.vials[self._to_index]

        for i in range(self._qty_moved):
            from_vial.append(to_vial.pop())


class AddEmptyVialAction:

    def apply(self, board):
        board.vials.append(list())
        return True

    def undo(self, board):
        board.vials.pop()


class Board:

    def __init__(self, vial_size, vials, history=tuple()):
        self.vial_size = vial_size
        self.vials = vials
        self._history = list(history)

    def is_vial_empty(self, vial_index):
        return len(self.vials[vial_index]) == 0

    def get_num_vials(self):
        return len(self.vials)
    
    def apply_action(self, action):
        if not action.apply(self):
            return
        self._history.append(action)

    def undo(self):
        if len(self._history) == 0:
            return
        action = self._history.pop()
        action.undo(self)

    def get_max_color(self):
        ret = 0

        for vial in self.vials:
            for obj in vial:
                ret = max(ret, obj)

        return ret

    def is_solved(self):

        # A board is solved if all of its vials are solved.
        # A vial is solved if it is either empty, or full of only one color

        for vial in self.vials:

            if len(vial) == 0:
                continue

            if len(vial) != self.vial_size:
                return False

            first_elem = vial[0]
            for elem in vial:
                if elem != first_elem:
                    return False

        return True

    def pour(self, from_vial_index, to_vial_index):
        self.apply_action(PourAction(from_vial_index, to_vial_index))

    def add_empty_vial(self):
        self.apply_action(AddEmptyVialAction())


def load_board(line):

    try:
        data = json.loads(line)
    except ValueError as e:
        raise ValueError(f'Invalid JSON ({e})') from e

    if 'vial_size' not in data:
        raise ValueError('Key "vial_size" is required')

    vial_size = data['vial_size']

    if 'vials' not in data:
        raise ValueError('Key "vials" is required')

    vials = data['vials']

    if not isinstance(vials, (list, tuple)):
        raise ValueError('Key "vials" must be an array')

    for vial in vials:

        if not isinstance(vial, (list, tuple)):
            raise ValueError('Every element in "vials" must be an array.')

        if len(vial) > vial_size:
            raise ValueError('Vial contains too many units')

        for unit in vial:
            if not isinstance(unit, int):
                raise ValueError('Every element in every vial must be an integer.')

    return Board(
        vial_size = vial_size,
        vials = vials,
    )


def draw_vial(vial_index, vial, vial_size, file):

    unit_width = 3
    number_pad = 2

    display_index = str(vial_index+1).rjust(number_pad)

    print(f'{display_index}.', end='', file=file)

    for index in range(vial_size):

        if index < len(vial):
            unit = vial[index]
        else:
            unit = None

        if unit is not None:

            ansi_fg = _ANSI_FG_COLORS[unit % len(_ANSI_FG_COLORS)]
            symbol = _SYMBOLS[unit % len(_SYMBOLS)]

            print(_ANSI_INVERT, end='', file=file)
            print(ansi_fg, end='', file=file)

            print(' ' + symbol + ' ', end='', file=file)

            print(_ANSI_NORMAL, end='', file=file)

        else:
            print(' '*unit_width, end='', file=file)


def play_board(board):

    playing = True

    selected_vial_index = None

    comment = None

    file = sys.stderr


    while playing:

        print(_ANSI_CLEAR, end='', file=file)
        print(_ANSI_GO_HOME, end='', file=file)

        unit_width = 3
        number_pad = 2
        space_between_vials = 4

        vial_draw_size = number_pad + 1 + (unit_width * board.vial_size) + space_between_vials

        term_width = 80
        pos_x = 0

        for vial_index in range(len(board.vials)):

            draw_vial(vial_index, board.vials[vial_index], board.vial_size, file=file)

            print(' ' * space_between_vials, end='', file=file)

            pos_x = pos_x + vial_draw_size

            if pos_x + vial_draw_size >= term_width:
                pos_x = 0
                print(file=file)
                print(file=file)

        print(file=file)
        print(file=file)

        if board.is_solved():
            playing = False
            print(f'Congratulations, you won!', file=file)
            continue

        if selected_vial_index is None:
            print('Select a vial by typing the number to its left.', file=file)
            print(f'Or, enter "help" for more commands.', file=file)
        else:
            print(f'Selected vial {selected_vial_index+1}. Now, select a destination vial.', file=file)
            print(f'Or, enter "c" to cancel.', file=file)

        if comment is not None:
            print(file=file)
            print(comment, file=file)
        comment = None

        print('> ', end='', file=sys.stderr)

        user_line = input().strip()

        if len(user_line) == 0:
            continue

        try:
            vial_index = int(user_line) - 1

            if vial_index < 0 or vial_index >= board.get_num_vials():
                comment = 'That vial does not exist'
                continue

            if selected_vial_index is None:

                if board.is_vial_empty(vial_index):
                    comment = 'That vial is empty'
                    continue

                selected_vial_index = vial_index

            else:
                if selected_vial_index != vial_index:
                    board.pour(selected_vial_index, vial_index)
                selected_vial_index = None

        except ValueError:
            pass

        if user_line == 'c' or user_line == 'C':
            selected_vial_index = None
            continue

        if user_line == 'v' or user_line == 'V':
            board.add_empty_vial()
            continue

        if user_line.lower() == 'help':
            lines = [
                #================================================================================
                'help: Show this message',
                'u: Undo last action',
                'v: Add an empty vial',
            ]
            comment = '\n'.join(lines)

        if user_line == 'u' or user_line == 'U' or user_line.lower() == 'undo':
            board.undo()
            continue

        if user_line.lower() == 'xyzzy':
            comment = 'Nothing happens'
            continue


def main(argv):

    import argparse

    argparser = argparse.ArgumentParser(
        prog='vialsort',
    )

    argparser.add_argument(
        'puzzle_file',
        help='Path to the file containing a puzzle.',
    )

    args = argparser.parse_args(argv)

    puzzle_file_path = args.puzzle_file


    if not sys.stdout.isatty():
        #      ================================================================================
        print('This application is interactive. Its output is not meant to be piped to other ', file=sys.stderr)
        print('applications or files.', file=sys.stderr)
        return 1


    with open(puzzle_file_path, 'r', encoding='utf-8') as puzzle_file:

        line_no = 0

        for line in puzzle_file:
            line_no = line_no + 1

            try:
                board = load_board(line)
            except ValueError as e:
                print(f'Failed to load board from line {line_no}: {e}', file=sys.stderr)
                return 1

            play_board(board)


if __name__ == '__main__':

    try:
        code = main(sys.argv[1:])
    except KeyboardInterrupt:
        code = 2

    if code is None:
        code = 0

    sys.exit(code)


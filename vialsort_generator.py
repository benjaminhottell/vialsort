#!/usr/bin/env python3

# Copyright (c) 2024 Ben Hottell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Generates a vialsort puzzle.


import argparse
import json
import random


def generate_random_vials(num_vials, vial_size, rand):

    items_to_distribute = list()

    for vial_idx in range(num_vials):
        color = vial_idx
        items_to_distribute.extend([color] * vial_size)

    rand.shuffle(items_to_distribute)

    ret = list()

    for i in range(0, num_vials*vial_size, vial_size):
        ret.append(items_to_distribute[i:i+vial_size])

    return ret


def main(argv):

    argparser = argparse.ArgumentParser(
        prog='vialsort_generator',
        description='Generates puzzles for vialsort',
    )

    argparser.add_argument(
        '--num-colors',
        type=int,
        help='Sets the number of distinct colors that will exist in the puzzle.',
        default=4
    )

    argparser.add_argument(
        '--num-empty-vials',
        type=int,
        help='Sets the number of empty vials. In general, more empty vials makes the puzzle easier. The puzzle will most likely be impossible without at least one or two empty vials.',
        default=2
    )

    argparser.add_argument(
        '--vial-size',
        type=int,
        help='Sets how many units can fit within a single vial',
        default=4
    )

    argparser.add_argument(
        '--seed',
        type=int,
        help='Sets the seed for the random number generator.',
        default=None
    )

    args = argparser.parse_args(argv)


    num_colors = args.num_colors
    num_empty_vials = args.num_empty_vials
    vial_size = args.vial_size
    seed = args.seed

    num_vials = num_colors + num_empty_vials

    rand = random.Random()

    if seed is not None:
        rand.seed(seed)

    if num_colors < 0:
        print('Cannot have a negative amount of colors.', file=sys.stderr)
        return 1

    if num_empty_vials < 0:
        print('Cannot have a negative amount of empty vials.', file=sys.stderr)
        return 1

    if vial_size < 0:
        print('Cannot have a negative vial size.', file=sys.stderr)
        return 1


    vials = generate_random_vials(num_colors, vial_size, rand)

    vials.extend([[] for i in range(num_empty_vials)])

    data = {
        'vial_size': vial_size,
        'vials': vials,
    }

    print(json.dumps(data))

    return 0


if __name__ == '__main__':
    import sys
    code = main(sys.argv[1:])
    if code is None:
        code = 0
    sys.exit(code)


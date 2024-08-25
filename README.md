# vialsort

A liquid/fluid sorting puzzle game for the terminal.

Developed and tested on Linux. Compatibility with other operating systems is not known.


## Quickstart

Clone this repository then run the following commands. The first command generates a puzzle and the second command opens the puzzle in an interactive player.

```bash
python3 vialsort_generator.py > puzzle.json
python3 vialsort.py puzzle.json
```


## Generating a puzzle

Puzzles are generated in a separate executable. This way, anyone can create a specialized puzzle generator or editor for their own purposes. The puzzle format specification is provided in a below section.

A simple puzzle generator is included in this repository. Try the following command:

```bash
python3 vialsort_generator.py > puzzle.json
```

Use `python3 puzzle_generator --help` to see additional options to customize the difficulty of the puzzle.


## Starting a puzzle

Once you have a puzzle file, you should open it in a puzzle runner. Try the following command:

```bash
python3 vialsort.py puzzle.json
```

The puzzle is considered solved when all vials are either empty or full of only one color.

To pour a vial into another vial, type its number, press enter, type the number of the destination vial, then press enter again.

Pouring a vial will only have an effect if the destination vial is empty or the top layer of the destination vial has the same color as the top layer of the source vial.

If you feel a puzzle is unsolvable, try adding an empty vial by entering `v` instead of a vial number. This will add a new empty vial to the puzzle, which should get you unstuck.

If you made a mistake, enter `u` to undo your last move. (This also applies to other actions such as adding an empty vial).

To exit the game, press ctrl+c to send an interrupt signal. The game will automaticlly exit if the puzzle is solved.


## Puzzle file format

Puzzle files are [JSON](https://www.json.org) files where the root element is an object with the following keys:

- `vial_size` - The capacity of each vial. In other words, how many units of fluid that each vial can store.
- `vials` - A two-dimensional array of integers. Each array represents one vial. Each vial may contain up to `vial_size` elements. Each integer vial element represents one unit of fluid, where equal integers are the same color.

Example:

```json
{
    "vial_size": 4,
    "vials": [
        [ 0, 0, 1, 1 ],
        [ 1, 0, 1, 0 ],
        [],
        []
    ]
}
```


### Extra keys

A puzzle generator may add additional keys to the document that are not contained in this specification. Puzzle runners may accept these keys and change their behavior in implementation-defined ways. Puzzle runners should ignore any keys they do not recognize.


## Feature wishlist

This is a list of features that are not implemented, but I would like to see them added someday.

- Scoring system. Each move adds one point. Each extra empty vial added adds a very large number of points. The goal is to solve the puzzle with as low of a score as possible.
- Saving progess. Currently, if you exit the program, your progress is not saved and you restart the puzzle from scratch.
- Automatically detect if a puzzle is solvable or not. Add additional empty vials until it becomes solvable.


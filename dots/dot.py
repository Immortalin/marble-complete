import sys

from .states import *


class Marble:
    def __init__(self, env, pos, id_=None, value=None, direction=None, state=None, stack=None):
        """
        The base unit of and ascii marble code : the marble.

        :param marbles.environement.Env env: The environement for the program
        :param marbles.vector.Pos pos: The position of the marble in the map
        :param float id_: the id of the marble
        :param float value: its value
        :param marbles.vector.Pos direction: The direction of the marble
        :param state: Its actual state
        :param list stack:
        """

        self.pos = pos

        self.env = env
        self.id = id_ or 0
        self.value = value or 0
        self.state = state(self) if state else TravelState(self)  # type: State
        self.dir = direction or self._calculate_direction()
        self.stack = stack or []

        self.move()

    def __repr__(self):
        return '<Marble pos={pos}, id={id}, value={value}, dir={dir}, stack={stack}>'.format(**self.__dict__)

    def move(self):
        """Move the marble according to its direction."""
        self.pos += self.dir

    def simulate_tick(self, run_until_waiting):
        """
        Update the marble to its next state.

        :param bool run_until_waiting: if false, the marble will perform only one tick, else it will run untill waiting
        """

        past_locations = []

        while True:

            # we need to update the screen if we keep this marble running, nobody will ever do it otherwise
            if run_until_waiting:
                self.env.io.on_microtick(self)

            # If it was already at this location, run someone else (prevent infinite loops)
            if self.pos in past_locations:
                return
            past_locations.append(self.pos)

            # If outside the map, he dies.
            if not self.env.world.does_loc_exist(self.pos):
                self.state = DeadState(self)
                return

            char = self.env.world.get_char_at(self.pos)

            # end of execution
            if char == '&':
                self.state = DeadState(self)

                self.env.io.on_finish()
                sys.exit(0)

            # update the marble
            self.state = self.state.next(char)
            self.state.run(char)

            if self.state.is_dead():
                return

            if self.state.isWaiting:
                break

            if not run_until_waiting:
                break

    def _calculate_direction(self):
        """Calculate the inial direction of a just created marble."""
        valid_chars = r'\/*^v><+'

        for direction in DIRECTIONS:
            loc = self.pos + direction

            # we have no interest in chars outside
            if not self.env.world.does_loc_exist(loc):
                continue

            if direction in (UP, DOWN) and self.env.world.get_char_at(loc) == '|':
                return direction

            if direction in (LEFT, RIGHT) and self.env.world.get_char_at(loc) == '-':
                return direction

            if self.env.world.get_char_at(loc) in valid_chars:
                return direction

        # If we get here without returning, the marble can't find a direction to go!
        self.env.io.on_error("marble cannot determine location...\nx: {}, y: {}".format(*self.pos))

        self.state = DeadState(self)
        return Pos(0, 0)

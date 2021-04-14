from typing import List, Tuple
from copy import deepcopy
import random

# initial_state = [
# 	[1, 2, 5],
# 	[3, 4, 8],
# 	[6, 7, 0]
# ]
initial_state = [
	[7, 2, 4],
	[5, 0, 6],
	[8, 3, 1]
]
goal_state = [
	[0, 1, 2],
	[3, 4, 5],
	[6, 7, 8]
]

MAX_ITERATION = 10000
ROW_CNT = len(goal_state)
COL_CNT = len(goal_state[0])


def get_fitness_value(state: List[List[int]]):
	fitness_value = 0
	for row in range(ROW_CNT):
		for col in range(COL_CNT):
			fitness_value += (3 * row + col) * state[row][col]
	return fitness_value


def get_blank_position(state: List[List[int]]):
	for row in range(ROW_CNT):
		for col in range(COL_CNT):
			if state[row][col] == 0:
				return row, col


GOAL_FITNESS_VALUE = get_fitness_value(goal_state)  # 204


def move(curr_state: List[List[int]], blank_position: Tuple[int, int]):
	global ROW_CNT
	global COL_CNT
	blankX = blank_position[0]
	blankY = blank_position[1]

	diff2state = {}
	possible_moves = []

	def up() -> List[List[int]]:
		nonlocal blank_position
		moved_state = deepcopy(curr_state)
		moved_state[blankX][blankY], moved_state[blankX + 1][blankY] = \
			moved_state[blankX + 1][blankY], moved_state[blankX][blankY]
		return moved_state

	def down() -> List[List[int]]:
		nonlocal blank_position
		moved_state = deepcopy(curr_state)
		moved_state[blankX][blankY], moved_state[blankX - 1][blankY] = \
			moved_state[blankX - 1][blankY], moved_state[blankX][blankY]
		return moved_state

	def left() -> List[List[int]]:
		moved_state = deepcopy(curr_state)
		moved_state[blankX][blankY], moved_state[blankX][blankY + 1] = \
			moved_state[blankX][blankY + 1], moved_state[blankX][blankY]
		return moved_state

	def right() -> List[List[int]]:
		moved_state = deepcopy(curr_state)
		moved_state[blankX][blankY], moved_state[blankX][blankY - 1] = \
			moved_state[blankX][blankY - 1], moved_state[blankX][blankY]
		return moved_state

	if blank_position == (int(ROW_CNT / 2), int(COL_CNT / 2)) and ROW_CNT % 2 == 1 and COL_CNT % 2 == 1:
		# Blank is at the center most position, 4 possible moves
		possible_moves = [up, down, left, right]


	elif blank_position in [(0, 0), (0, COL_CNT - 1), (ROW_CNT - 1, 0), (ROW_CNT - 1, COL_CNT - 1)]:
		# Blank is at the corner, 2 possible moves
		possible_moves = []
		if blankX == 0:
			possible_moves.append(up)
		if blankX == ROW_CNT - 1:
			possible_moves.append(down)
		if blankY == 0:
			possible_moves.append(left)
		if blankY == COL_CNT - 1:
			possible_moves.append(right)

	else:
		# Blank is on one side of the square, 3 possible moves
		if blankX == 0:
			possible_moves = [left, right, up]
		if blankX == ROW_CNT - 1:
			possible_moves = [left, right, down]
		if blankY == 0:
			possible_moves = [up, down, left]
		if blankY == COL_CNT - 1:
			possible_moves = [up, down, right]

	for possible_move in possible_moves:
		moved_state = possible_move()
		diff = GOAL_FITNESS_VALUE - get_fitness_value(moved_state)
		diff2state[diff] = moved_state

	return {k: v for k, v in sorted(diff2state.items())}  # Sort by diff in ascending order


# curr_state = deepcopy(initial_state)
# for iteration in range(MAX_ITERATION):
# 	fitness_value = get_fitness_value(curr_state)  # Get current fitness value
# 	if fitness_value == GOAL_FITNESS_VALUE:
# 		# Solved
# 		print("[*] Success! At iteration {}".format(iteration))
# 		break
#
# 	blank_position = get_blank_position(curr_state)  # Find out where the blank is to calculate possible moves
# 	curr_state = move(curr_state, blank_position)

class Particle:
	def __init__(self, state: List[List[int]] = initial_state,
	             pbest: int = GOAL_FITNESS_VALUE - get_fitness_value(initial_state),
	             pbest_state: List[List[int]] = initial_state):
		# pbest: Minimum difference from GOAL_FITNESS_VALUE
		self.state = state
		self.pbest = pbest
		self.pbest_state = pbest_state

	def choose_direction(self, pbest_chance, gbest_chance):
		# Choose the direction of a particle
		# Choose between 3 options at a given chance
		roulette = random.random()
		if roulette < pbest_chance:
			return 'pbest'
		elif roulette >= pbest_chance and roulette < pbest_chance + gbest_chance:
			return 'gbest'
		else:
			return 'explore'


class Swarm:
	def __init__(self, particles: List[Particle] = [], gbest: Particle = Particle()):
		# gbest: Minimum of all the particles' pbest
		self.particles = particles
		self.gbest = gbest

	def reset(self, seed_particle: Particle):
		self.particles = [seed_particle]


init_particle = Particle(initial_state)
swarm = Swarm([init_particle], init_particle)
MAX_PARTICLES_CNT = 1000
PBEST_CHANCE = 0.2  # c1 in the formula
GBEST_CHANCE = 0.3  # c2 in the formula
swarm_full_cnt = 0

for iteration in range(MAX_ITERATION):
	for particle in swarm.particles:
		if swarm.gbest.pbest == 0:
			print("[*] Success! At iteration {}".format(iteration))
			exit(0)

		diff2state = move(particle.state, get_blank_position(particle.state))
		diff2state = iter(diff2state.items())

		# Choose direction
		direction = particle.choose_direction(PBEST_CHANCE, GBEST_CHANCE)
		if direction == 'pbest' and swarm_full_cnt == 0:
			particle.state = particle.pbest_state
		elif direction == 'gbest' and swarm_full_cnt == 0:
			particle = swarm.gbest
		else:
			diff, state = next(diff2state)
			particle.state = state
			if diff < particle.pbest:
				particle.pbest = diff
				particle.pbest_state = particle.state

			if diff < swarm.gbest.pbest:
				swarm.gbest = particle

		# Generate new particles
		for diff, state in diff2state:
			if len(swarm.particles) < MAX_PARTICLES_CNT:
				new_particle = Particle(state, diff, state)
				swarm.particles.append(new_particle)
			else:
				swarm_full_cnt += 1
				if swarm_full_cnt == 1:
					# swarm full , remove some particles to free up space
					swarm.particles = swarm.particles[100:]
					swarm_full_cnt = 0

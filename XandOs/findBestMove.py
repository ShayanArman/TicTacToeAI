import sys
import json
from operator import itemgetter

PLAYER = 1 # Player tries to maximize the score. 
OPPONENT = 2 # Opponent tries to minimize the score
MINIMUM_VALUE = -sys.maxsize
MAXIMUM_VALUE = sys.maxsize
EMPTY_LETTER = "*"

def nextMove(board_string, player_letter):
	board = make_board_matrix(board_string, player_letter)
	best_moves_list = miniMax(board, 5, 5, PLAYER)
	
	# Do a sort on the scores, highest to lowest
	# Secondary sort ordering is applied for equal scoring
	best_moves_list = sorted(best_moves_list, key=itemgetter(0,1), reverse=True)

	# Only return the indexes, not the scores as well
	return map(lambda x: x[1], best_moves_list)

def make_board_matrix(board_string, player_letter):
	board = list(board_string)
	board_matrix = [[0 for x in xrange(3)] for x in xrange(3)]
	for row in xrange(3):
		for col in xrange(3):
			if (board[int(str(row)+str(col),3)] == player_letter):
				board_matrix[row][col] = 1
			elif (board[int(str(row)+str(col),3)] != EMPTY_LETTER):
				board_matrix[row][col] = 2
	return board_matrix

# MiniMax algorithm:
# This method works its way down the decision tree and only passes up
# The decisions which yield the MAXIMUM score for PLAYER
# and MINIMUM score for opponent
# Accepts:
# board_matrix: a matrix representing the board
# depth: the number of levels in the tree to traverse
# player: the current player in the level of the decision tree
def miniMax(board_matrix, original_depth, depth, player):
	# Get all empty spots in a list
	possible_moves_list = listAllPossibleMoves(board_matrix)

	# PLAYER is Maximizing; OPPONENT is MINIMIZING (from the point of view of the player)
	best_score = MINIMUM_VALUE if player == PLAYER else MAXIMUM_VALUE;
	current_score = 0
	best_row = -1
	best_column = -1

	scored_moves = []

	# Either no more decisions, or we've reached the max depth
	if(len(possible_moves_list)==0 or depth == 0):
		best_score = scoreBoard(board_matrix)
	else:
		for move in possible_moves_list:
			# Make a move for the current player (i.e try this possibility)
			board_matrix[move[0]][move[1]] = player

			# Decide if this new board should be scored in a 
			# Minimizing or maximising fashion
			# The PLAYER will choose the move with the highest score for herself (maximizing)
			# THE OPPONENT will choose the move with the greatest damage to PLAYER (minimizing)
			if(player == PLAYER):
				current_score = miniMax(board_matrix, original_depth, depth - 1, OPPONENT)[0]
				
				if(depth == original_depth):
					scored_moves.append([current_score, int(str(move[0])+str(move[1]),3)])

				if(current_score > best_score):
					best_score = current_score
					best_row = move[0]
					best_column = move[1]

			else: # Opponent's turn, pick the most damaging move
				current_score = miniMax(board_matrix, original_depth, depth - 1, PLAYER)[0]
				
				if(current_score < best_score):
					best_score = current_score
					best_row = move[0]
					best_column = move[1]

			# Undo last move
			board_matrix[move[0]][move[1]] = 0

	if(depth == original_depth):
		return scored_moves
	return [best_score, best_row, best_column]

def scoreBoard(matrix):
	if(isPlayerWinner(PLAYER, matrix)):
		return MAXIMUM_VALUE + 1

	reward = 0

	# Add up the reward for each line (3 horizontal, 3 vertical, and 2 diagonal)
	reward += scoreLine(0, 0, 0, 1, 0, 2, matrix);  # Row 0
	reward += scoreLine(1, 0, 1, 1, 1, 2, matrix);  # Row 1
	reward += scoreLine(2, 0, 2, 1, 2, 2, matrix);  # Row 2
	reward += scoreLine(0, 0, 1, 0, 2, 0, matrix);  # Col 0
	reward += scoreLine(0, 1, 1, 1, 2, 1, matrix);  # Col 1
	reward += scoreLine(0, 2, 1, 2, 2, 2, matrix);  # Col 2
	reward += scoreLine(0, 0, 1, 1, 2, 2, matrix);  # Left to right diagonal
	reward += scoreLine(0, 2, 1, 1, 2, 0, matrix);  # Right to left diagonal

	return reward

# Reward function for the input line
# +100, +10, +1 for 3-, 2-, 1-in-a-line for computer.
# -100, -10, -1 for 3-, 2-, 1-in-a-line for opponent.
# 0 otherwise
def scoreLine(row_1,col_1,row_2,col_2,row_3,col_3, matrix):
	reward = 0

	# First cell
	if (matrix[row_1][col_1] == PLAYER):
		reward = 1
	else:
		reward = -1

	# Second cell
	if (matrix[row_2][col_2] == PLAYER):
		if (reward == 1):
			reward *= 10
		elif (reward == -1):
			return 0
		else:
			reward = 1
	else:
		if(reward == -1):
			reward == -10
		elif (reward == 1):
			return 0
		else:
			reward = -1

	# Third cell
	if (matrix[row_3][col_3] == PLAYER):
		# Either one or both of previous cells are PLAYER
		if (reward > 0):
			reward *= 10
		# Either one or both of previous cells are OPPONENT
		elif (reward < 0): 
			return 0
		# Empty cells before hand, reward this move
		else:
			reward = 1 
	
	elif (matrix[row_3][col_3] == OPPONENT):
		# Either one or both of prevous cells are OPPONENT
		# This line should have a highly negative penalty imposed
		if (reward < 0):
			reward *= 10
		# Either one or both are PLAYER
		# Do not punish or reward this line
		elif (reward > 0):
			return 0
		# Empty cells
		else:
			reward = -1

	return reward

def listAllPossibleMoves(board_matrix):
	all_possible_moves_list = []

	# If the game is over, return an empty list
	if(isPlayerWinner(PLAYER, board_matrix) or isPlayerWinner(OPPONENT, board_matrix)):
		return all_possible_moves_list
	
	for r in xrange(3):
		for c in xrange(3):
			if(board_matrix[r][c] == 0): # Empty board
				all_possible_moves_list.append([r,c])
	
	return all_possible_moves_list

winning_boards = ['111000000', '000111000', '000000111','100100100', '010010010', '001001001','100010001', '001010100']
def isPlayerWinner(player, board):
	current_board = 0

	for r in xrange(3):
		for c in xrange(3):
			if(board[r][c] == player):
				current_board |= (1 << (8-int(str(r)+str(c),3)))
	
	for winner in winning_boards:
		if(current_board & int(winner,2) == int(winner,2)):
			return True
	
	return False

def createMovesResponse(input_json):
	response_list = []
	for ob in input_json:
		board = ob.get("board")
		player = ob.get("player")
		if(player and board):
			indexes = nextMove(board, player)
			if indexes:
				response_list.append({"indexes": indexes})
			else:
				response_list.append({"message": "board at end state"})
		elif (player and not board):
			response_list.append({"message": "invalid board"})
		else:
			response_list.append({"message": "invalid player"})
	return json.dumps(response_list)

if(len(sys.argv) > 1):
	try:
		input_json = json.loads(sys.argv[1])
		print createMovesResponse(input_json)
	except ValueError: # decoding failed
		print "Please include valid json"
else:
	print "Please include valid json"
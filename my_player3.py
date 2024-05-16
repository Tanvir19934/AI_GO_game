import time
import numpy as np
import copy

class MyPlayer():
    def __init__(self):
        self.type = 'minimax'

    def get_input(self, go, piece_type):
        self.go = go
        self.piece_type = piece_type
        self.previous_board = go.previous_board
        self.current_board = go.board 
        start = time.time()
        current_sum = sum(sum(row) for row in self.current_board)
        count_non_zero = sum(1 for row in self.current_board for element in row if element != 0)
        if count_non_zero>=15:
            max_ply = 4
        else: max_ply = 3
        #place at the middle if the board is empty
        if current_sum == 0:
            action = (2,2)
            #action = random.choice([(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)])
        elif current_sum==3-self.piece_type and self.current_board[2][2]==0:
            action = (2,2)
        else:
            action = self.minimax(self.previous_board, self.current_board, max_ply, 0, -np.inf, np.inf, self.piece_type)
            if action == None:
                action = 'PASS'
        end =time.time()
        time.sleep(1)
        print(f"Computer took {end-start} seconds")
        return action
    
    def minimax(self, previous_board, current_board, max_ply, current_ply, alpha, beta, player):
        try:
            best_val, best_action = self.max_player(previous_board, current_board, max_ply, current_ply, alpha, beta, player)
        except:
            best_action = 'PASS'
        return best_action
    
    def max_player(self, previous_board, current_board, max_ply, current_ply, alpha, beta, player):
        
        #base_case
        if current_ply == max_ply:
            return self.evaluation_heuristic(current_board, player)
        best_val= -np.inf
        best_action = None
        current_board_copy = copy.deepcopy(current_board)
        valid_moves = self.check_valid_moves(previous_board,current_board_copy, player)
        
        
        #move ordering
        evaluate_valid_moves = {}
        for action in valid_moves:
            current_board_copy[action[0]][action[1]] = player
            evaluate_valid_moves[action] = self.evaluation_heuristic(current_board_copy, player)
            current_board_copy = copy.deepcopy(current_board)
        evaluate_valid_moves_sorted = dict(sorted(evaluate_valid_moves.items(), key=lambda item: item[1], reverse=True))
        valid_moves = list(evaluate_valid_moves_sorted.keys())

        for action in valid_moves:
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[action[0]][action[1]] = player
            current_board_copy = self.remove_captures(current_board_copy,3-player)
            #zero_count_current_board_copy = sum(1 for row in current_board_copy for element in row if element == 0)
            #zero_count_current_board= sum(1 for row in current_board for element in row if element == 0)
            #if (zero_count_current_board_copy-zero_count_current_board) > 0:
            #    best_val = self.evaluation_heuristic(current_board_copy, player)        #greedy rule: immediately accept the move and return it if the move results in more than 1 capture
            #    if current_ply==0:
            #        return best_val, action
            #    else: return best_val
            v = self.min_player(current_board, current_board_copy, max_ply, current_ply+1, alpha, beta, 3-player)
            
            if v > best_val:
                best_val = v
                best_action = action
            
            if best_val >= beta:
                if current_ply==0: return best_val, best_action
                else: return best_val

            alpha = max(alpha,best_val)

        if current_ply == 0:
            return best_val, best_action
        else: return best_val


    def min_player(self, previous_board, current_board, max_ply, current_ply, alpha, beta, player):
        
        #base_case
        if current_ply == max_ply:
            return self.evaluation_heuristic(current_board, player)
        best_val= np.inf
        best_action = None
        current_board_copy = copy.deepcopy(current_board)
        valid_moves = self.check_valid_moves(previous_board,current_board_copy, player)

        #move ordering
        evaluate_valid_moves = {}
        for action in valid_moves:
            current_board_copy[action[0]][action[1]] = player
            evaluate_valid_moves[action] = self.evaluation_heuristic(current_board_copy, player)
            current_board_copy = copy.deepcopy(current_board)
        evaluate_valid_moves_sorted = dict(sorted(evaluate_valid_moves.items(), key=lambda item: item[1], reverse=False))
        valid_moves = list(evaluate_valid_moves_sorted.keys())

        for action in valid_moves:
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[action[0]][action[1]] = player
            current_board_copy = self.remove_captures(current_board_copy,3-player)
            v = self.max_player(current_board, current_board_copy, max_ply, current_ply+1, alpha, beta, 3-player)
            
            if v < best_val:
                best_val = v
                best_action = action
            
            if best_val<=alpha:
                return best_val
            beta = min(beta, best_val)

        return best_val
    
    def evaluation_heuristic(self, board, player):
        #count pieces
        my_piece = 0
        opponent_piece = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == player:
                    my_piece += 1
                elif board[i][j] == 3-player:
                    opponent_piece += 1
        #count liberties
        my_liberty = 0
        opponent_liberty = 0
        for i in range(0,5):
            for j in range(0,5):
                if board[i][j] == player:
                    my_neighbors = self.check_neighbors(board, i, j)
                    for item in my_neighbors:
                        if board[item[0]][item[1]] == 0:
                            my_liberty += 1
                elif board[i][j] == 3-player:
                    opponent_neighbors = self.check_neighbors(board, i, j)
                    for item in opponent_neighbors:
                        if board[item[0]][item[1]] == 0:
                            opponent_liberty += 1
        eye_score = self.potential_eye_strength(board, player)
        
        waste_move_player = self.waste_moves(board,player)*0.1
        waste_move_other_player = self.waste_moves(board,3-player)*0.1
        edge_plays = []
        my_edge_score = 0
        opponent_edge_score = 0
        for i in range(0,5):
            for j in range(0,5):
                if i==0 or j==0 or i==4 or j==4:
                    edge_plays.append((i,j))
        for item in edge_plays:
                if board[item[0]][item[1]] == player:
                    my_edge_score=my_edge_score+1
                if board[item[0]][item[1]] == 3-player:
                    opponent_edge_score=opponent_edge_score+1
    
        if player == self.piece_type:
            return 6*my_piece+2*my_liberty-10*opponent_piece-2*opponent_liberty+eye_score*1.2-waste_move_player+waste_move_other_player-my_edge_score*1
        else:
            return -1 * (6*my_piece+2*my_liberty-10*opponent_piece-2*opponent_liberty+eye_score*1.2-waste_move_player+waste_move_other_player-my_edge_score*1)

    def check_liberty(self, board, i, j):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        ally_members = self.ally_dfs(board, i, j)
        for member in ally_members:
            neighbors = self.check_neighbors(board, member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False
    def check_valid_moves(self, previous_board, current_board, player):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: a list of valid moves.
        '''   
        #board = self.board
        #verbose = self.verbose
        #if test_check:
        verbose = False
        valid_moves = []
        potential_liberty_after_capture = []
        # Check if the place is in the board range and if the place is empty
        for i in range(5):
            for j in range(5):
                if (i >= 0 and i < 5) and (j >= 0 and j < 5) and current_board[i][j]==0:
                    valid_moves.append((i,j))
                else:
                    if verbose:
                        print('Invalid placement.')
        valid_moves_copy = copy.deepcopy(valid_moves)
        
        # Check if the place has liberty
        for item in valid_moves_copy:
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[item[0]][item[1]] = player
            if not self.check_liberty(current_board_copy,item[0],item[1]):
                valid_moves.remove(item)
                potential_liberty_after_capture.append(item)
        potential_liberty_after_capture_copy = copy.deepcopy(potential_liberty_after_capture)
                
        # Check if the place having no liberty results in a capture and thus a new liberty
        for item in potential_liberty_after_capture_copy:
            current_board_copy = []
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[item[0]][item[1]] = player
            current_board_copy = copy.deepcopy(self.remove_captures(current_board_copy, 3-player))
            if not self.check_liberty(current_board_copy, item[0], item[1]):
                potential_liberty_after_capture.remove(item)

        valid_moves_copy = valid_moves + potential_liberty_after_capture
        valid_moves = copy.deepcopy(valid_moves_copy)
        
        valid_moves_copy = copy.deepcopy(valid_moves)
        
        # KO rule check
        for item in valid_moves_copy:
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[item[0]][item[1]] = player
            current_board_copy = self.remove_captures(current_board_copy,3-player) #jake captured = 3-player
            if current_board_copy==previous_board:
                valid_moves.remove(item)

        return valid_moves

    def check_neighbors(self, board, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors
    
    def check_neighbor_ally(self, board, i, j):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        neighbors = self.check_neighbors(board, i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, board, i, j):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.check_neighbor_ally(board, piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members
    
    def potential_eye_strength(self, board, player):
        #an evaluation score based on the creating of potential eyes
        #details: http://erikvanderwerf.tengen.nl/pubdown/thesis_erikvanderwerf.pdf
        # Van Der Werf, E. (2004). AI techniques for the game of Go.
        w = 1.5        #weight for qd
        extended_board = np.zeros([7, 7])
        for i in range(5):
            for j in range(5):
                extended_board[i+1][j+1] = board[i][j]

        q1_player = 0
        qd_player = 0
        q3_player = 0
        q1_other_player = 0
        qd_other_player = 0
        q3_other_player = 0

        for i in range(5):
            for j in range(5):
                board_window = extended_board[i:i+2, j:j+2]
                main_sum_player = sum(board_window[x][y] == player for x in range(2) for y in range(2))
                main_sum_other_player = sum(board_window[x][y] == 3-player for x in range(2) for y in range(2))
                if main_sum_player==1:
                    q1_player+=1
                elif main_sum_player==3:
                    q3_player+=1
                if main_sum_other_player==1:
                    q1_other_player+=1
                elif main_sum_other_player==3:
                    q3_other_player+=1
                qd_player += self.qd(board_window, player)
                qd_other_player += self.qd(board_window, 3-player)

        player_eye =(q1_player - q3_player + w * qd_player)/4
        other_player_eye = (q1_other_player - q3_other_player + w * qd_other_player)/4

        return other_player_eye-player_eye
    
    def qd(self, board_copy, player):
        if ((board_copy[0][0] == player and board_copy[0][1] != player and board_copy[1][0] != player and board_copy[1][1] == player)
                or (board_copy[0][0] != player and board_copy[0][1] == player and board_copy[1][0] == player and board_copy[1][1] != player)):
            return 1
        else: return 0

    def remove_captures(self, board, player):        
        captures = []
        for i in range(5):
            for j in range(5):
                if board[i][j] == player:
                    if not self.check_liberty(board, i, j):
                        captures.append((i, j))
        if not captures:
            return board
        else:
            for item in captures:
                board[item[0]][item[1]] = 0
            return board
    def waste_moves (self, current_board, player):
        count=0
        check = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)]
        for item in check:
            if current_board[item[0]][item[1]]==player:
                if current_board[item[0]-1][item[1]]==player and current_board[item[0]][item[1]-1]==player and current_board[item[0]+1][item[1]]==player and current_board[item[0]][item[1]+1]==player:
                    count+=1
        check_2 = [(1,0),(2,0),(3,0)]
        for item in check_2:
            if current_board[item[0]][item[1]]==player:
                if current_board[item[0]-1][item[1]]==player and current_board[item[0]+1][item[1]]==player and current_board[item[0]][item[1]+1]==player:
                    count+=1
        check_3 = [(1,4),(2,4),(3,4)]
        for item in check_3:
            if current_board[item[0]][item[1]]==player:
                if current_board[item[0]-1][item[1]]==player and current_board[item[0]+1][item[1]]==player and current_board[item[0]][item[1]-1]==player:
                    count+=1
        if current_board[0][0]==player:
            if current_board[0][1]==player and current_board[1][0]==player:
                count+=1 
        if current_board[0][4]==player:
            if current_board[0][3]==player and current_board[1][4]==player:
                count+=1 
        if current_board[4][0]==player:
            if current_board[4][1]==player and current_board[3][0]==player:
                count+=1 
        if current_board[4][4]==player:
            if current_board[4][3]==player and current_board[3][4]==player:
                count+=1
        check_4 = [(0,1),(0,2),(0,3)]
        check_5 = [(4,1),(4,2),(4,3)]
        for item in check_4:
            if current_board[item[0]][item[1]]==player:
                if current_board[item[0]][item[1]+1]==player and current_board[item[0]][item[1]-1]==player and current_board[item[0]+1][item[1]]==player:
                    count+=1
        for item in check_5:
            if current_board[item[0]][item[1]]==player:
                if current_board[item[0]][item[1]+1]==player and current_board[item[0]][item[1]-1]==player and current_board[item[0]-1][item[1]]==player:
                    count+=1
        return count


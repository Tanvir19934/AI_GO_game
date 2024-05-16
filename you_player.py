import time

class YouPlayer():
    def __init__(self):
        self.type = 'manual'

    def get_input(self, go, piece_type):
        self.go = go
        self.piece_type = piece_type
        self.previous_board = go.previous_board
        self.current_board = go.board 
        start = time.time()
        if piece_type==1:
            stone = "X"
        else: stone = "O"
        user_input = input(f"Your move. \n You are {stone}. To pass, press any key and return. \n Enter (row,column): ")
        try:
            user_input = tuple(map(int, user_input.split(',')))
        except:
            user_input = "PASS"
        end =time.time()
        print(f"You took {end-start} seconds")
        return user_input
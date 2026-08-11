import json
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
import math

app = Flask(__name__)
CORS(app)

# Game logic classes
class Player:
    X = 'X'
    O = 'O'
    EMPTY = ''

class Difficulty:
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    IMPOSSIBLE = 'impossible'

class TicTacToeGame:
    def __init__(self):
        self.reset_game()
        self.game_mode = 'pvp'  # 'pvp' or 'pvc'
        self.difficulty = Difficulty.MEDIUM
        self.stats_file = 'stats.json'
        self.stats = self.load_stats()
    
    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "pvp": {"x_wins": 0, "o_wins": 0, "draws": 0, "total_games": 0},
            "pvc": {"player_wins": 0, "ai_wins": 0, "draws": 0, "total_games": 0,
                   "easy": 0, "medium": 0, "hard": 0, "impossible": 0}
        }
    
    def save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def reset_game(self):
        self.board = [[Player.EMPTY for _ in range(3)] for _ in range(3)]
        self.current_player = Player.X
        self.winner = None
        self.winning_line = None
        self.game_over = False
    
    def check_winner(self):
        # Check rows
        for row in range(3):
            if (self.board[row][0] == self.board[row][1] == self.board[row][2] != Player.EMPTY):
                self.winning_line = (row, 0, row, 2)
                return self.board[row][0]
        
        # Check columns
        for col in range(3):
            if (self.board[0][col] == self.board[1][col] == self.board[2][col] != Player.EMPTY):
                self.winning_line = (0, col, 2, col)
                return self.board[0][col]
        
        # Check diagonals
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] != Player.EMPTY):
            self.winning_line = (0, 0, 2, 2)
            return self.board[0][0]
        
        if (self.board[0][2] == self.board[1][1] == self.board[2][0] != Player.EMPTY):
            self.winning_line = (0, 2, 2, 0)
            return self.board[0][2]
        
        return None
    
    def is_board_full(self):
        return all(self.board[row][col] != Player.EMPTY 
                  for row in range(3) for col in range(3))
    
    def get_empty_cells(self):
        return [(row, col) for row in range(3) for col in range(3) 
                if self.board[row][col] == Player.EMPTY]
    
    def minimax(self, depth, is_maximizing, alpha, beta):
        winner = self.check_winner()
        
        if winner == Player.O:
            return 10 - depth
        elif winner == Player.X:
            return depth - 10
        elif self.is_board_full():
            return 0
        
        if is_maximizing:
            max_eval = -math.inf
            for row, col in self.get_empty_cells():
                self.board[row][col] = Player.O
                eval_score = self.minimax(depth + 1, False, alpha, beta)
                self.board[row][col] = Player.EMPTY
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for row, col in self.get_empty_cells():
                self.board[row][col] = Player.X
                eval_score = self.minimax(depth + 1, True, alpha, beta)
                self.board[row][col] = Player.EMPTY
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_ai_move(self):
        empty_cells = self.get_empty_cells()
        
        if not empty_cells:
            return None
        
        if self.difficulty == Difficulty.EASY:
            return random.choice(empty_cells)
        
        elif self.difficulty == Difficulty.MEDIUM:
            if random.random() < 0.5:
                return random.choice(empty_cells)
        
        # HARD and IMPOSSIBLE use minimax
        best_score = -math.inf
        best_move = None
        
        for row, col in empty_cells:
            self.board[row][col] = Player.O
            score = self.minimax(0, False, -math.inf, math.inf)
            self.board[row][col] = Player.EMPTY
            
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        return best_move if best_move else random.choice(empty_cells)
    
    def make_move(self, row, col):
        if self.board[row][col] == Player.EMPTY and not self.game_over:
            self.board[row][col] = self.current_player
            
            # Check winner
            winner = self.check_winner()
            if winner:
                self.winner = winner
                self.game_over = True
                self.update_stats(winner)
            elif self.is_board_full():
                self.game_over = True
                self.update_stats(None)
            else:
                self.current_player = Player.O if self.current_player == Player.X else Player.X
            
            return True
        return False
    
    def update_stats(self, winner):
        if self.game_mode == 'pvp':
            self.stats['pvp']['total_games'] += 1
            if winner == Player.X:
                self.stats['pvp']['x_wins'] += 1
            elif winner == Player.O:
                self.stats['pvp']['o_wins'] += 1
            else:
                self.stats['pvp']['draws'] += 1
        else:
            self.stats['pvc']['total_games'] += 1
            if winner == Player.X:
                self.stats['pvc']['player_wins'] += 1
            elif winner == Player.O:
                self.stats['pvc']['ai_wins'] += 1
            else:
                self.stats['pvc']['draws'] += 1
            
            self.stats['pvc'][self.difficulty] += 1
        
        self.save_stats()

# Global game instance (or use sessions for multi-user)
game = TicTacToeGame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    return jsonify({
        'board': game.board,
        'currentPlayer': game.current_player,
        'winner': game.winner,
        'winningLine': game.winning_line,
        'gameOver': game.game_over,
        'gameMode': game.game_mode,
        'difficulty': game.difficulty
    })

@app.route('/api/game/move', methods=['POST'])
def make_move():
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    if game.make_move(row, col):
        return jsonify({'success': True, **get_game_state().json})
    return jsonify({'success': False})

@app.route('/api/game/ai-move', methods=['POST'])
def ai_move():
    if game.current_player == Player.O and not game.game_over:
        move = game.get_ai_move()
        if move:
            row, col = move
            game.make_move(row, col)
    return jsonify({'success': True, **get_game_state().json})

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    game.reset_game()
    return jsonify({'success': True, **get_game_state().json})

@app.route('/api/game/settings', methods=['POST'])
def update_settings():
    data = request.json
    game_mode = data.get('gameMode')
    difficulty = data.get('difficulty')
    
    if game_mode:
        game.game_mode = game_mode
    if difficulty:
        game.difficulty = difficulty
    
    game.reset_game()
    return jsonify({'success': True, **get_game_state().json})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(game.stats)

@app.route('/api/stats/reset', methods=['POST'])
def reset_stats():
    game.stats = {
        "pvp": {"x_wins": 0, "o_wins": 0, "draws": 0, "total_games": 0},
        "pvc": {"player_wins": 0, "ai_wins": 0, "draws": 0, "total_games": 0,
               "easy": 0, "medium": 0, "hard": 0, "impossible": 0}
    }
    game.save_stats()
    return jsonify({'success': True, 'stats': game.stats})

def get_game_state():
    return {
        'board': game.board,
        'currentPlayer': game.current_player,
        'winner': game.winner,
        'winningLine': game.winning_line,
        'gameOver': game.game_over,
        'gameMode': game.game_mode,
        'difficulty': game.difficulty
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
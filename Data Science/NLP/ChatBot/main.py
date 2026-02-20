import streamlit as st
import numpy as np
import time

# Set page configuration
st.set_page_config(
    page_title="Tic Tac Toe AI",
    page_icon="⭕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .board-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .board {
        display: grid;
        grid-template-columns: repeat(3, 100px);
        grid-gap: 10px;
    }
    .cell-button {
        width: 100px;
        height: 100px;
        font-size: 2.5rem;
        font-weight: bold;
        background-color: #fff;
        border: 2px solid #2c3e50;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 0;
        padding: 0;
    }
    .cell-button:hover:not(:disabled) {
        background-color: #f8f9fa;
        transform: scale(1.05);
    }
    .cell-button:disabled {
        cursor: not-allowed;
        opacity: 0.9;
    }
    .cell-x {
        color: #e74c3c;
    }
    .cell-o {
        color: #3498db;
    }
    .cell-winner {
        background-color: #f1c40f;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .score-board {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
        font-size: 1.2rem;
    }
    .score-item {
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        background-color: #f8f9fa;
        width: 30%;
    }
    .ai-thinking {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 60px;
        font-size: 1.2rem;
        color: #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = [''] * 9
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'ai_score' not in st.session_state:
    st.session_state.ai_score = 0
if 'draws' not in st.session_state:
    st.session_state.draws = 0
if 'player_turn' not in st.session_state:
    st.session_state.player_turn = True
if 'ai_difficulty' not in st.session_state:
    st.session_state.ai_difficulty = "Medium"
if 'ai_thinking' not in st.session_state:
    st.session_state.ai_thinking = False

# AI player using minimax algorithm
class TicTacToeAI:
    def __init__(self, difficulty="Medium"):
        self.difficulty = difficulty
        self.depth = 5 if difficulty == "Hard" else 3 if difficulty == "Medium" else 1
    
    def evaluate(self, board):
        # Check for winning lines
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for line in lines:
            if board[line[0]] == board[line[1]] == board[line[2]] != '':
                return 10 if board[line[0]] == 'O' else -10
        
        return 0  # No winner yet
    
    def is_moves_left(self, board):
        return '' in board
    
    def minimax(self, board, depth, is_max, alpha, beta):
        score = self.evaluate(board)
        
        # If maximizer or minimizer has won
        if score == 10 or score == -10:
            return score
        
        # If no moves left or depth limit reached
        if not self.is_moves_left(board) or depth == 0:
            return 0
        
        if is_max:
            best = -1000
            
            for i in range(9):
                if board[i] == '':
                    board[i] = 'O'
                    best = max(best, self.minimax(board, depth-1, not is_max, alpha, beta))
                    board[i] = ''
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
            return best
        else:
            best = 1000
            
            for i in range(9):
                if board[i] == '':
                    board[i] = 'X'
                    best = min(best, self.minimax(board, depth-1, not is_max, alpha, beta))
                    board[i] = ''
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
            return best
    
    def find_best_move(self, board):
        best_val = -1000
        best_move = -1
        
        for i in range(9):
            if board[i] == '':
                board[i] = 'O'
                move_val = self.minimax(board, self.depth, False, -1000, 1000)
                board[i] = ''
                
                if move_val > best_val:
                    best_move = i
                    best_val = move_val
        
        return best_move

# Check for a winner
def check_winner(board):
    # Check for winning lines
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    
    for line in lines:
        if board[line[0]] != '' and board[line[0]] == board[line[1]] == board[line[2]]:
            return board[line[0]]
    
    # Check for draw
    if '' not in board:
        return 'Draw'
    
    return None

# Reset the game
def reset_game():
    st.session_state.board = [''] * 9
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.player_turn = True

# Make a move when a cell is clicked
def make_move(position):
    if st.session_state.board[position] == '' and not st.session_state.game_over and st.session_state.player_turn:
        st.session_state.board[position] = 'X'
        st.session_state.player_turn = False
        
        # Check for winner after player's move
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.game_over = True
            st.session_state.winner = winner
            if winner == 'X':
                st.session_state.player_score += 1
            elif winner == 'Draw':
                st.session_state.draws += 1
        else:
            # AI's turn
            st.session_state.ai_thinking = True
        st.rerun()

# AI makes a move
def ai_move():
    if not st.session_state.player_turn and not st.session_state.game_over:
        time.sleep(0.5)  # Simulate thinking time
        
        ai = TicTacToeAI(st.session_state.ai_difficulty)
        move = ai.find_best_move(st.session_state.board)
        
        if move != -1:
            st.session_state.board[move] = 'O'
            st.session_state.player_turn = True
            
            # Check for winner after AI's move
            winner = check_winner(st.session_state.board)
            if winner:
                st.session_state.game_over = True
                st.session_state.winner = winner
                if winner == 'O':
                    st.session_state.ai_score += 1
                elif winner == 'Draw':
                    st.session_state.draws += 1
        
        st.session_state.ai_thinking = False
        st.rerun()

# Title and introduction
st.markdown('<div class="main-header">Tic Tac Toe AI</div>', unsafe_allow_html=True)
st.markdown("""
Play against an AI that uses the minimax algorithm with alpha-beta pruning to make optimal moves.
The AI evaluates all possible moves to determine the best strategy.
""")

# Sidebar for controls and information
with st.sidebar:
    st.header("Game Controls")
    
    if st.button("New Game"):
        reset_game()
    
    st.markdown("---")
    st.header("AI Difficulty")
    
    # Difficulty buttons
    if st.button("Easy", key="easy", use_container_width=True):
        st.session_state.ai_difficulty = "Easy"
        reset_game()
    
    if st.button("Medium", key="medium", use_container_width=True):
        st.session_state.ai_difficulty = "Medium"
        reset_game()
    
    if st.button("Hard", key="hard", use_container_width=True):
        st.session_state.ai_difficulty = "Hard"
        reset_game()
    
    st.markdown(f"**Current Difficulty:** {st.session_state.ai_difficulty}")
    
    st.markdown("---")
    st.header("How the AI Works")
    st.markdown("""
    The AI uses the **minimax algorithm** with **alpha-beta pruning**:
    
    - Evaluates all possible moves
    - Looks several moves ahead
    - Chooses the move with the best outcome
    - Difficulty levels change how far ahead the AI looks
    """)
    
    st.markdown("---")
    st.header("Score Explanation")
    st.markdown("""
    - **You (X)**: Player wins
    - **AI (O)**: AI wins
    - **Draws**: No winner
    """)

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    # Score board
    st.markdown('<div class="sub-header">Score Board</div>', unsafe_allow_html=True)
    
    score_html = """
    <div class="score-board">
        <div class="score-item">
            <div>You (X)</div>
            <div style="font-size: 2rem; font-weight: bold;">{}</div>
        </div>
        <div class="score-item">
            <div>Draws</div>
            <div style="font-size: 2rem; font-weight: bold;">{}</div>
        </div>
        <div class="score-item">
            <div>AI (O)</div>
            <div style="font-size: 2rem; font-weight: bold;">{}</div>
        </div>
    </div>
    """.format(st.session_state.player_score, st.session_state.draws, st.session_state.ai_score)
    
    st.markdown(score_html, unsafe_allow_html=True)
    
    # Game status
    st.markdown('<div class="sub-header">Game Status</div>', unsafe_allow_html=True)
    
    if st.session_state.game_over:
        if st.session_state.winner == 'Draw':
            st.success("Game Over: It's a draw!")
        else:
            winner_text = "You win!" if st.session_state.winner == 'X' else "AI wins!"
            st.success(f"Game Over: {winner_text}")
    else:
        if st.session_state.ai_thinking:
            st.info("AI is thinking...")
        else:
            turn_text = "Your turn (X)" if st.session_state.player_turn else "AI's turn (O)"
            st.info(turn_text)
    
    # Highlight winning cells if game is over
    winning_cells = []
    if st.session_state.game_over and st.session_state.winner != 'Draw':
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for line in lines:
            if (st.session_state.board[line[0]] != '' and 
                st.session_state.board[line[0]] == st.session_state.board[line[1]] == st.session_state.board[line[2]]):
                winning_cells = line
                break

with col2:
    # Game board
    st.markdown('<div class="sub-header">Game Board</div>', unsafe_allow_html=True)
    st.markdown("Click on an empty cell to place your X")
    
    # Create the board using Streamlit buttons in a grid
    st.markdown('<div class="board-container">', unsafe_allow_html=True)
    
    # Create 3 columns for the board rows
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            position = row * 3 + col
            with cols[col]:
                # Determine button label and styling
                label = st.session_state.board[position]
                button_class = "cell-button"
                if st.session_state.board[position] == 'X':
                    button_class += " cell-x"
                elif st.session_state.board[position] == 'O':
                    button_class += " cell-o"
                
                if position in winning_cells:
                    button_class += " cell-winner"
                
                # Create the button
                if st.button(
                    label if label else " ", 
                    key=f"cell_{position}",
                    use_container_width=True,
                    disabled=st.session_state.board[position] != '' or not st.session_state.player_turn or st.session_state.game_over
                ):
                    make_move(position)
    
    st.markdown('</div>', unsafe_allow_html=True)

# AI makes move if it's their turn
if not st.session_state.player_turn and not st.session_state.game_over:
    if st.session_state.ai_thinking:
        ai_move()

# Game instructions
st.markdown("---")
st.markdown('<div class="sub-header">How to Play</div>', unsafe_allow_html=True)

st.markdown("""
1. You play as **X**, and the AI plays as **O**
2. **Click directly on an empty cell** to place your X
3. The AI will automatically make its move after yours
4. The goal is to get three of your marks in a row (horizontally, vertically, or diagonally)
5. If all squares are filled with no winner, the game is a draw

**Pro Tip**: On Hard difficulty, the AI is unbeatable - the best you can do is force a draw!
""")

# Footer
st.markdown("---")
st.caption("This Tic Tac Toe AI uses the minimax algorithm with alpha-beta pruning to determine the optimal moves.")

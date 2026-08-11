#  Interactive Tic-Tac-Toe Game Application

An interactive Tic-Tac-Toe game built with Python (backend logic) and a web-based frontend (HTML, CSS, JavaScript), featuring game statistics tracking.

##  Overview

This project is a full-stack implementation of the classic Tic-Tac-Toe game. It combines a Python backend for game logic and state management with a responsive, interactive web interface for gameplay. The application also tracks and stores game statistics for future reference.

##  Project Structure

```
tic-tac-toe/
│
├── app.py                    # Main application file (server / entry point)
├── tictactoe.py               # Core game logic (win detection, moves, board state)
├── tictactoe_stats.json       # Stores game statistics (wins, losses, draws)
│
├── index.html                 # Main web page / game interface
├── style.css                  # Styling for the game board and UI
├── game.js                    # Frontend game interactions and logic
│
└── README.md                  # Project documentation
```

##  Features

- Interactive, browser-based Tic-Tac-Toe board
- Real-time move validation and turn switching
- Win, loss, and draw detection
- Persistent game statistics tracking (`tictactoe_stats.json`)
- Clean, responsive UI
- Python backend handling core game logic

##  Tech Stack

- **Backend:** Python *(Flask — update if different)*
- **Frontend:** HTML, CSS, JavaScript
- **Data Storage:** JSON (for game statistics)

##  Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tic-tac-toe.git
   cd tic-tac-toe
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

##  How to Run

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and go to:
   ```
   http://localhost:5000
   ```
   *(update the port based on your actual `app.py` configuration)*

##  How to Play

1. The game starts with Player X.
2. Click on any empty cell on the board to make a move.
3. Players alternate turns between X and O.
4. The first player to align three symbols horizontally, vertically, or diagonally wins.
5. If all cells are filled with no winner, the game ends in a draw.
6. Game results are automatically recorded in `tictactoe_stats.json`.

##  Game Statistics

The application tracks and stores statistics such as:
- Total games played
- Wins (X and O)
- Draws

All stats are saved in `tictactoe_stats.json` and updated after every game.

## Screenshots

*(Add screenshots or a GIF of gameplay here)*

##  Future Improvements

- Add single-player mode with AI opponent
- Add difficulty levels for AI
- Add sound effects and animations
- Add a leaderboard / player profiles
- Add reset stats functionality

##  Author

**Malika**
Computer Science Graduate | AI/ML & Full-Stack Developer

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

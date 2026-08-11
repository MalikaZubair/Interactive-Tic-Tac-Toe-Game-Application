// Game State
let gameState = {
    board: Array(3).fill().map(() => Array(3).fill('')),
    currentPlayer: 'X',
    winner: null,
    winningLine: null,
    gameOver: false,
    gameMode: 'pvp',
    difficulty: 'medium'
};

let moveHistory = [];
let totalMoves = 0;
let soundsEnabled = true;
let currentTheme = 'dark-mode';

// DOM Elements
const gameBoard = document.getElementById('gameBoard');
const currentTurn = document.getElementById('currentTurn');
const totalMovesEl = document.getElementById('totalMoves');
const gameModeEl = document.getElementById('gameMode');
const gameDifficulty = document.getElementById('gameDifficulty');
const difficultyBadge = document.getElementById('difficultyBadge');
const moveHistoryEl = document.getElementById('moveHistory');
const gameOverModal = document.getElementById('gameOverModal');
const resultText = document.getElementById('resultText');
const resultMessage = document.getElementById('resultMessage');
const resultIcon = document.getElementById('resultIcon');

// Sound Elements
const moveSound = document.getElementById('moveSound');
const winSound = document.getElementById('winSound');
const loseSound = document.getElementById('loseSound');
const drawSound = document.getElementById('drawSound');
const clickSound = document.getElementById('clickSound');
const hoverSound = document.getElementById('hoverSound');

// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Initialize Game
document.addEventListener('DOMContentLoaded', () => {
    initializeGame();
    setupEventListeners();
    loadGameState();
    loadStats();
});

function initializeGame() {
    createBoard();
    updateGameInfo();
    createParticles();
    startStarAnimation();
}

function createBoard() {
    gameBoard.innerHTML = '';
    for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.addEventListener('click', () => handleCellClick(row, col));
            cell.addEventListener('mouseenter', () => playSound('hover'));
            gameBoard.appendChild(cell);
        }
    }
    updateBoard();
}

function updateBoard() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        const value = gameState.board[row][col];
        
        cell.textContent = value;
        cell.className = 'cell';
        if (value === 'X') cell.classList.add('x');
        if (value === 'O') cell.classList.add('o');
        
        // Add winner highlight
        if (gameState.winningLine) {
            const [startRow, startCol, endRow, endCol] = gameState.winningLine;
            if ((row >= startRow && row <= endRow && col >= startCol && col <= endCol) ||
                (row <= startRow && row >= endRow && col <= startCol && col >= endCol)) {
                cell.classList.add('winner');
            }
        }
    });
    
    updateWinningLine();
}

function updateWinningLine() {
    const line = document.getElementById('winningLine');
    if (!gameState.winningLine || !line) return;
    
    const [startRow, startCol, endRow, endCol] = gameState.winningLine;
    const cells = document.querySelectorAll('.cell');
    const boardRect = gameBoard.getBoundingClientRect();
    
    // Calculate line position
    const startCell = Array.from(cells).find(c => 
        parseInt(c.dataset.row) === startRow && 
        parseInt(c.dataset.col) === startCol
    );
    const endCell = Array.from(cells).find(c => 
        parseInt(c.dataset.row) === endRow && 
        parseInt(c.dataset.col) === endCol
    );
    
    if (startCell && endCell) {
        const startRect = startCell.getBoundingClientRect();
        const endRect = endCell.getBoundingClientRect();
        
        const startX = startRect.left + startRect.width / 2 - boardRect.left;
        const startY = startRect.top + startRect.height / 2 - boardRect.top;
        const endX = endRect.left + endRect.width / 2 - boardRect.left;
        const endY = endRect.top + endRect.height / 2 - boardRect.top;
        
        const angle = Math.atan2(endY - startY, endX - startX) * 180 / Math.PI;
        const length = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
        
        line.style.left = startX + 'px';
        line.style.top = startY + 'px';
        line.style.width = length + 'px';
        line.style.transform = `rotate(${angle}deg)`;
        line.style.opacity = '1';
    }
}

function updateGameInfo() {
    currentTurn.textContent = gameState.currentPlayer;
    currentTurn.className = gameState.currentPlayer === 'X' ? 'info-value turn-x' : 'info-value turn-o';
    totalMovesEl.textContent = totalMoves;
    
    // Update game mode and difficulty
    const modeText = gameState.gameMode === 'pvp' ? 'Player vs Player' : 'Player vs AI';
    const difficultyText = gameState.difficulty.charAt(0).toUpperCase() + gameState.difficulty.slice(1);
    
    gameModeEl.textContent = modeText;
    gameDifficulty.textContent = difficultyText;
    difficultyBadge.innerHTML = `<i class="fas fa-robot"></i> ${difficultyText}`;
    
    // Update game status
    const statusEl = document.getElementById('gameStatus');
    if (gameState.gameOver) {
        if (gameState.winner) {
            statusEl.innerHTML = `<p>Game Over! <span class="turn-${gameState.winner.toLowerCase()}">${gameState.winner}</span> Wins!</p>`;
        } else {
            statusEl.innerHTML = '<p>Game Over! It\'s a Draw!</p>';
        }
    } else {
        statusEl.innerHTML = `<p>Player <span class="turn-${gameState.currentPlayer.toLowerCase()}">${gameState.currentPlayer}</span>'s turn</p>`;
    }
}

async function loadGameState() {
    try {
        const response = await fetch(`${API_BASE}/game/state`);
        const data = await response.json();
        gameState = data;
        updateBoard();
        updateGameInfo();
    } catch (error) {
        console.error('Error loading game state:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        updateStatsDisplay(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStatsDisplay(stats) {
    // PvP Stats
    document.getElementById('xWins').textContent = stats.pvp.x_wins;
    document.getElementById('oWins').textContent = stats.pvp.o_wins;
    document.getElementById('draws').textContent = stats.pvp.draws;
    
    document.getElementById('pvpTotal').textContent = stats.pvp.total_games;
    document.getElementById('pvpXWins').textContent = stats.pvp.x_wins;
    document.getElementById('pvpOWins').textContent = stats.pvp.o_wins;
    document.getElementById('pvpDraws').textContent = stats.pvp.draws;
    
    // PvC Stats
    document.getElementById('pvcTotal').textContent = stats.pvc.total_games;
    document.getElementById('pvcPlayerWins').textContent = stats.pvc.player_wins;
    document.getElementById('pvcAIWins').textContent = stats.pvc.ai_wins;
    document.getElementById('pvcDraws').textContent = stats.pvc.draws;
    
    // Difficulty stats
    document.getElementById('easyGames').textContent = stats.pvc.easy;
    document.getElementById('mediumGames').textContent = stats.pvc.medium;
    document.getElementById('hardGames').textContent = stats.pvc.hard;
    document.getElementById('impossibleGames').textContent = stats.pvc.impossible;
    
    // Update charts
    updateCharts(stats);
}

function updateCharts(stats) {
    // PvP Chart
    const pvpTotal = stats.pvp.total_games || 1;
    const pvpXPercent = (stats.pvp.x_wins / pvpTotal) * 100;
    const pvpOPercent = (stats.pvp.o_wins / pvpTotal) * 100;
    
    document.getElementById('pvpXBar').style.height = pvpXPercent + '%';
    document.getElementById('pvpOBar').style.height = pvpOPercent + '%';
    
    // PvC Chart
    const pvcTotal = stats.pvc.total_games || 1;
    const pvcPlayerPercent = (stats.pvc.player_wins / pvcTotal) * 100;
    const pvcAIPercent = (stats.pvc.ai_wins / pvcTotal) * 100;
    
    document.getElementById('pvcPlayerBar').style.height = pvcPlayerPercent + '%';
    document.getElementById('pvcAIBar').style.height = pvcAIPercent + '%';
}

async function handleCellClick(row, col) {
    if (gameState.gameOver || gameState.board[row][col] !== '') return;
    
    playSound('click');
    
    try {
        const response = await fetch(`${API_BASE}/game/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row, col })
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState = {
                board: data.board,
                currentPlayer: data.currentPlayer,
                winner: data.winner,
                winningLine: data.winningLine,
                gameOver: data.gameOver,
                gameMode: data.gameMode,
                difficulty: data.difficulty
            };
            
            totalMoves++;
            addMoveToHistory(row, col, 'X');
            updateBoard();
            updateGameInfo();
            playSound('move');
            
            if (gameState.gameOver) {
                showGameOver();
            } else if (gameState.gameMode === 'pvc' && gameState.currentPlayer === 'O') {
                // AI's turn
                setTimeout(makeAIMove, 500);
            }
        }
    } catch (error) {
        console.error('Error making move:', error);
    }
}

async function makeAIMove() {
    try {
        const response = await fetch(`${API_BASE}/game/ai-move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState = {
                board: data.board,
                currentPlayer: data.currentPlayer,
                winner: data.winner,
                winningLine: data.winningLine,
                gameOver: data.gameOver,
                gameMode: data.gameMode,
                difficulty: data.difficulty
            };
            
            totalMoves++;
            updateBoard();
            updateGameInfo();
            playSound('move');
            
            if (gameState.gameOver) {
                showGameOver();
            }
        }
    } catch (error) {
        console.error('Error making AI move:', error);
    }
}

function addMoveToHistory(row, col, player) {
    const moveItem = document.createElement('div');
    moveItem.className = 'move-item';
    moveItem.innerHTML = `
        <span>Move ${totalMoves}:</span>
        <span>Player ${player} at (${row + 1}, ${col + 1})</span>
    `;
    
    const emptyMessage = moveHistoryEl.querySelector('.empty-history');
    if (emptyMessage) emptyMessage.remove();
    
    moveHistoryEl.prepend(moveItem);
    moveHistory.unshift({ row, col, player, moveNumber: totalMoves });
    
    // Keep only last 10 moves visible
    if (moveHistoryEl.children.length > 10) {
        moveHistoryEl.removeChild(moveHistoryEl.lastChild);
    }
}

function showGameOver() {
    if (gameState.winner) {
        if (gameState.winner === 'X') {
            resultText.textContent = gameState.gameMode === 'pvp' ? 'Player X Wins!' : 'You Win!';
            resultMessage.textContent = 'Congratulations on an amazing victory!';
            resultIcon.innerHTML = '<i class="fas fa-trophy"></i>';
            playSound('win');
            createConfetti();
        } else {
            resultText.textContent = gameState.gameMode === 'pvp' ? 'Player O Wins!' : 'AI Wins!';
            resultMessage.textContent = gameState.gameMode === 'pvp' ? 'Great game!' : 'Better luck next time!';
            resultIcon.innerHTML = '<i class="fas fa-robot"></i>';
            playSound('lose');
        }
    } else {
        resultText.textContent = "It's a Draw!";
        resultMessage.textContent = 'The game ended in a stalemate!';
        resultIcon.innerHTML = '<i class="fas fa-handshake"></i>';
        playSound('draw');
    }
    
    gameOverModal.style.display = 'flex';
}

function playSound(soundName) {
    if (!soundsEnabled) return;
    
    const soundMap = {
        'move': moveSound,
        'win': winSound,
        'lose': loseSound,
        'draw': drawSound,
        'click': clickSound,
        'hover': hoverSound
    };
    
    const sound = soundMap[soundName];
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(e => console.log('Sound play failed:', e));
    }
}

function setupEventListeners() {
    // New Game Button
    document.getElementById('newGameBtn').addEventListener('click', async () => {
        playSound('click');
        await updateSettings();
    });
    
    // Restart Button
    document.getElementById('restartBtn').addEventListener('click', async () => {
        playSound('click');
        try {
            const response = await fetch(`${API_BASE}/game/reset`, {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                gameState = {
                    board: data.board,
                    currentPlayer: data.currentPlayer,
                    winner: data.winner,
                    winningLine: data.winningLine,
                    gameOver: data.gameOver,
                    gameMode: data.gameMode,
                    difficulty: data.difficulty
                };
                totalMoves = 0;
                moveHistory = [];
                moveHistoryEl.innerHTML = '<p class="empty-history">No moves yet</p>';
                updateBoard();
                updateGameInfo();
            }
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    });
    
    // Menu Button
    document.getElementById('menuBtn').addEventListener('click', () => {
        playSound('click');
        gameOverModal.style.display = 'flex';
    });
    
    // Apply Settings
    document.getElementById('applySettings').addEventListener('click', async () => {
        playSound('click');
        await updateSettings();
    });
    
    // Mode Buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            playSound('click');
        });
    });
    
    // Difficulty Buttons
    document.querySelectorAll('.difficulty-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            playSound('click');
        });
    });
    
    // Sound Buttons
    document.querySelectorAll('.sound-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.sound-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            soundsEnabled = btn.dataset.sound === 'on';
            playSound('click');
        });
    });
    
    // Sound Toggle
    document.getElementById('soundToggle').addEventListener('click', () => {
        soundsEnabled = !soundsEnabled;
        const icon = document.querySelector('#soundToggle i');
        icon.className = soundsEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
        playSound('click');
    });
    
    // Theme Toggle
    document.getElementById('themeToggle').addEventListener('click', () => {
        currentTheme = currentTheme === 'dark-mode' ? 'light-mode' : 'dark-mode';
        document.body.className = currentTheme;
        const icon = document.querySelector('#themeToggle i');
        icon.className = currentTheme === 'dark-mode' ? 'fas fa-moon' : 'fas fa-sun';
        playSound('click');
    });
    
    // Stats Tabs
    document.querySelectorAll('.stat-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;
            document.querySelectorAll('.stat-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.stat-content').forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`${tabId}Stats`).classList.add('active');
            playSound('click');
        });
    });
    
    // Reset Stats
    document.getElementById('resetStats').addEventListener('click', async () => {
        playSound('click');
        if (confirm('Are you sure you want to reset all statistics?')) {
            try {
                const response = await fetch(`${API_BASE}/stats/reset`, {
                    method: 'POST'
                });
                const data = await response.json();
                if (data.success) {
                    updateStatsDisplay(data.stats);
                }
            } catch (error) {
                console.error('Error resetting stats:', error);
            }
        }
    });
    
    // Play Again Button
    document.getElementById('playAgainBtn').addEventListener('click', async () => {
        playSound('click');
        gameOverModal.style.display = 'none';
        await updateSettings();
    });
    
    // Main Menu Button
    document.getElementById('mainMenuBtn').addEventListener('click', () => {
        playSound('click');
        gameOverModal.style.display = 'none';
    });
    
    // Close Modal
    document.querySelector('.close-modal').addEventListener('click', () => {
        playSound('click');
        gameOverModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    gameOverModal.addEventListener('click', (e) => {
        if (e.target === gameOverModal) {
            gameOverModal.style.display = 'none';
        }
    });
}

async function updateSettings() {
    const gameMode = document.querySelector('.mode-btn.active').dataset.mode;
    const difficulty = document.querySelector('.difficulty-btn.active').dataset.difficulty;
    
    try {
        const response = await fetch(`${API_BASE}/game/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gameMode, difficulty })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState = {
                board: data.board,
                currentPlayer: data.currentPlayer,
                winner: data.winner,
                winningLine: data.winningLine,
                gameOver: data.gameOver,
                gameMode: data.gameMode,
                difficulty: data.difficulty
            };
            totalMoves = 0;
            moveHistory = [];
            moveHistoryEl.innerHTML = '<p class="empty-history">No moves yet</p>';
            updateBoard();
            updateGameInfo();
            gameOverModal.style.display = 'none';
        }
    } catch (error) {
        console.error('Error updating settings:', error);
    }
}

// Visual Effects
function createParticles() {
    const container = document.querySelector('.particles-container');
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 5}s`;
        container.appendChild(particle);
    }
}

function startStarAnimation() {
    const stars = document.querySelector('.stars');
    setInterval(() => {
        stars.style.backgroundPosition = `${Math.random() * 100}px ${Math.random() * 100}px`;
    }, 10000);
}

function createConfetti() {
    const canvas = document.getElementById('confettiCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const confettiPieces = [];
    const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#22c55e', '#f97316', '#ef4444'];
    
    // Create confetti pieces
    for (let i = 0; i < 150; i++) {
        confettiPieces.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            r: Math.random() * 10 + 5,
            d: Math.random() * 5 + 2,
            color: colors[Math.floor(Math.random() * colors.length)],
            tilt: Math.random() * 10 - 10,
            tiltAngleIncremental: Math.random() * 0.07 + 0.05,
            tiltAngle: 0
        });
    }
    
    function drawConfetti() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        confettiPieces.forEach(p => {
            ctx.beginPath();
            ctx.lineWidth = p.d;
            ctx.strokeStyle = p.color;
            ctx.moveTo(p.x + p.tilt + p.r, p.y);
            ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r);
            ctx.stroke();
        });
        
        updateConfetti();
    }
    
    function updateConfetti() {
        confettiPieces.forEach(p => {
            p.tiltAngle += p.tiltAngleIncremental;
            p.y += (Math.cos(p.d) + 3 + p.r / 2) / 2;
            p.tilt = Math.sin(p.tiltAngle) * 15;
            
            if (p.y > canvas.height) {
                p.x = Math.random() * canvas.width;
                p.y = -20;
            }
        });
    }
    
    let animationId;
    function animateConfetti() {
        drawConfetti();
        animationId = requestAnimationFrame(animateConfetti);
        
        // Stop after 5 seconds
        setTimeout(() => {
            cancelAnimationFrame(animationId);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }, 5000);
    }
    
    animateConfetti();
}

// Add CSS for particles
const style = document.createElement('style');
style.textContent = `
    .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: white;
        border-radius: 50%;
        pointer-events: none;
        animation: float 15s infinite linear;
    }
    
    @keyframes float {
        0% {
            transform: translateY(100vh) translateX(0);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100px) translateX(100px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Handle window resize
window.addEventListener('resize', () => {
    const canvas = document.getElementById('confettiCanvas');
    if (canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
});
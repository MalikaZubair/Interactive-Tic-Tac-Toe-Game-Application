import pygame
import sys
import math
import random
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CELL_SIZE = 150
GRID_SIZE = 3
LINE_WIDTH = 8
ANIMATION_SPEED = 15
FPS = 60

# Colors - Modern Vibrant Theme
BACKGROUND = (15, 23, 42)
PRIMARY = (99, 102, 241)
SECONDARY = (139, 92, 246)
ACCENT = (236, 72, 153)
SUCCESS = (34, 197, 94)
WARNING = (251, 146, 60)
DANGER = (239, 68, 68)
BOARD_BG = (30, 41, 59)
GRID_COLOR = (51, 65, 85)
X_COLOR = (239, 68, 68)
O_COLOR = (59, 130, 246)
TEXT_WHITE = (248, 250, 252)
TEXT_GRAY = (203, 213, 225)
GLOW_COLOR = (255, 255, 255)

# Game States
class GameState(Enum):
    MAIN_MENU = 1
    MODE_SELECT = 2
    DIFFICULTY_SELECT = 3
    PLAYING = 4
    GAME_OVER = 5
    STATS = 6
    SETTINGS = 7

# Player Types
class Player(Enum):
    X = 1
    O = 2
    EMPTY = 0

# AI Difficulty
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    IMPOSSIBLE = 4

# Fonts
title_font = pygame.font.Font(None, 84)
header_font = pygame.font.Font(None, 56)
button_font = pygame.font.Font(None, 40)
text_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.volume = 0.6
        self.enabled = True
        self.create_sounds()
    
    def create_sounds(self):
        """Create synthesized sound effects"""
        try:
            # Move sound
            self.sounds["move"] = self.create_tone(400, 0.08, 0.3)
            # Win sound
            self.sounds["win"] = self.create_win_sound()
            # Lose sound
            self.sounds["lose"] = self.create_tone(200, 0.3, 0.4)
            # Draw sound
            self.sounds["draw"] = self.create_tone(300, 0.2, 0.3)
            # Click sound
            self.sounds["click"] = self.create_tone(600, 0.05, 0.2)
            # Hover sound
            self.sounds["hover"] = self.create_tone(500, 0.03, 0.15)
        except Exception as e:
            print(f"Sound creation error: {e}")
            for sound_name in ["move", "win", "lose", "draw", "click", "hover"]:
                self.sounds[sound_name] = pygame.mixer.Sound(buffer=bytes([0]))
    
    def create_tone(self, frequency, duration, volume=0.5):
        """Create a simple tone"""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        
        buf = bytearray(n_samples * 2)
        for i in range(n_samples):
            t = float(i) / sample_rate
            wave = math.sin(2 * math.pi * frequency * t)
            
            # Fade out
            if i > n_samples - sample_rate * 0.05:
                wave *= (n_samples - i) / (sample_rate * 0.05)
            
            sample = int(wave * 32767 * volume)
            buf[2*i] = sample & 0xff
            buf[2*i+1] = (sample >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(self.volume)
        return sound
    
    def create_win_sound(self):
        """Create victory sound"""
        sample_rate = 22050
        duration = 1.0
        n_samples = int(sample_rate * duration)
        
        buf = bytearray(n_samples * 2)
        frequencies = [523.25, 659.25, 783.99, 1046.50]
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            wave = 0
            
            for j, freq in enumerate(frequencies):
                tone_start = j * duration / len(frequencies)
                tone_end = (j + 1) * duration / len(frequencies)
                
                if tone_start <= t < tone_end:
                    tone_t = t - tone_start
                    wave += math.sin(2 * math.pi * freq * tone_t) * 0.3
            
            if i > n_samples - sample_rate * 0.2:
                wave *= (n_samples - i) / (sample_rate * 0.2)
            
            sample = int(wave * 32767 * 0.4)
            buf[2*i] = sample & 0xff
            buf[2*i+1] = (sample >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(self.volume)
        return sound
    
    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def toggle(self):
        self.enabled = not self.enabled

class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY, hover_color=SECONDARY, 
                 icon="", text_color=TEXT_WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.icon = icon
        self.text_color = text_color
        self.is_hovered = False
        self.scale = 1.0
        self.glow_alpha = 0
        
    def draw(self, screen):
        # Calculate scaled rect
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Glow effect
        if self.glow_alpha > 0:
            glow_surf = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GLOW_COLOR, self.glow_alpha), 
                           (0, 0, scaled_width + 20, scaled_height + 20), 
                           border_radius=16)
            screen.blit(glow_surf, (scaled_rect.x - 10, scaled_rect.y - 10))
        
        # Shadow
        shadow_rect = scaled_rect.move(0, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=14)
        
        # Main button
        pygame.draw.rect(screen, self.current_color, scaled_rect, border_radius=14)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255, 40), scaled_rect, 2, border_radius=14)
        
        # Icon and text
        full_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surf = button_font.render(full_text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos, dt):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Smooth transitions
        target_scale = 1.05 if self.is_hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.3
        
        target_color = self.hover_color if self.is_hovered else self.color
        self.current_color = self.lerp_color(self.current_color, target_color, 0.3)
        
        target_glow = 50 if self.is_hovered else 0
        self.glow_alpha += (target_glow - self.glow_alpha) * 0.3
        
        return self.is_hovered and not was_hovered
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    @staticmethod
    def lerp_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        self.color = color
        self.alpha = 255
        self.size = random.randint(3, 8)
        self.lifetime = 60
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.alpha -= 255 / self.lifetime
        self.lifetime -= 1
        
    def draw(self, screen):
        if self.alpha > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(self.alpha)), 
                             (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class TicTacToe:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎮 Tic-Tac-Toe Pro")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.MAIN_MENU
        self.board = [[Player.EMPTY for _ in range(3)] for _ in range(3)]
        self.current_player = Player.X
        self.game_mode = "pvp"  # pvp or pvc
        self.difficulty = Difficulty.MEDIUM
        self.winner = None
        self.winning_line = None
        self.game_over = False
        
        # Animation
        self.particles = []
        self.stars = [(random.randint(0, SCREEN_WIDTH), 
                      random.randint(0, SCREEN_HEIGHT), 
                      random.randint(1, 3)) for _ in range(150)]
        self.animations = {}
        
        # Stats
        self.stats_file = "tictactoe_stats.json"
        self.stats = self.load_stats()
        
        # Sound
        self.sound_manager = SoundManager()
        
        # Initialize buttons
        self.init_buttons()
        
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
    
    def init_buttons(self):
        # Main Menu
        center_x = SCREEN_WIDTH // 2
        btn_width = 350
        btn_height = 70
        start_y = 280
        
        self.play_btn = Button(center_x - btn_width//2, start_y, btn_width, btn_height, 
                               "PLAY", SUCCESS, (60, 220, 120), "▶")
        self.stats_btn = Button(center_x - btn_width//2, start_y + 90, btn_width, btn_height,
                               "STATISTICS", PRIMARY, SECONDARY, "📊")
        self.settings_btn = Button(center_x - btn_width//2, start_y + 180, btn_width, btn_height,
                                  "SETTINGS", WARNING, (255, 170, 90), "⚙")
        self.quit_btn = Button(center_x - btn_width//2, start_y + 270, btn_width, btn_height,
                              "EXIT", DANGER, (255, 90, 90), "✕")
        
        # Mode Selection
        self.pvp_btn = Button(center_x - 380, 300, 350, 200, "PLAYER VS PLAYER", 
                             PRIMARY, SECONDARY, "👥")
        self.pvc_btn = Button(center_x + 30, 300, 350, 200, "PLAYER VS AI", 
                             ACCENT, (255, 100, 180), "🤖")
        
        # Difficulty buttons
        diff_y = 250
        self.easy_btn = Button(center_x - btn_width//2, diff_y, btn_width, btn_height,
                              "EASY", SUCCESS, (60, 220, 120), "🌱")
        self.medium_btn = Button(center_x - btn_width//2, diff_y + 90, btn_width, btn_height,
                                "MEDIUM", WARNING, (255, 170, 90), "⚡")
        self.hard_btn = Button(center_x - btn_width//2, diff_y + 180, btn_width, btn_height,
                              "HARD", DANGER, (255, 90, 90), "🔥")
        self.impossible_btn = Button(center_x - btn_width//2, diff_y + 270, btn_width, btn_height,
                                    "IMPOSSIBLE", SECONDARY, (180, 120, 255), "💀")
        
        # Back button
        self.back_btn = Button(50, 30, 150, 50, "BACK", (71, 85, 105), (100, 116, 139), "←")
        
        # Game buttons
        self.menu_btn = Button(SCREEN_WIDTH - 200, 30, 150, 50, "MENU", 
                              (71, 85, 105), (100, 116, 139), "🏠")
        self.restart_btn = Button(SCREEN_WIDTH - 200, 90, 150, 50, "RESTART",
                                 WARNING, (255, 170, 90), "🔄")
    
    def draw_gradient_background(self):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(BACKGROUND[0] + (BOARD_BG[0] - BACKGROUND[0]) * ratio)
            g = int(BACKGROUND[1] + (BOARD_BG[1] - BACKGROUND[1]) * ratio)
            b = int(BACKGROUND[2] + (BOARD_BG[2] - BACKGROUND[2]) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_stars(self):
        for i, (x, y, size) in enumerate(self.stars):
            if random.random() < 0.01:
                size = random.randint(1, 3)
                self.stars[i] = (x, y, size)
            
            brightness = 150 + 50 * math.sin(pygame.time.get_ticks() / 1000 + i)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (x, y), size)
    
    def draw_glass_card(self, x, y, width, height):
        # Shadow
        shadow = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), (10, 10, width, height), border_radius=24)
        self.screen.blit(shadow, (x - 10, y - 10))
        
        # Glass effect
        card = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(card, (255, 255, 255, 15), (0, 0, width, height), border_radius=24)
        pygame.draw.rect(card, (255, 255, 255, 30), (0, 0, width, height), 2, border_radius=24)
        
        self.screen.blit(card, (x, y))
    
    def draw_main_menu(self):
        self.draw_gradient_background()
        self.draw_stars()
        
        # Animated title
        title = title_font.render("TIC-TAC-TOE PRO", True, TEXT_WHITE)
        pulse = math.sin(pygame.time.get_ticks() / 500) * 5
        title_y = 100 + pulse
        
        # Title glow
        glow_surf = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        glow_title = title_font.render("TIC-TAC-TOE PRO", True, (*PRIMARY, 100))
        self.screen.blit(glow_title, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, title_y + 2))
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, title_y))
        
        # Subtitle
        subtitle = header_font.render("Ultimate Edition", True, TEXT_GRAY)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 180))
        
        # XO animation
        x_symbol = header_font.render("X", True, X_COLOR)
        o_symbol = header_font.render("O", True, O_COLOR)
        rotation = pygame.time.get_ticks() / 20
        
        x_pos = (SCREEN_WIDTH//2 - 100, 220)
        o_pos = (SCREEN_WIDTH//2 + 70, 220)
        
        self.screen.blit(x_symbol, x_pos)
        self.screen.blit(o_symbol, o_pos)
        
        # Buttons
        self.draw_glass_card(SCREEN_WIDTH//2 - 200, 260, 400, 400)
        self.play_btn.draw(self.screen)
        self.stats_btn.draw(self.screen)
        self.settings_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)
    
    def draw_mode_select(self):
        self.draw_gradient_background()
        self.draw_stars()
        
        title = header_font.render("SELECT GAME MODE", True, TEXT_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        self.back_btn.draw(self.screen)
        
        # Mode cards
        self.pvp_btn.draw(self.screen)
        self.pvc_btn.draw(self.screen)
        
        # Mode descriptions
        pvp_desc = text_font.render("Challenge a friend!", True, TEXT_GRAY)
        pvc_desc = text_font.render("Battle against AI", True, TEXT_GRAY)
        
        self.screen.blit(pvp_desc, (SCREEN_WIDTH//2 - 380 + 175 - pvp_desc.get_width()//2, 520))
        self.screen.blit(pvc_desc, (SCREEN_WIDTH//2 + 30 + 175 - pvc_desc.get_width()//2, 520))
    
    def draw_difficulty_select(self):
        self.draw_gradient_background()
        self.draw_stars()
        
        title = header_font.render("SELECT DIFFICULTY", True, TEXT_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        self.back_btn.draw(self.screen)
        
        # Glass card
        self.draw_glass_card(SCREEN_WIDTH//2 - 200, 220, 400, 430)
        
        self.easy_btn.draw(self.screen)
        self.medium_btn.draw(self.screen)
        self.hard_btn.draw(self.screen)
        self.impossible_btn.draw(self.screen)
        
        # Difficulty descriptions
        descriptions = [
            "Perfect for beginners",
            "Balanced challenge",
            "Expert opponent",
            "Unbeatable AI"
        ]
        
        y_positions = [250, 340, 430, 520]
        for desc, y in zip(descriptions, y_positions):
            text = small_font.render(desc, True, TEXT_GRAY)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y + 55))
    
    def draw_board(self):
        board_size = CELL_SIZE * 3
        board_x = (SCREEN_WIDTH - board_size) // 2
        board_y = 200
        
        # Board background with glow
        glow_size = board_size + 40
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_alpha = 30 + 20 * math.sin(pygame.time.get_ticks() / 500)
        pygame.draw.rect(glow_surf, (*PRIMARY, int(glow_alpha)), 
                        (0, 0, glow_size, glow_size), border_radius=20)
        self.screen.blit(glow_surf, (board_x - 20, board_y - 20))
        
        # Board
        pygame.draw.rect(self.screen, BOARD_BG, 
                        (board_x, board_y, board_size, board_size), border_radius=16)
        
        # Grid lines with glow
        for i in range(1, 3):
            # Vertical
            x = board_x + i * CELL_SIZE
            pygame.draw.line(self.screen, (*GRID_COLOR, 100), 
                           (x, board_y), (x, board_y + board_size), LINE_WIDTH + 4)
            pygame.draw.line(self.screen, GRID_COLOR, 
                           (x, board_y), (x, board_y + board_size), LINE_WIDTH)
            
            # Horizontal
            y = board_y + i * CELL_SIZE
            pygame.draw.line(self.screen, (*GRID_COLOR, 100), 
                           (board_x, y), (board_x + board_size, y), LINE_WIDTH + 4)
            pygame.draw.line(self.screen, GRID_COLOR, 
                           (board_x, y), (board_x + board_size, y), LINE_WIDTH)
        
        # Draw symbols with animation
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != Player.EMPTY:
                    x = board_x + col * CELL_SIZE + CELL_SIZE // 2
                    y = board_y + row * CELL_SIZE + CELL_SIZE // 2
                    
                    anim_key = f"{row},{col}"
                    if anim_key not in self.animations:
                        self.animations[anim_key] = 0
                    
                    progress = min(self.animations[anim_key], 1.0)
                    self.animations[anim_key] += 0.1
                    
                    if self.board[row][col] == Player.X:
                        self.draw_x(x, y, progress)
                    else:
                        self.draw_o(x, y, progress)
        
        # Draw winning line
        if self.winning_line:
            self.draw_winning_line(board_x, board_y)
    
    def draw_x(self, x, y, progress=1.0):
        size = 50 * progress
        thickness = 8
        
        # Glow
        glow_surf = pygame.Surface((int(size * 2.5), int(size * 2.5)), pygame.SRCALPHA)
        alpha = int(100 * progress)
        pygame.draw.line(glow_surf, (*X_COLOR, alpha), 
                        (size * 0.25, size * 0.25), (size * 1.75, size * 1.75), thickness + 6)
        pygame.draw.line(glow_surf, (*X_COLOR, alpha), 
                        (size * 1.75, size * 0.25), (size * 0.25, size * 1.75), thickness + 6)
        self.screen.blit(glow_surf, (x - size * 1.25, y - size * 1.25))
        
        # X symbol
        pygame.draw.line(self.screen, X_COLOR, 
                        (x - size, y - size), (x + size, y + size), thickness)
        pygame.draw.line(self.screen, X_COLOR, 
                        (x + size, y - size), (x - size, y + size), thickness)
    
    def draw_o(self, x, y, progress=1.0):
        radius = int(50 * progress)
        thickness = 8
        
        # Glow
        glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
        alpha = int(100 * progress)
        pygame.draw.circle(glow_surf, (*O_COLOR, alpha), 
                          (radius * 1.5, radius * 1.5), radius + 5, thickness + 6)
        self.screen.blit(glow_surf, (x - radius * 1.5, y - radius * 1.5))
        
        # O symbol
        pygame.draw.circle(self.screen, O_COLOR, (x, y), radius, thickness)
    
    def draw_winning_line(self, board_x, board_y):
        if not self.winning_line:
            return
        
        start_row, start_col, end_row, end_col = self.winning_line
        
        start_x = board_x + start_col * CELL_SIZE + CELL_SIZE // 2
        start_y = board_y + start_row * CELL_SIZE + CELL_SIZE // 2
        end_x = board_x + end_col * CELL_SIZE + CELL_SIZE // 2
        end_y = board_y + end_row * CELL_SIZE + CELL_SIZE // 2
        
        # Animated line
        progress = (pygame.time.get_ticks() % 2000) / 2000
        
        # Glow
        for offset in range(5):
            alpha = 50 - offset * 10
            pygame.draw.line(self.screen, (*SUCCESS, alpha), 
                           (start_x, start_y), (end_x, end_y), 20 - offset * 2)
        
        # Main line
        pygame.draw.line(self.screen, SUCCESS, (start_x, start_y), (end_x, end_y), 10)
    
    def draw_game(self):
        self.draw_gradient_background()
        self.draw_stars()
        
        # Header
        mode_text = "PLAYER vs PLAYER" if self.game_mode == "pvp" else f"PLAYER vs AI ({self.difficulty.name})"
        header = text_font.render(mode_text, True, TEXT_WHITE)
        self.screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 50))
        
        # Current turn indicator
        if not self.game_over:
            turn_text = f"Current Turn: {'X' if self.current_player == Player.X else 'O'}"
            turn_color = X_COLOR if self.current_player == Player.X else O_COLOR
            turn = text_font.render(turn_text, True, turn_color)
            self.screen.blit(turn, (SCREEN_WIDTH//2 - turn.get_width()//2, 110))
        
        # Draw board
        self.draw_board()
        
        # Draw particles
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Game buttons
        self.menu_btn.draw(self.screen)
        self.restart_btn.draw(self.screen)
        
        # Game over overlay
        if self.game_over:
            self.draw_game_over()
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Result card
        self.draw_glass_card(SCREEN_WIDTH//2 - 250, 200, 500, 300)
        
        # Result text
        if self.winner:
            if self.winner == Player.X:
                text = "X WINS!" if self.game_mode == "pvp" else "YOU WIN!"
                color = X_COLOR
            else:
                text = "O WINS!" if self.game_mode == "pvp" else "AI WINS!"
                color = O_COLOR
        else:
            text = "IT'S A DRAW!"
            color = WARNING
        
        # Draw result text
        result = header_font.render(text, True, color)
        self.screen.blit(result, (SCREEN_WIDTH//2 - result.get_width()//2, 250))
        
        # Emoji
        emoji = "🎉" if self.winner else "🤝"
        emoji_text = title_font.render(emoji, True, TEXT_WHITE)
        self.screen.blit(emoji_text, (SCREEN_WIDTH//2 - emoji_text.get_width()//2, 310))
        
        # Buttons
        play_again_btn = Button(SCREEN_WIDTH//2 - 220, 400, 200, 60, "PLAY AGAIN", 
                               SUCCESS, (60, 220, 120), "🔄")
        menu_btn_overlay = Button(SCREEN_WIDTH//2 + 20, 400, 200, 60, "MAIN MENU", 
                                  PRIMARY, SECONDARY, "🏠")
        
        play_again_btn.update(pygame.mouse.get_pos(), 0)
        menu_btn_overlay.update(pygame.mouse.get_pos(), 0)
        
        play_again_btn.draw(self.screen)
        menu_btn_overlay.draw(self.screen)
        
        # Store for click detection
        self.play_again_btn = play_again_btn
        self.menu_btn_overlay = menu_btn_overlay

    def draw_stats(self):
        self.draw_gradient_background()
        self.draw_stars()
        
        title = header_font.render("STATISTICS", True, TEXT_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        
        self.back_btn.draw(self.screen)
        
        # PvP Stats
        self.draw_glass_card(100, 180, 400, 440)
        pvp_title = text_font.render("👥 Player vs Player", True, TEXT_WHITE)
        self.screen.blit(pvp_title, (300 - pvp_title.get_width()//2, 200))
        
        pvp_stats = self.stats["pvp"]
        stats_y = 260
        stats_list = [
            f"Total Games: {pvp_stats['total_games']}",
            f"X Wins: {pvp_stats['x_wins']}",
            f"O Wins: {pvp_stats['o_wins']}",
            f"Draws: {pvp_stats['draws']}"
        ]
        
        for stat in stats_list:
            stat_text = text_font.render(stat, True, TEXT_GRAY)
            self.screen.blit(stat_text, (150, stats_y))
            stats_y += 60
        
        # Win rate chart
        if pvp_stats['total_games'] > 0:
            chart_y = 500
            chart_x = 150
            bar_width = 80
            max_height = 80
            
            x_rate = pvp_stats['x_wins'] / pvp_stats['total_games']
            o_rate = pvp_stats['o_wins'] / pvp_stats['total_games']
            
            pygame.draw.rect(self.screen, X_COLOR, 
                           (chart_x, chart_y - x_rate * max_height, bar_width, x_rate * max_height))
            pygame.draw.rect(self.screen, O_COLOR, 
                           (chart_x + 120, chart_y - o_rate * max_height, bar_width, o_rate * max_height))
            
            x_label = small_font.render("X", True, TEXT_GRAY)
            o_label = small_font.render("O", True, TEXT_GRAY)
            self.screen.blit(x_label, (chart_x + bar_width//2 - x_label.get_width()//2, chart_y + 10))
            self.screen.blit(o_label, (chart_x + 120 + bar_width//2 - o_label.get_width()//2, chart_y + 10))
        
        # PvC Stats
        self.draw_glass_card(520, 180, 400, 440)
        pvc_title = text_font.render("🤖 Player vs AI", True, TEXT_WHITE)
        self.screen.blit(pvc_title, (720 - pvc_title.get_width()//2, 200))
        
        pvc_stats = self.stats["pvc"]
        stats_y = 260
        stats_list = [
            f"Total Games: {pvc_stats['total_games']}",
            f"Player Wins: {pvc_stats['player_wins']}",
            f"AI Wins: {pvc_stats['ai_wins']}",
            f"Draws: {pvc_stats['draws']}"
        ]
        
        for stat in stats_list:
            stat_text = text_font.render(stat, True, TEXT_GRAY)
            self.screen.blit(stat_text, (570, stats_y))
            stats_y += 60
        
        # Difficulty breakdown
        diff_y = 500
        diff_text = small_font.render("Games by difficulty:", True, TEXT_GRAY)
        self.screen.blit(diff_text, (570, diff_y))
        
        difficulties = ["Easy", "Medium", "Hard", "Impossible"]
        diff_keys = ["easy", "medium", "hard", "impossible"]
        colors = [SUCCESS, WARNING, DANGER, SECONDARY]
        
        for i, (diff, key, color) in enumerate(zip(difficulties, diff_keys, colors)):
            x = 570 + i * 70
            count = pvc_stats[key]
            
            pygame.draw.rect(self.screen, color, (x, diff_y + 30, 50, 50), border_radius=8)
            count_text = small_font.render(str(count), True, TEXT_WHITE)
            self.screen.blit(count_text, (x + 25 - count_text.get_width()//2, diff_y + 45))

    def draw_settings(self):
        self.draw_gradient_background()
        self.draw_stars()
        
        title = header_font.render("SETTINGS", True, TEXT_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        
        self.back_btn.draw(self.screen)
        
        # Settings card
        self.draw_glass_card(SCREEN_WIDTH//2 - 300, 180, 600, 400)
        
        # Sound toggle
        sound_title = text_font.render("🔊 Sound Effects", True, TEXT_WHITE)
        self.screen.blit(sound_title, (SCREEN_WIDTH//2 - 250, 230))
        
        sound_status = "ON" if self.sound_manager.enabled else "OFF"
        sound_btn = Button(SCREEN_WIDTH//2 + 50, 220, 150, 50, sound_status, 
                          SUCCESS if self.sound_manager.enabled else DANGER,
                          (60, 220, 120) if self.sound_manager.enabled else (255, 90, 90))
        sound_btn.update(pygame.mouse.get_pos(), 0)
        sound_btn.draw(self.screen)
        self.sound_toggle_btn = sound_btn
        
        # Volume slider
        volume_title = text_font.render("🎚️ Volume", True, TEXT_WHITE)
        self.screen.blit(volume_title, (SCREEN_WIDTH//2 - 250, 320))
        
        slider_x = SCREEN_WIDTH//2 - 250
        slider_y = 370
        slider_width = 500
        slider_height = 10
        
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        (slider_x, slider_y, slider_width, slider_height), border_radius=5)
        
        fill_width = slider_width * self.sound_manager.volume
        pygame.draw.rect(self.screen, PRIMARY, 
                        (slider_x, slider_y, fill_width, slider_height), border_radius=5)
        
        # Volume percentage
        vol_text = text_font.render(f"{int(self.sound_manager.volume * 100)}%", True, TEXT_GRAY)
        self.screen.blit(vol_text, (SCREEN_WIDTH//2 - vol_text.get_width()//2, 390))
        
        # Reset stats button
        reset_btn = Button(SCREEN_WIDTH//2 - 150, 480, 300, 60, "RESET STATISTICS", 
                          DANGER, (255, 90, 90), "⚠")
        reset_btn.update(pygame.mouse.get_pos(), 0)
        reset_btn.draw(self.screen)
        self.reset_stats_btn = reset_btn

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
        
        if self.difficulty == Difficulty.EASY:
            return random.choice(empty_cells)
        
        elif self.difficulty == Difficulty.MEDIUM:
            # 50% chance of optimal move
            if random.random() < 0.5:
                return random.choice(empty_cells)
            # Fall through to hard difficulty logic
        
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
            self.animations[f"{row},{col}"] = 0
            self.sound_manager.play("move")
            
            # Create particles
            board_size = CELL_SIZE * 3
            board_x = (SCREEN_WIDTH - board_size) // 2
            board_y = 200
            x = board_x + col * CELL_SIZE + CELL_SIZE // 2
            y = board_y + row * CELL_SIZE + CELL_SIZE // 2
            color = X_COLOR if self.current_player == Player.X else O_COLOR
            
            for _ in range(15):
                self.particles.append(Particle(x, y, color))
            
            # Check winner
            winner = self.check_winner()
            if winner:
                self.winner = winner
                self.game_over = True
                self.update_stats(winner)
                self.sound_manager.play("win" if winner == Player.X else "lose")
                
                # Victory particles
                for _ in range(50):
                    self.particles.append(Particle(x, y, color))
            elif self.is_board_full():
                self.game_over = True
                self.update_stats(None)
                self.sound_manager.play("draw")
            else:
                self.current_player = Player.O if self.current_player == Player.X else Player.X
            
            return True
        return False

    def update_stats(self, winner):
        if self.game_mode == "pvp":
            self.stats["pvp"]["total_games"] += 1
            if winner == Player.X:
                self.stats["pvp"]["x_wins"] += 1
            elif winner == Player.O:
                self.stats["pvp"]["o_wins"] += 1
            else:
                self.stats["pvp"]["draws"] += 1
        else:
            self.stats["pvc"]["total_games"] += 1
            if winner == Player.X:
                self.stats["pvc"]["player_wins"] += 1
            elif winner == Player.O:
                self.stats["pvc"]["ai_wins"] += 1
            else:
                self.stats["pvc"]["draws"] += 1
            
            diff_key = self.difficulty.name.lower()
            self.stats["pvc"][diff_key] += 1
        
        self.save_stats()

    def reset_game(self):
        self.board = [[Player.EMPTY for _ in range(3)] for _ in range(3)]
        self.current_player = Player.X
        self.winner = None
        self.winning_line = None
        self.game_over = False
        self.animations = {}
        self.particles = []

    def handle_board_click(self, pos):
        board_size = CELL_SIZE * 3
        board_x = (SCREEN_WIDTH - board_size) // 2
        board_y = 200
        
        x, y = pos
        if (board_x <= x < board_x + board_size and 
            board_y <= y < board_y + board_size):
            
            col = (x - board_x) // CELL_SIZE
            row = (y - board_y) // CELL_SIZE
            
            if self.current_player == Player.X:
                if self.make_move(row, col):
                    if self.game_mode == "pvc" and not self.game_over:
                        # AI move after short delay
                        pygame.time.wait(300)
                        ai_row, ai_col = self.get_ai_move()
                        self.make_move(ai_row, ai_col)

    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.state == GameState.MAIN_MENU:
                            if self.play_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.MODE_SELECT
                            elif self.stats_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.STATS
                            elif self.settings_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.SETTINGS
                            elif self.quit_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                running = False
                        
                        elif self.state == GameState.MODE_SELECT:
                            if self.back_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.MAIN_MENU
                            elif self.pvp_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.game_mode = "pvp"
                                self.reset_game()
                                self.state = GameState.PLAYING
                            elif self.pvc_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.game_mode = "pvc"
                                self.state = GameState.DIFFICULTY_SELECT
                        
                        elif self.state == GameState.DIFFICULTY_SELECT:
                            if self.back_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.MODE_SELECT
                            elif self.easy_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.difficulty = Difficulty.EASY
                                self.reset_game()
                                self.state = GameState.PLAYING
                            elif self.medium_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.difficulty = Difficulty.MEDIUM
                                self.reset_game()
                                self.state = GameState.PLAYING
                            elif self.hard_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.difficulty = Difficulty.HARD
                                self.reset_game()
                                self.state = GameState.PLAYING
                            elif self.impossible_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.difficulty = Difficulty.IMPOSSIBLE
                                self.reset_game()
                                self.state = GameState.PLAYING
                        
                        elif self.state == GameState.PLAYING:
                            if self.menu_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.MAIN_MENU
                            elif self.restart_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.reset_game()
                            elif self.game_over:
                                if hasattr(self, 'play_again_btn') and self.play_again_btn.is_clicked(mouse_pos):
                                    self.sound_manager.play("click")
                                    self.reset_game()
                                elif hasattr(self, 'menu_btn_overlay') and self.menu_btn_overlay.is_clicked(mouse_pos):
                                    self.sound_manager.play("click")
                                    self.state = GameState.MAIN_MENU
                            else:
                                self.handle_board_click(mouse_pos)
                        
                        elif self.state == GameState.STATS:
                            if self.back_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.MAIN_MENU
                        
                        elif self.state == GameState.SETTINGS:
                            if self.back_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.state = GameState.MAIN_MENU
                            elif hasattr(self, 'sound_toggle_btn') and self.sound_toggle_btn.is_clicked(mouse_pos):
                                self.sound_manager.toggle()
                                self.sound_manager.play("click")
                            elif hasattr(self, 'reset_stats_btn') and self.reset_stats_btn.is_clicked(mouse_pos):
                                self.sound_manager.play("click")
                                self.stats = {
                                    "pvp": {"x_wins": 0, "o_wins": 0, "draws": 0, "total_games": 0},
                                    "pvc": {"player_wins": 0, "ai_wins": 0, "draws": 0, "total_games": 0,
                                           "easy": 0, "medium": 0, "hard": 0, "impossible": 0}
                                }
                                self.save_stats()
            
            # Update animations
            if self.state == GameState.MAIN_MENU:
                hover = self.play_btn.update(mouse_pos, dt)
                if hover: self.sound_manager.play("hover")
                hover = self.stats_btn.update(mouse_pos, dt)
                if hover: self.sound_manager.play("hover")
                hover = self.settings_btn.update(mouse_pos, dt)
                if hover: self.sound_manager.play("hover")
                hover = self.quit_btn.update(mouse_pos, dt)
                if hover: self.sound_manager.play("hover")
            
            elif self.state == GameState.MODE_SELECT:
                self.back_btn.update(mouse_pos, dt)
                self.pvp_btn.update(mouse_pos, dt)
                self.pvc_btn.update(mouse_pos, dt)
            
            elif self.state == GameState.DIFFICULTY_SELECT:
                self.back_btn.update(mouse_pos, dt)
                self.easy_btn.update(mouse_pos, dt)
                self.medium_btn.update(mouse_pos, dt)
                self.hard_btn.update(mouse_pos, dt)
                self.impossible_btn.update(mouse_pos, dt)
            
            elif self.state == GameState.PLAYING:
                self.menu_btn.update(mouse_pos, dt)
                self.restart_btn.update(mouse_pos, dt)
            
            elif self.state == GameState.STATS:
                self.back_btn.update(mouse_pos, dt)
            
            elif self.state == GameState.SETTINGS:
                self.back_btn.update(mouse_pos, dt)
            
            # Draw
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.MODE_SELECT:
                self.draw_mode_select()
            elif self.state == GameState.DIFFICULTY_SELECT:
                self.draw_difficulty_select()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.STATS:
                self.draw_stats()
            elif self.state == GameState.SETTINGS:
                self.draw_settings()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# Main execution
if __name__ == "__main__":
    game = TicTacToe()
    game.run()
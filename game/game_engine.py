import random
import pygame
from game.button import ChoiceButton


class GameEngine:

  def __init__(self, width, height, target_score=3):
    self.width = width
    self.height = height
    self.target_score = target_score

    self.choices = ["ROCK", "PAPER", "SCISSORS"]
    btn_w, btn_h = 130, 50
    gap = 20
    total_w = 3 * btn_w + 2 * gap
    start_x = (width - total_w) // 2
    btn_y = height - 85

    self.buttons = [
        ChoiceButton(
            "ROCK",
            pygame.Rect(start_x, btn_y, btn_w, btn_h),
            (160, 50, 50),
            (200, 70, 70),
        ),
        ChoiceButton(
            "PAPER",
            pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h),
            (40, 100, 170),
            (60, 130, 210),
        ),
        ChoiceButton(
            "SCISSORS",
            pygame.Rect(start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h),
            (180, 140, 30),
            (220, 180, 50),
        ),
    ]

    self.player_choice = None
    self.cpu_choice = None
    self.result_text = "Make your move!"
    self.result_color = (220, 225, 235)

    self.player_score = 0
    self.cpu_score = 0

    self.round_resolved_time = 0
    self.display_duration = 1800
    self.showing_result = False

    # Match state variables
    self.match_over = False
    self.match_winner = None

    # Adaptive AI tracking
    self.player_history = []
    self.player_move_counts = {"ROCK": 0, "PAPER": 0, "SCISSORS": 0}

    # Moves mapped to their direct counter
    self.counters = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}

    self.font_title = pygame.font.SysFont(None, 36)
    self.font_hud = pygame.font.SysFont(None, 26)
    self.font_arena = pygame.font.SysFont(None, 32)
    self.font_banner = pygame.font.SysFont(None, 48)

  def reset_match(self):
    """Resets scores, match state, and AI tracking memory."""
    self.player_score = 0
    self.cpu_score = 0
    self.player_choice = None
    self.cpu_choice = None
    self.result_text = "Make your move!"
    self.result_color = (220, 225, 235)
    self.showing_result = False
    self.match_over = False
    self.match_winner = None

    # Reset adaptive AI state
    self.player_history.clear()
    self.player_move_counts = {"ROCK": 0, "PAPER": 0, "SCISSORS": 0}

  def get_adaptive_cpu_choice(self):
    """Generates CPU choice biased toward countering player tendency."""
    total_moves = len(self.player_history)

    # Pick purely randomly for early moves (under 2 rounds)
    if total_moves < 2:
      return random.choice(self.choices)

    # Base probability weights for [ROCK, PAPER, SCISSORS]
    weights = [1.0, 1.0, 1.0]

    # Adjust CPU weights based on player choice frequencies
    for i, choice in enumerate(self.choices):
      # Frequency of player picking this choice
      player_freq = self.player_move_counts[choice] / total_moves

      # Find which CPU move counters this player choice
      counter_move = self.counters[choice]
      counter_index = self.choices.index(counter_move)

      # Increase weight of counter-move proportionally to player choice bias
      weights[counter_index] += player_freq * 3.0

    return random.choices(self.choices, weights=weights, k=1)[0]

  def determine_winner(self, player, cpu):
    if player == cpu:
      return "TIE"

    winning_moves = {"ROCK": "SCISSORS", "PAPER": "ROCK", "SCISSORS": "PAPER"}

    if winning_moves.get(player) == cpu:
      return "PLAYER"
    return "CPU"

  def play_round(self, choice):
    if self.match_over:
      return

    self.player_choice = choice

    # Get CPU selection from adaptive tracking module
    self.cpu_choice = self.get_adaptive_cpu_choice()

    # Record player move into AI memory
    self.player_history.append(choice)
    self.player_move_counts[choice] += 1

    outcome = self.determine_winner(self.player_choice, self.cpu_choice)
    if outcome == "PLAYER":
      self.player_score += 1
      self.result_text = (
          f"You Win! {self.player_choice} beats {self.cpu_choice}."
      )
      self.result_color = (80, 230, 120)
    elif outcome == "CPU":
      self.cpu_score += 1
      self.result_text = (
          f"You Lose! {self.cpu_choice} beats {self.player_choice}."
      )
      self.result_color = (240, 80, 80)
    else:
      self.result_text = f"It's a Draw! Both picked {self.player_choice}."
      self.result_color = (240, 210, 80)

    # Check match conclusion
    if self.player_score >= self.target_score:
      self.match_over = True
      self.match_winner = "PLAYER"
    elif self.cpu_score >= self.target_score:
      self.match_over = True
      self.match_winner = "CPU"
    else:
      self.showing_result = True
      self.round_resolved_time = pygame.time.get_ticks()

  def handle_event(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key in (pygame.K_r, pygame.K_SPACE) and self.match_over:
        self.reset_match()
        return

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      if self.showing_result or self.match_over:
        return

      for btn in self.buttons:
        if btn.contains(event.pos):
          self.play_round(btn.choice_name)
          break

  def update(self):
    if self.match_over:
      return

    now = pygame.time.get_ticks()
    if self.showing_result and (
        now - self.round_resolved_time >= self.display_duration
    ):
      self.player_choice = None
      self.cpu_choice = None
      self.result_text = "Make your move!"
      self.result_color = (190, 195, 205)
      self.showing_result = False

  def render(self, screen):
    screen.fill((24, 28, 36))

    # Header / Title
    title_surf = self.font_title.render(
        f"Rock Paper Scissors (First to {self.target_score})",
        True,
        (245, 245, 245),
    )
    screen.blit(
        title_surf, (self.width // 2 - title_surf.get_width() // 2, 14)
    )

    # HUD / Scores
    p_surf = self.font_hud.render(
        f"Player Score: {self.player_score}", True, (100, 180, 255)
    )
    c_surf = self.font_hud.render(
        f"CPU Score: {self.cpu_score}", True, (255, 120, 120)
    )
    screen.blit(p_surf, (35, 52))
    screen.blit(c_surf, (self.width - c_surf.get_width() - 35, 52))

    pygame.draw.line(
        screen, (45, 52, 66), (25, 82), (self.width - 25, 82), 2
    )

    # Arena status
    p_str = self.player_choice if self.player_choice else "--"
    c_str = self.cpu_choice if self.cpu_choice else "--"

    arena_p = self.font_arena.render(
        f"Your Pick:  {p_str}", True, (225, 225, 230)
    )
    arena_c = self.font_arena.render(
        f"CPU Pick:  {c_str}", True, (225, 225, 230)
    )
    screen.blit(arena_p, (self.width // 2 - arena_p.get_width() // 2, 115))
    screen.blit(arena_c, (self.width // 2 - arena_c.get_width() // 2, 155))

    res_surf = self.font_arena.render(
        self.result_text, True, self.result_color
    )
    screen.blit(res_surf, (self.width // 2 - res_surf.get_width() // 2, 205))

    # Buttons
    mouse_pos = pygame.mouse.get_pos()
    for btn in self.buttons:
      if hasattr(btn, "update"):
        btn.update(
            mouse_pos, disabled=(self.showing_result or self.match_over)
        )
      btn.render(screen)

    # Match Victory Overlay
    if self.match_over:
      overlay = pygame.Surface((self.width - 80, 160), pygame.SRCALPHA)
      overlay.fill((15, 18, 24, 230))
      screen.blit(overlay, (40, 100))

      if self.match_winner == "PLAYER":
        banner_txt = "MATCH VICTORY!"
        color = (80, 235, 120)
      else:
        banner_txt = "MATCH DEFEAT!"
        color = (240, 80, 80)

      banner_surf = self.font_banner.render(banner_txt, True, color)
      sub_surf = self.font_hud.render(
          "Press [SPACE] or [R] to Play Again", True, (210, 215, 225)
      )

      screen.blit(
          banner_surf, (self.width // 2 - banner_surf.get_width() // 2, 125)
      )
      screen.blit(
          sub_surf, (self.width // 2 - sub_surf.get_width() // 2, 185)
      )
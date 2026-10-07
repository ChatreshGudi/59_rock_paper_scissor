import math
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
    self.display_duration = 2000
    self.showing_result = False

    # Match state variables
    self.match_over = False
    self.match_winner = None

    # Reveal animation state variables
    self.animating_reveal = False
    self.reveal_start_time = 0
    self.reveal_duration = 1500  # Total animation duration before reveal
    self.pending_player_choice = None
    self.pending_cpu_choice = None
    self.countdown_text = ""

    # Adaptive AI tracking
    self.player_history = []
    self.player_move_counts = {"ROCK": 0, "PAPER": 0, "SCISSORS": 0}
    self.counters = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}

    self.font_title = pygame.font.SysFont(None, 36)
    self.font_hud = pygame.font.SysFont(None, 26)
    self.font_arena = pygame.font.SysFont(None, 30)
    self.font_banner = pygame.font.SysFont(None, 48)
    self.font_count = pygame.font.SysFont(None, 44)

  def reset_match(self):
    """Resets scores, match state, and AI tracking memory."""
    self.player_score = 0
    self.cpu_score = 0
    self.player_choice = None
    self.cpu_choice = None
    self.result_text = "Make your move!"
    self.result_color = (220, 225, 235)
    self.showing_result = False
    self.animating_reveal = False
    self.match_over = False
    self.match_winner = None

    self.player_history.clear()
    self.player_move_counts = {"ROCK": 0, "PAPER": 0, "SCISSORS": 0}

  def get_adaptive_cpu_choice(self):
    total_moves = len(self.player_history)
    if total_moves < 2:
      return random.choice(self.choices)

    weights = [1.0, 1.0, 1.0]
    for i, choice in enumerate(self.choices):
      player_freq = self.player_move_counts[choice] / total_moves
      counter_move = self.counters[choice]
      counter_index = self.choices.index(counter_move)
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
    if self.match_over or self.animating_reveal or self.showing_result:
      return

    # Store choices for deferred reveal post-animation
    self.pending_player_choice = choice
    self.pending_cpu_choice = self.get_adaptive_cpu_choice()

    self.player_choice = None
    self.cpu_choice = None

    self.player_history.append(choice)
    self.player_move_counts[choice] += 1

    # Start reveal animation sequence
    self.animating_reveal = True
    self.reveal_start_time = pygame.time.get_ticks()

  def finalize_round(self):
    """Evaluates and presents results after shaking animation ends."""
    self.player_choice = self.pending_player_choice
    self.cpu_choice = self.pending_cpu_choice
    self.animating_reveal = False

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
      if self.showing_result or self.match_over or self.animating_reveal:
        return

      for btn in self.buttons:
        if btn.contains(event.pos):
          self.play_round(btn.choice_name)
          break

  def update(self):
    now = pygame.time.get_ticks()

    # Progress reveal animation steps
    if self.animating_reveal:
      elapsed = now - self.reveal_start_time
      if elapsed < 400:
        self.countdown_text = "ROCK..."
      elif elapsed < 800:
        self.countdown_text = "PAPER..."
      elif elapsed < 1200:
        self.countdown_text = "SCISSORS..."
      elif elapsed < self.reveal_duration:
        self.countdown_text = "SHOOT!"
      else:
        self.finalize_round()
      return

    # Handle post-round result display reset
    if self.showing_result and (
        now - self.round_resolved_time >= self.display_duration
    ):
      self.player_choice = None
      self.cpu_choice = None
      self.result_text = "Make your move!"
      self.result_color = (190, 195, 205)
      self.showing_result = False

  def draw_gesture_icon(self, surface, choice, center, size=40, color=(220, 220, 230)):
    """Procedural vector graphics renderer for Rock, Paper, and Scissors icons."""
    cx, cy = center
    hs = size // 2

    if choice == "ROCK":
      # Circle stone emblem with faceted geometry
      pygame.draw.circle(surface, color, (cx, cy), hs, width=3)
      pygame.draw.circle(surface, (140, 60, 60), (cx, cy), hs - 4)
      pts = [
          (cx - 10, cy - 8),
          (cx + 8, cy - 12),
          (cx + 14, cy + 4),
          (cx + 2, cy + 12),
          (cx - 12, cy + 6),
      ]
      pygame.draw.polygon(surface, color, pts, width=2)

    elif choice == "PAPER":
      # Sheet document icon with corner fold
      rect = pygame.Rect(cx - hs + 4, cy - hs, size - 8, size)
      pygame.draw.rect(surface, (50, 120, 190), rect, border_radius=4)
      pygame.draw.rect(surface, color, rect, width=2, border_radius=4)
      # Lines representing text on paper
      pygame.draw.line(
          surface, color, (cx - 8, cy - 6), (cx + 8, cy - 6), 2
      )
      pygame.draw.line(
          surface, color, (cx - 8, cy), (cx + 8, cy), 2
      )
      pygame.draw.line(
          surface, color, (cx - 8, cy + 6), (cx + 4, cy + 6), 2
      )

    elif choice == "SCISSORS":
      # Scissors blades with handle rings
      pygame.draw.circle(surface, color, (cx - 10, cy + 12), 7, width=2)
      pygame.draw.circle(surface, color, (cx + 10, cy + 12), 7, width=2)
      pygame.draw.line(
          surface, color, (cx - 7, cy + 6), (cx + 10, cy - 12), 3
      )
      pygame.draw.line(
          surface, color, (cx + 7, cy + 6), (cx - 10, cy - 12), 3
      )
      pygame.draw.circle(surface, (220, 180, 50), (cx, cy - 1), 3)

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

    # Arena Positions
    p_center_x = self.width // 4 + 20
    c_center_x = (3 * self.width) // 4 - 20
    arena_y = 145

    # Compute shaking vertical offset during reveal countdown
    shake_y = 0
    if self.animating_reveal:
      shake_y = int(math.sin(pygame.time.get_ticks() * 0.03) * 12)

    # Render Player Icon & Label
    if self.animating_reveal:
      self.draw_gesture_icon(
          screen, "ROCK", (p_center_x, arena_y + shake_y), size=44
      )
    elif self.player_choice:
      self.draw_gesture_icon(
          screen, self.player_choice, (p_center_x, arena_y), size=44
      )

    p_str = self.player_choice if self.player_choice else "--"
    p_lbl = self.font_arena.render(f"You: {p_str}", True, (225, 225, 230))
    screen.blit(p_lbl, (p_center_x - p_lbl.get_width() // 2, arena_y + 32))

    # Render CPU Icon & Label
    if self.animating_reveal:
      self.draw_gesture_icon(
          screen, "ROCK", (c_center_x, arena_y + shake_y), size=44
      )
    elif self.cpu_choice:
      self.draw_gesture_icon(
          screen, self.cpu_choice, (c_center_x, arena_y), size=44
      )

    c_str = self.cpu_choice if self.cpu_choice else "--"
    c_lbl = self.font_arena.render(f"CPU: {c_str}", True, (225, 225, 230))
    screen.blit(c_lbl, (c_center_x - c_lbl.get_width() // 2, arena_y + 32))

    # Result / Countdown Banner
    if self.animating_reveal:
      res_surf = self.font_count.render(
          self.countdown_text, True, (240, 210, 80)
      )
    else:
      res_surf = self.font_arena.render(
          self.result_text, True, self.result_color
      )
    screen.blit(res_surf, (self.width // 2 - res_surf.get_width() // 2, 212))

    # Render Action Buttons
    mouse_pos = pygame.mouse.get_pos()
    is_disabled = (
        self.showing_result or self.match_over or self.animating_reveal
    )
    for btn in self.buttons:
      if hasattr(btn, "update"):
        btn.update(mouse_pos, disabled=is_disabled)
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
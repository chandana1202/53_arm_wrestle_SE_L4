import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35

        # AI stamina cycle
        self.AI_NORMAL_DURATION = 4.0
        self.AI_SURGE_DURATION = 1.5
        self.AI_COOLDOWN_DURATION = 3.0

        self.AI_NORMAL_MULTIPLIER = 1.0
        self.AI_SURGE_MULTIPLIER = 3.0
        self.AI_COOLDOWN_MULTIPLIER = 0.25

        self.ai_state = "NORMAL"
        self.ai_state_timer = self.AI_NORMAL_DURATION
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

        
    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.stamina <= 10:
                return
                
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT: 
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT: 
                    self.arm_position += 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_RIGHT



    def update(self):
        if self.game_state != "PLAYING":
            return

        # Update AI stamina state timer
        self.ai_state_timer -= 1 / 60.0

        if self.ai_state_timer <= 0:
            if self.ai_state == "NORMAL":
                self.ai_state = "SURGE"
                self.ai_state_timer = self.AI_SURGE_DURATION

            elif self.ai_state == "SURGE":
                self.ai_state = "COOLDOWN"
                self.ai_state_timer = self.AI_COOLDOWN_DURATION

            else:
                self.ai_state = "NORMAL"
                self.ai_state_timer = self.AI_NORMAL_DURATION

        # Select AI force based on current stamina state
        if self.ai_state == "SURGE":
            force_multiplier = self.AI_SURGE_MULTIPLIER
        elif self.ai_state == "COOLDOWN":
            force_multiplier = self.AI_COOLDOWN_MULTIPLIER
        else:
            force_multiplier = self.AI_NORMAL_MULTIPLIER

        ai_variance = random.uniform(0.3, 1.0)
        self.arm_position += (
            self.ai_strength
            * ai_variance
            * force_multiplier
        )

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + 0.8)

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"


    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        self.ai_state = "NORMAL"
        self.ai_state_timer = self.AI_NORMAL_DURATION

    def render(self, screen):
        screen.fill((30, 30, 30))

        # Draw center line
        pygame.draw.line(
            screen,
            (100, 100, 100),
            (self.width // 2, 100),
            (self.width // 2, 400),
            3
        )

        # Draw table
        pygame.draw.rect(
            screen,
            (120, 80, 40),
            (100, 350, self.width - 200, 100)
        )

        # Calculate arm position
        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)

        # Draw arm
        pygame.draw.line(
            screen,
            (220, 180, 140),
            (self.width // 2, 200),
            (hand_x, 200),
            15
        )

        # Draw hand
        pygame.draw.circle(
            screen,
            (240, 200, 160),
            (hand_x, 200),
            25
        )

        # Draw stamina bar
        stamina_width = 200
        stamina_height = 20
        stamina_x = 40
        stamina_y = 40

        pygame.draw.rect(
            screen,
            (80, 80, 80),
            (stamina_x, stamina_y, stamina_width, stamina_height)
        )

        pygame.draw.rect(
            screen,
            (50, 200, 50),
            (
                stamina_x,
                stamina_y,
                int(stamina_width * (self.stamina / self.max_stamina)),
                stamina_height
            )
        )

        # Stamina text
        stamina_text = self.font_med.render(
            f"Stamina: {int(self.stamina)}",
            True,
            (255, 255, 255)
        )
        screen.blit(
            stamina_text,
            (40, 70)
        )

        # AI SURGE warning — flashes while AI is in SURGE state
        if self.ai_state == "SURGE":
            if int(pygame.time.get_ticks() / 250) % 2 == 0:
                surge_surf = self.font_big.render(
                    "AI SURGE!",
                    True,
                    (255, 70, 70)
                )
                screen.blit(
                    surge_surf,
                    (
                        self.width // 2 - surge_surf.get_width() // 2,
                        65
                    )
                )

        # Player exhaustion indicator
        if self.stamina < 10:
            exhausted_surf = self.font_med.render(
                "EXHAUSTED!",
                True,
                (255, 80, 80)
            )
            screen.blit(
                exhausted_surf,
                (40, 480)
            )

        # Winner / game over message
        if self.game_state == "GAME_OVER":
            winner_text = self.font_big.render(
                f"{self.winner} WINS!",
                True,
                (255, 255, 255)
            )
            screen.blit(
                winner_text,
                (
                    self.width // 2 - winner_text.get_width() // 2,
                    500
                )
            )
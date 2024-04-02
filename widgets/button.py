import pygame
import pygame.mouse

pygame.init()

WHITE = (255, 255, 255)


class Button:
    def __init__(self, text, x, y, font_size=36):
        self.font = pygame.font.Font(pygame.font.get_default_font(), font_size)

        # Place the text field
        self.text = self.font.render(text, True, WHITE)
        self.x, self.y = x, y

        # Create rect and update its position to track the text
        self.rect = self.text.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

        # Cooldown
        self.last_clicked_time = 0

    def blit(self, window):
        window.blit(self.text, (self.x, self.y))

    def hovering(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_pressed(self):
        pressed = self.hovering() and pygame.mouse.get_pressed()[0]
        if pressed:
            return True
        return False

    def update_text(self, new_text):
        self.text = self.font.render(new_text, True, WHITE)
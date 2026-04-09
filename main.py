# main.py
import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE
from src.core.game import Game


def main():
    pygame.init()
    # Start in fullscreen mode - press F11 to toggle windowed mode
    fullscreen = True
    # Use SCALED to automatically fill screen while maintaining aspect ratio
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game = Game(screen)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # F11 to toggle fullscreen
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    game.screen = screen  # Update game's screen reference
                    print(f"Fullscreen: {'ON' if fullscreen else 'OFF'}")
                # Handle pause menu input when active
                elif game.pause_menu.active:
                    action = game.pause_menu.handle_input(event)
                    if action == "RESUME":
                        game.pause_menu.toggle()  # Close pause menu
                    elif action == "RESTART LEVEL":
                        game.pause_menu.toggle()  # Close pause menu
                        # Restart current level
                        if game.current_level > 0:
                            game.load_level(game.current_level)
                    elif action == "QUIT TO MENU":
                        game = Game(screen)  # Restart game (goes to intro)
                    elif action == "QUIT" or action == "QUIT GAME":
                        running = False  # Quit the game entirely
                    elif action and action[0] == "music_volume":
                        game.audio.set_music_volume(action[1])
                    elif action and action[0] == "sfx_volume":
                        game.audio.set_sfx_volume(action[1])
                # Handle level select menu input when active
                elif game.level_select.active:
                    selected = game.level_select.handle_input(event)
                    if selected is not None:
                        # Jump to selected level
                        game.jump_to_level(selected)
                # Handle intro screen - any key to start
                elif game.state == "intro":
                    game.state = "tutorial"
                    game.in_tutorial = True
                    print("Starting tutorial...")
                # Handle architect mode input
                elif game.state == "architect":
                    if event.key == pygame.K_SPACE:
                        # Shoot purple orb at mouse position
                        mouse_pos = pygame.mouse.get_pos()
                        game.architect_mode.shoot_orb(mouse_pos)
                    elif event.key == pygame.K_ESCAPE:
                        # Exit architect mode back to main menu
                        game = Game(screen)  # Restart game
                # Handle endgame choice input
                elif game.state == "endgame" and hasattr(game, 'end_sequence'):
                    if game.end_sequence.phase == "choice":
                        if event.key == pygame.K_1 or event.key == pygame.K_2:
                            game.end_sequence.handle_choice_input(event.key)
                    elif game.end_sequence.phase == "credits":
                        # Any key to reboot after credits
                        if game.end_sequence.credits_scroll < -len(game.end_sequence.credits_lines) * 60:
                            game = Game(screen)  # Restart game
                # SECRET: K key to open level select during tutorial
                elif event.key == pygame.K_k and game.state == "tutorial":
                    game.level_select.toggle()
                # Handle restart
                elif event.key == pygame.K_r and (game.state == "game_over" or game.state == "victory"):
                    old_game = game
                    game = Game(screen)  # Restart game
                    # If died, allow tutorial skip this session
                    if old_game.state == "game_over":
                        game.died_this_session = True
                elif event.key == pygame.K_c and game.state == "victory":
                    # Start chaos mode (only unlocked after beating the final boss)
                    game = Game(screen)
                    game.start_chaos_mode()
                elif event.key == pygame.K_ESCAPE:
                    # Toggle pause menu (only in playing state)
                    if game.state in ["playing", "tutorial", "chaos"]:
                        game.pause_menu.toggle()
                    else:
                        running = False  # Quit from other states
                elif event.key == pygame.K_RETURN and game.state == "tutorial" and not game.level_select.active:
                    # Allow skip at any time
                    game.skip_tutorial()  # Skip tutorial

        # Handle architect mode continuous input (WASD movement)
        if game.state == "architect":
            keys = pygame.key.get_pressed()
            game.architect_mode.handle_input(keys)

        game.update(dt)
        game.draw(dt)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

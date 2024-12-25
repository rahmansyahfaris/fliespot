import pygame  # Import the pygame library

# keybindings and configs
common_var = {}
common_var['keybinds'] = {
    "forward": "w",
    "backward": "s",
    "left": "a",
    "right": "d",
    "turn_left": "q",
    "turn_right": "e",
    "up": "space",
    "down": "left shift",
    "alarm": "t"
}
common_var['config'] = {
    "manual_height": 1,
    "manual_velocity": 0.2,
    "manual_yaw_rate": 15
}

def crazy_manual_flight(common_var):
    # Initialize all pygame modules
    pygame.init()

    screen = pygame.display.set_mode((400, 350)) # window size
    pygame.display.set_caption("Drone Manual Control") # window title
    running = True # running flag
    font = pygame.font.SysFont("Arial", 13) # font setup
    keypressed = "none" # initial keypressed
    movement_status = "hold"

    # Function to render multi-line text
    def render_multiline_text(lines, font, color, x, y, line_spacing):
        """Render multiple lines of text."""
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (x, y + i * line_spacing))


    # Main loop
    while running:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the user clicks the close button
                running = False  # Exit the main loop
            elif event.type == pygame.KEYDOWN:  # Detect when a key is pressed
                # print(f"Key pressed: {pygame.key.name(event.key)}")
                keypressed = pygame.key.name(event.key)  # Update the keypressed variable
                # finding the type of movement from the key pressed
                movement_status = next((movement_status for movement_status, value in common_var["keybinds"].items() if value == keypressed), "hold")
            elif event.type == pygame.KEYUP:  # Detect when a key is released
                # print(f"Key released: {pygame.key.name(event.key)}")
                keypressed = "none"  # Reset the keypressed variable when key is released
                movement_status = "hold"


        # Fill the window with a color (RGB: Red, Green, Blue)
        screen.fill((0, 0, 0))  # Black background

        # Text to display on the pygame screen window
        keybind_display = [f"STATUS",
                        f"",
                        f"key pressed: {keypressed}",
                        f"current movement: {movement_status}",
                        f"velocity: {common_var['config']['manual_velocity']}",
                        f"yaw rate: {common_var['config']['manual_yaw_rate']}",
                        f"",
                        f"CONTROLS",
                        f"",
                        f"forward: {common_var['keybinds']['forward']}",
                        f"backward: {common_var['keybinds']['backward']}",
                        f"left: {common_var['keybinds']['left']}",
                        f"right: {common_var['keybinds']['right']}",
                        f"turn_left: {common_var['keybinds']['turn_left']}",
                        f"turn_right: {common_var['keybinds']['turn_right']}",
                        f"up: {common_var['keybinds']['up']}",
                        f"down: {common_var['keybinds']['down']}",
                        f"alarm: {common_var['keybinds']['alarm']}",
                        ]

        # Render the text to display the current key pressed
        render_multiline_text(keybind_display, font, (255, 255, 255), 10, 10, 14)  # White text, starting at (10, 10), 3px spacing

        # Update the display to show the changes
        pygame.display.flip()

    # Quit pygame
    pygame.quit()

crazy_manual_flight(common_var)
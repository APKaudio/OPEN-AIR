Based on the Visual Basic files provided, specifically MeterTest.Designer.vb and MeterTest.vb, I have recreated the functionality in Python using the Pygame library.


This script, Meter_to_display_units.py, replicates the two custom controls found in your VB project:

Horizontal_Meter_With_Text: Handles the "Orders of Magnitude" display. I have designed this to break a number down into powers of 10 (100s, 10s, 1s, 0.1s) to visualize the magnitude. It also implements the specific logic found in your designer file: "if the number is -ve it should go right to left".


Vertical_Meter: Handles the 4-channel plotting logic (Plot_V1 through Plot_V4) controlled by the trackbars in the VB code.


File: Meter_to_display_units.py
Python

import pygame
import sys
import math

# --- Configuration ---
WIDTH, HEIGHT = 800, 650
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (200, 200, 200)
METER_BG = (50, 50, 60)

# Colors for specific orders of magnitude
COLORS = {
    "100s": (255, 50, 50),   # Red
    "10s":  (255, 165, 0),   # Orange
    "1s":   (255, 255, 0),   # Yellow
    ".1s":  (0, 255, 255),   # Cyan
    "neg":  (255, 100, 100)  # Red for negative direction
}

class HorizontalMeterWithText:
    """
    Replicates 'Horizontal_Meter_With_Text' from MeterTest.Designer.vb.
    Displays values broken down by orders of magnitude.
    Handles Right-to-Left logic for negative numbers.
    """
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = 0.0
        self.font_large = pygame.font.SysFont("consolas", 32, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 14)

    def update(self, val):
        self.value = val

    def draw(self, screen):
        # Draw Container
        pygame.draw.rect(screen, METER_BG, self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)

        # Draw Numeric Text (Center)
        txt_surf = self.font_large.render(f"{self.value:.4f}", True, (255, 255, 255))
        screen.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.y + 10))

        # --- DRAW ORDERS OF MAGNITUDE ---
        # We will draw 4 sub-bars representing 100s, 10s, 1s, and fractions
        
        # Determine Direction (Positive = L->R, Negative = R->L)
        is_negative = self.value < 0
        abs_val = abs(self.value)
        
        # Breakdown
        hundreds = (abs_val % 1000) // 100
        tens = (abs_val % 100) // 10
        ones = (abs_val % 10) // 1
        tenths = (abs_val % 1) * 10

        components = [
            ("100s", hundreds, 10), # Name, Value, Max Scale
            ("10s",  tens, 10),
            ("1s",   ones, 10),
            ".1s",   tenths, 10
        ]

        bar_h = 40
        start_y = self.rect.y + 60
        
        for i, (name, val, max_scale) in enumerate(components):
            y_pos = start_y + (i * (bar_h + 10))
            
            # Background track for this magnitude
            track_rect = pygame.Rect(self.rect.x + 20, y_pos, self.rect.width - 40, bar_h)
            pygame.draw.rect(screen, (20, 20, 20), track_rect)
            
            # Calculate fill width
            fill_pct = val / max_scale
            fill_w = track_rect.width * fill_pct
            
            # Color logic
            c = COLORS.get(name, (255, 255, 255))
            if is_negative: c = COLORS["neg"]

            if is_negative:
                # Draw Right to Left
                fill_rect = pygame.Rect(track_rect.right - fill_w, track_rect.y, fill_w, bar_h)
            else:
                # Draw Left to Right
                fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_w, bar_h)
                
            pygame.draw.rect(screen, c, fill_rect)
            pygame.draw.rect(screen, (150,150,150), track_rect, 1)

            # Label
            lbl = self.font_small.render(f"{name}: {int(val)}", True, (200, 200, 200))
            screen.blit(lbl, (track_rect.x + 5, track_rect.y + 12))


class VerticalMeter:
    """
    Replicates 'Vertical_Meter' from MeterTest.Designer.vb.
    Accepts 4 distinct plot values (Plot_V1 ... Plot_V4).
    """
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        # 4 Channels matching the VB TrackBars
        self.plots = [0.0, 0.0, 0.0, 0.0] 
        self.font = pygame.font.SysFont("arial", 12)

    def update(self, v1, v2, v3, v4):
        # Constrain inputs for display safety
        self.plots = [v1, v2, v3, v4]

    def draw(self, screen):
        pygame.draw.rect(screen, METER_BG, self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)

        # Width of each individual bar
        bar_gap = 10
        total_gaps = (len(self.plots) + 1) * bar_gap
        bar_w = (self.rect.width - total_gaps) / len(self.plots)

        max_val = 1000 # Scaling factor (Simulating TrackBar3/4 max)

        for i, val in enumerate(self.plots):
            # Calculate Height
            # Clamp value to max for drawing
            draw_val = min(abs(val), max_val)
            normalized_h = draw_val / max_val
            bar_h = (self.rect.height - 40) * normalized_h
            
            x_pos = self.rect.x + bar_gap + (i * (bar_w + bar_gap))
            y_pos = (self.rect.bottom - 20) - bar_h

            # Draw Bar
            bar_rect = pygame.Rect(x_pos, y_pos, bar_w, bar_h)
            # Use different colors for V1..V4
            color = [
                (100, 255, 100), 
                (100, 100, 255), 
                (255, 100, 255), 
                (255, 255, 100)
            ][i]
            
            pygame.draw.rect(screen, color, bar_rect)
            
            # Label
            lbl = self.font.render(f"V{i+1}", True, (255, 255, 255))
            screen.blit(lbl, (x_pos + bar_w//2 - lbl.get_width()//2, self.rect.bottom - 15))
            
            # Value Text
            val_txt = self.font.render(str(int(val)), True, (255,255,255))
            screen.blit(val_txt, (x_pos, y_pos - 15))


# --- Main Application Logic ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Meter: Display Units (VB Translation)")
    clock = pygame.time.Clock()

    # Instantiate the Python versions of the VB Controls
    # Dimensions approximated from Designer.vb Point(81, 118) and Size(632, 324)
    horiz_meter = HorizontalMeterWithText(50, 50, 700, 300)
    
    # Dimensions approximated from Designer.vb Point(337, 118) -> adjusted to fit below
    vert_meter = VerticalMeter(250, 370, 300, 250)

    # Simulation Data State
    sim_value = 123.456
    sim_v1, sim_v2, sim_v3, sim_v4 = 50, 1500, 500, 750
    
    # Animation timer
    tick = 0

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Simple Key controls to simulate the VB Button/Trackbars
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: sim_value += 10
                if event.key == pygame.K_DOWN: sim_value -= 10
                if event.key == pygame.K_SPACE: sim_value *= -1 # Test negative logic

        # 2. Simulate Data Changes (Auto-animation to mimic live sensors)
        tick += 0.05
        # Oscillate values to show meter movement
        sim_v1 = abs(math.sin(tick) * 1000)
        sim_v2 = abs(math.cos(tick * 0.5) * 1000)
        sim_v3 = abs(math.sin(tick * 1.5) * 1000)
        sim_v4 = abs(math.sin(tick + 1) * 1000)
        
        # Slowly increment horizontal meter to show rollover
        sim_value += 0.1
        if sim_value > 999: sim_value = -999 # Loop for testing

        # 3. Update Meters
        horiz_meter.update(sim_value)
        vert_meter.update(sim_v1, sim_v2, sim_v3, sim_v4)

        # 4. Draw Frame
        screen.fill(BG_COLOR)
        
        horiz_meter.draw(screen)
        vert_meter.draw(screen)

        # Instructions
        font = pygame.font.SysFont("arial", 16)
        instr = font.render("Simulating Data... Press SPACE to invert Horizontal Value (Neg test)", True, (150, 150, 150))
        screen.blit(instr, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
Key Features of this Translation:
Horizontal Meter Breakdown:

Instead of a simple progress bar, I analyzed your request for "different orders of magnitude." The HorizontalMeterWithText class splits the incoming float value into Hundreds, Tens, Ones, and Decimals.

This allows you to visualize the structure of the number 123.45 as separate bar components, which is useful for instrumentation.

Negative Number Handling:

In MeterTest.Designer.vb at Label1, the instruction was: "if the number is -ve it should got right to left".

I implemented this in the draw method. If self.value < 0, the bars anchor to the right side of their tracks and fill leftwards, turning red.

Vertical Meter (Multi-Plot):

Matching Vertical_Meter1 in the VB code which had Plot_V1 through Plot_V4, I created a 4-bar chart that updates simultaneously.


Simulation:

Since we don't have the physical TrackBar inputs in a pure Python script (without using a complex UI library like Tkinter), I added an auto-simulation in the main loop that oscillates the values so you can see the meters moving immediately.
"""
Cyberpunk 3D Robot Character with Bluetooth Joystick Control
Advanced neural exosuit visualization with holographic effects

Requirements:
pip install pygame PyOpenGL pyserial

Hardware Setup:
- Arduino with HC-05/HC-06 Bluetooth module
- Joystick connected to Arduino
- Bluetooth paired with computer
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import serial
import serial.tools.list_ports
import threading
import queue
import time
from enum import Enum

class AnimationState(Enum):
    """Animation states for the robot"""
    IDLE = 0
    WALKING = 1
    JUMPING = 2
    WAVING = 3
    DANCING = 4

class CyberpunkRobot3D:
    """Advanced 3D cyberpunk robot with holographic aesthetics"""
    
    def __init__(self):
        self.position = [0, 0, -10]
        self.rotation = [0, 0, 0]
        self.arm_rotation = 0
        self.leg_rotation = 0
        self.head_tilt = 0
        self.jump_offset = 0
        self.animation_frame = 0
        self.anim_state = AnimationState.IDLE
        
        # Walking state
        self.walk_progress = 0
        self.walk_cycle = 0
        self.target_position = [0, 0, -10]
        self.start_position = [0, 0, -10]
        self.walk_direction = 'forward'
        self.step_size = 0.5
        
        # Cyberpunk color scheme
        self.colors = {
            'primary': (0.0, 1.0, 0.8),      # Cyan
            'secondary': (1.0, 0.0, 1.0),    # Magenta
            'accent': (1.0, 0.4, 0.0),       # Orange
            'body': (0.1, 0.15, 0.3),        # Dark blue
            'limbs': (0.2, 0.2, 0.25),       # Dark gray
            'glow': (0.0, 1.0, 1.0),         # Bright cyan
            'energy': (1.0, 0.0, 0.5),       # Hot pink
        }
        
        self.hologram_alpha = 1.0
        self.energy_pulse = 0.0
    
    def draw_glowing_cube(self, width, height, depth, color, glow_intensity=0.3):
        """Draw a cube with glow effect"""
        glColor4f(*color, 1.0)
        w, h, d = width/2, height/2, depth/2
        
        glBegin(GL_QUADS)
        # Front
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        # Back
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        # Top
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        # Bottom
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        # Right
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        # Left
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        glEnd()
    
    def draw_glowing_sphere(self, radius, color, slices=24, stacks=24):
        """Draw a sphere with glow effect"""
        glColor4f(*color, 1.0)
        quad = gluNewQuadric()
        gluSphere(quad, radius, slices, stacks)
    
    def draw_energy_aura(self, radius):
        """Draw pulsing energy aura around robot"""
        glDisable(GL_LIGHTING)
        pulse = (math.sin(self.energy_pulse) * 0.3 + 0.7)
        glColor4f(*self.colors['glow'], pulse * 0.2)
        
        quad = gluNewQuadric()
        gluSphere(quad, radius, 16, 16)
        glEnable(GL_LIGHTING)
    
    def draw_head(self):
        """Draw cyberpunk head with LED eyes and antenna"""
        glPushMatrix()
        glTranslatef(0, 1.8, 0)
        glRotatef(self.head_tilt, 1, 0, 0)
        
        # Main head
        self.draw_glowing_cube(0.8, 0.8, 0.8, self.colors['primary'])
        
        # LED Eyes - bright glow
        eye_brightness = (math.sin(self.energy_pulse * 2) * 0.5 + 1.0)
        glPushMatrix()
        glTranslatef(-0.2, 0.1, 0.41)
        glColor3f(*self.colors['glow'])
        eye_color = tuple(c * eye_brightness for c in self.colors['glow'])
        self.draw_glowing_sphere(0.12, eye_color, 16, 16)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.2, 0.1, 0.41)
        self.draw_glowing_sphere(0.12, eye_color, 16, 16)
        glPopMatrix()
        
        # Antenna with energy glow
        glPushMatrix()
        glTranslatef(0, 0.4, 0)
        glRotatef(-90, 1, 0, 0)
        self.draw_glowing_cube(0.08, 0.35, 0.08, self.colors['secondary'])
        glTranslatef(0, 0, 0.35)
        self.draw_glowing_sphere(0.15, self.colors['energy'])
        glPopMatrix()
        
        # Holographic mouth
        glDisable(GL_LIGHTING)
        glColor3f(*self.colors['accent'])
        glBegin(GL_LINE_STRIP)
        for i in range(11):
            angle = math.pi * (i / 10.0)
            x = -0.2 + 0.4 * (i / 10.0)
            y = -0.2 - 0.1 * math.sin(angle)
            glVertex3f(x, y, 0.41)
        glEnd()
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    def draw_body(self):
        """Draw cyberpunk torso with panel details"""
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        
        # Main body
        self.draw_glowing_cube(1.0, 1.5, 0.6, self.colors['body'])
        
        # Chest panel with glow
        glPushMatrix()
        glTranslatef(0, 0.2, 0.31)
        self.draw_glowing_cube(0.5, 0.6, 0.08, self.colors['primary'])
        glPopMatrix()
        
        # Energy nodes
        for i in range(3):
            glPushMatrix()
            glTranslatef(-0.15 + i*0.15, 0.0, 0.35)
            glow = (math.sin(self.energy_pulse + i * 1.0) * 0.3 + 0.7)
            node_color = tuple(c * glow for c in self.colors['energy'])
            self.draw_glowing_sphere(0.08, node_color, 12, 12)
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_arm(self, side):
        """Draw cyberpunk arm with rotating joints"""
        glPushMatrix()
        glTranslatef(side * 0.7, 0.8, 0)
        
        # Shoulder joint
        self.draw_glowing_sphere(0.18, self.colors['limbs'])
        
        # Arm rotation based on animation state
        if self.anim_state == AnimationState.WAVING and side == 1:
            glRotatef(math.sin(self.animation_frame * 0.2) * 60 + 100, 1, 0, 0)
        elif self.anim_state == AnimationState.DANCING:
            glRotatef(math.sin(self.arm_rotation + side * math.pi) * 35, 1, 0, 0)
        elif self.anim_state == AnimationState.WALKING:
            glRotatef(math.sin(self.arm_rotation + side * math.pi) * 25, 1, 0, 0)
        else:
            glRotatef(math.sin(self.arm_rotation) * 8, 1, 0, 0)
        
        # Upper arm
        glPushMatrix()
        glTranslatef(0, -0.3, 0)
        self.draw_glowing_cube(0.2, 0.65, 0.2, self.colors['limbs'])
        glPopMatrix()
        
        # Elbow joint and forearm
        glPushMatrix()
        glTranslatef(0, -0.65, 0)
        self.draw_glowing_sphere(0.15, self.colors['secondary'])
        
        glTranslatef(0, -0.3, 0)
        self.draw_glowing_cube(0.18, 0.65, 0.18, self.colors['primary'])
        
        glTranslatef(0, -0.4, 0)
        self.draw_glowing_sphere(0.18, self.colors['accent'])
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_leg(self, side):
        """Draw cyberpunk leg with articulated joints"""
        glPushMatrix()
        glTranslatef(side * 0.3, -0.3, 0)
        
        # Hip joint
        self.draw_glowing_sphere(0.18, self.colors['limbs'])
        
        # Leg rotation
        if self.anim_state == AnimationState.DANCING:
            glRotatef(math.sin(self.animation_frame * 0.3 + side * math.pi) * 40, 1, 0, 0)
        elif self.anim_state == AnimationState.WALKING:
            glRotatef(math.sin(self.walk_cycle + side * math.pi) * 30, 1, 0, 0)
        
        # Thigh
        glPushMatrix()
        glTranslatef(0, -0.45, 0)
        self.draw_glowing_cube(0.25, 0.9, 0.25, self.colors['limbs'])
        glPopMatrix()
        
        # Knee and shin
        glPushMatrix()
        glTranslatef(0, -0.9, 0)
        self.draw_glowing_sphere(0.15, self.colors['secondary'])
        
        glTranslatef(0, -0.4, 0)
        self.draw_glowing_cube(0.22, 0.9, 0.22, self.colors['primary'])
        
        # Foot with glow stripe
        glPushMatrix()
        glTranslatef(0, -0.5, 0.15)
        self.draw_glowing_cube(0.28, 0.12, 0.45, self.colors['energy'])
        glPopMatrix()
        
        glPopMatrix()
        glPopMatrix()
    
    def start_walking(self, direction):
        """Start walking animation"""
        if self.anim_state == AnimationState.WALKING:
            return
        
        self.anim_state = AnimationState.WALKING
        self.walk_progress = 0
        self.walk_direction = direction
        self.start_position = self.position.copy()
        
        angle_rad = math.radians(self.rotation[1])
        
        directions = {
            'forward': (-math.sin(angle_rad), 0, -math.cos(angle_rad)),
            'backward': (math.sin(angle_rad), 0, math.cos(angle_rad)),
            'left': (-math.cos(angle_rad), 0, math.sin(angle_rad)),
            'right': (math.cos(angle_rad), 0, -math.sin(angle_rad)),
        }
        
        dx, dy, dz = directions.get(direction, (0, 0, 0))
        self.target_position = [
            self.position[0] + dx * self.step_size,
            self.position[1],
            self.position[2] + dz * self.step_size
        ]
    
    def update_animation(self):
        """Update all animation states"""
        self.animation_frame += 1
        self.energy_pulse += 0.05
        
        if self.anim_state == AnimationState.JUMPING:
            self.jump_offset = abs(math.sin(self.animation_frame * 0.2)) * 1.5
            if self.animation_frame > 30:
                self.anim_state = AnimationState.IDLE
                self.animation_frame = 0
                self.jump_offset = 0
        
        elif self.anim_state == AnimationState.WALKING:
            self.walk_progress += 0.08
            self.walk_cycle += 0.3
            
            t = min(self.walk_progress, 1.0)
            t_smooth = t * t * (3 - 2 * t)
            
            self.position[0] = self.start_position[0] + (self.target_position[0] - self.start_position[0]) * t_smooth
            self.position[2] = self.start_position[2] + (self.target_position[2] - self.start_position[2]) * t_smooth
            self.jump_offset = abs(math.sin(self.walk_progress * math.pi)) * 0.12
            
            if self.walk_progress >= 1.0:
                self.anim_state = AnimationState.IDLE
                self.position = self.target_position.copy()
        
        if self.anim_state not in [AnimationState.DANCING, AnimationState.WALKING]:
            self.arm_rotation += 0.02
        elif self.anim_state == AnimationState.WALKING:
            self.arm_rotation += 0.15
    
    def draw(self):
        """Render complete robot with aura"""
        glPushMatrix()
        
        glTranslatef(*self.position)
        glTranslatef(0, self.jump_offset, 0)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        
        # Energy aura
        self.draw_energy_aura(1.2)
        
        # Robot body
        self.draw_body()
        self.draw_head()
        self.draw_arm(-1)
        self.draw_arm(1)
        self.draw_leg(-1)
        self.draw_leg(1)
        
        glPopMatrix()


class BluetoothReceiver:
    """Enhanced Bluetooth serial communication handler"""
    
    def __init__(self):
        self.serial_conn = None
        self.command_queue = queue.Queue()
        self.running = False
        self.connected = False
        self.port = None
    
    def find_port(self):
        """Auto-detect available serial ports"""
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        print("\n" + "="*70)
        print("AVAILABLE SERIAL PORTS:")
        print("="*70)
        
        for i, port in enumerate(ports):
            print(f"  [{i}] {port.device:<15} - {port.description}")
            available_ports.append(port.device)
            
            if any(bt in port.description for bt in ['HC-05', 'HC-06', 'Bluetooth']):
                print(f"      ⚡ Bluetooth device detected!")
                self.port = port.device
        
        if not available_ports:
            print("  ⚠ No ports found - check connection and drivers")
        
        return available_ports
    
    def connect(self, port=None, baudrate=38400):
        """Establish serial connection"""
        if port:
            self.port = port
        
        if not self.port:
            available = self.find_port()
            if not available:
                return False
            
            if not self.port:
                try:
                    choice = input("\nSelect port (0-X) or 'q' to skip: ").strip()
                    if choice.lower() == 'q':
                        print("⚠ Using keyboard control only")
                        return False
                    self.port = available[int(choice)]
                except (ValueError, IndexError):
                    return False
        
        try:
            print(f"\n⏳ Connecting to {self.port} @ {baudrate} baud...")
            self.serial_conn = serial.Serial(port=self.port, baudrate=baudrate, timeout=0.1)
            time.sleep(2)
            self.connected = True
            print("✓ Connection established!")
            return True
        except serial.SerialException as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def start_listening(self):
        """Start background listening thread"""
        if not self.connected:
            return False
        
        self.running = True
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        return True
    
    def _listen_loop(self):
        """Background thread for serial listening"""
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        self.command_queue.put(line)
            except (serial.SerialException, UnicodeDecodeError):
                pass
            time.sleep(0.01)
    
    def get_command(self):
        """Retrieve queued command"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Close connection"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()


class CyberpunkViewer:
    """Main 3D viewer with Bluetooth + keyboard control"""
    
    def __init__(self):
        pygame.init()
        self.display = (1000, 800)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("⚡ NEXUS - Cyberpunk Robot Control System")
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glClearColor(0.05, 0.05, 0.1, 1.0)
        glLight(GL_LIGHT0, GL_POSITION, (8, 8, 8, 1))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.5, 1))
        glLight(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1))
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        
        self.robot = CyberpunkRobot3D()
        self.clock = pygame.time.Clock()
        self.running = True
        self.bt_receiver = BluetoothReceiver()
    
    def handle_command(self, cmd):
        """Process control commands"""
        cmd = cmd.lower().strip()
        
        walk_cmds = {'forward', 'backward', 'left', 'right'}
        if cmd in walk_cmds:
            self.robot.start_walking(cmd)
        elif cmd == 'rotate_left':
            self.robot.rotation[1] -= 15
        elif cmd == 'rotate_right':
            self.robot.rotation[1] += 15
        elif cmd == 'jump':
            if self.robot.anim_state != AnimationState.WALKING:
                self.robot.anim_state = AnimationState.JUMPING
                self.robot.animation_frame = 0
        elif cmd == 'wave':
            self.robot.anim_state = AnimationState.WAVING if self.robot.anim_state != AnimationState.WAVING else AnimationState.IDLE
        elif cmd == 'dance':
            self.robot.anim_state = AnimationState.DANCING if self.robot.anim_state != AnimationState.DANCING else AnimationState.IDLE
        elif cmd == 'nod':
            self.robot.head_tilt = 25 if self.robot.head_tilt == 0 else 0
        elif cmd == 'reset':
            self.robot.position = [0, 0, -10]
            self.robot.rotation = [0, 0, 0]
            self.robot.anim_state = AnimationState.IDLE
    
    def draw_grid(self):
        """Render glowing ground grid"""
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.5, 0.8)
        glBegin(GL_LINES)
        for i in range(-15, 16):
            glVertex3f(i, -1.5, -25)
            glVertex3f(i, -1.5, 5)
            glVertex3f(-15, -1.5, -25 + i)
            glVertex3f(15, -1.5, -25 + i)
        glEnd()
        glEnable(GL_LIGHTING)
    
    def run(self):
        """Main loop"""
        print("\n" + "="*70)
        print("⚡ NEXUS - CYBERPUNK 3D ROBOT CONTROL SYSTEM ⚡")
        print("="*70)
        print("\n🎮 KEYBOARD CONTROLS:")
        print("  ↑↓←→: Move/Rotate  |  SPACE: Jump  |  W: Wave")
        print("  D: Dance  |  N: Nod  |  R: Reset  |  ESC: Quit")
        print("\n")
        
        if self.bt_receiver.connect() and self.bt_receiver.start_listening():
            print("✓ Bluetooth active - joystick enabled")
        else:
            print("⚠ Using keyboard control only")
        
        print("="*70 + "\n")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    key_map = {
                        pygame.K_ESCAPE: None,
                        pygame.K_UP: 'forward',
                        pygame.K_DOWN: 'backward',
                        pygame.K_LEFT: 'rotate_left',
                        pygame.K_RIGHT: 'rotate_right',
                        pygame.K_SPACE: 'jump',
                        pygame.K_w: 'wave',
                        pygame.K_d: 'dance',
                        pygame.K_n: 'nod',
                        pygame.K_r: 'reset',
                    }
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key in key_map and key_map[event.key]:
                        self.handle_command(key_map[event.key])
            
            if cmd := self.bt_receiver.get_command():
                self.handle_command(cmd)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            gluLookAt(0, 2.5, 3, 0, 0.8, -10, 0, 1, 0)
            
            self.draw_grid()
            self.robot.update_animation()
            self.robot.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.bt_receiver.stop()
        pygame.quit()


if __name__ == '__main__':
    try:
        viewer = CyberpunkViewer()
        viewer.run()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
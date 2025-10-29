# 🤖 3D Robot Character with Wireless Control

An innovative 3D robot character sprite built with PyOpenGL and Pygame, featuring wireless control capabilities through a beautiful web interface.

## ✨ Features

### 🎨 Creative 3D Design
- **Articulated Robot Character**: Fully 3D robot with moving limbs, head, and body
- **Step-Based Movement**: One click = one animated step with natural walking motion
- **Stable at Rest**: Legs stay still when not moving, no continuous animation drift
- **Smooth Animations**: Walking, jumping, waving, dancing, and nodding animations
- **Color-Coded Design**: Blue body, golden head, pink accents, and green eyes
- **Real-time Rendering**: 60 FPS OpenGL rendering with lighting and shadows

### 🎮 Control Methods
1. **Keyboard Controls** (Direct):
   - Arrow Keys: Move and rotate
   - SPACE: Jump
   - W: Wave
   - D: Dance
   - N: Nod
   - R: Reset position

2. **Wireless Web Control**:
   - Beautiful responsive web interface
   - Control from any device on the same network
   - Real-time status updates
   - Touch-friendly mobile controls

### 🎭 Character Actions
- **Step-Based Movement**: Forward, backward, left, right (one step per click)
- **Rotation**: Rotate left/right (15° per click)
- **Jump**: Animated jumping motion
- **Wave**: Right arm waving animation
- **Dance**: Full body dance routine
- **Nod**: Head tilting motion

> **New!** Movement is now step-based - each click makes the robot take one animated step with natural leg swinging. Legs remain stable when at rest. See `MOVEMENT_GUIDE.md` for details.

## 📋 Requirements

- Python 3.8+
- PyOpenGL
- Pygame
- Flask
- Flask-CORS

## 🚀 Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python character_3d.py
```

3. Open the web control interface:
   - Local: http://localhost:5000
   - Network: http://[your-ip]:5000

## 🎯 How It Works

### Architecture
```
┌─────────────────┐         ┌──────────────────┐
│  Web Interface  │────────▶│  Flask Server    │
│  (HTML/JS)      │  HTTP   │  (Port 5000)     │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Character3D     │
                            │  Viewer          │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Robot3D Model   │
                            │  (OpenGL)        │
                            └──────────────────┘
```

### Technical Details

**3D Rendering**:
- Uses OpenGL for hardware-accelerated 3D graphics
- Implements custom geometric primitives (cubes, spheres, cylinders)
- Real-time lighting with GL_LIGHT0
- Depth testing for proper 3D occlusion

**Animation System**:
- Frame-based animation counter
- Sinusoidal motion for smooth, natural movements
- State machine for different animation modes
- Independent limb articulation

**Wireless Control**:
- Flask REST API for command handling
- CORS enabled for cross-origin requests
- Real-time status endpoint for UI updates
- Thread-safe command processing

## 🎨 Customization

### Change Robot Colors
Edit the `colors` dictionary in the `Robot3D.__init__` method:
```python
self.colors = {
    'body': (0.2, 0.6, 0.9),      # RGB values (0-1)
    'head': (0.9, 0.7, 0.2),
    'limbs': (0.3, 0.3, 0.3),
    'eyes': (0.0, 1.0, 0.0),
    'accent': (1.0, 0.2, 0.5)
}
```

### Add New Actions
1. Add a new command handler in `Character3DViewer.handle_command()`
2. Implement the animation in `Robot3D.update_animation()`
3. Add a button in `templates/control.html`

### Adjust Animation Speed
Modify the animation frame increments in `Robot3D.update_animation()`:
```python
self.arm_rotation += 0.05  # Increase for faster arm movement
self.leg_rotation += 0.08  # Increase for faster leg movement
```

## 🌐 Network Setup

### Find Your IP Address
**Windows**:
```bash
ipconfig
```
Look for "IPv4 Address"

**Linux/Mac**:
```bash
ifconfig
```
or
```bash
ip addr show
```

### Firewall Configuration
Make sure port 5000 is open:
- Windows: Allow Python through Windows Firewall
- Linux: `sudo ufw allow 5000`

## 🎓 Educational Value

This project demonstrates:
- **3D Graphics Programming**: OpenGL rendering pipeline
- **Network Programming**: REST API design
- **Animation Techniques**: Keyframe and procedural animation
- **Web Development**: Responsive UI design
- **Threading**: Concurrent server and rendering
- **Embedded Systems Concepts**: Wireless device control

## 🐛 Troubleshooting

**Issue**: Black screen or no rendering
- **Solution**: Update graphics drivers, ensure OpenGL support

**Issue**: Web interface not accessible
- **Solution**: Check firewall settings, verify IP address

**Issue**: Laggy animations
- **Solution**: Reduce animation complexity or increase hardware acceleration

**Issue**: Import errors
- **Solution**: Reinstall dependencies with `pip install -r requirements.txt`

## 🔮 Future Enhancements

- [ ] Add more complex animations (backflip, spin)
- [ ] Implement path recording and playback
- [ ] Add voice control integration
- [ ] Support multiple robot instances
- [ ] Add VR/AR viewing mode
- [ ] Implement inverse kinematics for realistic movement
- [ ] Add physics simulation
- [ ] Create a mobile app controller

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Credits

Created with PyOpenGL, Pygame, and Flask for embedded systems education.

---

**Enjoy controlling your 3D robot! 🤖✨**

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# ArUco PID Angular Visual Servoing - Root Locus Visualizer
# ---------------------------------------------------------

# PID Gains (Angular)
kp_ang = 0.5
ki_ang = 0.01
kd_ang = 0.05

# The characteristic equation is: 1 + K * C(s)P(s) = 0
# 1 + K * [ (kd*s^2 + kp*s + ki) / s^2 ] = 0
# 
# Multiplying by s^2:
# (1 + K*kd)*s^2 + (K*kp)*s + (K*ki) = 0

# Generate a wide range of gains
K_values = np.logspace(-2, 4, 10000)
roots = []

print("Calculating angular root locus branches...")
for K in K_values:
    # polynomial coefficients: a*s^2 + b*s + c = 0
    a = 1 + K * kd_ang
    b = K * kp_ang
    c = K * ki_ang
    
    # Calculate roots for this specific gain
    r = np.roots([a, b, c])
    roots.append(r)

roots = np.array(roots)

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------
plt.figure(figsize=(10, 8))

# Plot the root locus branches
plt.plot(np.real(roots[:, 0]), np.imag(roots[:, 0]), color='purple', linewidth=2, label='Root Locus Branch 1')
plt.plot(np.real(roots[:, 1]), np.imag(roots[:, 1]), color='magenta', linewidth=2, label='Root Locus Branch 2')

# Calculate and plot the exact Open-Loop Poles and Zeros
poles = [0, 0]
zeros = np.roots([kd_ang, kp_ang, ki_ang])

plt.plot(np.real(poles), np.imag(poles), 'rX', markersize=14, label='Open-Loop Poles (s=0, 0)')
plt.plot(np.real(zeros), np.imag(zeros), 'go', markersize=12, label=f'Open-Loop Zeros (s={zeros[0]:.2f}, {zeros[1]:.2f})')

# Formatting the plot
plt.axhline(0, color='black', lw=1.5)
plt.axvline(0, color='black', lw=1.5)
plt.grid(True, linestyle='--', alpha=0.7)
plt.title('Angular Root Locus (Pitch/Yaw) of ArUco PID System', fontsize=16, fontweight='bold')
plt.xlabel('Real Axis (Decay Rate)', fontsize=12)
plt.ylabel('Imaginary Axis (Oscillation Frequency)', fontsize=12)

# Set axes limits to frame the larger circle
plt.xlim(-12, 2)
plt.ylim(-6, 6)
plt.legend(loc='upper right')

# Save and show
plt.savefig('aruco_angular_root_locus.png', dpi=300, bbox_inches='tight')
print("Success! Root locus plot saved as 'aruco_angular_root_locus.png'")

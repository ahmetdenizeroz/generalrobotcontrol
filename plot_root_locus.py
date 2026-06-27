import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# ArUco PID Visual Servoing - Root Locus Visualizer
# ---------------------------------------------------------

# PID Gains (Positional)
kp_lin = 0.01
ki_lin = 0.000002
kd_lin = 0.0002

# The characteristic equation is: 1 + K * C(s)P(s) = 0
# 1 + K * [ (kd*s^2 + kp*s + ki) / s^2 ] = 0
# 
# Multiplying by s^2:
# s^2 + K*(kd*s^2 + kp*s + ki) = 0
# (1 + K*kd)*s^2 + (K*kp)*s + (K*ki) = 0

# Generate a wide range of gains (K_cam) from very small to very large
K_values = np.logspace(-2, 6, 10000)
roots = []

print("Calculating root locus branches...")
for K in K_values:
    # polynomial coefficients: a*s^2 + b*s + c = 0
    a = 1 + K * kd_lin
    b = K * kp_lin
    c = K * ki_lin
    
    # Calculate roots for this specific gain
    r = np.roots([a, b, c])
    roots.append(r)

roots = np.array(roots)

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------
plt.figure(figsize=(10, 8))

# Plot the root locus branches
plt.plot(np.real(roots[:, 0]), np.imag(roots[:, 0]), color='blue', linewidth=2, label='Root Locus Branch 1')
plt.plot(np.real(roots[:, 1]), np.imag(roots[:, 1]), color='cyan', linewidth=2, label='Root Locus Branch 2')

# Calculate and plot the exact Open-Loop Poles and Zeros
poles = [0, 0]
zeros = np.roots([kd_lin, kp_lin, ki_lin])

plt.plot(np.real(poles), np.imag(poles), 'rX', markersize=14, label='Open-Loop Poles (s=0, 0)')
plt.plot(np.real(zeros), np.imag(zeros), 'go', markersize=12, label=f'Open-Loop Zeros (s={zeros[0]:.2f}, {zeros[1]:.2f})')

# Formatting the plot
plt.axhline(0, color='black', lw=1.5)
plt.axvline(0, color='black', lw=1.5)
plt.grid(True, linestyle='--', alpha=0.7)
plt.title('Root Locus of ArUco PID Tracking System', fontsize=16, fontweight='bold')
plt.xlabel('Real Axis (Decay Rate)', fontsize=12)
plt.ylabel('Imaginary Axis (Oscillation Frequency)', fontsize=12)

# Set axes limits to perfectly frame the circle
plt.xlim(-6, 1)
plt.ylim(-3.5, 3.5)
plt.legend(loc='upper right')

# Save and show
plt.savefig('aruco_root_locus.png', dpi=300, bbox_inches='tight')
print("Success! Root locus plot saved as 'aruco_root_locus.png'")

try:
    plt.show()
except:
    print("Could not display plot in window. Check the saved aruco_root_locus.png file.")

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

# ---------------------------------------------------------
# ArUco PID - Root Locus with Network Latency
# ---------------------------------------------------------

# PID Gains (Positional)
kp_lin = 0.001
ki_lin = 0.0005
kd_lin = 0.0002

# Assume 100ms (0.1s) of latency (OpenCV processing + UDP Network + MoveIt IK)
Td = 0.1

# Pade Approximation of Time Delay e^(-Td * s)
# 1st order Pade: (1 - (Td/2)*s) / (1 + (Td/2)*s)
pade_num = [-Td/2, 1]
pade_den = [Td/2, 1]

# Original PID Numerator and Integrator Denominator
pid_num = [kd_lin, kp_lin, ki_lin]
pid_den = [1, 0, 0]

# Combine them by multiplying polynomials
open_loop_num = np.polymul(pid_num, pade_num)
open_loop_den = np.polymul(pid_den, pade_den)

# Generate a wide range of gains
K_values = np.logspace(-2, 5, 10000)
roots = []

print(f"Calculating root locus with {Td*1000}ms latency...")
for K in K_values:
    # 1 + K * (num / den) = 0  =>  den + K*num = 0
    char_eq = np.polyadd(open_loop_den, K * open_loop_num)
    
    # Calculate roots for this specific gain
    r = np.roots(char_eq)
    roots.append(r)

roots = np.array(roots)

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------
plt.figure(figsize=(10, 8))

# Plot the root locus branches
for i in range(roots.shape[1]):
    plt.plot(np.real(roots[:, i]), np.imag(roots[:, i]), linewidth=2)

# Calculate and plot the exact Open-Loop Poles and Zeros
poles = np.roots(open_loop_den)
zeros = np.roots(open_loop_num)

plt.plot(np.real(poles), np.imag(poles), 'rX', markersize=14, label='Open-Loop Poles')
plt.plot(np.real(zeros), np.imag(zeros), 'go', markersize=12, label='Open-Loop Zeros')

# Formatting the plot
plt.axhline(0, color='black', lw=1.5)
plt.axvline(0, color='black', lw=1.5)

# Highlight the unstable region
plt.axvspan(0, 30, color='red', alpha=0.1, label='Unstable Region (Right-Half Plane)')

plt.grid(True, linestyle='--', alpha=0.7)
plt.title(f'Root Locus WITH {Td*1000}ms Network Latency', fontsize=16, fontweight='bold')
plt.xlabel('Real Axis (Decay Rate)', fontsize=12)
plt.ylabel('Imaginary Axis (Oscillation Frequency)', fontsize=12)

# Set axes limits to see the bending effect
plt.xlim(-25, 25)
plt.ylim(-15, 15)
plt.legend(loc='upper right')

# Save and show
plt.savefig('aruco_latency_root_locus.png', dpi=300, bbox_inches='tight')
print("Success! Root locus plot saved as 'aruco_latency_root_locus.png'")

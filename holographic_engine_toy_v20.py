import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure scratch directory exists
os.makedirs('/workspace/scratch', exist_ok=True)

# Set Seaborn theme for publication quality
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')

# Parameters for the Entropic Gravity Tax Gradient Simulation
G = 1.0       # Gravitational constant (simulation units)
m1 = 10.0     # Mass 1 (rendering tax baseline 1)
m2 = 5.0      # Mass 2 (rendering tax baseline 2)
r_min = 0.8   # Minimum separation distance
r_max = 10.0  # Maximum separation distance
num_points = 200

r = np.linspace(r_min, r_max, num_points)

# Isolated rendering tax sum (far separation limit)
C_isolated = 1000.0 + 500.0  # C_1 + C_2 baseline

# Overlap tax savings (boundary MERA tree unification)
# Delta_C_overlap(r) = G * m1 * m2 / r
delta_C_overlap = (G * m1 * m2) / r

# Total Combined Boundary Rendering Tax Functional
C_total = C_isolated - delta_C_overlap

# Gravitational Entropic Force F = - dC_total / dr = - d( - G m1 m2 / r ) / dr = - G m1 m2 / r^2
# Negative sign indicates attractive force pushing towards r -> 0
F_entropic = - (G * m1 * m2) / (r**2)
F_magnitude = np.abs(F_entropic)

# Create 2-panel figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Panel 1: Boundary Rendering Tax Functional C_total(r)
ax1.plot(r, C_total, color='#1f77b4', linewidth=2.5, label=r'Combined Tax $\mathcal{C}_{12}(r) = \mathcal{C}_1 + \mathcal{C}_2 - \frac{G m_1 m_2}{r}$')
ax1.axhline(C_isolated, color='gray', linestyle='--', alpha=0.7, label=r'Isolated Boundary Tax Limit ($\mathcal{C}_1 + \mathcal{C}_2$)')
ax1.set_title(r'Boundary MERA Rendering Tax Drops as Fields Unify', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Spatial Separation Distance $r$ (Bulk Radius)', fontsize=11)
ax1.set_ylabel(r'Total Boundary Rendering Tax $\mathcal{C}[B_n]$ (units)', fontsize=11)
ax1.annotate('Tax Optimization Zone\n(Field Unification)', xy=(1.5, C_isolated - (G*m1*m2/1.5)), 
             xytext=(3.5, C_isolated - 30),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="b", lw=1, alpha=0.5))
ax1.legend(loc='lower right', fontsize=10)

# Panel 2: Entropic Force Gradient F(r) = - dC/dr
ax2.plot(r, F_magnitude, color='#d62728', linewidth=2.5, label=r'Entropic Push Force $|F| = \frac{\partial \mathcal{C}}{\partial r} = \frac{G m_1 m_2}{r^2}$')
ax2.set_title(r'Emergent Gravitational Force Follows $1/r^2$ Tax Gradient', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Spatial Separation Distance $r$ (Bulk Radius)', fontsize=11)
ax2.set_ylabel(r'Attractive Gravitational Force $F_{\text{gravity}}$ (units)', fontsize=11)
ax2.annotate('Substrate Push\n(Unifying Boundary Trees)', xy=(1.2, (G*m1*m2)/(1.2**2)), 
             xytext=(3.0, 20.0),
             arrowprops=dict(facecolor='#d62728', shrink=0.05, width=1.5, headwidth=8),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#ffe6e6", ec="#d62728", lw=1))
ax2.legend(loc='upper right', fontsize=10)

fig.suptitle('Entropic Gravity: Field Unification & Rendering Tax Gradient (v20.0)', fontsize=16, fontweight='bold', y=1.02)
sns.despine(fig=fig)
plt.tight_layout(pad=1.5)

chart_path = '/workspace/scratch/entropic_gravity_tax_gradient_graph.png'
fig.savefig(chart_path, dpi=150, bbox_inches='tight')
plt.close()

print(f"Successfully generated {chart_path}")

# Print quantitative verification table
print("\n=== ENTROPIC GRAVITY TAX GRADIENT NUMERICAL SUMMARY ===")
sample_indices = [5, 20, 50, 100, 199]
for idx in sample_indices:
    r_val = r[idx]
    tax_val = C_total[idx]
    force_val = F_magnitude[idx]
    print(f"Separation r = {r_val:5.2f} | Total Tax C = {tax_val:8.2f} units | Overlap Savings = {delta_C_overlap[idx]:6.2f} | Entropic Force F = {force_val:6.2f}")

# Copy to out directory
shutil.copy('/workspace/scratch/entropic_gravity_tax_gradient_graph.png', '/workspace/out/entropic_gravity_tax_gradient_graph.png')
shutil.copy('/workspace/scratch/holographic_engine_toy_v20.py', '/workspace/out/holographic_engine_toy_v20.py')
print("Published entropic_gravity_tax_gradient_graph.png and holographic_engine_toy_v20.py to /workspace/out/")

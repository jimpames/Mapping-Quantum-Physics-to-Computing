import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs('/workspace/scratch', exist_ok=True)
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')

# Elements dataset
elements_data = [
    {"name": "Hydrogen", "symbol": "H", "Z": 1, "A": 1, "magic": False},
    {"name": "Helium", "symbol": "He", "Z": 2, "A": 4, "magic": True},
    {"name": "Carbon", "symbol": "C", "Z": 6, "A": 12, "magic": False},
    {"name": "Oxygen", "symbol": "O", "Z": 8, "A": 16, "magic": True},
    {"name": "Calcium", "symbol": "Ca", "Z": 20, "A": 40, "magic": True},
    {"name": "Iron", "symbol": "Fe", "Z": 26, "A": 56, "magic": False},
    {"name": "Tin", "symbol": "Sn", "Z": 50, "A": 120, "magic": True},
    {"name": "Lead", "symbol": "Pb", "Z": 82, "A": 208, "magic": True},
    {"name": "Uranium", "symbol": "U", "Z": 92, "A": 238, "magic": False},
    {"name": "Plutonium", "symbol": "Pu", "Z": 94, "A": 244, "magic": False},
    {"name": "Fermium", "symbol": "Fm", "Z": 100, "A": 257, "magic": False},
    {"name": "Oganesson", "symbol": "Og", "Z": 118, "A": 294, "magic": False},
    {"name": "Unbinilium", "symbol": "Ubn", "Z": 120, "A": 300, "magic": True}, # Island of Stability
    {"name": "Unbihexium", "symbol": "Ubh", "Z": 126, "A": 310, "magic": True}, # Magic Shell
]

# Continuous Z sweep for smooth curves
Z_continuous = np.linspace(1, 130, 200)

def calculate_superheavy_tax(Z, A, is_magic=False):
    # Static Registration Overhead
    C_reg = 20.0 * (Z ** 1.35) + 3.0 * A
    
    # Dynamic MERA Orbital Tax
    C_dyn = 12.0 * (Z ** 1.65)
    
    # Pre-compiled Magic Shell Struct Lock Discount
    magic_discount = 0.25 * C_reg if is_magic else 0.0
    
    C_total = (C_reg + C_dyn) - magic_discount
    return C_reg, C_dyn, magic_discount, C_total

# Substrate MERA Channel Capacity Threshold
C_CRITICAL = 10000.0  # MERA Bond Dimension Limit

# Process elements data
results = []
for elem in elements_data:
    Z = elem["Z"]
    A = elem["A"]
    magic = elem["magic"]
    C_reg, C_dyn, disc, C_total = calculate_superheavy_tax(Z, A, magic)
    
    # MERA Truncation Strain
    strain = max(0.0, (C_total - C_CRITICAL) / C_CRITICAL)
    
    # Stability / Half-life Proxy (arbitrary log scale for display)
    if strain == 0:
        log_half_life = 25.0 - 0.15 * Z + (5.0 if magic else 0.0) # Stable to very long
    else:
        # Exponential plummet due to MERA Strain Garbage Collection
        log_half_life = max(-9.0, 5.0 - 120.0 * strain + (4.0 if magic else 0.0))
        
    results.append({
        "name": elem["name"],
        "symbol": elem["symbol"],
        "Z": Z,
        "A": A,
        "C_reg": C_reg,
        "C_dyn": C_dyn,
        "C_total": C_total,
        "strain": strain,
        "log_half_life": log_half_life,
        "magic": magic
    })

# Continuous Curves
C_reg_cont = 20.0 * (Z_continuous ** 1.35) + 3.0 * (2.5 * Z_continuous)
C_dyn_cont = 12.0 * (Z_continuous ** 1.65)
C_total_cont = C_reg_cont + C_dyn_cont
strain_cont = np.maximum(0.0, (C_total_cont - C_CRITICAL) / C_CRITICAL)

# Create 4-panel Telemetry Dashboard
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle('Superheavy Element Tax Overflow & MERA Channel Capacity Limit (v22.0)', fontsize=16, fontweight='bold')

# Panel 1: Tax Functional vs Nuclear Charge Z
ax1 = axes[0, 0]
ax1.plot(Z_continuous, C_total_cont, label='Total Rendering Tax C(Z)', color='#0f2043', linewidth=2.5)
ax1.plot(Z_continuous, C_reg_cont, '--', label='Static Registration Overhead', color='#b45309', alpha=0.8)
ax1.plot(Z_continuous, C_dyn_cont, ':', label='Dynamic MERA Orbital Tax', color='#2563eb', alpha=0.8)
ax1.axhline(C_CRITICAL, color='red', linestyle='-', linewidth=1.5, label='MERA Channel Capacity Limit')

# Scatter key elements
for r in results:
    color = 'green' if r['magic'] else 'purple'
    marker = 'D' if r['magic'] else 'o'
    ax1.scatter(r['Z'], r['C_total'], color=color, s=50, zorder=5, marker=marker)
    if r['Z'] in [1, 26, 82, 92, 118, 120, 126]:
        ax1.annotate(f"{r['symbol']} ({r['Z']})", (r['Z'], r['C_total']), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, fontweight='bold')

ax1.set_title('Substrate Rendering Tax vs. Atomic Number (Z)', fontsize=13, fontweight='bold')
ax1.set_xlabel('Atomic Number (Z)')
ax1.set_ylabel('Substrate Tax (Tax Units)')
ax1.legend(loc='upper left', fontsize=9)

# Panel 2: MERA Truncation Strain & Garbage Collection Threshold
ax2 = axes[0, 1]
ax2.plot(Z_continuous, strain_cont * 100, color='red', linewidth=2.5, label='MERA Truncation Strain (%)')
ax2.fill_between(Z_continuous, 0, strain_cont * 100, color='red', alpha=0.15)
ax2.axvline(106, color='black', linestyle='--', label='Superheavy Stability Cutoff (Z ~ 106)')

for r in results:
    if r['strain'] > 0:
        ax2.scatter(r['Z'], r['strain'] * 100, color='darkred', s=60, zorder=5)
        ax2.annotate(f"{r['symbol']}", (r['Z'], r['strain'] * 100), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, fontweight='bold')

ax2.set_title('MERA Channel Capacity Overflow & Strain', fontsize=13, fontweight='bold')
ax2.set_xlabel('Atomic Number (Z)')
ax2.set_ylabel('MERA Truncation Strain (%)')
ax2.legend(loc='upper left', fontsize=9)

# Panel 3: Half-Life / Stability Proxy & Island of Stability
ax3 = axes[1, 0]
Z_res = [r['Z'] for r in results]
hl_res = [r['log_half_life'] for r in results]
colors_res = ['#16a34a' if r['magic'] else '#dc2626' if r['strain'] > 0 else '#2563eb' for r in results]

ax3.scatter(Z_res, hl_res, c=colors_res, s=80, zorder=5)
ax3.plot(Z_res, hl_res, color='gray', linestyle=':', alpha=0.6)

# Annotate Island of Stability
ax3.annotate('Island of Stability\n(Pre-compiled Struct Lock)', xy=(120, hl_res[Z_res.index(120)]), xytext=(100, 12),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#16a34a", lw=1.5))

ax3.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)
ax3.set_title('Nuclear Half-Life Proxy vs. Z (Substrate De-allocation)', fontsize=13, fontweight='bold')
ax3.set_xlabel('Atomic Number (Z)')
ax3.set_ylabel('Log10 Half-life (sec proxy)')

# Panel 4: De-allocation Memory Reclamation Scheme (Decay Chains)
ax4 = axes[1, 1]
decay_elements = ["Oganesson (118)", "Livermorium (116)", "Flerovium (114)", "Copernicium (112)"]
taxes_before = [calculate_superheavy_tax(z, 2.5*z)[3] for z in [118, 116, 114, 112]]
taxes_reclaimed = [calculate_superheavy_tax(z, 2.5*z)[3] - calculate_superheavy_tax(z-2, 2.5*(z-2))[3] - calculate_superheavy_tax(2, 4)[3] for z in [118, 116, 114, 112]]

x = np.arange(len(decay_elements))
width = 0.35

ax4.bar(x - width/2, taxes_before, width, label='Pre-Decay Tax', color='#991b1b')
ax4.bar(x + width/2, taxes_reclaimed, width, label='Reclaimed Tax per Alpha Ejection', color='#16a34a')

ax4.set_title('Alpha Decay Memory Reclamation (Garbage Collection)', fontsize=13, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(["Og (118)", "Lv (116)", "Fl (114)", "Cn (112)"])
ax4.set_ylabel('Substrate Tax Units')
ax4.legend(loc='upper right', fontsize=9)

sns.despine()
plt.tight_layout(pad=1.5)

graph_path = '/workspace/scratch/superheavy_decay_tax_overflow_graph.png'
fig.savefig(graph_path, dpi=150, bbox_inches='tight')
plt.close()

# Print summary log
print("=== SUPERHEAVY ELEMENT MERA TAX OVERFLOW SUMMARY ===")
for r in results:
    status = "MAGIC STRUCT" if r['magic'] else "OVERFLOW DECAY" if r['strain'] > 0 else "STABLE/LONG"
    print(f"Element: {r['name']:12s} (Z={r['Z']:3d}) | Total Tax: {r['C_total']:8.1f} | Strain: {r['strain']*100:5.1f}% | Status: {status}")

# Copy outputs to /workspace/out/
shutil.copy(graph_path, '/workspace/out/superheavy_decay_tax_overflow_graph.png')
shutil.copy('/workspace/scratch/holographic_engine_toy_v22.py', '/workspace/out/holographic_engine_toy_v22.py')
print("\nPublished superheavy_decay_tax_overflow_graph.png and holographic_engine_toy_v22.py to /workspace/out/")

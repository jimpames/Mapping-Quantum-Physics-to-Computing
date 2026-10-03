import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure scratch directory exists
os.makedirs('/workspace/scratch', exist_ok=True)

# Seaborn theme setup
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
CHART_DPI = 150

def run_v25_simulation():
    # Velocity range v/c from 0 to 0.9999
    v_over_c = np.linspace(0.0, 0.9999, 1000)
    
    # 1. Lorentz Factor gamma(v) and Proper Time Ratio dtau/dt = 1/gamma
    gamma = 1.0 / np.sqrt(1.0 - v_over_c**2)
    dtau_dt = 1.0 / gamma  # Internal processing fraction
    spatial_bus_load = v_over_c  # Fractional spatial translation load
    
    # Rest mass baseline tax
    rest_tax_baseline = 1000.0  # arbitrary tax units for 1 kg spaceship
    dynamic_tax = rest_tax_baseline * gamma
    
    # 2. Simulated Ship Trajectories over N_lab = 10,000 Planck Ticks
    N_lab_ticks = 10000
    sample_velocities = [0.0, 0.5, 0.866, 0.95, 0.99, 0.9999]
    sample_names = ['v = 0.0 (Rest)', 'v = 0.50c', 'v = 0.866c', 'v = 0.95c', 'v = 0.99c', 'v = 0.9999c']
    
    internal_ticks_processed = []
    spatial_grid_cells_traversed = []
    dynamic_taxes_sample = []
    
    for v in sample_velocities:
        g = 1.0 / np.sqrt(1.0 - v**2)
        dtau = 1.0 / g
        internal_ticks = int(N_lab_ticks * dtau)
        spatial_cells = int(N_lab_ticks * v)
        tax = rest_tax_baseline * g
        
        internal_ticks_processed.append(internal_ticks)
        spatial_grid_cells_traversed.append(spatial_cells)
        dynamic_taxes_sample.append(tax)

    # 3. Create 4-Panel Telemetry Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Substrate Thread Scheduler & Kinematic Time Dilation Telemetry (v25.0)\nBus Bandwidth Allocation, Proper Time Decay, and Relativistic Mass Tax',
                 fontsize=15, fontweight='bold', y=0.98)

    # Panel 1: Substrate Compute Budget Trade-off
    axes[0, 0].plot(v_over_c, dtau_dt * 100, label='Internal Processing Budget (d$\\tau$/dt %)', color='#1f77b4', linewidth=2.5)
    axes[0, 0].plot(v_over_c, v_over_c * 100, label='Spatial Translation Bus Load (v/c %)', color='#ff7f0e', linestyle='--', linewidth=2.0)
    axes[0, 0].axvline(x=0.866, color='red', linestyle=':', label='v = 0.866c (50% Internal Budget)')
    axes[0, 0].set_title('Substrate Bandwidth Allocation vs Velocity', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Velocity (v/c)')
    axes[0, 0].set_ylabel('Substrate Capacity (%)')
    axes[0, 0].set_xlim(0, 1.0)
    axes[0, 0].set_ylim(0, 105)
    axes[0, 0].legend(loc='center left', fontsize=9)

    # Panel 2: Relativistic Rendering Tax Divergence
    axes[0, 1].plot(v_over_c, dynamic_tax, color='#2ca02c', linewidth=2.5, label='Dynamic Tax $\\mathcal{C} = \\gamma m_0 c^2$')
    axes[0, 1].axhline(y=rest_tax_baseline, color='gray', linestyle='--', label='Rest Tax Baseline ($m_0$)')
    axes[0, 1].set_yscale('log')
    axes[0, 1].set_title('Relativistic Rendering Tax Divergence (Log Scale)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Velocity (v/c)')
    axes[0, 1].set_ylabel('Rendering Tax (Tax Units)')
    axes[0, 1].set_xlim(0, 1.0)
    axes[0, 1].legend(loc='upper left', fontsize=9)

    # Panel 3: Internal Clock Ticks Processed (over 10,000 Lab Ticks)
    bars = axes[1, 0].bar(range(len(sample_names)), internal_ticks_processed, color=sns.color_palette('colorblind', len(sample_velocities)))
    axes[1, 0].set_title('Internal Clock Ticks per 10,000 Reference Planck Ticks', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Internal Ticks Processed ($\\tau$)')
    axes[1, 0].set_xticks(range(len(sample_names)))
    axes[1, 0].set_xticklabels(sample_names, rotation=25, ha='right', fontsize=9)
    for bar in bars:
        height = bar.get_height()
        axes[1, 0].annotate(f'{height:,}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Panel 4: Substrate Scheduler Thread Distribution Matrix
    cell_text = []
    for i, v in enumerate(sample_velocities):
        g = 1.0 / np.sqrt(1.0 - v**2)
        cell_text.append([
            f"{v:.4f}c",
            f"{g:.2f}",
            f"{(1/g)*100:.1f}%",
            f"{v*100:.1f}%",
            f"{internal_ticks_processed[i]:,}"
        ])

    columns = ['Velocity (v/c)', 'Lorentz ($\\gamma$)', 'Internal Budget', 'Spatial Bus Load', 'Internal Ticks']
    axes[1, 1].axis('tight')
    axes[1, 1].axis('off')
    table = axes[1, 1].table(cellText=cell_text, colLabels=columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.8)
    axes[1, 1].set_title('Substrate Scheduler Resource Table', fontsize=12, fontweight='bold', pad=15)

    sns.despine()
    plt.tight_layout(pad=2.0)
    
    # Save chart to scratch
    chart_path = '/workspace/scratch/kinematic_time_dilation_scheduler_graph.png'
    fig.savefig(chart_path, dpi=CHART_DPI, bbox_inches='tight')
    plt.close()
    print(f"Saved {chart_path}")

    # Console Summary
    print("\n=== SUBSTRATE THREAD SCHEDULER & TIME DILATION SUMMARY ===")
    for i, v in enumerate(sample_velocities):
        g = 1.0 / np.sqrt(1.0 - v**2)
        print(f"Velocity: {v:7.4f}c | Gamma: {g:7.2f} | Internal Budget: {(1/g)*100:6.2f}% | Dynamic Tax: {dynamic_taxes_sample[i]:10.1f} units | Internal Ticks: {internal_ticks_processed[i]:5d}")

if __name__ == '__main__':
    run_v25_simulation()
    
    # Publish to /workspace/out/
    import shutil
    shutil.copy('/workspace/scratch/kinematic_time_dilation_scheduler_graph.png', '/workspace/out/kinematic_time_dilation_scheduler_graph.png')
    shutil.copy('/workspace/scratch/holographic_engine_toy_v25.py', '/workspace/out/holographic_engine_toy_v25.py')
    print("Published holographic_engine_toy_v25.py and kinematic_time_dilation_scheduler_graph.png to /workspace/out/")

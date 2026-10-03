import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_v26_simulation():
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Alcubierre Warp Metric & MERA Tensor Grid Reconfiguration (v26.0)\nSuperluminal Grid Deformation, Zero Time Dilation, & Negative Tax Deficit',
                 fontsize=14, fontweight='bold', color='#0f2043')

    # -------------------------------------------------------------------------
    # Panel 1: MERA Tensor Grid Distortion Profile f(x)
    # -------------------------------------------------------------------------
    ax1 = axes[0, 0]
    x = np.linspace(-10, 10, 400)
    x_ship = 0.0
    R_bubble = 3.0
    sigma = 1.2
    
    # Top-hat shape function f(x) for Alcubierre metric
    # f(x) = (tanh(sigma*(x + R)) - tanh(sigma*(x - R))) / (2 * tanh(sigma * R))
    f_x = (np.tanh(sigma * (x + R_bubble)) - np.tanh(sigma * (x - R_bubble))) / (2 * np.tanh(sigma * R_bubble))
    
    # Grid contraction / expansion rate (df/dx)
    df_dx = np.gradient(f_x, x)
    
    ax1.plot(x, f_x, label='Warp Bubble Profile $f(x)$', color='#1f77b4', lw=2.5)
    ax1.plot(x, df_dx * 5, label='MERA Grid Strain $\\partial f/\\partial x$ (x5)', color='#e377c2', ls='--', lw=2)
    
    ax1.axvspan(-R_bubble, R_bubble, color='#0f2043', alpha=0.1, label='Flat Local Space (Ship Rest)')
    ax1.axvline(x=R_bubble, color='green', ls=':', label='Contraction Ahead (Downsampling)')
    ax1.axvline(x=-R_bubble, color='red', ls=':', label='Expansion Behind (Upsampling)')
    
    ax1.set_title('1. MERA Grid Deformation & Spatial Density', fontsize=11, fontweight='bold', color='#0f2043')
    ax1.set_xlabel('Spatial Position along Trajectory $x$ [arb]', fontsize=10)
    ax1.set_ylabel('Metric Distortion $f(x)$ / Grid Strain', fontsize=10)
    ax1.legend(loc='upper right', fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 2: Proper Time Preservation (dtau/dt = 1.0) vs. Effective Velocity
    # -------------------------------------------------------------------------
    ax2 = axes[0, 1]
    v_eff = np.linspace(0.0, 5.0, 200) # v_eff / c
    
    # Standard Relativistic Kinematic Translation
    dtau_dt_kinematic = np.where(v_eff < 1.0, np.sqrt(np.maximum(0, 1.0 - v_eff**2)), 0.0)
    
    # Alcubierre Warp Drive (v_local = 0 inside bubble)
    dtau_dt_warp = np.ones_like(v_eff) # Always 1.0 regardless of v_eff
    
    ax2.plot(v_eff, dtau_dt_kinematic, label='Kinematic Translation ($d\\tau/dt = 1/\\gamma$)', color='#d62728', lw=2.5, ls='--')
    ax2.plot(v_eff, dtau_dt_warp, label='Warp Bubble ($d\\tau/dt = 1.00$ - Zero Dilation)', color='#2ca02c', lw=3)
    
    ax2.axvline(x=1.0, color='gray', ls=':', label='Substrate Bus Limit $c$')
    ax2.set_title('2. Proper Time Preservation vs. Effective Velocity', fontsize=11, fontweight='bold', color='#0f2043')
    ax2.set_xlabel('Effective Velocity $v_{\\text{eff}} / c$', fontsize=10)
    ax2.set_ylabel('Proper Time Rate $d\\tau / dt$ (Internal Budget)', fontsize=10)
    ax2.set_ylim(-0.05, 1.15)
    ax2.legend(loc='center right', fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 3: Negative Energy Density & Negative MERA Tax Profile
    # -------------------------------------------------------------------------
    ax3 = axes[1, 0]
    # Energy density T_00 ~ - (v_eff^2 / (8*pi)) * (df/dx)^2
    v_test = 2.0
    rho_energy = - (v_test**2 / (8 * np.pi)) * (df_dx**2) * 100.0 # scaled
    tax_deficit = rho_energy * 15.0 # MERA tax deficit operator
    
    ax3.plot(x, rho_energy, label='Energy Density $T_{00}(x) < 0$', color='#ff7f0e', lw=2.5)
    ax3.plot(x, tax_deficit, label='MERA Tax Deficit $\\mathcal{C}_{\\text{warp}}(x) < 0$', color='#9467bd', lw=2, ls='-.')
    
    ax3.axhline(0, color='black', lw=0.8, ls='--')
    ax3.fill_between(x, rho_energy, 0, color='#ff7f0e', alpha=0.2)
    
    ax3.set_title('3. Negative Energy Density & MERA Tax Deficit', fontsize=11, fontweight='bold', color='#0f2043')
    ax3.set_xlabel('Spatial Position along Trajectory $x$ [arb]', fontsize=10)
    ax3.set_ylabel('Energy Density $T_{00}$ / Tax Deficit Units', fontsize=10)
    ax3.legend(loc='lower right', fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 4: Substrate Resource Budget Comparison
    # -------------------------------------------------------------------------
    ax4 = axes[1, 1]
    modes = ['Kinematic\n(v = 0.0c)', 'Kinematic\n(v = 0.99c)', 'Kinematic\n(v = 1.0c)', 'Warp Drive\n(v_eff = 2.0c)', 'Warp Drive\n(v_eff = 10.0c)']
    
    internal_compute = [100.0, 14.11, 0.0, 100.0, 100.0]
    spatial_bus_load = [0.0, 85.89, 100.0, 0.0, 0.0]
    mera_grid_cost   = [0.0, 0.0, 0.0, 150.0, 450.0] # MERA grid reconfiguration cost
    
    x_indices = np.arange(len(modes))
    width = 0.55
    
    ax4.bar(x_indices, internal_compute, width, label='Internal State Compute ($d\\tau/dt$)', color='#2ca02c')
    ax4.bar(x_indices, spatial_bus_load, width, bottom=internal_compute, label='Spatial Bus Re-indexing Load', color='#d62728')
    bottom_2 = np.array(internal_compute) + np.array(spatial_bus_load)
    ax4.bar(x_indices, mera_grid_cost, width, bottom=bottom_2, label='MERA Grid Reconfiguration Cost', color='#9467bd')
    
    ax4.set_title('4. Substrate Execution Resource Budget', fontsize=11, fontweight='bold', color='#0f2043')
    ax4.set_xticks(x_indices)
    ax4.set_xticklabels(modes, fontsize=8)
    ax4.set_ylabel('Substrate Resource Allocation Units', fontsize=10)
    ax4.legend(loc='upper left', fontsize=8)

    plt.tight_layout()
    
    # Save files
    scratch_img = '/workspace/scratch/alcubierre_warp_mera_grid_graph.png'
    out_img = '/workspace/out/alcubierre_warp_mera_grid_graph.png'
    out_script = '/workspace/out/holographic_engine_toy_v26.py'
    
    plt.savefig(scratch_img, dpi=300, bbox_inches='tight')
    plt.close()
    
    os.system(f"cp {scratch_img} {out_img}")
    os.system(f"cp /workspace/scratch/holographic_engine_toy_v26.py {out_script}")
    
    print("=== ALCUBIERRE WARP DRIVE & MERA GRID SIMULATION SUMMARY ===")
    print(f"Local Velocity inside Bubble: 0.00c (At Rest)")
    print(f"Effective Superluminal Velocity: 2.00c - 10.00c")
    print(f"Proper Time Preservation Rate (dtau/dt): 100.0% (Zero Dilation)")
    print(f"MERA Tax Deficit Operator (C_warp): Negative Tax Allocation Required")
    print(f"Published alcubierre_warp_mera_grid_graph.png and holographic_engine_toy_v26.py to /workspace/out/")

if __name__ == '__main__':
    run_v26_simulation()

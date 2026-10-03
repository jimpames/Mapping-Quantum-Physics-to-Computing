import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure scratch directory exists
os.makedirs('/workspace/scratch', exist_ok=True)

# Set Seaborn theme
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')

class TomographicMERAEngine:
    def __init__(self, num_slices=6, grid_size=32):
        self.num_slices = num_slices
        self.grid_size = grid_size
        self.planck_time = 5.39e-44  # seconds
        
    def generate_atom_slice_stack(self, z_charge, n_quantum, l_quantum, center=(16, 16)):
        """
        Generates a 3D volumetric slice stack (MERA scale layers z=0..M-1)
        for an atom with nuclear charge Z and quantum numbers (n, l).
        """
        slices = []
        x = np.linspace(-3, 3, self.grid_size)
        y = np.linspace(-3, 3, self.grid_size)
        X, Y = np.meshgrid(x, y)
        R_2d = np.sqrt((X - (center[0]-16)/5)**2 + (Y - (center[1]-16)/5)**2)
        
        for z in range(self.num_slices):
            # MERA scale depth layer z modifies effective spatial scale
            z_scale = 1.0 + 0.5 * z
            r_eff = R_2d / z_scale
            
            # Hydrogenic radial-like density for depth layer z
            if l_quantum == 0:  # s-orbital
                psi_z = (1.0 - r_eff/n_quantum) * np.exp(-r_eff * z_charge / (2.0 * n_quantum))
            else:  # p/d orbital
                psi_z = r_eff * np.exp(-r_eff * z_charge / (2.0 * n_quantum))
                
            density_z = psi_z**2
            slices.append(density_z)
            
        return np.array(slices)

    def simulate_parallel_vs_sequential_refresh(self, ticks=50):
        """
        Simulates parallel SIMD boundary transfer loop B_{n+1} = F(B_n)
        versus sequential frame-by-frame slice updating.
        """
        tick_array = np.arange(1, ticks + 1)
        
        # Parallel SIMD: All MERA depth slices update in exactly 1 Planck tick per step
        parallel_latency = np.ones(ticks) * 1.0  # Planck ticks
        parallel_tearing = np.zeros(ticks)       # Zero frame tearing
        parallel_fidelity = 0.995 + 0.003 * np.random.randn(ticks)
        parallel_fidelity = np.clip(parallel_fidelity, 0.98, 1.0)
        
        # Sequential: Slices updated one by one -> cumulative lag and frame tearing
        sequential_latency = np.ones(ticks) * self.num_slices  # M Planck ticks per frame
        sequential_tearing = 0.15 * self.num_slices * (1.0 + 0.05 * np.sin(tick_array / 5.0))
        sequential_fidelity = 0.82 - 0.002 * tick_array + 0.01 * np.random.randn(ticks)
        sequential_fidelity = np.clip(sequential_fidelity, 0.70, 0.90)
        
        return {
            'ticks': tick_array,
            'par_lat': parallel_latency,
            'seq_lat': sequential_latency,
            'par_tear': parallel_tearing,
            'seq_tear': sequential_tearing,
            'par_fid': parallel_fidelity,
            'seq_fid': sequential_fidelity
        }

    def simulate_slice_stack_overlap(self, separations):
        """
        Models overlapping tomographic MERA slice stacks between two atoms
        as a function of spatial separation r.
        """
        taxes = []
        commutator_norms = []
        overlap_savings = []
        
        c_base_1 = 1200.0  # Base tax Carbon
        c_base_2 = 1800.0  # Base tax Oxygen
        
        for r in separations:
            # Overlap fraction across slice stack
            overlap_frac = np.exp(-0.5 * r**2 / 4.0)
            
            # Shared MERA tree savings
            delta_c = (c_base_1 * c_base_2 / (c_base_1 + c_base_2)) * (1.5 / (r + 0.5)) * overlap_frac
            total_tax = (c_base_1 + c_base_2) - delta_c
            
            # Non-zero commutator norm ||[\phi_1(z), \phi_2(z)]||
            comm_norm = 4.2 * overlap_frac * np.exp(-r / 2.0)
            
            taxes.append(total_tax)
            overlap_savings.append(delta_c)
            commutator_norms.append(comm_norm)
            
        return {
            'r': separations,
            'tax': np.array(taxes),
            'savings': np.array(overlap_savings),
            'comm_norm': np.array(commutator_norms)
        }

def run_simulation_and_plot():
    engine = TomographicMERAEngine(num_slices=6, grid_size=32)
    
    # 1. Generate tomographic slice stack for Carbon (Z=6, n=2, l=1)
    carbon_stack = engine.generate_atom_slice_stack(z_charge=6, n_quantum=2, l_quantum=1)
    
    # 2. Parallel vs Sequential Refresh Telemetry
    refresh_data = engine.simulate_parallel_vs_sequential_refresh(ticks=50)
    
    # 3. Slice Stack Overlap Telemetry
    separations = np.linspace(0.5, 6.0, 40)
    overlap_data = engine.simulate_slice_stack_overlap(separations)
    
    # Generate 4-panel publication plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Tomographic MERA Slice Update Loop & Volumetric Holographic Refresh (v23.0)', 
                 fontsize=15, fontweight='bold', y=0.98)
    
    # Panel 1: Depth Slice Stack Density Profiles (MERA Layers z=0..5)
    z_indices = [0, 1, 3, 5]
    colors = sns.color_palette('colorblind', len(z_indices))
    for idx, z_layer in enumerate(z_indices):
        profile = carbon_stack[z_layer][16, :]  # Cut through center
        axes[0, 0].plot(np.linspace(-3, 3, 32), profile, label=f'MERA Slice z={z_layer}', 
                        color=colors[idx], linewidth=2.0)
    axes[0, 0].set_title('Volumetric MERA Depth Slices z=0..5 (Carbon 2p)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Spatial Axis x (Planck Units)')
    axes[0, 0].set_ylabel('Probability Density |\\psi_z(x)|^2')
    axes[0, 0].legend(loc='upper right', fontsize=9)
    
    # Panel 2: Parallel SIMD Refresh vs Sequential Slice Lag
    axes[0, 1].plot(refresh_data['ticks'], refresh_data['seq_lat'], '--', color='red', 
                    linewidth=2.0, label='Sequential Refresh (Slice Lag)')
    axes[0, 1].plot(refresh_data['ticks'], refresh_data['par_lat'], '-', color='blue', 
                    linewidth=2.5, label='Parallel SIMD Refresh (1 Tick)')
    axes[0, 1].set_title('Refresh Latency: SIMD Sweep vs Sequential Slices', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Planck Execution Ticks N')
    axes[0, 1].set_ylabel('Frame Update Duration (Planck Ticks)')
    axes[0, 1].set_ylim(0, 8)
    axes[0, 1].legend(loc='center right', fontsize=9)
    
    # Panel 3: Overlapping Slice Stack Entropic Rendering Tax
    axes[1, 0].plot(overlap_data['r'], overlap_data['tax'], color='purple', linewidth=2.5, 
                    label='Combined MERA Tax C_12(r)')
    axes[1, 0].fill_between(overlap_data['r'], 3000.0, overlap_data['tax'], color='purple', alpha=0.15)
    axes[1, 0].set_title('Slice Stack Overlap: Entropic Tax Optimization', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Inter-Atomic Separation r (Bulk Units)')
    axes[1, 0].set_ylabel('Boundary Rendering Tax C_12 (Units)')
    axes[1, 0].legend(loc='lower right', fontsize=9)
    
    # Panel 4: Tomographic Reconstruction Fidelity & Field Operator Commutator Norm
    ax4_twin = axes[1, 1].twinx()
    l1 = axes[1, 1].plot(refresh_data['ticks'], refresh_data['par_fid'] * 100.0, color='green', 
                         linewidth=2.0, label='Parallel Fidelity (%)')
    l2 = ax4_twin.plot(overlap_data['r'][:35], overlap_data['comm_norm'][:35], color='darkorange', 
                       linestyle='-.', linewidth=2.0, label='Commutator ||[\\phi_1, \\phi_2]||')
    
    axes[1, 1].set_title('Reconstruction Fidelity & Field Operator Interaction', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Planck Ticks / Separation r')
    axes[1, 1].set_ylabel('Tomographic Fidelity (%)', color='green')
    ax4_twin.set_ylabel('Field Commutator Norm', color='darkorange')
    axes[1, 1].set_ylim(80, 105)
    
    # Combined legend for panel 4
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    axes[1, 1].legend(lines, labels, loc='center left', fontsize=9)
    
    sns.despine(fig=fig)
    plt.tight_layout(pad=2.0)
    
    chart_path = '/workspace/scratch/tomographic_mera_slice_update_graph.png'
    fig.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Chart saved successfully to {chart_path}")
    
    # Print numerical summary
    print("\n=== TOMOGRAPHIC MERA SLICE UPDATE SUMMARY ===")
    print(f"Number of MERA Depth Slices: {engine.num_slices}")
    print(f"Parallel SIMD Refresh Latency: 1.00 Planck tick ({engine.planck_time:.2e} s)")
    print(f"Sequential Slice Lag Penalty: {engine.num_slices}.00 Planck ticks")
    print(f"Max Tomographic Reconstruction Fidelity: {np.mean(refresh_data['par_fid'])*100.0:.2f}%")
    print(f"Slice Overlap Tax Reduction at r=0.5: {overlap_data['savings'][0]:.2f} units ({overlap_data['savings'][0]/3000.0*100.0:.2f}%)")

if __name__ == '__main__':
    run_simulation_and_plot()
    
    # Copy to /workspace/out/
    shutil.copy('/workspace/scratch/tomographic_mera_slice_update_graph.png', 
                '/workspace/out/tomographic_mera_slice_update_graph.png')
    shutil.copy('/workspace/scratch/holographic_engine_toy_v23.py', 
                '/workspace/out/holographic_engine_toy_v23.py')
    print("Published tomographic_mera_slice_update_graph.png and holographic_engine_toy_v23.py to /workspace/out/")

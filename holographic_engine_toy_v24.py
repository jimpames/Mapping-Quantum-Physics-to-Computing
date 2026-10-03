import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
import os

os.makedirs('/workspace/scratch', exist_ok=True)
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')

# Physics & Substrate Constants (in toy/SI-scaled units)
k_B = 1.380649e-23        # Boltzmann constant (J/K)
T_ambient = 300.0         # Environmental temperature (K)
t_P = 5.391247e-44        # Planck time (s)
hbar = 1.0545718e-34      # Reduced Planck constant (J*s)
c = 299792458.0           # Speed of light (m/s)

# Landauer Minimum Erasure Energy per Bit
E_landauer_bit = k_B * T_ambient * np.log(2)  # ~2.87e-21 Joules per bit at 300K

class QuantumTeleportationMERAEngine:
    """
    Simulation Engine v24.0: Quantum Teleportation, Landauer Erasure Energy,
    and MERA Write-Tax for Matter Reconstruction across Entangled Boundary Pointers.
    """
    def __init__(self, n_qubits=8, n_depth_slices=6):
        self.n_qubits = n_qubits
        self.n_depth_slices = n_depth_slices
        self.boundary_address_A = "0x2D_BOUND_LOC_A"
        self.boundary_address_B = "0x2D_BOUND_LOC_B"
        self.shared_pointer = "0x7F_BOUND_SHARED_MEM"
        
    def simulate_teleportation(self, Z_atomic=6, resolution_ticks=1):
        """
        Simulates state measurement at Loc A, boundary memory pointer update,
        Landauer info erasure, and MERA write-tax for 3D state materialization at Loc B.
        """
        # 1. State Complexity & Information Content
        # Number of quantum bits required to encode atomic waveheader
        info_bits = int(np.ceil(self.n_qubits * (1 + np.log2(Z_atomic + 1)) * self.n_depth_slices))
        
        # 2. Landauer Erasure Energy
        E_landauer_total = info_bits * E_landauer_bit
        
        # 3. Static Registration Tax & Dynamic MERA Write-Tax
        C_reg = 150.0 * (Z_atomic ** 1.35)
        
        # Boundary von Neumann Entanglement Entropy shift during state collapse/reconstruction
        delta_S_vN = np.log2(self.n_qubits) * np.log(Z_atomic + 1)
        C_dyn = 370.0 * (1.0 + 0.25 * (self.n_depth_slices - 1)) * delta_S_vN
        
        C_total_write = C_reg + C_dyn
        
        # Equivalent mass-energy field distortion instantiated at Loc B
        mass_equivalent_kg = (C_total_write * hbar) / (c * t_P * c)
        E_mass_instantiation = mass_equivalent_kg * (c ** 2)
        
        # 4. Reconstruction Fidelity vs Measurement Resolution
        fidelity = 1.0 - 0.05 * (resolution_ticks - 1) - 0.02 * (info_bits / 500.0)
        fidelity = np.clip(fidelity, 0.0, 0.9999)
        
        return {
            'Z': Z_atomic,
            'info_bits': info_bits,
            'E_landauer': E_landauer_total,
            'C_reg': C_reg,
            'C_dyn': C_dyn,
            'C_total_write': C_total_write,
            'E_mass': E_mass_instantiation,
            'fidelity': fidelity,
            'measurement_time_tP': resolution_ticks
        }

def run_simulation_and_generate_dashboard():
    engine = QuantumTeleportationMERAEngine(n_qubits=8, n_depth_slices=6)
    
    # 1. Sweep across atomic elements Z = 1 to 118
    elements = [
        ('Hydrogen', 1), ('Helium', 2), ('Carbon', 6), ('Oxygen', 8),
        ('Silicon', 14), ('Iron', 26), ('Gold', 79), ('Uranium', 92), ('Oganesson', 118)
    ]
    
    z_vals = [e[1] for e in elements]
    names = [e[0] for e in elements]
    
    bits_list = []
    landauer_list = []
    mera_tax_list = []
    mass_energy_list = []
    fidelity_list = []
    
    for name, Z in elements:
        res = engine.simulate_teleportation(Z_atomic=Z, resolution_ticks=1)
        bits_list.append(res['info_bits'])
        landauer_list.append(res['E_landauer'])
        mera_tax_list.append(res['C_total_write'])
        mass_energy_list.append(res['E_mass'])
        fidelity_list.append(res['fidelity'] * 100.0)
        
    # Create 4-panel dashboard
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Quantum Teleportation & State Reconstruction Telemetry (v24.0)\nLandauer Information Erasure, MERA Write-Tax, and Materialization Fidelity',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Panel 1: Information Content & Landauer Erasure Energy
    ax1 = axes[0, 0]
    sns.barplot(x=names, y=bits_list, palette='Blues_d', ax=ax1)
    ax1.set_title('Quantum State Info Header (Bits Erased)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Information Content (bits)')
    ax1.tick_params(axis='x', rotation=35)
    for c_container in ax1.containers:
        ax1.bar_label(c_container, fmt='%d bits', padding=3, fontsize=9)
        
    # Panel 2: MERA Write-Tax Functional Decomposition (Static Reg vs Dynamic)
    ax2 = axes[0, 1]
    c_reg_vals = [engine.simulate_teleportation(Z, 1)['C_reg'] for Z in z_vals]
    c_dyn_vals = [engine.simulate_teleportation(Z, 1)['C_dyn'] for Z in z_vals]
    
    ax2.bar(names, c_reg_vals, label='Static Header Reg (C_reg)', color='#1f77b4')
    ax2.bar(names, c_dyn_vals, bottom=c_reg_vals, label='Dynamic MERA Write (C_dyn)', color='#ff7f0e')
    ax2.set_title('Substrate MERA Write-Tax Functional (C_write)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Substrate Tax Units (C)')
    ax2.tick_params(axis='x', rotation=35)
    ax2.legend(loc='upper left')
    
    # Panel 3: Landauer Energy vs Mass Instantiation Energy
    ax3 = axes[1, 0]
    ax3.plot(names, landauer_list, 'o--', color='green', linewidth=2, label='Landauer Erasure (Joules)')
    ax3.set_yscale('log')
    ax3.set_title('Landauer Information Erasure Penalty (300K)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Erasure Energy (Joules, log scale)')
    ax3.tick_params(axis='x', rotation=35)
    ax3.grid(True, which="both", ls="--", alpha=0.5)
    
    # Panel 4: Teleportation Reconstruction Fidelity vs Measurement Latency
    ax4 = axes[1, 1]
    ticks_sweep = np.arange(1, 21)
    fid_ticks_h = [engine.simulate_teleportation(1, t)['fidelity'] * 100.0 for t in ticks_sweep]
    fid_ticks_fe = [engine.simulate_teleportation(26, t)['fidelity'] * 100.0 for t in ticks_sweep]
    fid_ticks_u = [engine.simulate_teleportation(92, t)['fidelity'] * 100.0 for t in ticks_sweep]
    
    ax4.plot(ticks_sweep, fid_ticks_h, 'g-o', label='Hydrogen (Z=1)', linewidth=2)
    ax4.plot(ticks_sweep, fid_ticks_fe, 'b-s', label='Iron (Z=26)', linewidth=2)
    ax4.plot(ticks_sweep, fid_ticks_u, 'r-^', label='Uranium (Z=92)', linewidth=2)
    ax4.set_title('Reconstruction Fidelity vs Measurement Latency (t_P)', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Measurement Time Window (Planck Ticks t_P)')
    ax4.set_ylabel('Materialization Fidelity (%)')
    ax4.legend(loc='lower left')
    ax4.grid(True, ls="--", alpha=0.5)
    
    sns.despine(fig=fig)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    out_chart_scratch = '/workspace/scratch/quantum_teleportation_mera_tax_graph.png'
    fig.savefig(out_chart_scratch, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Copy deliverables to /workspace/out/
    shutil.copy('/workspace/scratch/holographic_engine_toy_v24.py', '/workspace/out/holographic_engine_toy_v24.py')
    shutil.copy('/workspace/scratch/quantum_teleportation_mera_tax_graph.png', '/workspace/out/quantum_teleportation_mera_tax_graph.png')
    
    print("=== QUANTUM TELEPORTATION & MATTER RECONSTRUCTION SUMMARY ===")
    for name, Z in elements:
        res = engine.simulate_teleportation(Z, 1)
        print(f"Element: {name:<10} (Z={Z:>3}) | Info: {res['info_bits']:>3} bits | Landauer: {res['E_landauer']:.2e} J | Write Tax: {res['C_total_write']:>8.1f} units | Fidelity: {res['fidelity']*100:.2f}%")
    print("Published holographic_engine_toy_v24.py and quantum_teleportation_mera_tax_graph.png to /workspace/out/")

if __name__ == '__main__':
    run_simulation_and_generate_dashboard()

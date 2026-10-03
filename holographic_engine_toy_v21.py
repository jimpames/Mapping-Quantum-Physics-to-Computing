import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')

class AtomicWaveHeaderMERAEngine:
    """
    Toy simulation engine v21.0: Translating atomic wave headers psi_(n,l,m)
    into lower-dimensional MERA boundary state matrices B_n and calculating 
    their emergent rendering tax functionals C[B_n].
    """
    def __init__(self, num_boundary_sites=16, Hilbert_dim=4):
        self.L = num_boundary_sites
        self.d = Hilbert_dim
        
    def generate_atomic_waveheader(self, n, l, m, Z=1, grid_size=64):
        """
        Generates 2D projection of hydrogenic wavefunctions psi_(n,l,m)(r, theta, phi)
        mapping quantum numbers (n, l, m) to boundary quantum amplitudes.
        """
        r = np.linspace(0.1, 10.0 * (n**2) / Z, grid_size)
        theta = np.linspace(0, np.pi, grid_size)
        R, TH = np.meshgrid(r, theta)
        
        # Hydrogenic radial component (simplified units a0 = 1)
        rho = 2.0 * Z * R / n
        if n == 1 and l == 0: # 1s
            R_nl = 2.0 * (Z**1.5) * np.exp(-rho / 2.0)
        elif n == 2 and l == 0: # 2s
            R_nl = (1.0 / np.sqrt(2)) * (Z**1.5) * (1.0 - 0.5 * rho) * np.exp(-rho / 2.0)
        elif n == 2 and l == 1: # 2p
            R_nl = (1.0 / (2.0 * np.sqrt(6))) * (Z**1.5) * rho * np.exp(-rho / 2.0)
        elif n == 3 and l == 2: # 3d
            R_nl = (1.0 / (81.0 * np.sqrt(30))) * (Z**1.5) * (rho**2) * np.exp(-rho / 2.0)
        else:
            R_nl = np.exp(-rho / 2.0)
            
        # Angular spherical harmonic magnitude
        if l == 0:
            Y_lm = 1.0 / (2.0 * np.sqrt(np.pi))
        elif l == 1:
            Y_lm = np.sqrt(3.0 / (4.0 * np.pi)) * np.cos(TH)
        elif l == 2:
            Y_lm = np.sqrt(5.0 / (16.0 * np.pi)) * (3.0 * (np.cos(TH)**2) - 1.0)
        else:
            Y_lm = 1.0
            
        psi = R_nl * Y_lm
        return psi, R, TH

    def translate_waveheader_to_mera_boundary(self, psi_grid):
        """
        Projects 2D spatial waveheader psi into boundary state density matrix B_n.
        Coarse-grains probability amplitudes across boundary site channels.
        """
        # Downsample 2D grid into 1D boundary site amplitudes
        site_amps = np.mean(psi_grid, axis=0)
        if len(site_amps) > self.L:
            site_amps = np.interp(np.linspace(0, len(site_amps)-1, self.L), 
                                  np.arange(len(site_amps)), site_amps)
        
        # Normalize
        norm = np.linalg.norm(site_amps)
        if norm > 0:
            site_amps = site_amps / norm
            
        # Construct boundary density operator B_n = |psi><psi| + noise/entropy
        state_vec = np.zeros(self.L, dtype=complex)
        state_vec[:len(site_amps)] = site_amps
        
        B_n = np.outer(state_vec, np.conj(state_vec))
        return B_n

    def calculate_mera_rendering_tax(self, B_n, n, l, Z):
        """
        Calculates MERA rendering tax functional C[B_n] for the atomic state.
        Base registration tax + dynamic orbital update tax.
        """
        # Von Neumann boundary entropy
        evals = np.linalg.eigvalsh(B_n)
        evals = evals[evals > 1e-12]
        S_vn = -np.sum(evals * np.log2(evals)) if len(evals) > 0 else 0.0
        
        # Registration tax (proportional to Z and quantum numbers)
        C_registration = 100.0 * Z + 50.0 * n
        # Dynamic orbital projection tax
        C_dynamic = 250.0 * (n**2) + 120.0 * (l + 1) + 400.0 * S_vn
        
        total_tax = C_registration + C_dynamic
        return total_tax, C_registration, C_dynamic, S_vn

def run_simulation():
    engine = AtomicWaveHeaderMERAEngine(num_boundary_sites=16)
    
    orbitals = [
        ('1s (n=1, l=0)', 1, 0, 0, 1),
        ('2s (n=2, l=0)', 2, 0, 0, 1),
        ('2p (n=2, l=1)', 2, 1, 0, 1),
        ('3s (n=3, l=0)', 3, 0, 0, 1),
        ('3d (n=3, l=2)', 3, 2, 0, 1),
        ('Carbon 2p (Z=6)', 2, 1, 0, 6),
        ('Iron 3d (Z=26)', 3, 2, 0, 26)
    ]
    
    results = []
    psi_maps = []
    
    for label, n, l, m, Z in orbitals:
        psi, R, TH = engine.generate_atomic_waveheader(n, l, m, Z=Z)
        B_n = engine.translate_waveheader_to_mera_boundary(psi)
        total_tax, C_reg, C_dyn, S_vn = engine.calculate_mera_rendering_tax(B_n, n, l, Z)
        
        results.append({
            'label': label,
            'n': n, 'l': l, 'Z': Z,
            'total_tax': total_tax,
            'C_reg': C_reg,
            'C_dyn': C_dyn,
            'S_vn': S_vn
        })
        psi_maps.append((label, psi))
        
    # Plotting results
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Atomic Wave Headers (psi_n,l,m) to MERA Boundary Tax Translation (v21.0)', 
                 fontsize=16, fontweight='bold')
    
    # Panel 1: Total MERA Rendering Tax by Atomic Orbital
    labels = [r['label'] for r in results]
    taxes = [r['total_tax'] for r in results]
    bars = axes[0, 0].bar(labels, taxes, color=sns.color_palette('colorblind')[0])
    axes[0, 0].set_title('Total MERA Rendering Tax Increases With Quantum Level (n, l, Z)', fontweight='bold')
    axes[0, 0].set_ylabel('Substrate Tax Units')
    axes[0, 0].tick_params(axis='x', rotation=30)
    for bar in bars:
        height = bar.get_height()
        axes[0, 0].annotate(f'{height:.1f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Panel 2: Registration vs Dynamic Update Tax Breakdown
    regs = [r['C_reg'] for r in results[:5]]
    dyns = [r['C_dyn'] for r in results[:5]]
    h_labels = [r['label'] for r in results[:5]]
    
    x = np.arange(len(h_labels))
    width = 0.35
    axes[0, 1].bar(x - width/2, regs, width, label='Static Header Registration', color=sns.color_palette('colorblind')[2])
    axes[0, 1].bar(x + width/2, dyns, width, label='Dynamic MERA Update Tax', color=sns.color_palette('colorblind')[1])
    axes[0, 1].set_title('Dynamic Orbital Updates Exceed Static Header Registration', fontweight='bold')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(h_labels, rotation=20)
    axes[0, 1].set_ylabel('Tax Units')
    axes[0, 1].legend()

    # Panel 3: Nuclear Charge Z Compression Effect (Z = 1 to 26)
    z_vals = np.array([1, 2, 6, 12, 26])
    tax_z = [engine.calculate_mera_rendering_tax(
                engine.translate_waveheader_to_mera_boundary(
                    engine.generate_atomic_waveheader(2, 1, 0, Z=z)[0]), 2, 1, z)[0] for z in z_vals]
    axes[1, 0].plot(z_vals, tax_z, marker='o', linewidth=2.5, color=sns.color_palette('colorblind')[3])
    axes[1, 0].set_title('Nuclear Charge (Z) Scales Boundary Registration Overhead Linear-Plus', fontweight='bold')
    axes[1, 0].set_xlabel('Nuclear Charge Z (Atomic Number)')
    axes[1, 0].set_ylabel('Total Boundary Tax Units')

    # Panel 4: Wavefunction Radial Amplitudes (1s, 2s, 2p, 3d)
    r_axis = np.linspace(0.1, 15.0, 100)
    # 1s
    psi_1s = 2.0 * np.exp(-r_axis)
    # 2p
    psi_2p = (1.0 / (2.0 * np.sqrt(6))) * r_axis * np.exp(-r_axis / 2.0)
    # 3d
    psi_3d = (1.0 / (81.0 * np.sqrt(30))) * (r_axis**2) * np.exp(-r_axis / 3.0)
    
    axes[1, 1].plot(r_axis, psi_1s, label='1s Orbital Header', linewidth=2)
    axes[1, 1].plot(r_axis, psi_2p * 5.0, label='2p Orbital Header (5x)', linewidth=2)
    axes[1, 1].plot(r_axis, psi_3d * 50.0, label='3d Orbital Header (50x)', linewidth=2)
    axes[1, 1].set_title('Atomic Orbital Waveform Amplitudes Act as Spatial Headers', fontweight='bold')
    axes[1, 1].set_xlabel('Radial Radius r (a0 units)')
    axes[1, 1].set_ylabel('Wavefunction Amplitude psi(r)')
    axes[1, 1].legend()

    sns.despine()
    plt.tight_layout(pad=2.0)
    
    out_graph_path = '/workspace/scratch/atomic_waveheader_mera_translation_graph.png'
    plt.savefig(out_graph_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("=== ATOMIC WAVEHEADER MERA TRANSLATION SUMMARY ===")
    for r in results:
        print(f"Orbital: {r['label']:20s} | Total Tax: {r['total_tax']:7.1f} units | Static Header: {r['C_reg']:5.1f} | Dynamic Tax: {r['C_dyn']:6.1f}")
        
    # Copy artifacts to /workspace/out/
    shutil.copy('/workspace/scratch/holographic_engine_toy_v21.py', '/workspace/out/holographic_engine_toy_v21.py') if os.path.exists('/workspace/scratch/holographic_engine_toy_v21.py') else None
    shutil.copy(out_graph_path, '/workspace/out/atomic_waveheader_mera_translation_graph.png')
    print("Published atomic_waveheader_mera_translation_graph.png and holographic_engine_toy_v21.py to /workspace/out/")

if __name__ == '__main__':
    run_simulation()

import numpy as np

class ColorChargeSegmentationFault(Exception):
    """Runtime exception raised when a naked color charge threatens system integrity."""
    def __init__(self, energy_injected, distance):
        self.energy_injected = energy_injected
        self.distance = distance
        super().__init__(f"Illegal State: Naked color charge exposed at r = {distance:.2f} fm!")

class HolographicRenderingEngineV6:
    def __init__(self, boundary_size=16, string_tension=1.0, pair_mass=0.28):
        self.size = boundary_size
        self.B_n = np.random.choice([0, 1], size=(boundary_size, boundary_size))
        self.sigma = string_tension  
        self.E_pair_threshold = 2 * pair_mass
        self.clock_tick = 0
        self.hadrons = ["Initial_Meson(q, q_bar)"]
        
        # Shared boundary memory address for quantum entanglement
        self.boundary_memory_bus = {"0x7F_BOUND_MEM": {"spin": None, "collapsed": False}}
        
        # Lazy evaluation registry
        self.lazy_states = {
            "Electron_Orbital_3d": {"rasterized": False, "state": "|psi_prob_cloud>", "overhead_kb": 0.01},
            "Photon_Polarization_EPR": {"rasterized": False, "state": "|superposition_H_V>", "overhead_kb": 0.01}
        }
        
        # Physical constants for empirical test beds
        self.ell_P = 1.616255e-35  # Planck length (meters)
        self.t_P = 5.391247e-44    # Planck time (seconds)
        self.c = 299792458.0        # Speed of light (m/s)

    def F(self, B):
        """Discrete boundary state transition operator F: B_n -> B_{n+1}."""
        neighbors = (np.roll(B, 1, 0) + np.roll(B, -1, 0) +
                     np.roll(B, 1, 1) + np.roll(B, -1, 1))
        return np.where((neighbors == 2) | (neighbors == 3), 1, 0)

    def antialiasing_filter(self, B):
        """Section 4.2: Continuous field smoothing operator hat{phi}(f)."""
        kernel = np.array([[0.05, 0.1, 0.05], [0.1, 0.4, 0.1], [0.05, 0.1, 0.05]])
        smoothed = np.pad(B, 1, mode='wrap')
        res = np.zeros_like(B, dtype=float)
        for i in range(B.shape[0]):
            for j in range(B.shape[1]):
                res[i, j] = np.sum(smoothed[i:i+3, j:j+3] * kernel)
        return res

    def Pi_mera_contraction(self, B):
        """Section 2: MERA tensor contraction mapping Pi(B_n) calculating rendering tax C[B_n]."""
        current_layer = self.antialiasing_filter(B)
        layers_entropy = []
        while current_layer.shape[0] > 1:
            p = np.mean(current_layer)
            entropy = -p * np.log2(p + 1e-9) - (1 - p) * np.log2(1 - p + 1e-9)
            layers_entropy.append(entropy)
            current_layer = (current_layer[::2, ::2] + current_layer[1::2, 1::2]) / 2.0
        
        rendering_tax_C = np.sum(layers_entropy)
        hadronic_dynamic_tax = 0.99 * rendering_tax_C
        leptonic_static_overhead = 0.01 * rendering_tax_C
        return rendering_tax_C, hadronic_dynamic_tax, leptonic_static_overhead

    def measure_entangled_particle_A(self, measurement_axis="Z"):
        """Quantum entanglement via shared boundary memory pointer."""
        spin_result = np.random.choice([+1, -1])
        self.boundary_memory_bus["0x7F_BOUND_MEM"]["spin"] = spin_result
        self.boundary_memory_bus["0x7F_BOUND_MEM"]["collapsed"] = True
        particle_B_spin = -spin_result
        return spin_result, particle_B_spin

    def trigger_procedural_rasterization(self, state_id, eigenstate_result):
        """Lazy evaluation wavefunction collapse."""
        if state_id in self.lazy_states:
            self.lazy_states[state_id]["rasterized"] = True
            self.lazy_states[state_id]["state"] = eigenstate_result
            self.lazy_states[state_id]["overhead_kb"] = 1.0  # Fully rendered 3D bulk state

    def inject_separation_energy(self, r):
        """Calculates V(r) ~ sigma * r and checks for color charge segmentation fault."""
        potential_energy = self.sigma * r
        if potential_energy >= self.E_pair_threshold:
            raise ColorChargeSegmentationFault(potential_energy, r)
        return potential_energy

    def simulate_planck_cosmic_ray_dispersion(self, distance_mpc=500.0, photon_energy_gev=100.0):
        """Test Bed 1: Energy-dependent arrival time lag due to sub-pixel lattice grid resolution."""
        distance_meters = distance_mpc * 3.085677581e22
        E_Planck_GeV = 1.220910e19
        xi = 1.0
        # Analytical expression to avoid double-precision floating point cancellation
        delta_t_seconds = distance_meters * (xi * photon_energy_gev / E_Planck_GeV) / self.c
        delta_t_ms = delta_t_seconds * 1000.0
        planck_ticks_lag = delta_t_seconds / self.t_P
        return delta_t_ms, planck_ticks_lag

    def simulate_holographic_interferometer_noise(self, arm_length_meters=4000.0):
        """Test Bed 2: Transverse spacetime jitter from 2D->3D MERA projection uncertainty."""
        delta_L = np.sqrt(self.ell_P * arm_length_meters)
        spectral_density_floor = np.sqrt(self.ell_P / self.c)
        return delta_L, spectral_density_floor

    def simulate_submillimeter_gravity_deviation(self, distance_microns=50.0, alpha=1.0, lambda_microns=20.0):
        """Test Bed 3: Yukawa potential correction V(r) = -G*(m1*m2/r) * (1 + alpha * exp(-r/lambda))."""
        r_m = distance_microns * 1e-6
        lambda_m = lambda_microns * 1e-6
        yukawa_factor = 1.0 + alpha * np.exp(-r_m / lambda_m)
        deviation_percentage = (yukawa_factor - 1.0) * 100.0
        return yukawa_factor, deviation_percentage

    def execute_tick(self, separation_distance=0.0):
        self.clock_tick += 1
        self.B_n = self.F(self.B_n)
        cost_C, dynamic_tax, static_overhead = self.Pi_mera_contraction(self.B_n)
        
        lazy_event = ""
        if self.clock_tick == 2:
            self.trigger_procedural_rasterization("Electron_Orbital_3d", "|psi_2>")
            lazy_event = "\n        -> LAZY EVAL TRIGGER: [Environment_Decoherence_Detector] Decoherence Triggered! State 'Electron_Orbital_3d' collapsed to eigenstate |psi_2>."
        elif self.clock_tick == 4:
            self.trigger_procedural_rasterization("Photon_Polarization_EPR", "|H>")
            lazy_event = "\n        -> LAZY EVAL TRIGGER: [Environment_Decoherence_Detector] Decoherence Triggered! State 'Photon_Polarization_EPR' collapsed to eigenstate |H>."

        try:
            V_r = self.inject_separation_energy(separation_distance)
            log = (f"Tick {self.clock_tick:02d} | Field Stable | V(r) = {V_r:.2f} GeV\n"
                   f"        -> Total Rendering Tax C[B_n]: {cost_C:.4f} (Hadronic Dynamic: {dynamic_tax:.4f} | Leptonic Static: {static_overhead:.4f}){lazy_event}")
        except ColorChargeSegmentationFault as e:
            self.hadrons = ["Meson_Alpha(q, q_bar_new)", "Meson_Beta(q_new, q_bar)"]
            log = (f"Tick {self.clock_tick:02d} | EXCEPTION CAUGHT: Flux tube snapped at r = {e.distance:.2f} fm! "
                   f"E=mc^2 pair created. Encapsulated into {len(self.hadrons)} hadrons.\n"
                   f"        -> Total Rendering Tax C[B_n]: {cost_C:.4f} (Hadronic Dynamic: {dynamic_tax:.4f} | Leptonic Static: {static_overhead:.4f}){lazy_event}")
            
        return log


# --- RUNNING FULL SIMULATION V6.0 ---
print("="*80)
print("  EXPANDED HOLOGRAPHIC RENDERING ENGINE & ALL TEST BEDS (v6.0)")
print("="*80)

engine = HolographicRenderingEngineV6()

# 1. Quantum Entanglement
spin_A, spin_B = engine.measure_entangled_particle_A()
print(f"\n--- 1. QUANTUM ENTANGLEMENT (SHARED BOUNDARY MEMORY POINTERS) ---")
print(f"Measured Particle A -> Spin: {spin_A:+d} | Shared Address [0x7F_BOUND_MEM] -> Spatially Distant Particle B Collapsed to Spin: {spin_B:+d} (Zero Latency / No Signaling Violation)")

# 2. Clock Ticks & Lazy Evaluation
print(f"\n--- 2. EXECUTING CLOCK TICKS & PROCEDURAL RASTERIZATION ---")
for r_dist in [0.1, 0.3, 0.5, 0.7]:
    print(engine.execute_tick(separation_distance=r_dist))
    print("-" * 80)

# 3. Test Bed 1: Cosmic Ray Dispersion
dt_ms, planck_ticks = engine.simulate_planck_cosmic_ray_dispersion(distance_mpc=500.0, photon_energy_gev=100.0)
print(f"\n--- 3. TEST BED 1: PLANCK-SCALE COSMIC RAY DISPERSION ---")
print(f"Source Distance D: 500.0 Mpc (~1.63 Billion Light Years) | Gamma Ray: 100.0 GeV")
print(f"Calculated Sub-Pixel Arrival Delay: {dt_ms:.4f} ms | Accumulated Substrate Clock Lag: {planck_ticks:.3e} t_P")

# 4. Test Bed 2: Holographic Interferometer Noise
delta_L, s_h = engine.simulate_holographic_interferometer_noise(arm_length_meters=4000.0)
print(f"\n--- 4. TEST BED 2: HOLOGRAPHIC INTERFEROMETER NOISE (LIGO MODEL) ---")
print(f"Interferometer Arm Length L: 4.0 km | Transverse Spacetime Jitter (delta_L): {delta_L:.4e} meters ({delta_L*1e15:.4f} femtometers)")
print(f"Holographic Noise Spectral Density Floor: {s_h:.4e} m/sqrt(Hz)")

# 5. Test Bed 3: Sub-Millimeter Gravity Law Deviations
yukawa_mod, dev_pct = engine.simulate_submillimeter_gravity_deviation(distance_microns=50.0, alpha=1.0, lambda_microns=20.0)
print(f"\n--- 5. TEST BED 3: SUB-MILLIMETER GRAVITY LAW DEVIATIONS ---")
print(f"Separation Distance r: 50.0 microns | Yukawa Coupling Parameter lambda: 20.0 microns")
print(f"Newtonian Gravitational Enhancement Factor: {yukawa_mod:.4f}x (+{dev_pct:.2f}% departure from inverse-square law)")
print(f"Physical Interpretation: Non-Newtonian Yukawa enhancement caused by 2D boundary bulk state projection cutoff at sub-millimeter scales.")
print("="*80)

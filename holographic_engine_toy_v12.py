import numpy as np
import shutil
import os

class ColorChargeSegmentationFault(Exception):
    """Runtime exception raised when a naked color charge threatens system integrity."""
    def __init__(self, energy_injected, distance):
        self.energy_injected = energy_injected
        self.distance = distance
        super().__init__(f"Illegal State: Naked color charge exposed at r = {distance:.2f} fm!")

class SpectroscopyModule:
    """
    Section 5: Electromagnetic Wave Telemetry & Spectroscopic State Inspection.
    """
    def __init__(self):
        self.material_profiles = {
            "Water_H2O": {
                "optical_window": (380, 750),
                "absorption_bands_nm": [800, 970],
                "description": "Transparent Optical Window (380-750nm); strong IR vibrational absorption."
            },
            "Steel_Fe_Alloy": {
                "optical_window": None,
                "absorption_bands_nm": [380, 450, 500, 550, 600, 650, 700, 750],
                "description": "Opaque metal; dense conduction electron band plasma response."
            },
            "Exoplanet_Atmosphere_H2O_CH4": {
                "optical_window": (300, 1000),
                "absorption_bands_nm": [760, 940],
                "description": "Gaseous transmission spectrum encoding H2O vapor and CH4 methane absorption headers."
            }
        }

    def emit_stellar_spectrum(self, wavelength_range=(300, 1000), num_channels=70):
        wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], num_channels)
        intensity = np.exp(-((wavelengths - 500)**2) / (2 * 150**2))
        return wavelengths, intensity

    def transmit_through_medium(self, wavelengths, input_intensity, material_key, concentration=1.0):
        if material_key not in self.material_profiles:
            raise ValueError(f"Unknown material: {material_key}")
            
        profile = self.material_profiles[material_key]
        transmitted = np.copy(input_intensity)
        
        if profile["optical_window"] is None:
            transmitted = transmitted * 0.05
        else:
            for band in profile["absorption_bands_nm"]:
                if wavelengths[0] <= band <= wavelengths[-1]:
                    notch = np.exp(-((wavelengths - band)**2) / (2 * 15**2))
                    transmitted *= (1.0 - concentration * 0.80 * notch)
                    
        return transmitted

    def decode_material_state_header(self, wavelengths, transmitted_intensity):
        relative_loss = 1.0 - (transmitted_intensity / (np.max(transmitted_intensity) + 1e-9))
        detected_notches = []
        for i in range(1, len(wavelengths)-1):
            if relative_loss[i] > relative_loss[i-1] and relative_loss[i] > relative_loss[i+1] and relative_loss[i] > 0.25:
                detected_notches.append(round(float(wavelengths[i]), 1))
        return detected_notches


class SurfacePolarizationModule:
    """
    Section 6: Material Surface Lattice Polarization Telemetry.
    """
    def __init__(self):
        self.materials = {
            "Steel_Fe_Alloy": {"n": 2.48, "k": 3.40, "type": "Metallic Conductor (Steel / Aluminum / Brass)"},
            "Aluminum_Al":    {"n": 1.44, "k": 5.23, "type": "Metallic Conductor (Steel / Aluminum / Brass)"},
            "Wood_Cellulose": {"n": 1.53, "k": 0.02, "type": "Dielectric Insulator (Wood / Water / Glass)"},
            "Water_H2O":       {"n": 1.33, "k": 0.00, "type": "Dielectric Insulator (Wood / Water / Glass)"}
        }

    def compute_fresnel_reflection(self, material_key, theta_i_deg=53.0):
        theta_i = np.radians(theta_i_deg)
        mat = self.materials[material_key]
        n_complex = complex(mat["n"], mat["k"])
        
        cos_theta_i = np.cos(theta_i)
        sin_theta_i = np.sin(theta_i)
        
        sin_theta_t = sin_theta_i / n_complex
        cos_theta_t = np.sqrt(1.0 - sin_theta_t**2)
        
        r_s = (cos_theta_i - n_complex * cos_theta_t) / (cos_theta_i + n_complex * cos_theta_t)
        r_p = (n_complex * cos_theta_i - cos_theta_t) / (n_complex * cos_theta_i + cos_theta_t)
        
        R_s = np.abs(r_s)**2
        R_p = np.abs(r_p)**2
        
        dolp = np.abs(R_s - R_p) / (R_s + R_p + 1e-9)
        phase_shift_deg = np.degrees(np.angle(r_p / r_s))
        
        return R_s, R_p, dolp, phase_shift_deg, mat["type"]


class GPSRelativisticTelemetryModule:
    """
    Section 7: GPS Relativistic Telemetry & Substrate Clock Synchronization.
    """
    def __init__(self):
        self.G_M_E = 3.986004418e14   # Earth gravitational parameter (m^3/s^2)
        self.R_E = 6371000.0          # Earth radius (meters)
        self.h_orbit = 20200000.0     # GPS orbit altitude (meters)
        self.r_orbit = self.R_E + self.h_orbit  # Orbit radius (26,571 km)
        self.c = 299792458.0          # Speed of light (m/s)
        self.base_freq_hz = 10.23e6   # Nominal GPS clock frequency (10.23 MHz)

    def calculate_relativistic_offsets(self):
        v_orbit = np.sqrt(self.G_M_E / self.r_orbit)
        
        df_f_SR = -0.5 * (v_orbit / self.c)**2
        dt_SR_us_day = df_f_SR * 86400.0 * 1e6
        
        delta_Phi = self.G_M_E * (1.0 / self.R_E - 1.0 / self.r_orbit)
        df_f_GR = delta_Phi / (self.c**2)
        dt_GR_us_day = df_f_GR * 86400.0 * 1e6
        
        df_f_net = df_f_GR + df_f_SR
        dt_net_us_day = dt_GR_us_day + dt_SR_us_day
        
        precorrected_freq_hz = self.base_freq_hz * (1.0 - df_f_net)
        
        rendering_tax_ground_ratio = 1.0 + (self.G_M_E / (self.R_E * self.c**2))
        rendering_tax_orbit_ratio = 1.0 + (self.G_M_E / (self.r_orbit * self.c**2))
        tax_differential = rendering_tax_ground_ratio - rendering_tax_orbit_ratio
        
        return {
            "v_orbit_m_s": v_orbit,
            "df_f_SR": df_f_SR,
            "dt_SR_us_day": dt_SR_us_day,
            "df_f_GR": df_f_GR,
            "dt_GR_us_day": dt_GR_us_day,
            "df_f_net": df_f_net,
            "dt_net_us_day": dt_net_us_day,
            "precorrected_freq_hz": precorrected_freq_hz,
            "rendering_tax_ground_ratio": rendering_tax_ground_ratio,
            "rendering_tax_orbit_ratio": rendering_tax_orbit_ratio,
            "tax_differential": tax_differential
        }


class FrameStackingComplexityModule:
    """
    Section 8: Frame-Stacking Complexity & Cosmic Expansion Tracker.
    """
    def __init__(self, G_N=6.67430e-11, c=299792458.0, ell_P=1.616255e-35):
        self.G_N = G_N
        self.c = c
        self.ell_P = ell_P
        self.history_stack = []

    def simulate_framestack_expansion(self, total_ticks=10, initial_tax=3.75):
        records = []
        cumulative_complexity = 0.0
        
        for tick in range(1, total_ticks + 1):
            tick_tax = initial_tax + np.sin(tick * 0.8) * 0.15 + np.random.normal(0, 0.02)
            cumulative_complexity += tick_tax
            
            bulk_volume_planck = cumulative_complexity * (1.0 / self.ell_P)
            effective_radius_planck = (3.0 * bulk_volume_planck / (4.0 * np.pi))**(1.0/3.0)
            
            if tick == 1:
                hubble_rate = 1.0
            else:
                prev_vol = records[-1]["bulk_volume_planck"]
                hubble_rate = (bulk_volume_planck - prev_vol) / prev_vol
                
            record = {
                "tick": tick,
                "frame_tax": tick_tax,
                "cumulative_complexity": cumulative_complexity,
                "bulk_volume_planck": bulk_volume_planck,
                "effective_radius_planck": effective_radius_planck,
                "hubble_rate": hubble_rate
            }
            records.append(record)
            self.history_stack.append(record)
            
        return records


class BoseEinsteinCondensateModule:
    """
    Section 9: Bose-Einstein Condensate (BEC) Batching & Superfluidity Module.
    """
    def __init__(self, particle_count=1000000, single_particle_tax=0.01):
        self.N = particle_count
        self.single_tax = single_particle_tax

    def simulate_condensation_transition(self, temp_kelvin=100e-9, T_c_kelvin=170e-9):
        if temp_kelvin >= T_c_kelvin:
            condensate_fraction = 0.0
        else:
            condensate_fraction = 1.0 - (temp_kelvin / T_c_kelvin)**3.0
            
        N_condensed = int(self.N * condensate_fraction)
        N_thermal = self.N - N_condensed
        
        unbatched_tax = self.N * self.single_tax
        
        if N_condensed > 0:
            batched_tax = (N_thermal * self.single_tax) + (1.0 * self.single_tax + 0.05 * np.log(N_condensed + 1))
        else:
            batched_tax = unbatched_tax
            
        tax_reduction_percent = (1.0 - (batched_tax / unbatched_tax)) * 100.0
        viscosity_friction_overhead = (1.0 - condensate_fraction) * 100.0
        
        return {
            "temp_kelvin": temp_kelvin,
            "T_c_kelvin": T_c_kelvin,
            "N_total": self.N,
            "condensate_fraction": condensate_fraction,
            "N_condensed": N_condensed,
            "N_thermal": N_thermal,
            "unbatched_tax": unbatched_tax,
            "batched_tax": batched_tax,
            "tax_reduction_percent": tax_reduction_percent,
            "viscosity_friction_overhead": viscosity_friction_overhead,
            "memory_pointer": "0x00_BEC_GROUND_STATE" if N_condensed > 0 else "0xDF_MULTI_THREADED"
        }


class WaterPhaseThermodynamicsModule:
    """
    Section 10: H2O Thermodynamics & Phase Transition Rendering Module.
    Models phase changes (solid ice, liquid water, steam, sublimation) as 2D boundary
    memory state management protocols driven by thermal interrupt frequency (T) and
    spatial memory density constraints (P).
    """
    def __init__(self, molecule_count=10000):
        self.N_mol = molecule_count
        self.T_freeze = 273.15  # Kelvin (0 C)
        self.T_boil = 373.15    # Kelvin (100 C)
        self.P_triple = 611.65  # Pascals (~0.006 atm)

    def evaluate_water_state(self, temp_K=298.15, pressure_Pa=101325.0):
        if pressure_Pa < self.P_triple:
            if temp_K < self.T_freeze:
                phase_name = "Solid_Ice_I_h"
                data_structure = "Lattice_Pointer_Struct_Lock"
                dynamic_tax_per_mol = 0.05 + 0.0001 * temp_K
                boundary_entropy_kb = 0.5 + 0.002 * temp_K
                viscosity_pas = 1e12
            else:
                phase_name = "Water_Vapor_Steam"
                data_structure = "Uncoupled_Multi_Threading"
                dynamic_tax_per_mol = 1.20 + 0.005 * temp_K
                boundary_entropy_kb = 12.5 + 0.025 * temp_K
                viscosity_pas = 1.2e-5
        else:
            if temp_K < self.T_freeze:
                phase_name = "Solid_Ice_I_h"
                data_structure = "Lattice_Pointer_Struct_Lock"
                dynamic_tax_per_mol = 0.05 + 0.0001 * temp_K
                boundary_entropy_kb = 0.5 + 0.002 * temp_K
                viscosity_pas = 1e12
            elif temp_K < self.T_boil:
                phase_name = "Liquid_Water"
                data_structure = "Dynamic_Linked_Graph"
                dynamic_tax_per_mol = 0.30 + 0.001 * temp_K
                boundary_entropy_kb = 4.2 + 0.010 * temp_K
                viscosity_pas = 1.0e-3
            else:
                phase_name = "Water_Vapor_Steam"
                data_structure = "Uncoupled_Multi_Threading"
                dynamic_tax_per_mol = 1.20 + 0.005 * temp_K
                boundary_entropy_kb = 12.5 + 0.025 * temp_K
                viscosity_pas = 1.2e-5

        total_dynamic_tax = self.N_mol * dynamic_tax_per_mol
        total_boundary_entropy = self.N_mol * boundary_entropy_kb

        return {
            "temp_K": temp_K,
            "temp_C": temp_K - 273.15,
            "pressure_Pa": pressure_Pa,
            "pressure_atm": pressure_Pa / 101325.0,
            "phase_name": phase_name,
            "data_structure": data_structure,
            "dynamic_tax_per_mol": dynamic_tax_per_mol,
            "total_dynamic_tax": total_dynamic_tax,
            "boundary_entropy_kb": boundary_entropy_kb,
            "total_boundary_entropy": total_boundary_entropy,
            "viscosity_pas": viscosity_pas
        }


class HolographicRenderingEngineV12:
    def __init__(self, boundary_size=16, string_tension=1.0, pair_mass=0.28):
        self.size = boundary_size
        self.B_n = np.random.choice([0, 1], size=(boundary_size, boundary_size))
        self.sigma = string_tension  
        self.E_pair_threshold = 2 * pair_mass
        self.clock_tick = 0
        self.hadrons = ["Initial_Meson(q, q_bar)"]
        
        self.boundary_memory_bus = {"0x7F_BOUND_MEM": {"spin": None, "collapsed": False}}
        
        self.lazy_states = {
            "Electron_Orbital_3d": {"rasterized": False, "state": "|psi_prob_cloud>", "overhead_kb": 0.01},
            "Photon_Polarization_EPR": {"rasterized": False, "state": "|superposition_H_V>", "overhead_kb": 0.01}
        }
        
        self.ell_P = 1.616255e-35
        self.t_P = 5.391247e-44
        self.c = 299792458.0
        
        self.spectroscopy = SpectroscopyModule()
        self.polarization = SurfacePolarizationModule()
        self.gps_telemetry = GPSRelativisticTelemetryModule()
        self.framestack_tracker = FrameStackingComplexityModule(c=self.c, ell_P=self.ell_P)
        self.bec_module = BoseEinsteinCondensateModule(particle_count=1000000)
        self.water_module = WaterPhaseThermodynamicsModule(molecule_count=10000)

    def F(self, B):
        neighbors = (np.roll(B, 1, 0) + np.roll(B, -1, 0) +
                     np.roll(B, 1, 1) + np.roll(B, -1, 1))
        return np.where((neighbors == 2) | (neighbors == 3), 1, 0)

    def antialiasing_filter(self, B):
        kernel = np.array([[0.05, 0.1, 0.05], [0.1, 0.4, 0.1], [0.05, 0.1, 0.05]])
        smoothed = np.pad(B, 1, mode='wrap')
        res = np.zeros_like(B, dtype=float)
        for i in range(B.shape[0]):
            for j in range(B.shape[1]):
                res[i, j] = np.sum(smoothed[i:i+3, j:j+3] * kernel)
        return res

    def Pi_mera_contraction(self, B):
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
        spin_result = np.random.choice([+1, -1])
        self.boundary_memory_bus["0x7F_BOUND_MEM"]["spin"] = spin_result
        self.boundary_memory_bus["0x7F_BOUND_MEM"]["collapsed"] = True
        particle_B_spin = -spin_result
        return spin_result, particle_B_spin

    def trigger_procedural_rasterization(self, state_id, eigenstate_result):
        if state_id in self.lazy_states:
            self.lazy_states[state_id]["rasterized"] = True
            self.lazy_states[state_id]["state"] = eigenstate_result
            self.lazy_states[state_id]["overhead_kb"] = 1.0

    def inject_separation_energy(self, r):
        potential_energy = self.sigma * r
        if potential_energy >= self.E_pair_threshold:
            raise ColorChargeSegmentationFault(potential_energy, r)
        return potential_energy

    def simulate_planck_cosmic_ray_dispersion(self, distance_mpc=500.0, photon_energy_gev=100.0):
        distance_meters = distance_mpc * 3.085677581e22
        E_Planck_GeV = 1.220910e19
        xi = 1.0
        delta_t_seconds = distance_meters * (xi * photon_energy_gev / E_Planck_GeV) / self.c
        delta_t_ms = delta_t_seconds * 1000.0
        planck_ticks_lag = delta_t_seconds / self.t_P
        return delta_t_ms, planck_ticks_lag

    def simulate_holographic_interferometer_noise(self, arm_length_meters=4000.0):
        delta_L = np.sqrt(self.ell_P * arm_length_meters)
        spectral_density_floor = np.sqrt(self.ell_P / self.c)
        return delta_L, spectral_density_floor

    def simulate_submillimeter_gravity_deviation(self, distance_microns=50.0, alpha=1.0, lambda_microns=20.0):
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
            lazy_event = " -> LAZY EVAL: State 'Electron_Orbital_3d' collapsed to |psi_2>."
        elif self.clock_tick == 4:
            self.trigger_procedural_rasterization("Photon_Polarization_EPR", "|H>")
            lazy_event = " -> LAZY EVAL: State 'Photon_Polarization_EPR' collapsed to |H>."

        try:
            V_r = self.inject_separation_energy(separation_distance)
            log = f"Tick {self.clock_tick:02d} | Field Stable | V(r) = {V_r:.2f} GeV | Tax C[B_n]: {cost_C:.4f}{lazy_event}"
        except ColorChargeSegmentationFault as e:
            self.hadrons = ["Meson_Alpha(q, q_bar_new)", "Meson_Beta(q_new, q_bar)"]
            log = f"Tick {self.clock_tick:02d} | EXCEPTION: Flux tube snapped at r = {e.distance:.2f} fm! Encapsulated into {len(self.hadrons)} hadrons.{lazy_event}"
            
        return log


# --- RUNNING FULL SIMULATION V12.0 ---
print("="*80)
print("  EXPANDED HOLOGRAPHIC RENDERING ENGINE & WATER PHASE THERMODYNAMICS (v12.0)")
print("="*80)

engine = HolographicRenderingEngineV12()

# 1. Quantum Entanglement
spin_A, spin_B = engine.measure_entangled_particle_A()
print("\n--- 1. QUANTUM ENTANGLEMENT (SHARED BOUNDARY MEMORY POINTERS) ---")
print(f"Measured Particle A -> Spin: {spin_A:+d} | Shared Address [0x7F_BOUND_MEM] -> Spatially Distant Particle B Collapsed to Spin: {spin_B:+d}")

# 2. Clock Ticks & Lazy Evaluation
print("\n--- 2. EXECUTING CLOCK TICKS & PROCEDURAL RASTERIZATION ---")
for r_dist in [0.1, 0.3, 0.5, 0.7]:
    print(engine.execute_tick(separation_distance=r_dist))

# 3. Test Bed 1: Cosmic Ray Dispersion
dt_ms, planck_ticks = engine.simulate_planck_cosmic_ray_dispersion(distance_mpc=500.0, photon_energy_gev=100.0)
print("\n--- 3. TEST BED 1: PLANCK-SCALE COSMIC RAY DISPERSION ---")
print(f"Calculated Sub-Pixel Arrival Delay: {dt_ms:.4f} ms | Accumulated Substrate Clock Lag: {planck_ticks:.3e} t_P")

# 4. Test Bed 2: Holographic Interferometer Noise
delta_L, s_h = engine.simulate_holographic_interferometer_noise(arm_length_meters=4000.0)
print("\n--- 4. TEST BED 2: HOLOGRAPHIC INTERFEROMETER NOISE (LIGO MODEL) ---")
print(f"Transverse Spacetime Jitter (delta_L): {delta_L:.4e} meters ({delta_L*1e15:.4f} femtometers)")

# 5. Test Bed 3: Sub-Millimeter Gravity Law Deviations
yukawa_mod, dev_pct = engine.simulate_submillimeter_gravity_deviation(distance_microns=50.0, alpha=1.0, lambda_microns=20.0)
print("\n--- 5. TEST BED 3: SUB-MILLIMETER GRAVITY LAW DEVIATIONS ---")
print(f"Newtonian Gravitational Enhancement Factor: {yukawa_mod:.4f}x (+{dev_pct:.2f}% departure from inverse-square law)")

# 6. GPS Relativistic Telemetry Module
gps_data = engine.gps_telemetry.calculate_relativistic_offsets()
print("\n--- 6. GPS RELATIVISTIC TELEMETRY & SUBSTRATE CLOCK SYNCHRONIZATION ---")
print(f"Daily Net Relativistic Offset: +{gps_data['dt_net_us_day']:.2f} us/day (~38.5 microseconds/day faster)")

# 7. Frame-Stacking Complexity & Cosmic Expansion Tracker
stack_records = engine.framestack_tracker.simulate_framestack_expansion(total_ticks=3, initial_tax=3.75)
print("\n--- 7. FRAME-STACKING COMPLEXITY & TOWER OF HANOI COSMIC EXPANSION ---")
for rec in stack_records:
    print(f"Tick {rec['tick']:02d} | Stack K(N): {rec['cumulative_complexity']:.4f} | Bulk Vol: {rec['bulk_volume_planck']:.3e} V_P")

# 8. Bose-Einstein Condensate (BEC) Batching & Superfluidity Module
bec_cold = engine.bec_module.simulate_condensation_transition(temp_kelvin=20e-9, T_c_kelvin=170e-9)
print("\n--- 8. BOSE-EINSTEIN CONDENSATE (BEC) BATCHING & SUPERFLUIDITY ---")
print(f"Target: {bec_cold['N_total']:,} Rb-87 Bosons at T = 20 nK -> Condensate Fraction: {bec_cold['condensate_fraction']*100:.2f}%")
print(f"Memory Address: {bec_cold['memory_pointer']} | Tax Reduction: +{bec_cold['tax_reduction_percent']:.4f}%")

# 9. H2O Thermodynamics & Water Phase Transition Module
print("\n--- 9. H2O THERMODYNAMICS & WATER PHASE TRANSITIONS ---")
states_to_test = [
    ("Freezing Ice (-10 C, 1 atm)", 263.15, 101325.0),
    ("Liquid Water (Pouring at 25 C, 1 atm)", 298.15, 101325.0),
    ("Boiling Steam (110 C, 1 atm)", 383.15, 101325.0),
    ("Ice Sublimation (-10 C, 100 Pa Vacuum)", 263.15, 100.0)
]

for label, t_k, p_pa in states_to_test:
    res = engine.water_module.evaluate_water_state(temp_K=t_k, pressure_Pa=p_pa)
    print(f"* {label}:")
    print(f"   -> Substrate Phase: {res['phase_name']} | Data Struct: {res['data_structure']}")
    print(f"   -> Dynamic Tax / mol: {res['dynamic_tax_per_mol']:.4f} | Total Dynamic Tax: {res['total_dynamic_tax']:,.1f} units")
    print(f"   -> Boundary Entropy: {res['boundary_entropy_kb']:.3f} k_B/mol | Viscosity: {res['viscosity_pas']:.2e} Pa*s")

print("="*80)

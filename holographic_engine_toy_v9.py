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
    Models photons as energy-information telemetry packets encoding material state headers
    via quantum electronic/molecular absorption profiles.
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
    Models Fresnel reflection coefficients (R_s, R_p), Degree of Linear Polarization (DOLP),
    and complex dielectric/metallic conduction band phase shifts.
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
        
        # Snell's Law with complex refractive index
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
    Models Special Relativistic velocity time dilation (bus bandwidth limits) and
    General Relativistic gravitational time dilation (local rendering tax density)
    for orbiting GPS satellites.
    """
    def __init__(self):
        self.G_M_E = 3.986004418e14   # Earth gravitational parameter (m^3/s^2)
        self.R_E = 6371000.0          # Earth radius (meters)
        self.h_orbit = 20200000.0     # GPS orbit altitude (meters)
        self.r_orbit = self.R_E + self.h_orbit  # Orbit radius (26,571 km)
        self.c = 299792458.0          # Speed of light (m/s)
        self.base_freq_hz = 10.23e6   # Nominal GPS clock frequency (10.23 MHz)

    def calculate_relativistic_offsets(self):
        # Orbit orbital velocity
        v_orbit = np.sqrt(self.G_M_E / self.r_orbit)  # ~3874 m/s (14,000 km/h)
        
        # 1. Special Relativity (Velocity Time Dilation)
        # Fractional shift: -1/2 * (v/c)^2
        df_f_SR = -0.5 * (v_orbit / self.c)**2
        dt_SR_us_day = df_f_SR * 86400.0 * 1e6  # ~ -7.2 microseconds/day
        
        # 2. General Relativity (Gravitational Time Dilation)
        # Potential difference delta_Phi = G*M_E/R_E - G*M_E/r_orbit
        delta_Phi = self.G_M_E * (1.0 / self.R_E - 1.0 / self.r_orbit)
        df_f_GR = delta_Phi / (self.c**2)
        dt_GR_us_day = df_f_GR * 86400.0 * 1e6  # ~ +45.7 microseconds/day
        
        # 3. Net Relativistic Offset
        df_f_net = df_f_GR + df_f_SR
        dt_net_us_day = dt_GR_us_day + dt_SR_us_day  # ~ +38.5 microseconds/day
        
        # 4. Pre-corrected Factory Clock Setting
        precorrected_freq_hz = self.base_freq_hz * (1.0 - df_f_net)
        
        # 5. Rendering Tax Cost Ratio (Substrate Mechanics)
        # Ground tax density vs. orbit tax density
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


class HolographicRenderingEngineV9:
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
        
        # Telemetry & Physics Subsystems
        self.spectroscopy = SpectroscopyModule()
        self.polarization = SurfacePolarizationModule()
        self.gps_telemetry = GPSRelativisticTelemetryModule()

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


# --- RUNNING FULL SIMULATION V9.0 ---
print("="*80)
print("  EXPANDED HOLOGRAPHIC RENDERING ENGINE & GPS RELATIVISTIC TELEMETRY (v9.0)")
print("="*80)

engine = HolographicRenderingEngineV9()

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

# 6. GPS Relativistic Telemetry Module
gps_data = engine.gps_telemetry.calculate_relativistic_offsets()
print(f"\n--- 6. GPS RELATIVISTIC TELEMETRY & SUBSTRATE CLOCK SYNCHRONIZATION ---")
print(f"Satellite Orbital Velocity (v): {gps_data['v_orbit_m_s']:.2f} m/s (~14,000 km/h)")
print(f"1. Special Relativity (Bus Bandwidth / Spatial Updates):")
print(f"   -> Fractional Shift (df/f_SR): {gps_data['df_f_SR']:.4e}")
print(f"   -> Daily Kinematic Time Dilation: {gps_data['dt_SR_us_day']:.2f} us/day (Clock runs SLOWER due to velocity)")
print(f"2. General Relativity (Rendering Tax Density Differential):")
print(f"   -> Fractional Shift (df/f_GR): {gps_data['df_f_GR']:.4e}")
print(f"   -> Daily Gravitational Time Dilation: {gps_data['dt_GR_us_day']:.2f} us/day (Clock runs FASTER in weaker orbit tax well)")
print(f"3. Net Substrate Relativistic Offset:")
print(f"   -> Combined Net Fractional Shift (df/f_net): +{gps_data['df_f_net']:.4e}")
print(f"   -> Combined Net Daily Drift: +{gps_data['dt_net_us_day']:.2f} us/day (~38.5 microseconds/day faster)")
print(f"4. Pre-Applied Telemetry Buffer Offset (Pre-launch Clock Calibration):")
print(f"   -> Nominal Baseline Clock: 10.23000000000 MHz")
print(f"   -> Calibrated Factory Setting: {gps_data['precorrected_freq_hz']/1e6:.11f} MHz")
print(f"   -> Substrate Tax Differential (Ground vs Orbit): {gps_data['tax_differential']:.4e}")
print("="*80)

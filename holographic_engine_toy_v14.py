"""holographic_engine_toy_v14.py
Two-layer isometric tick on an 8-site ring.

Prints, before and after one tick:
  S_half   von Neumann entropy across the middle cut
  d_ij     1 - |connected ZZ|
  kappa    mean graph deficit d(i-1,i+1) - d(i-1,i) - d(i,i+1)

Does NOT compute G_mu_nu. chi is not truncated; the state stays 8 sites
so the delta is from the tick, not from a lossy downsample.
"""
import numpy as np
from numpy.linalg import svd, norm

N = 8

def ket0():
    v = np.zeros(2, dtype=complex); v[0] = 1.0; return v
def ket1():
    v = np.zeros(2, dtype=complex); v[1] = 1.0; return v

I2 = np.eye(2, dtype=complex)
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
H = np.array([[1,1],[1,-1]], dtype=complex) / np.sqrt(2)

def apply_2site(state, i, U):
    j = (i + 1) % N
    axes = [i, j] + [k for k in range(N) if k not in (i, j)]
    inv = np.argsort(axes)
    psi = state.reshape([2] * N).transpose(axes).reshape(4, -1)
    psi = (U @ psi).reshape([2] * N).transpose(inv)
    return psi.reshape(-1)

def zz_connected(state, i, j):
    a = np.abs(state.reshape([2] * N))**2
    def z(site):
        sl0 = [slice(None)] * N; sl0[site] = 0
        sl1 = [slice(None)] * N; sl1[site] = 1
        return a[tuple(sl0)].sum() - a[tuple(sl1)].sum()
    acc = 0.0
    for si in (0, 1):
        for sj in (0, 1):
            sl = [slice(None)] * N
            sl[i], sl[j] = si, sj
            acc += (1 if si == sj else -1) * a[tuple(sl)].sum()
    return acc - z(i) * z(j)

def half_entropy(state):
    s = svd(state.reshape(16, 16), compute_uv=False)
    p = s**2
    p = p[p > 1e-15]
    p = p / p.sum()
    return float(-(p * np.log(p)).sum())

def site_entropy(state):
    a = np.abs(state.reshape([2] * N))**2
    out = []
    for i in range(N):
        p0 = a.take(0, axis=i).sum()
        ps = np.array([p0, 1 - p0])
        ps = ps[ps > 1e-15]
        out.append(float(-(ps * np.log(ps)).sum()))
    return float(np.mean(out))

def metrics(state):
    C = np.zeros((N, N))
    for i in range(N):
        for j in range(i + 1, N):
            C[i, j] = C[j, i] = zz_connected(state, i, j)
    d = 1.0 - np.abs(C)
    np.fill_diagonal(d, 0.0)
    ks = [d[(i-1) % N, (i+1) % N] - d[(i-1) % N, i] - d[i, (i+1) % N] for i in range(N)]
    nn = float(np.mean([d[i, (i+1) % N] for i in range(N)]))
    return {"S_half": half_entropy(state), "S_site": site_entropy(state),
            "nn": nn, "kappa": float(np.mean(ks))}

def tick(state):
    psi = state.copy()
    U = np.kron(H, I2) @ CNOT          # disentangler on odd bonds
    for i in (1, 3, 5, 7):
        psi = apply_2site(psi, i, U)
    for i in (0, 2, 4, 6):             # isometry prep on even bonds
        psi = apply_2site(psi, i, CNOT)
    return psi / norm(psi)

bell = (np.kron(ket0(), ket0()) + np.kron(ket1(), ket1())) / np.sqrt(2)
psi = bell
for _ in range(3):
    psi = np.kron(psi, bell)
psi /= norm(psi)

before, after = metrics(psi), metrics(tick(psi))
print(f"{'':8} {'before':>10} {'after':>10} {'delta':>10}")
for k in ("S_half", "S_site", "nn", "kappa"):
    print(f"{k:8} {before[k]:10.4f} {after[k]:10.4f} {after[k]-before[k]:10.4f}")
print("kappa is a graph-length deficit, not G_mu_nu.")
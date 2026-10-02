"""holographic_engine_toy_v15.py
v14 tick, then a real chi=2 isometry on each even pair.

W: C^4 -> C^2 keeps span{|00>, |11>}. Bell dimers are lossless.
After the disentangler, most of the weight is discarded.

Prints kept probability and the three deltas with and without truncation.
kappa is a graph-length deficit, not G_mu_nu.
"""
import numpy as np
from numpy.linalg import svd, norm

N = 8
W = np.zeros((2, 4), dtype=complex)
W[0, 0] = 1.0
W[1, 3] = 1.0
I2 = np.eye(2, dtype=complex)
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
H = np.array([[1,1],[1,-1]], dtype=complex) / np.sqrt(2)

def ket0():
    v = np.zeros(2, dtype=complex); v[0] = 1; return v
def ket1():
    v = np.zeros(2, dtype=complex); v[1] = 1; return v

def apply_2site(state, n, i, U):
    j = (i + 1) % n
    axes = [i, j] + [k for k in range(n) if k not in (i, j)]
    inv = np.argsort(axes)
    psi = state.reshape([2] * n).transpose(axes).reshape(4, -1)
    psi = (U @ psi).reshape([2] * n).transpose(inv)
    return psi.reshape(-1)

def zz_connected(state, n, i, j):
    a = np.abs(state.reshape([2] * n))**2
    def z(site):
        sl0 = [slice(None)] * n; sl0[site] = 0
        sl1 = [slice(None)] * n; sl1[site] = 1
        return a[tuple(sl0)].sum() - a[tuple(sl1)].sum()
    acc = 0.0
    for si in (0, 1):
        for sj in (0, 1):
            sl = [slice(None)] * n
            sl[i], sl[j] = si, sj
            acc += (1 if si == sj else -1) * a[tuple(sl)].sum()
    return acc - z(i) * z(j)

def metrics(state, n):
    C = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            C[i, j] = C[j, i] = zz_connected(state, n, i, j)
    d = 1.0 - np.abs(C)
    np.fill_diagonal(d, 0.0)
    ks = [d[(i-1)%n, (i+1)%n] - d[(i-1)%n, i] - d[i, (i+1)%n] for i in range(n)]
    na = n // 2
    s = svd(state.reshape(2**na, 2**na), compute_uv=False)
    p = s**2; p = p[p > 1e-15]; p = p / p.sum()
    return {"S_half": float(-(p*np.log(p)).sum()),
            "nn": float(np.mean([d[i, (i+1)%n] for i in range(n)])),
            "kappa": float(np.mean(ks))}

def disentangle(state):
    psi = state.copy()
    U = np.kron(H, I2) @ CNOT
    for i in (1, 3, 5, 7):
        psi = apply_2site(psi, N, i, U)
    return psi / norm(psi)

def truncate(state):
    psi = state.reshape(4, 4, 4, 4)
    coarse = np.einsum("ap,bq,cr,ds,pqrs->abcd", W, W, W, W, psi, optimize=True)
    kept = float(norm(coarse)**2)
    coarse = coarse / norm(coarse)
    Wdg = W.conj().T
    fine = np.einsum("pa,qb,rc,sd,abcd->pqrs", Wdg, Wdg, Wdg, Wdg, coarse, optimize=True)
    return coarse.reshape(-1), fine.reshape(-1), kept

bell = (np.kron(ket0(), ket0()) + np.kron(ket1(), ket1())) / np.sqrt(2)
psi = bell
for _ in range(3):
    psi = np.kron(psi, bell)
psi /= norm(psi)

tick = disentangle(psi)
for i in (0, 2, 4, 6):
    tick = apply_2site(tick, N, i, CNOT)
tick /= norm(tick)

_, lift0, kept0 = truncate(psi)
_, lift1, kept1 = truncate(disentangle(psi))
fine0, fine1 = metrics(psi, N), metrics(tick, N)
tr0, tr1 = metrics(lift0, N), metrics(lift1, N)

print(f"kept t=0 {kept0:.3f}   kept t=1 {kept1:.3f}   discarded {1-kept1:.3f}")
print(f"{'':8} {'no trunc':>10} {'chi=2':>10}")
for k in ("S_half", "nn", "kappa"):
    print(f"d{k:7} {fine1[k]-fine0[k]:10.4f} {tr1[k]-tr0[k]:10.4f}")
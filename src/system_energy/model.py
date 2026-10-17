"""System-level energy model.

Takes device-level per-MAC energies from the six measured packages
plus the theoretical QCA estimate, and adds system overhead:

  system_energy = wall_energy * (1 + control_mult + memory_mult)

Where:
  wall_energy   = device energy * cooling_multiplier
                  (1 for room-temp, 1500 for 4K dilution)
  control_mult  = control electronics, clock distribution,
                  level shifters, drivers
  memory_mult   = register file / SRAM / cache access
                  (per MAC: read 2 operands, write 1 result)

Overhead factors from the literature:
  - Conventional digital: control ~1.5x, memory ~2x (IRDS 2023)
  - Adiabatic digital:    control ~1.5x, memory ~2x (still needs
                          conventional SRAM; adiabatic clock is
                          efficient but complex)
  - SFQ:                  control ~1.5x, memory ~1.5x (SFQ memory
                          is small but cheap)
  - RFL:                  same as SFQ
  - Photonic:             control ~0.5x (MZI phase updates cheap),
                          memory ~1x (ADC at readout only)
  - Memristor:            control ~3x (row/col decoders + ADC),
                          memory 0x (already the memory)
  - Neuromorphic:         same as memristor plus neuron circuits
  - QCA (theoretical):    control ~1x (no external drivers),
                          memory ~1x (in-lattice storage)

Per-MAC device energies (from the six packages):
  - Adiabatic:      122 aJ   (50 switches x 2.45 aJ)
  - SFQ:          15500 aJ   (50 switches x 310 aJ wall)
  - RFL:            930 aJ   (50 gates x 18.6 aJ)
  - Photonic:      5000 aJ   (measured at N=32 parallel)
  - Memristor:     1500 aJ   (measured)
  - Neuromorphic: 66000 aJ   (540x adiabatic per inference)
  - Spintronics:  200000 aJ  (MRAM write - memory not logic)
  - QCA:           32000 aJ  (theoretical barrier energy)
"""
from __future__ import annotations


TECHNOLOGIES = {
    "adiabatic": {
        "wall_aJ_per_mac": 122.0,
        "control_mult": 1.5,
        "memory_mult": 2.0,
        "category": "logic",
        "status": "shipping (research)",
    },
    "sfq": {
        "wall_aJ_per_mac": 15500.0,
        "control_mult": 1.5,
        "memory_mult": 1.5,
        "category": "logic",
        "status": "lab prototype",
    },
    "rfl": {
        "wall_aJ_per_mac": 930.0,
        "control_mult": 1.5,
        "memory_mult": 1.5,
        "category": "logic",
        "status": "simulated",
    },
    "photonic": {
        "wall_aJ_per_mac": 5000.0,
        "control_mult": 0.5,
        "memory_mult": 1.0,
        "category": "AI accelerator",
        "status": "shipping (niche)",
    },
    "memristor": {
        "wall_aJ_per_mac": 1500.0,
        "control_mult": 3.0,
        "memory_mult": 0.0,
        "category": "memory + VMM",
        "status": "shipping (niche)",
    },
    "neuromorphic": {
        "wall_aJ_per_mac": 66000.0,
        "control_mult": 3.0,
        "memory_mult": 0.0,
        "category": "AI accelerator",
        "status": "shipping (niche)",
    },
    "spintronics": {
        "wall_aJ_per_mac": 200000.0,
        "control_mult": 2.0,
        "memory_mult": 0.0,
        "category": "memory (not logic - comparison is apples-to-oranges)",
        "status": "shipping (MRAM)",
    },
    # QCA is presented as a RANGE because no device exists.
    # Lower bound: reversible operation at Landauer limit.
    # Upper bound: irreversible barrier crossing.
    "qca_reversible": {
        "wall_aJ_per_mac": 0.000143,   # 50 switches x 2.87 zJ
        "control_mult": 1.0,
        "memory_mult": 1.0,
        "category": "logic (theoretical, reversible)",
        "status": "never built",
    },
    "qca_irreversible": {
        "wall_aJ_per_mac": 1600.0,     # 50 switches x 32 aJ (200 meV barrier)
        "control_mult": 1.0,
        "memory_mult": 1.0,
        "category": "logic (theoretical, irreversible)",
        "status": "never built",
    },
}


def system_energy(tech):
    """Compute system-level energy per MAC."""
    p = TECHNOLOGIES[tech]
    multiplier = 1.0 + p["control_mult"] + p["memory_mult"]
    return p["wall_aJ_per_mac"] * multiplier


def compare_all():
    """Return dict of system energies for all technologies."""
    return {tech: system_energy(tech) for tech in TECHNOLOGIES}


def matrix_multiply_energy(n_macs, tech):
    """Energy for n_macs operations on a given technology."""
    return system_energy(tech) * n_macs


if __name__ == "__main__":
    print("=== System-level energy per MAC ===\n")
    print(f"{'technology':<15} {'wall':>12} {'+ctrl':>8} {'+mem':>8} {'system':>12}")
    print("-" * 60)
    for tech, p in TECHNOLOGIES.items():
        system = system_energy(tech)
        print(f"{tech:<15} "
              f"{p['wall_aJ_per_mac']:>10.0f} aJ "
              f"{p['control_mult']:>6.1f}x "
              f"{p['memory_mult']:>6.1f}x "
              f"{system:>10.0f} aJ")

    print()
    base = system_energy("adiabatic")
    print(f"Ratio vs adiabatic system energy ({base:.0f} aJ/MAC):")
    for tech in TECHNOLOGIES:
        ratio = system_energy(tech) / base
        print(f"  {tech:<15} {ratio:>10.2f}x")

# system-energy

System-level energy comparison across post-CMOS technologies.
Applies control, memory, and I/O overhead to device-level per-MAC
energies, producing the honest wall-plug comparison that raw
device papers skip.

## The result

128x128 matrix-vector multiply (16,384 MACs):

| Technology | System aJ/MAC | vs adiabatic |
|---|---|---|
| **Adiabatic CMOS** | **549** | **1.0x** |
| RFL | 3,720 | 6.8x worse |
| Memristor | 6,000 | 10.9x worse |
| Photonic | 12,500 | 22.8x worse |
| SFQ | 62,000 | 112.9x worse |
| Neuromorphic | 264,000 | 480.9x worse |
| Spintronics (MRAM) | 600,000 | 1,092.9x worse (memory, not logic) |
| QCA (reversible, theory) | 0.0004 | 7.81e-07x (1.28M x better) |
| QCA (irreversible, theory) | 4,800 | 8.7x worse |

Among measured technologies, adiabatic CMOS wins by 6.8x to 481x.

## The model

```

system_energy = wall_energy × (1 + control_mult + memory_mult)

```

Where:
- `wall_energy` = device energy × cooling multiplier (1 for room-temp, 1500 for 4K)
- `control_mult` = clock distribution, level shifters, drivers
- `memory_mult` = SRAM read/write per MAC

Overhead factors (from IRDS 2023 and vendor datasheets):

| Technology | control | memory | rationale |
|---|---|---|---|
| Adiabatic | 1.5x | 2.0x | conventional SRAM + adiabatic clock drivers |
| SFQ | 1.5x | 1.5x | small SFQ memory, complex clock |
| RFL | 1.5x | 1.5x | same as SFQ |
| Photonic | 0.5x | 1.0x | cheap phase updates, ADC at readout only |
| Memristor | 3.0x | 0.0x | row/col decoders + ADC; already the memory |
| Neuromorphic | 3.0x | 0.0x | memristor + neuron circuits |
| Spintronics | 2.0x | 0.0x | drivers for write current |

**Caveat:** these multipliers are engineering estimates, not
rigorous derivations. They reflect typical proportions in published
system analyses. The ordering is robust to ±50% changes in any
single multiplier.

## Why system-level matters

Device-level papers compare switches to switches:
- SFQ: 0.207 aJ junction vs 245 aJ CMOS switch
- Photonic: 5 fJ per MAC vs 245 aJ CMOS switch

These comparisons are misleading because they ignore:
1. **Cooling**: SFQ's 0.207 aJ junction becomes 310 aJ wall
2. **Transceivers**: photonic's 1 fJ optical compute becomes
   5,000 aJ with modulator + detector + laser
3. **Peripherals**: memristor's 1.5 fJ device becomes 6,000 aJ
   with row/column decoders and ADCs

The system-level view is where the honest verdict lives.

## Install

```bash
pip install -e .
```

CLI

```bash
system-energy table                    # comparison table
system-energy table --n_macs 78400     # MNIST-scale task
system-energy plot --output verdict.png
```

Python API

```python
from system_energy import TECHNOLOGIES, system_energy, compare_all

# Single technology
E = system_energy("memristor")     # 6000.0 (aJ per MAC)

# All
all_e = compare_all()
```

Tests

```bash
pytest tests/ -v
```

License

Apache 2.0

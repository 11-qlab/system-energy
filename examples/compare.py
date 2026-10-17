"""Generate the system-level comparison plot and table."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from system_energy import TECHNOLOGIES, system_energy


items = sorted(TECHNOLOGIES.items(),
               key=lambda x: system_energy(x[0]))
techs = [t for t, _ in items]
energies = [system_energy(t) for t in techs]
base = system_energy("adiabatic")
ratios = [e / base for e in energies]


def color(t):
    if t == "adiabatic":
        return "#2ca02c"
    if t.startswith("qca"):
        return "#d62728"
    if t == "spintronics":
        return "#9467bd"
    return "#1f77b4"


colors = [color(t) for t in techs]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(techs, ratios, color=colors, edgecolor="black", lw=0.5)
ax.set_yscale("log")
ax.set_ylabel("System energy / adiabatic (log scale)")
ax.set_title("System-level energy per MAC (adiabatic = 1x)")
ax.axhline(1.0, color="green", ls="--", lw=1.5,
           label="Adiabatic baseline")
ax.grid(axis="y", which="both", alpha=0.3)
ax.legend(loc="upper left")

for bar, val in zip(bars, ratios):
    y = bar.get_height() * 1.15
    label = f"{val:.1f}x" if val >= 0.1 else f"{val:.1e}x"
    ax.text(bar.get_x() + bar.get_width() / 2, y, label,
            ha="center", va="bottom", fontsize=8)

plt.xticks(rotation=25, ha="right")
plt.tight_layout()
out = Path(__file__).parent / "verdict.png"
plt.savefig(out, dpi=140)
print(f"wrote {out}")

print()
print(f"{'technology':<20} {'system aJ/MAC':>15} {'vs adiabatic':>14}")
print("-" * 52)
for t, e, r in zip(techs, energies, ratios):
    rstr = f"{r:.1f}x" if r >= 0.1 else f"{r:.2e}x"
    print(f"{t:<20} {e:>13.4f} {rstr:>14}")

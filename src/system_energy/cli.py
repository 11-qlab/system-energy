"""CLI for system-energy."""
import argparse, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .model import TECHNOLOGIES, system_energy, compare_all


def main(argv=None):
    p = argparse.ArgumentParser(prog="system-energy",
        description="System-level energy comparison")
    sub = p.add_subparsers(dest="cmd", required=True)

    ptable = sub.add_parser("table", help="Print comparison table")
    ptable.add_argument("--n_macs", type=int, default=16384,
                        help="MACs per task (16384 = 128x128 matvec)")

    pplot = sub.add_parser("plot", help="Generate comparison plot")
    pplot.add_argument("--output", default="verdict.png")

    args = p.parse_args(argv)

    if args.cmd == "table":
        base = system_energy("adiabatic")
        print(f"Task: {args.n_macs:,} MACs (128x128 matrix-vector multiply)")
        print()
        print(f"{'technology':<15} {'system aJ/MAC':>15} {'task total':>14} "
              f"{'vs adiabatic':>14}")
        print("-" * 62)
        for tech in TECHNOLOGIES:
            E_mac = system_energy(tech)
            E_task = E_mac * args.n_macs
            ratio = E_mac / base
            # Format task total in human units
            if E_task > 1e9:
                task_str = f"{E_task/1e9:.2f} nJ"
            elif E_task > 1e6:
                task_str = f"{E_task/1e6:.2f} pJ"
            else:
                task_str = f"{E_task/1e3:.2f} fJ"
            ratio_str = f"{ratio:.1f}x" if ratio >= 0.1 else f"{ratio:.2e}x"
            print(f"{tech:<15} {E_mac:>13.4f} aJ {task_str:>14} "
                  f"{ratio_str:>12}")
        return 0

    if args.cmd == "plot":
        techs = list(TECHNOLOGIES.keys())
        energies = [system_energy(t) for t in techs]
        base = system_energy("adiabatic")
        ratios = [e / base for e in energies]

        fig, ax = plt.subplots(figsize=(11, 5))
        colors = ['#2ca02c' if t == 'adiabatic' else
                  '#d62728' if t == 'qca' else '#1f77b4'
                  for t in techs]
        bars = ax.bar(techs, ratios, color=colors,
                      edgecolor='black', lw=0.5)
        ax.set_yscale("log")
        ax.set_ylabel("System energy / adiabatic (log scale)")
        ax.set_title("System-level energy per MAC (adiabatic = 1x)")
        ax.axhline(1.0, color='green', ls='--', lw=1.5, label='Adiabatic baseline')
        ax.grid(axis='y', which='both', alpha=0.3)
        ax.legend()

        for bar, val in zip(bars, ratios):
            y = bar.get_height() * 1.1
            ax.text(bar.get_x() + bar.get_width()/2, y,
                    f"{val:.1f}x", ha='center', va='bottom', fontsize=9)

        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig(args.output, dpi=140)
        print(f"wrote {args.output}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

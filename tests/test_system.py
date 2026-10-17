"""Tests for system-energy model."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import pytest


def test_technologies_dict_populated():
    from system_energy import TECHNOLOGIES
    assert len(TECHNOLOGIES) >= 8
    for tech, p in TECHNOLOGIES.items():
        assert "wall_aJ_per_mac" in p
        assert "control_mult" in p
        assert "memory_mult" in p


def test_system_energy_adiabatic_baseline():
    from system_energy import system_energy
    assert abs(system_energy("adiabatic") - 549.0) < 1.0


def test_system_energy_sfq():
    from system_energy import system_energy
    assert abs(system_energy("sfq") - 62000.0) < 1.0


def test_system_energy_memristor():
    from system_energy import system_energy
    assert abs(system_energy("memristor") - 6000.0) < 1.0


def test_system_energy_rfl_beats_sfq():
    from system_energy import system_energy
    assert system_energy("rfl") < system_energy("sfq")


def test_system_energy_adiabatic_wins_all_measured():
    from system_energy import system_energy
    adiabatic = system_energy("adiabatic")
    for tech in ("sfq", "rfl", "photonic", "memristor",
                 "neuromorphic", "spintronics"):
        assert system_energy(tech) > adiabatic, f"{tech} should lose"


def test_qca_range_spans_orders():
    from system_energy import system_energy
    rev = system_energy("qca_reversible")
    irr = system_energy("qca_irreversible")
    assert irr / rev > 1e6


def test_compare_all_returns_all():
    from system_energy import compare_all, TECHNOLOGIES
    c = compare_all()
    assert set(c.keys()) == set(TECHNOLOGIES.keys())


def test_matrix_multiply_energy_scales():
    from system_energy import matrix_multiply_energy
    e1 = matrix_multiply_energy(1, "adiabatic")
    e100 = matrix_multiply_energy(100, "adiabatic")
    assert abs(e100 / e1 - 100) < 1e-9


def test_all_wall_energies_positive():
    from system_energy import TECHNOLOGIES
    for tech, p in TECHNOLOGIES.items():
        assert p["wall_aJ_per_mac"] > 0


def test_overhead_multipliers_non_negative():
    from system_energy import TECHNOLOGIES
    for tech, p in TECHNOLOGIES.items():
        assert p["control_mult"] >= 0
        assert p["memory_mult"] >= 0

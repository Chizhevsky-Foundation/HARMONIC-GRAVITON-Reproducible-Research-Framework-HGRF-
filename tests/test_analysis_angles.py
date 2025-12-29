import math
import awkward as ak
import numpy as np
import pytest

from src.analysis import compute_angles_from_pt_eta_phi, summarize_angles


def test_compute_angles_right_angle():
    pt = ak.Array([[1.0, 1.0]])
    eta = ak.Array([[0.0, 0.0]])
    phi = ak.Array([[0.0, math.pi / 2]])

    angles = compute_angles_from_pt_eta_phi(pt, eta, phi)
    angle_deg = ak.to_numpy(ak.flatten(angles))[0]
    assert pytest.approx(angle_deg, rel=1e-6) == 90.0


def test_summarize_angles():
    pt = ak.Array([[1.0, 1.0], [1.0]])
    eta = ak.Array([[0.0, 0.0], [0.0]])
    phi = ak.Array([[0.0, math.pi / 2], [0.0]])

    angles = compute_angles_from_pt_eta_phi(pt, eta, phi)
    n_pairs, min_a, mean_a, max_a = summarize_angles(angles)

    assert int(n_pairs[0]) == 1
    assert int(n_pairs[1]) == 0
    assert pytest.approx(float(mean_a[0]), rel=1e-6) == 90.0
    assert np.isnan(mean_a[1])

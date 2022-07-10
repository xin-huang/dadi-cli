import dadi
import os
import pytest
import numpy as np
from dadi_cli import utilities


def test_pts_l_func():
    fs = dadi.Spectrum([0, 1, 2, 3])
    assert utilities.pts_l_func(fs.sample_sizes) == (5, 7, 9)


def test_convert_to_None():
    inference_input = [1, 2, 3, 4]
    p0_len = 4
    assert utilities.convert_to_None(inference_input, p0_len) == [1, 2, 3, 4]

    inference_input = -1
    assert utilities.convert_to_None(inference_input, p0_len) == [None, None, None, None]

    inference_input = [-1, 2, 3, 4]
    assert utilities.convert_to_None(inference_input, p0_len) == [None, 2, 3, 4]


def test_get_opts_and_theta(capfd):
    # no misid
    opts, theta = utilities.get_opts_and_theta("tests/example_data/example.split_mig.demo.params.InferDM.bestfits")
    assert np.allclose(opts, [1.2176133096314186, 1.217675913949673, 0.009847665426385547, 1.0068236071499865])
    assert np.isclose(theta, 99910.43972307118)

    # with misid
    opts, theta = utilities.get_opts_and_theta("tests/example_data/example.split_mig.demo.params.with.misid.InferDM.bestfits")
    assert np.allclose(opts, [1.2176133096314186, 1.217675913949673, 0.009847665426385547, 1.0068236071499865])
    assert np.isclose(theta, 99910.43972307118)

    # no convergence
    opts, theta = utilities.get_opts_and_theta("tests/example_data/example.split_mig.demo.params.InferDM.no.convergence.bestfits")
    out, err = capfd.readouterr()
    assert out.rstrip() == "No converged optimization results found."

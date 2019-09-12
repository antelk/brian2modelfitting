'''
Test the metric class
'''
import numpy as np
from numpy.testing.utils import assert_equal, assert_raises, assert_almost_equal
from brian2 import ms
from brian2.units.fundamentalunits import DimensionMismatchError
from brian2modelfitting import Metric, MSEMetric, GammaFactor, firing_rate, get_gamma_factor


def test_firing_rate():
    assert_equal(firing_rate([1, 2, 3]), 1)
    assert_equal(firing_rate([1, 1.2, 1.4, 1.6, 1.8]), 5)
    assert_almost_equal(firing_rate([1.1, 1.2, 1.3, 1.4, 1.5]), 10)


def test_get_gamma_factor():
    src = [7, 9, 11] * ms
    src2 = [1, 2, 3] * ms
    trg = [0, 2, 4, 6, 8] * ms

    gf0 = get_gamma_factor(trg, trg, delta=12*ms, time=12*ms, dt=0.1*ms)
    gf1 = get_gamma_factor(src2, trg, delta=12*ms, time=12*ms, dt=0.1*ms)
    gf2 = get_gamma_factor(src, src2, delta=5*ms, time=5*ms, dt=0.1*ms)

    assert_equal(gf0, 2.0)
    assert gf1 > 1.0
    assert gf2 > 1.0
    assert gf1 < gf2


def test_init():
    MSEMetric()
    GammaFactor(10*ms, time=10*ms)


def test_calc_mse():
    mse = MSEMetric()
    out = np.random.rand(2, 20)
    inp = np.random.rand(10, 20)

    errors = mse.calc(inp, out, 2, 0.01*ms)
    assert_equal(np.shape(errors), (5,))
    assert_equal(mse.calc(out, out, 2, 0.1*ms), [0.])
    assert(np.all(mse.calc(inp, out, 2, 0.1*ms) > 0))

def test_calc_mse_t_start():
    mse = MSEMetric(t_start=1*ms)
    out = np.random.rand(2, 200)
    inp = np.random.rand(10, 200)

    errors = mse.calc(inp, out, 2, 0.1*ms)
    assert_equal(np.shape(errors), (5,))
    assert_equal(mse.calc(out, out, 2, 0.1*ms), [0.])
    assert(np.all(mse.calc(inp, out, 2, 0.1*ms) > 0))


def test_calc_gf():
    assert_raises(TypeError, GammaFactor)
    assert_raises(DimensionMismatchError, GammaFactor, delta=10)
    assert_raises(DimensionMismatchError, GammaFactor, time=10)

    inp_gf = np.round(np.sort(np.random.rand(10, 5) * 10), 2)
    out_gf = np.round(np.sort(np.random.rand(2, 5) * 10), 2)

    gf = GammaFactor(delta=10*ms, time=10*ms)
    errors = gf.calc(inp_gf, out_gf, 2, 0.1*ms)
    assert_equal(np.shape(errors), (5,))
    assert(np.all(errors > 0))
    errors = gf.calc(out_gf, out_gf, 2, 0.1*ms)
    assert_almost_equal(errors, [2.])

def test_get_features_mse():
    mse = MSEMetric()
    out_mse = np.random.rand(2, 20)
    inp_mse = np.random.rand(6, 20)

    features = mse.get_features(inp_mse, out_mse, 2, 0.1*ms)
    assert_equal(np.shape(features), (2, 3))
    assert(np.all(np.array(features) > 0))

    features = mse.get_features(out_mse, out_mse, 2, 0.1*ms)
    assert_equal(np.shape(features), (2, 1))
    assert_equal(features, [[0.], [0.]])


def test_get_features_mse_t_start():
    mse = MSEMetric(t_start=1*ms)
    out_mse = np.random.rand(2, 200)
    inp_mse = np.random.rand(6, 200)

    features = mse.get_features(inp_mse, out_mse, 2, 0.1*ms)
    assert_equal(np.shape(features), (2, 3))
    assert(np.all(np.array(features) > 0))

    features = mse.get_features(out_mse, out_mse, 2, 0.1*ms)
    assert_equal(np.shape(features), (2, 1))
    assert_equal(features, [[0.], [0.]])


def test_get_errors_mse():
    mse = MSEMetric()
    errors = mse.get_errors(np.random.rand(10, 5))
    print(errors)
    assert_equal(np.shape(errors), (5,))
    assert(np.all(np.array(errors) > 0))

    errors = mse.get_errors(np.zeros((10, 2)))
    assert_equal(np.shape(errors), (2,))
    assert_equal(errors, [0., 0.])


def test_get_features_gamma():
    inp_gf = np.round(np.sort(np.random.rand(6, 5) * 10), 2)
    out_gf = np.round(np.sort(np.random.rand(2, 5) * 10), 2)

    gf = GammaFactor(delta=10*ms, time=10*ms)
    features = gf.get_features(inp_gf, out_gf, 2, 0.1*ms)
    assert_equal(np.shape(features), (2, 3))
    assert(np.all(np.array(features) > 0))

    features = gf.get_features(out_gf, out_gf, 2, 0.1*ms)
    assert_equal(np.shape(features), (2, 1))
    assert_almost_equal(features, [[2.], [2.]])


def test_get_errors_gamma():
    gf = GammaFactor(delta=10*ms, time=10*ms)
    errors = gf.get_errors(np.random.rand(10, 5))
    assert_equal(np.shape(errors), (5,))
    assert(np.all(np.array(errors) > 0))

    errors = gf.get_errors(np.zeros((10, 2)))
    assert_equal(np.shape(errors), (2,))
    assert_almost_equal(errors, [0., 0.])

import numpy as np
import pytest
import numpy.testing as npt
import unittest
from hierarc.Likelihood.LensLikelihood.kin_likelihood import KinLikelihood
from lenstronomy.Util import constants as const


class TestIFUKinLikelihood(object):

    def setup(self):
        np.random.seed(seed=41)

    def test_log_likelihood(self):
        num_ifu = 10
        z_lens = 0.5
        z_source = 2
        ddt, dd = 5000., 2000.
        ds_dds = ddt / dd / (1 + z_lens)
        j_mean_list = np.ones(num_ifu)
        scaling_ifu = 1
        sigma_v_measurement = np.sqrt(ds_dds * scaling_ifu * j_mean_list) * const.c / 1000
        sigma_v_sigma = sigma_v_measurement/10.
        error_cov_measurement = np.diag(sigma_v_sigma ** 2)
        error_cov_j_sqrt = np.diag(np.zeros_like(sigma_v_measurement))
        ifu_likelihood = KinLikelihood(z_lens, z_source, sigma_v_measurement, j_mean_list, error_cov_measurement,
                                       error_cov_j_sqrt, normalized=False)
        logl = ifu_likelihood.log_likelihood(ddt, dd, aniso_scaling=None)
        npt.assert_almost_equal(logl, 0, decimal=5)
        logl = ifu_likelihood.log_likelihood(ddt*(0.9**2), dd, aniso_scaling=None)
        npt.assert_almost_equal(logl, -num_ifu/2, decimal=5)
        logl = ifu_likelihood.log_likelihood(ddt * (1 - np.sqrt(0.1**2 + 0.1**2))**2, dd, aniso_scaling=None)
        npt.assert_almost_equal(logl, -num_ifu, decimal=5)

    def test_error_systematic(self):
        num_ifu = 10
        z_lens = 0.5
        z_source = 2
        ddt, dd = 5000., 2000.
        ds_dds = ddt / dd / (1 + z_lens)
        j_mean_list = np.ones(num_ifu)
        scaling_ifu = 1
        sigma_v_measurement = np.sqrt(ds_dds * scaling_ifu * j_mean_list) * const.c / 1000
        sigma_v_sigma = sigma_v_measurement / 1000.
        error_cov_measurement = np.diag(sigma_v_sigma ** 2)
        error_cov_j_sqrt = np.diag(np.zeros_like(sigma_v_measurement))
        ifu_likelihood = KinLikelihood(z_lens, z_source, sigma_v_measurement, j_mean_list, error_cov_measurement,
                                       error_cov_j_sqrt, normalized=False)
        logl = ifu_likelihood.log_likelihood(ddt * (1 - np.sqrt(0.1**2)) ** 2, dd, aniso_scaling=1, sigma_v_sys_error=0.1)
        npt.assert_almost_equal(logl, -1/2., decimal=5)

    def test_log_likikelihood_marg(self):
        num_ifu = 1
        z_lens = 0.5
        z_source = 2
        ddt, dd = 5000., 2000.
        ds_dds = ddt / dd / (1 + z_lens)
        j_mean_list = np.ones(num_ifu) / 10**6
        scaling_ifu = 1
        sigma_v_measurement = np.sqrt(ds_dds * scaling_ifu * j_mean_list) * const.c / 1000
        sigma_v_sigma = sigma_v_measurement / 100.
        error_cov_measurement = np.diag(sigma_v_sigma ** 2)
        error_cov_j_sqrt = np.diag((np.sqrt(j_mean_list) / 100)**2)
        print(error_cov_j_sqrt, 'cov_j_sqrt')
        ifu_likelihood = KinLikelihood(z_lens, z_source, sigma_v_measurement, j_mean_list, error_cov_measurement,
                                       error_cov_j_sqrt, normalized=True)
        logl = ifu_likelihood.log_likelihood(ddt, dd, aniso_scaling=1)
        aniso_scaling = 0.8
        logl_ani = ifu_likelihood.log_likelihood(ddt, dd*aniso_scaling, aniso_scaling=aniso_scaling)
        npt.assert_almost_equal(logl_ani - logl, 0, decimal=1)

        # here we test that a Monte Carlo marginalization of a systematic uncertainty leads to the same result as the
        # analytical Gaussian calculatino in the covariance matrix normalization
        sigma_v_sys_error = 0.1
        logl = ifu_likelihood.log_likelihood(ddt, dd, aniso_scaling=1, sigma_v_sys_error=sigma_v_sys_error)
        l_sum = 0
        num_sample = 10000
        for i in range(num_sample):
            sigma_v_pert = np.random.normal(loc=0, scale=sigma_v_sys_error)
            logl_i = ifu_likelihood.log_likelihood(ddt, dd, aniso_scaling=1, sigma_v_pert=sigma_v_pert)
            l_sum += np.exp(logl_i)
        logl_average = np.log(l_sum/num_sample)
        npt.assert_almost_equal(logl, logl_average, decimal=1)


class TestRaise(unittest.TestCase):

    def test_raise(self):

        with self.assertRaises(ValueError):
            raise ValueError()


if __name__ == '__main__':
    pytest.main()
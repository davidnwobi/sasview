"""
This module implements corfunc
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema
from numpy.linalg import lstsq

from sas.qtgui.Perspectives.Corfunc.util import TransformedData
from sas.sascalc.corfunc.extrapolation_data import ExtrapolationParameters

from sasdata.dataloader.data_info import Data1D
from sas.sascalc.corfunc.transform_thread import FourierThread
from sas.sascalc.corfunc.transform_thread import HilbertThread
from sas.sascalc.corfunc.smoothing import SmoothJoin

from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class SupplementaryParameters:
    tangent_point_x: float
    tangent_point_y: float
    tangent_gradient: float
    first_minimum_x: float
    first_minimum_y: float
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]

@dataclass
class ExtractedParameters:
    long_period: float
    interface_thickness: float
    hard_block_thickness: float
    soft_block_thickness: float
    core_thickness: float
    polydispersity_ryan: float
    polydispersity_stribeck: float
    local_crystallinity: float



class CorfuncCalculator:

    def __init__(self,
                 data: Optional[Data1D]=None,
                 lowerq: Optional[float]=None,
                 upperq: Optional[Tuple[float, float]]=None,
                 scale: float=1.0):
        """
        Initialize the class.

        :param data: Data of the type DataLoader.Data1D
        :param lowerq: The Q value to use as the boundary for
            Guinier extrapolation
        :param upperq: A tuple of the form (lower, upper).
            Values between lower and upper will be used for Porod extrapolation
        :param scale: Scaling factor for I(q)
        """
        self._data = None
        self.set_data(data, scale)
        self.lowerq = lowerq
        self.upperq = upperq
        self.background = self.compute_background()
        self._transform_thread = None

    @property
    def extrapolation_parameters(self) -> Optional[ExtrapolationParameters]:
        if self._data is None or self.lowerq is None or self.upperq is None:
            return None
        else:
            return ExtrapolationParameters(
                min(self._data.x),
                self.lowerq,
                self.upperq[0],
                self.upperq[1],
                max(self._data.x))

    @extrapolation_parameters.setter
    def extrapolation_parameters(self, extrap: ExtrapolationParameters):
        self.lowerq = extrap.point_1
        self.upperq = (extrap.point_2, extrap.point_3)


    def set_data(self, data: Optional[Data1D], scale: float=1):
        """
        Prepares the data for analysis

        :return: new_data = data * scale - background
        """
        if data is None:
            return
        # Only process data of the class Data1D
        if not issubclass(data.__class__, Data1D):
            raise ValueError("Correlation function cannot be computed with 2D data.")

        # Prepare the data
        new_data = Data1D(x=data.x, y=data.y)
        new_data *= scale

        # Ensure the errors are set correctly
        if new_data.dy is None or len(new_data.x) != len(new_data.dy) or \
            (min(new_data.dy) == 0 and max(new_data.dy) == 0):
            new_data.dy = np.ones(len(new_data.x))

        self._data = new_data

    def compute_background(self, upperq=None):
        """
        Compute the background level from the Porod region of the data
        """
        if self._data is None: return 0
        elif upperq is None and self.upperq is not None: upperq = self.upperq
        elif upperq is None and self.upperq is None: return 0
        q = self._data.x
        mask = np.logical_and(q > upperq[0], q < upperq[1])
        _, _, bg = self._fit_porod(q[mask], self._data.y[mask])

        return bg

    def compute_extrapolation(self):
        """
        Extrapolate and interpolate scattering data

        :return: The extrapolated data
        """
        q = self._data.x
        iq = self._data.y

        params, s2 = self._fit_data(q, iq)
        # Extrapolate to 100*Qmax in experimental data
        qs = np.arange(0, q[-1]*100, (q[1]-q[0]))
        iqs = s2(qs)

        extrapolation = Data1D(qs, iqs)

        return params, extrapolation, s2

    def compute_transform(self, extrapolation, trans_type, background=None,
        completefn=None, updatefn=None):
        """
        Transform an extrapolated scattering curve into a correlation function.

        :param extrapolation: The extrapolated data
        :param background: The background value (if not provided, previously
            calculated value will be used)
        :param extrap_fn: A callable function representing the extraoplated data
        :param completefn: The function to call when the transform calculation
            is complete
        :param updatefn: The function to call to update the GUI with the status
            of the transform calculation
        :return: The transformed data
        """
        if self._transform_thread is not None:
            if self._transform_thread.isrunning(): return

        if background is None: background = self.background

        if trans_type == 'fourier':
            self._transform_thread = FourierThread(self._data, extrapolation,
                                                   background, completefn=completefn,
                                                   updatefn=updatefn)
        elif trans_type == 'hilbert':
            self._transform_thread = HilbertThread(self._data, extrapolation,
                                                   background, completefn=completefn, updatefn=updatefn)
        else:
            err = ("Incorrect transform type supplied, must be 'fourier'",
                " or 'hilbert'")
            raise ValueError(err)

        self._transform_thread.queue()

    def transform_isrunning(self):
        if self._transform_thread is None: return False
        return self._transform_thread.isrunning()

    def stop_transform(self):
        if self._transform_thread.isrunning():
            self._transform_thread.stop()

    def extract_parameters(self, transformed_data: TransformedData) -> Optional[Tuple[ExtractedParameters, SupplementaryParameters]]:
        """
        Extract the interesting measurements from a correlation function

        :param transformed_data: TransformedData object
        """

        gamma_1 = transformed_data.gamma_1  # 1D transform
        idf = transformed_data.idf

        # Calculate indexes of maxima and minima
        x = gamma_1.x
        y = gamma_1.y
        maxs = argrelextrema(y, np.greater)[0]
        mins = argrelextrema(y, np.less)[0]

        # If there are no maxima, return None
        if len(maxs) == 0:
            return None

        gamma_min = y[mins[0]]  # The value at the first minimum



        dy = (y[2:]-y[:-2])/(x[2:]-x[:-2])  # 1st derivative of y


        # Find where the second derivative goes to zero
        #  * the IDF is the second derivative of gamma_1
        #  * ... but has a large DC component that needs to be ignored

        above_zero = idf.y[1:] > 0

        zero_crossings = \
            np.argwhere(
                np.logical_xor(
                    above_zero[1:],
                    above_zero[:-1]))

        inflection_point_index = zero_crossings[0] + 1 # +1 for ignoring DC, left side of crossing, not right

        # Try to calculate slope around linear_point using 80 data points
        inflection_region_lower = inflection_point_index - 40
        inflection_region_upper = inflection_point_index + 40

        # If too few data points to the left, use linear_point*2 data points
        if inflection_region_lower < 0:
            inflection_region_lower = 0
            inflection_region_upper = inflection_point_index * 2

        # If too few to right, use 2*(dy.size - linear_point) data points
        elif inflection_region_upper > len(dy):
            inflection_region_upper = len(dy)
            width = len(dy) - inflection_point_index
            inflection_region_lower = 2*inflection_point_index - dy.size

        # Slope at inflection point calculated by mean over inflection region
        inflection_point_tangent_slope = np.mean(dy[inflection_region_lower:inflection_region_upper])  # Linear slope
        inflection_point_tangent_intercept = y[1:-1][inflection_point_index]-inflection_point_tangent_slope*x[1:-1][inflection_point_index]  # Linear intercept

        long_period = x[maxs[0]]
        hard_block_thickness = (gamma_min - inflection_point_tangent_intercept) / inflection_point_tangent_slope  # Hard block thickness
        soft_block_thickness = long_period - hard_block_thickness

        # Find the data points where the graph is linear to within 1%
        mask = np.where(np.abs((y-(inflection_point_tangent_slope*x+inflection_point_tangent_intercept))/y) < 0.01)[0]
        if len(mask) == 0:  # Return garbage for bad fits
            return None

        interface_thickness = x[mask[0]]  # Beginning of Linear Section
        core_thickness = x[mask[-1]]  # End of Linear Section

        local_crystallinity = hard_block_thickness / long_period

        gamma_max = y[mask[-1]]

        polydispersity_ryan = np.abs(gamma_min / gamma_max)  # Normalized depth of minimum
        polydispersity_stribeck = np.abs(local_crystallinity / ((local_crystallinity - 1) * gamma_max))  # Normalized depth of minimum


        supplementary_parameters = SupplementaryParameters(
            tangent_point_x=x[inflection_point_index],
            tangent_point_y=y[inflection_point_index],
            tangent_gradient=float(inflection_point_tangent_slope),
            first_minimum_x=0.0,
            first_minimum_y=0.0,
            x_range=(1/transformed_data.q_range[1], 1/transformed_data.q_range[0]),
            y_range=(np.min(y), np.max(y))
        )

        extracted_parameters = ExtractedParameters(
                    long_period,
                    interface_thickness,
                    hard_block_thickness,
                    soft_block_thickness,
                    core_thickness,
                    polydispersity_ryan,
                    polydispersity_stribeck,
                    local_crystallinity)

        return extracted_parameters, supplementary_parameters


    def _porod(self, q, K, sigma, bg):
        """Equation for the Porod region of the data"""
        return bg + (K*q**(-4))*np.exp(-q**2*sigma**2)

    def _fit_guinier(self, q, iq):
        """Fit the Guinier region of the curve"""
        A = np.vstack([q**2, np.ones(q.shape)]).T
        # CRUFT: numpy>=1.14.0 allows rcond=None for the following default
        rcond = np.finfo(float).eps * max(A.shape)
        return lstsq(A, np.log(iq), rcond=rcond)

    def _fit_porod(self, q, iq):
        """Fit the Porod region of the curve"""
        fitp = curve_fit(lambda q, k, sig, bg: self._porod(q, k, sig, bg)*q**2,
                         q, iq*q**2, bounds=([-np.inf, 0, -np.inf], [np.inf, np.inf, np.inf]))[0]
        k, sigma, bg = fitp
        return k, sigma, bg

    def _fit_data(self, q, iq):
        """
        Given a data set, extrapolate out to large q with Porod and
        to q=0 with Guinier
        """
        mask = np.logical_and(q > self.upperq[0], q < self.upperq[1])

        # Returns an array where the 1st and 2nd elements are the values of k
        # and sigma for the best-fit Porod function
        k, sigma, _ = self._fit_porod(q[mask], iq[mask])
        bg = self.background

        # Smooths between the best-fit porod function and the data to produce a
        # better fitting curve
        data = interp1d(q, iq)
        s1 = SmoothJoin(data,
                        lambda x: self._porod(x, k, sigma, bg), self.upperq[0], q[-1])

        mask = np.logical_and(q < self.lowerq, 0 < q)

        # Returns parameters for the best-fit Guinier function
        g = self._fit_guinier(q[mask], iq[mask])[0]

        # Smooths between the best-fit Guinier function and the Porod curve
        s2 = SmoothJoin((lambda x: (np.exp(g[1] + g[0] * x ** 2))), s1, q[0],
                        self.lowerq)

        params = {'A': g[1], 'B': g[0], 'K': k, 'sigma': sigma}

        return params, s2

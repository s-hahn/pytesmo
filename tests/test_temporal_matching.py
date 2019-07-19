# Copyright (c) 2019, TU Wien, Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Vienna University of Technology,
#      Department of Geodesy and Geoinformation nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Tests for the temporal matching module
Created on Wed Jul  8 19:37:14 2015
'''


import pytz
from datetime import datetime

import pandas as pd
import numpy as np
import numpy.testing as nptest

import pytesmo.temporal_matching as tmatching


def test_df_match_borders():
    """
    Border values can be problematic for temporal matching.

    See issue #51
    """
    ref_df = pd.DataFrame(
        {"data": np.arange(5)}, index=pd.date_range(
            datetime(2007, 1, 1, 0),
            "2007-01-05", freq="D"))

    match_df = pd.DataFrame({"matched_data": np.arange(5)},
                            index=[datetime(2007, 1, 1, 9),
                                   datetime(2007, 1, 2, 9),
                                   datetime(2007, 1, 3, 9),
                                   datetime(2007, 1, 4, 9),
                                   datetime(2007, 1, 5, 9)])

    matched = tmatching.df_match(ref_df, match_df, return_distance=True)

    nptest.assert_allclose(
        np.array([0.375, 0.375, 0.375, 0.375, 0.375]),
        matched['dist_other'].values)
    nptest.assert_allclose(np.arange(5), matched.matched_data)


def test_df_match_borders_unequal_query_points():
    """
    Border values can be problematic for temporal matching.

    See issue #51
    """

    ref_df = pd.DataFrame({"data": np.arange(5)},
                          index=pd.date_range(datetime(2007, 1, 1, 0),
                                              "2007-01-05", freq="D"))

    match_df = pd.DataFrame({"matched_data": np.arange(4)},
                            index=[datetime(2007, 1, 1, 9),
                                   datetime(2007, 1, 2, 9),
                                   datetime(2007, 1, 4, 9),
                                   datetime(2007, 1, 5, 9)])

    matched = tmatching.df_match(ref_df, match_df, return_distance=True)

    nptest.assert_allclose(np.array([0.375, 0.375, -0.625, 0.375, 0.375]),
                           matched['dist_other'].values)

    nptest.assert_allclose(np.array([0, 1, 1, 2, 3]), matched.matched_data)


def test_matching():
    """
    test matching function
    """
    data = np.arange(10.0)
    data[3] = np.nan

    ref_df = pd.DataFrame({"data": data}, index=pd.date_range(
        datetime(2007, 1, 1, 0), "2007-01-10", freq="D"))

    match_df = pd.DataFrame({"matched_data": np.arange(5)},
                            index=[datetime(2007, 1, 1, 9),
                                   datetime(2007, 1, 2, 9),
                                   datetime(2007, 1, 3, 9),
                                   datetime(2007, 1, 4, 9),
                                   datetime(2007, 1, 5, 9)])

    matched = tmatching.matching(ref_df, match_df)

    nptest.assert_allclose(np.array([0, 1, 2, 4]), matched.matched_data)
    assert len(matched) == 4


def test_matching_series():
    """
    test matching function with pd.Series as input
    """
    data = np.arange(10.)
    data[3] = np.nan

    ref_ser = pd.Series(data, index=pd.date_range(datetime(2007, 1, 1, 0),
                                                  "2007-01-10", freq="D"))
    match_ser = pd.Series(np.arange(5),
                          index=[datetime(2007, 1, 1, 9),
                                 datetime(2007, 1, 2, 9),
                                 datetime(2007, 1, 3, 9),
                                 datetime(2007, 1, 4, 9),
                                 datetime(2007, 1, 5, 9)],
                          name='matched_data')

    matched = tmatching.matching(ref_ser, match_ser)

    nptest.assert_allclose(np.array([0, 1, 2, 4]), matched.matched_data)
    assert len(matched) == 4

    matched = tmatching.df_match(ref_ser, match_ser, duplicate_nan=True)

    nptest.assert_allclose(np.array([0, 1, 2, 3, 4, np.nan, np.nan,
                                     np.nan, np.nan, np.nan]),
                           matched.matched_data)


def test_matching_tz():
    """
    test matching function with pd.Series as input and timezone information
    """
    ref_tz = 'Europe/London'
    ref_index = pd.date_range("2007-01-01", "2007-01-10", tz=ref_tz)

    data = np.arange(10.)
    data[3] = np.nan
    ref_ser = pd.Series(data, index=ref_index)

    match_tz = 'US/Pacific'
    match_index = pd.date_range("2007-01-01 09:00:00",
                                "2007-01-05 09:00:00", tz=match_tz)

    match_ser = pd.Series(np.arange(len(match_index)),
                          index=match_index, name='matched_data')

    matched = tmatching.matching(ref_ser, match_ser)

    nptest.assert_allclose(np.array([0, 1, 3, 4]), matched.matched_data)
    assert len(matched) == 4

    matched = tmatching.df_match(ref_ser, match_ser)

    nptest.assert_allclose(np.array([0, 0, 1, 2, 3, 4, 4, 4, 4, 4]),
                           matched.matched_data)
    assert len(matched) == 10

    matched = tmatching.df_match(ref_ser, match_ser, duplicate_nan=True)

    nptest.assert_allclose(np.array([np.nan, 0, 1, 2, 3, 4, np.nan, np.nan,
                                     np.nan, np.nan]),
                           matched.matched_data)
    assert len(matched) == 10


def test_timezone_handling():
    """
    Test timezone handling.
    """
    data = np.arange(5.0)
    data[3] = np.nan

    match_df = pd.DataFrame({"data": data}, index=pd.date_range(datetime(2007, 1, 1, 0),
                                                                "2007-01-05", freq="D", tz="UTC"))
    timezone = pytz.timezone("UTC")
    ref_df = pd.DataFrame({"matched_data": np.arange(5)},
                          index=[timezone.localize(datetime(2007, 1, 1, 9)),
                                 timezone.localize(datetime(2007, 1, 2, 9)),
                                 timezone.localize(datetime(2007, 1, 3, 9)),
                                 timezone.localize(datetime(2007, 1, 4, 9)),
                                 timezone.localize(datetime(2007, 1, 5, 9))])
    matched = tmatching.matching(ref_df, match_df)

    nptest.assert_allclose(np.array([0, 1, 2, 4]), matched.matched_data)
    assert len(matched) == 4

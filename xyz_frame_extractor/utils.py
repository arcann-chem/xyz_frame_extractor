"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023-2024 ArcaNN developers group <https://github.com/arcann-chem>                     #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/09/20
Last modified: 2024/05/15

This script provides utility functions for reading and writing XYZ format trajectory files.

It includes the following functions:
- string_to_nine_floats_array: Convert a string containing nine space-separated floats into a NumPy array of these floats.
- string_to_three_floats_array: Convert a string containing three space-separated floats into a NumPy array of these floats.
"""

# Third-party modules
import numpy as np
from typing import Tuple


def string_to_nine_floats_array(s: str) -> Tuple[bool, np.ndarray]:
    """
    Convert a string containing nine space-separated floats into a NumPy array of these floats.

    Parameters
    ----------
    s : str
        Input string containing space-separated numbers.

    Returns
    -------
    bool
        True if conversion is successful, False otherwise.
    np.ndarray
        A numpy array of floats if conversion is successful, otherwise an empty numpy array.

    Raises
    ------
    ValueError
        If any of the parts of the string cannot be converted to a float.
    """
    parts = s.split()
    if len(parts) != 9:
        return False, np.zeros(0)

    array_elements = []
    for part in parts:
        try:
            array_elements.append(float(part))
        except ValueError:
            raise ValueError(f"'{part}' cannot be converted to float.")

    return True, np.array(array_elements)


def string_to_three_floats_array(s: str) -> Tuple[bool, np.ndarray]:
    """
    Convert a string containing three space-separated floats into a NumPy array of these floats.

    Parameters
    ----------
    s : str
        Input string containing space-separated numbers.

    Returns
    -------
    bool
        True if conversion is successful, False otherwise.
    np.ndarray
        A numpy array of floats if conversion is successful, otherwise an empty numpy array.

    Raises
    ------
    ValueError
        If any of the parts of the string cannot be converted to a float.
    """
    parts = s.split()
    if len(parts) != 3:
        return False, np.zeros(0)

    array_elements = []
    for part in parts:
        try:
            array_elements.append(float(part))
        except ValueError:
            raise ValueError(f"'{part}' cannot be converted to float.")

    return True, np.array(array_elements)

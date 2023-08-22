"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023 ArcaNN developers group <https://github.com/arcann-chem>                          #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/07/17
Last modified: 2023/08/08

This script provides utility functions for reading and writing XYZ format trajectory files.

It includes the following functions:
- read_xyz_trajectory: Read an XYZ format trajectory file and extract the number of atoms, atomic symbols, and atomic coordinates.
- write_xyz_frame: Write the XYZ coordinates of a specific frame of a trajectory to a file.
"""
# Standard library modules
import re
from pathlib import Path
from typing import Tuple

# Third-party modules
import numpy as np


def read_xyz_trajectory(
    file_path: Path,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Read an XYZ format trajectory file and return the number of atoms, atomic symbols, and atomic coordinates.

    Parameters
    ----------
    file_path : Path
        The path to the trajectory file.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        A tuple containing the following numpy arrays:
        - num_atoms (np.ndarray): Array of the number of atoms for each step with dim(nb_step)
        - atom_symbols (np.ndarray): Array of atomic symbols with dim(nb_step, num_atoms)
        - atom_coords (np.ndarray): Array of atomic coordinates with dim(nb_step, num_atoms, 3)
        - step_info (np.ndarray): Array of step information with shape (nb_step, 3), containing step number, time, and energy.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    TypeError
        If the number of atoms is not an integer.
    ValueError
        If the number of atoms is not constant throughout the trajectory file.
        If the file format is incorrect.
    """
    # Check if the file exists
    if not file_path.is_file():
        # If the file does not exist, log an error message and abort
        error_msg = f"File not found {file_path.name} not in {file_path.parent}"
        raise FileNotFoundError(error_msg)

    # Initialize the output lists
    num_atoms_list = []
    atom_symbols_list = []
    atom_coords_list = []
    step_info_list = []

    # Open the file and read in the lines
    with file_path.open("r") as f:
        lines = f.readlines()

        # Loop through each line in the file
        i = 0
        while i < len(lines):
            # First line contains the total number of atoms in the molecule
            num_atoms_str = lines[i].strip()
            if not re.match(r"^\d+$", num_atoms_str):
                error_msg = "Incorrect file format: number of atoms must be an integer."
                raise TypeError(error_msg)
            num_atoms = int(num_atoms_str)
            num_atoms_list.append(num_atoms)

            # Second line contains the molecule name or comment (optional)
            comment_line = lines[i + 1].strip()
            match = re.search(
                r"i\s*=\s*(\d+),\s*time\s*=\s*(\d+\.\d+),\s*E\s*=\s*(-?\d+\.\d+)",
                comment_line,
            )

            if match:
                step_info_list.append(
                    [int(match.group(1)), float(match.group(2)), float(match.group(3))]
                )

            # Initialize arrays to store the symbols and coordinates for the current timestep
            step_atom_symbols = np.zeros((num_atoms,), dtype="<U2")
            step_atom_coords = np.zeros((num_atoms, 3))

            # Loop through the lines for the current timestep
            for j in range(num_atoms):
                # Parse the line to get the symbol and coordinates
                try:
                    fields = lines[i + j + 2].split()
                except IndexError:
                    error_msg = (
                        "Incorrect file format: end of file reached prematurely."
                    )
                    raise IndexError(error_msg)

                if len(fields) != 4:
                    error_msg = "Incorrect file format: each line after the first two must contain an atomic symbol and three floating point numbers."
                    raise ValueError(error_msg)

                symbol = fields[0]
                if not re.match(r"^[A-Za-z]{1,2}$", symbol):
                    error_msg = f"Incorrect file format: invalid atomic symbol '{symbol}' on line {i+j+2}."
                    raise ValueError(error_msg)
                try:
                    x, y, z = map(float, fields[1:4])
                except ValueError:
                    error_msg = f"Incorrect file format: could not parse coordinates on line {i+j+2}."
                    raise ValueError(error_msg)

                # Add the symbol and coordinates to the arrays
                step_atom_symbols[j] = symbol
                step_atom_coords[j] = [x, y, z]

            # Add the arrays for the current timestep to the output lists
            atom_symbols_list.append(step_atom_symbols)
            atom_coords_list.append(step_atom_coords)

            # Increment the line index by num_atoms + 2 (to skip the two lines for the current timestep)
            i += num_atoms + 2

    # Check if the number of atoms is constant throughout the trajectory file.
    if len(set(num_atoms_list)) > 1:
        error_msg = "Number of atoms is not constant throughout the trajectory file."
        raise ValueError(error_msg)

    # Convert the lists to numpy arrays.
    num_atoms = np.array(num_atoms_list, dtype=int)
    step_info = np.array(step_info_list)
    atom_symbols = np.array(atom_symbols_list)
    atom_coords = np.array(atom_coords_list)

    return num_atoms, atom_symbols, atom_coords, step_info


def write_xyz_frame(
    file_path: Path,
    frame_idx: int,
    num_atoms: np.ndarray,
    atom_coords: np.ndarray,
    atom_symbols: np.ndarray,
    comment_line: np.ndarray = None,
    comment: str = "frame",
) -> None:
    """
    Write the XYZ coordinates of a specific frame of a trajectory to a file.

    Parameters
    ----------
    file_path : Path
        The file path to write the XYZ coordinates to.
    frame_idx : int
        The index of the frame to write the XYZ coordinates for.
    num_atoms : np.ndarray
        An array containing the number of atoms in each frame of the trajectory with shape (num_frames).
    atom_coords : np.ndarray
        An array containing the coordinates of each atom in each frame of the trajectory with shape (num_frames, num_atoms, 3).
    atom_symbols : np.ndarray
        An array containing the atomic symbols for each atom in each frame of the trajectory with shape (num_frames, num_atoms).
    comment_line : np.ndarray, optional
        An array containing additional information for the comment line with shape (num_frames, num_comment_values).
    comment : str, optional
        Type of comment line: "frame", "cp2k", or "cell".

    Returns
    -------
    None

    Raises
    ------
    IndexError
        If the specified frame index is out of range.
    ValueError
        If an incorrect value is provided for the comment line type.
    """

    # Check that the specified frame index is within the range of available frames
    if frame_idx >= num_atoms.size:
        error_msg = f"Frame index out of range: {frame_idx} (number of frames: {num_atoms.size})"
        raise IndexError(error_msg)

    if comment not in ["frame", "cp2k", "cell"]:
        error_msg = f"Incorrect value for comment line type: frame, cp2k or cell."
        raise IndexError(error_msg)

    # Open the specified file in append mode
    with file_path.open("a") as xyz_file:
        # Write the number of atoms in the specified frame to the file
        xyz_file.write(f"{num_atoms[frame_idx]}\n")

        # Write the comment line
        if comment == "frame":
            xyz_file.write(f"Frame index: {frame_idx}\n")
        elif comment == "cp2k":
            xyz_file.write(
                f"i = {comment_line[frame_idx, 0]}, time = {comment_line[frame_idx, 1]}, E = {comment_line[frame_idx, 2]}\n"
            )
        elif comment == "cell":
            cell = " ".join([f"{value:.4f}" for value in comment_line[frame_idx, 2:11]])
            xyz_file.write(f"ABC = {cell}\n")

        # Loop over each atom in the specified frame
        for ii in range(num_atoms[frame_idx]):
            # Write the atomic symbol and Cartesian coordinates to the file in XYZ format
            xyz_file.write(
                f"{atom_symbols[frame_idx, ii]} "
                f"{atom_coords[frame_idx, ii, 0]:.6f} "
                f"{atom_coords[frame_idx, ii, 1]:.6f} "
                f"{atom_coords[frame_idx, ii, 2]:.6f}\n"
            )
    # Close the file
    xyz_file.close()

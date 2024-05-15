"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023-2024 ArcaNN developers group <https://github.com/arcann-chem>                     #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/07/17
Last modified: 2024/05/15

This script provides utility functions for reading and writing XYZ format trajectory files.

It includes the following functions:
- parse_xyz_trajectory_file: Read an XYZ format trajectory file and extract the number of atoms, atomic symbols, and atomic coordinates.
- write_xyz_frame: Write the XYZ coordinates of a specific frame of a trajectory to a file.
"""
# Standard library modules
import re
from pathlib import Path
from typing import List, Tuple, Union

# Third-party modules
import numpy as np


def parse_xyz_trajectory_file(
    trajectory_file_path: Path, is_extended: bool
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List]:
    """
    Read an XYZ format trajectory file and return the number of atoms, atomic symbols, and atomic coordinates.

    Parameters
    ----------
    trajectory_file_path : Path
        The path to the trajectory file.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, List]
        A tuple containing the following numpy arrays:
        - atom_counts (np.ndarray): Array of the number of atoms for each frame with dim(frame_count)
        - atomic_symbols (np.ndarray): Array of atomic symbols with dim(frame_count, atom_count_frame) and a size of 3 char
        - atomic_coordinates (np.ndarray): Array of atomic coordinates with dim(frame_count, atom_count_frame, 3)
        - comments (List): List of comment file_lines with dim(frame_count)

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
    if not trajectory_file_path.is_file():
        # If the file does not exist, log an error message and abort
        error_msg = f"File not found {trajectory_file_path.name} not in {trajectory_file_path.parent}"
        raise FileNotFoundError(error_msg)

    # Initialize the output lists
    atom_counts = []
    atomic_symbols = []
    atomic_coordinates = []
    comments = []

    # Open the file and read in the file_lines
    with trajectory_file_path.open("r") as f:
        file_lines = f.readlines()

        # Loop through each line in the file
        i = 0
        while i < len(file_lines):
            # First line contains the total number of atoms in the molecule
            atom_count_str = file_lines[i].strip()
            if not re.match(r"^\d+$", atom_count_str):
                error_msg = "Incorrect file format: number of atoms must be an integer."
                raise TypeError(error_msg)
            atom_count_frame = int(atom_count_str)
            atom_counts.append(atom_count_frame)

            # Second line is the comment line (optional)
            comments_frame = file_lines[i + 1].strip()
            if is_extended:
                lattice_regex = r"Lattice=\"([-\d\.]+\s+){8}[-\d\.]+\""
                properties_regex = r"Properties=species:S:1:pos:R:3"

                lattice_match = re.search(lattice_regex, comments_frame)
                properties_match = re.search(properties_regex, comments_frame)
                lattice_match_found = bool(lattice_match)
                properties_match_found = bool(properties_match)

                if lattice_match_found and properties_match_found:
                    pass
                else:
                    error_msg = f"Wrong extended format: line {i}, comment '{comments_frame}'.\nEither use --cell_file or --lattice, or write a correct extended xyz."
                    raise TypeError(error_msg)

            comments.append(comments_frame)

            # Initialize arrays to store the symbols and coordinates for the current timeframe
            atomic_symbols_frame = np.zeros((atom_count_frame,), dtype="<U3")
            atomic_coordinates_frame = np.zeros((atom_count_frame, 3))

            # Loop through the file_lines for the current timeframe
            for j in range(atom_count_frame):
                # Parse the line to get the symbol and coordinates
                try:
                    fields = file_lines[i + j + 2].split()
                except IndexError:
                    error_msg = (
                        "Incorrect file format: end of file reached prematurely."
                    )
                    raise IndexError(error_msg)

                if len(fields) != 4:
                    error_msg = "Incorrect file format: each line after the first two must contain an atomic symbol and three floating point numbers."
                    raise ValueError(error_msg)

                atomic_symbol = fields[0]
                if not re.match(r"^[A-Za-z]{1,2}$", atomic_symbol):
                    error_msg = f"Incorrect file format: invalid atomic symbol '{atomic_symbol}' on line {i+j+2}."
                    raise ValueError(error_msg)
                try:
                    x, y, z = map(float, fields[1:4])
                except ValueError:
                    error_msg = f"Incorrect file format: could not parse coordinates on line {i+j+2}."
                    raise ValueError(error_msg)

                # Add the symbol and coordinates to the arrays
                atomic_symbols_frame[j] = atomic_symbol
                atomic_coordinates_frame[j] = [x, y, z]

            # Add the arrays for the current timeframe to the output lists
            atomic_symbols.append(atomic_symbols_frame)
            atomic_coordinates.append(atomic_coordinates_frame)

            # Increment the line index by atom_count_frame + 2 (to skip the two file_lines for the current timeframe)
            i += atom_count_frame + 2

    # Check if the number of atoms is constant throughout the trajectory file.
    if len(set(atom_counts)) > 1:
        error_msg = "Number of atoms is not constant throughout the trajectory file."
        raise ValueError(error_msg)

    # Convert the lists to numpy arrays.
    atom_counts = np.array(atom_counts, dtype=int)
    atomic_symbols = np.array(atomic_symbols)
    atomic_coordinates = np.array(atomic_coordinates)

    return atom_counts, atomic_symbols, atomic_coordinates, comments, is_extended


def write_xyz_frame(
    trajectory_file_path: Path,
    frame_idx: int,
    atom_counts: np.ndarray,
    atomic_symbols: np.ndarray,
    atomic_coordinates: np.ndarray,
    comments: Union[np.ndarray, List, str],
    mode_type: str,
) -> None:
    """
    Write the XYZ coordinates of a specific frame of a trajectory to a file.

    Parameters
    ----------
    trajectory_file_path : Path
        The file path to write the XYZ coordinates to.
    frame_idx : int
        The index of the frame to write the XYZ coordinates for.
    atom_counts : np.ndarray
        An array containing the number of atoms in each frame of the trajectory with dim(num_frames).
    atomic_symbols : np.ndarray
        An array containing the atomic symbols for each atom in each frame of the trajectory with dim(num_frames, atom_counts).
    atomic_coordinates : np.ndarray
        An array containing the coordinates of each atom in each frame of the trajectory with dim(num_frames, atom_counts, 3).
    comments : Union[np.ndarray, List, str]
        Depending on the mode_comment value, the shape and type of this argument might vary:
          - "copy": dim(num_frames)
          - Other values might have different expected shapes.
    mode_type : str
        Defines the type of comment line to write. Possible values are: "nothing", "copy", "lattice", "cell_array".

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
    if frame_idx >= atom_counts.size:
        error_msg = f"Frame index out of range: {frame_idx} (number of frames: {atom_counts.size})"
        raise IndexError(error_msg)

    # Open the specified file in append mode
    with trajectory_file_path.open("a") as xyz_file:
        # Write the number of atoms in the specified frame to the file
        xyz_file.write(f"{atom_counts[frame_idx]}\n")

        # Write the comment line
        if mode_type == "nothing":
            xyz_file.write(f"Frame={frame_idx}\n")
        elif mode_type == "copy":
            xyz_file.write(f"{comments[frame_idx]}\n")
        elif mode_type == "lattice":
            extended_comment = f'Lattice="{" ".join(map(str,comments))}" Properties=species:S:1:pos:R:3 Frame={frame_idx}\n'
            xyz_file.write(extended_comment)
        elif mode_type == "cell_array":
            cell = " ".join([f"{value:.4f}" for value in comments[frame_idx, 2:11]])
            extended_comment = (
                f'Lattice="{cell}" Properties=species:S:1:pos:R:3 Frame={frame_idx}\n'
            )
            xyz_file.write(extended_comment)
        elif mode_type == "extended":
            xyz_file.write(f"{comments[frame_idx]}\n")

        # Loop over each atom in the specified frame
        for ii in range(atom_counts[frame_idx]):
            # Write the atomic symbol and Cartesian coordinates to the file in XYZ format
            xyz_file.write(
                f"{atomic_symbols[frame_idx, ii]} "
                f"{atomic_coordinates[frame_idx, ii, 0]:.6f} "
                f"{atomic_coordinates[frame_idx, ii, 1]:.6f} "
                f"{atomic_coordinates[frame_idx, ii, 2]:.6f}\n"
            )

    # Close the file
    xyz_file.close()

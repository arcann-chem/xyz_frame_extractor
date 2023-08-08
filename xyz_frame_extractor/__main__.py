"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023 ArcaNN developers group <https://github.com/arcann-chem>                          #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/07/17
Last modified: 2023/08/08

This script extracts individual frames from a trajectory file in XYZ format and saves them to a new trajectory file.
"""
# Standard library modules
import argparse
import logging
from pathlib import Path

import numpy as np

from xyz_frame_extractor.xyz import read_xyz_trajectory, write_xyz_frame

parser = argparse.ArgumentParser(
    description="Process a xyz trajectory file with options."
)
parser.add_argument("input", type=str, help="path to the input trajectory xyz file")
parser.add_argument("output", type=str, help="path to the output trajectory xyz file")
parser.add_argument(
    "--stride",
    type=int,
    default=1,
    help="stride value: positive integer specifying the frame extraction interval (default: 1)",
)
parser.add_argument(
    "--skip",
    type=int,
    default=0,
    help="number of frames to skip from the beginning of the trajectory (default: 0)",
)
parser.add_argument(
    "--comment",
    type=str,
    default="frame",
    choices=["frame", "cell", "cp2k"],
    help="path to the cell information file (required for 'cell' comment type)",
)
parser.add_argument(
    "--cell_file",
    type=str,
    default="",
    help="TODO"
)

def main(input_file, output_file, frame_stride, skip_frames, comment, cell_file):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    input_xyz = Path(input_file)
    output_xyz = Path(output_file)

    # Check comment type
    known_comment_types = ["frame", "cell", "cp2k"]
    if comment not in known_comment_types:
        logging.error(f"'{comment}' is not a known comment type. Choose from {', '.join(known_comment_types)}.")
        return 1

    # Process cell file for 'cell' comment type
    if comment == "cell":
        cell_file_path = Path(cell_file)
        if not cell_file_path.is_file():
            logging.error(f"Cell file '{cell_file_path}' not found.")
            return 1
        comment_line = np.genfromtxt(cell_file_path)
    else:
        comment_line = None

    # Check input file existence
    if not input_xyz.is_file():
        error_msg = f"{input_xyz} file not found"
        logging.error(error_msg)
        return 1

    # Prompt before overwriting output file
    if output_xyz.is_file():
        while True:
            user_input = input(f"File '{output_xyz}' already exists. Delete it (Y) or abort (N)? ").strip().upper()
            if user_input == "Y":
                output_xyz.unlink()
                logging.info(f"Deleted '{output_xyz}'.")
                break
            elif user_input == "N":
                logging.info("Operation aborted.")
                return 1
            else:
                logging.warning("Invalid input. Please enter 'Y' or 'N'.")


    # Validate stride and skip_frames values
    if frame_stride <= 0 or skip_frames < 0:
        logging.error("Stride should be a positive integer, and skip count should be non-negative.")
        return 1

    num_atoms, atom_symbols, atom_coords, step_infos = read_xyz_trajectory(input_xyz)

    if frame_stride > num_atoms.size:
        logging.error("Stride value cannot be greater than the total number of frames in the trajectory.")
        return 1

    if comment_line is None and comment == "cp2k":
        comment_line = step_infos

    num_saved_frames = 0
    for frame_idx in range(skip_frames, num_atoms.size, frame_stride):
        if frame_idx >= num_atoms.size:
            continue
        write_xyz_frame(output_xyz, frame_idx, num_atoms, atom_coords, atom_symbols, comment_line, comment=comment)
        num_saved_frames += 1

    logging.info("Processing complete without errors.")
    logging.info(f"{num_saved_frames} frames saved.")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.input, args.output, args.stride, args.skip, args.comment, args.cell_file)

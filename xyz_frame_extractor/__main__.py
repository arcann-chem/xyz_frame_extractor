"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023 ArcaNN developers group <https://github.com/arcann-chem>                          #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/07/17
Last modified: 2023/07/17

This script extracts individual frames from a trajectory file in XYZ format and saves them to a new trajectory file.
"""
# Standard library modules
import argparse
import logging
from pathlib import Path


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


def main(input_file, output_file, frame_stride, skip_frames):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    input_xyz = Path(input_file)
    output_xyz = Path(output_file)

    if not input_xyz.is_file():
        error_msg = f"{input_xyz} file not found"
        logging.error(error_msg)
        return

    if frame_stride <= 0 or skip_frames < 0:
        error_msg = (
            "Stride should be a positive integer and skip count should be non-negative."
        )
        logging.error(error_msg)
        return

    num_atoms, atom_symbols, atom_coords = read_xyz_trajectory(input_xyz)

    if frame_stride > num_atoms.size:
        error_msg = "Stride value cannot be greater than the total number of frames in the trajectory."
        logging.error(error_msg)
        return

    for frame_idx in range(skip_frames, num_atoms.size, frame_stride):
        if frame_idx >= num_atoms.size:
            continue
        write_xyz_frame(output_xyz, frame_idx, num_atoms, atom_coords, atom_symbols)

    logging.info("Processing complete without errors.")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.input, args.output, args.stride, args.skip)

"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023 ArcaNN developers group <https://github.com/arcann-chem>                          #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/07/17
Last modified: 2023/09/20

This script extracts individual frames from a trajectory file in XYZ format and saves them to a new trajectory file.
"""
# Standard library modules
import argparse
import logging
from pathlib import Path

# Third-party modules
import numpy as np

# Local modules
from xyz_frame_extractor.xyz import read_xyz_trajectory, write_xyz_frame
from xyz_frame_extractor.utils import (
    string_to_nine_floats_array,
    string_to_three_floats_array,
)


def process_arguments():
    parser = argparse.ArgumentParser(
        description="Process an XYZ trajectory file with options."
    )

    parser.add_argument("input", type=str, help="Path to the input trajectory XYZ file")
    parser.add_argument(
        "output", type=str, help="Path to the output trajectory XYZ file"
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Stride value: a positive integer specifying the frame extraction interval (default: 1)",
    )
    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Number of frames to skip from the beginning of the trajectory (default: 0)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="frame",
        choices=["frame", "copy", "extended"],
        help="Mode type for the mode line (default: 'frame', choices: 'frame', 'copy', 'extended')",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cell_file",
        type=str,
        default=None,
        help="Path to the cell information file in CP2K format (required for 'extended' mode type)",
    )
    group.add_argument(
        "--lattice",
        type=str,
        default=None,
        help="String representing lattice parameters ('R1x R1y R1z R2x R2y R2z R3x R3y R3z' or 'A B C') and constant for all steps (required for 'extended' mode type)",
    )

    return parser.parse_args()


def handle_mode_type(args):
    # This function manages the mode type and related parameters, returning the mode type to be used in the main function
    mode_copy = False
    lattice_array = None
    cell_array = None

    if args.mode == "extended" and args.lattice:
        is_nine, lattice_values = string_to_nine_floats_array(args.lattice)
        is_three, three_values = string_to_three_floats_array(args.lattice)
        if is_nine:
            lattice_array = lattice_values
            return lattice_array, "lattice", 0
        elif is_three:
            lattice_array = np.array(
                [
                    three_values[0],
                    0.0,
                    0.0,
                    0.0,
                    three_values[1],
                    0.0,
                    0.0,
                    0.0,
                    three_values[2],
                ]
            )
            return lattice_array, "lattice", 0
        else:
            logging.error(
                "Wrong format for --lattice: 'R1x R1y R1z R2x R2y R2z R3x R3y R3z' or 'A B C'."
            )
            return None, None, 1
    elif args.mode == "extended" and args.cell_file:
        cell_file_path = Path(args.cell_file)
        if not cell_file_path.is_file():
            logging.error(f"Cell information file '{cell_file_path}' not found.")
            return None, None, 1
        cell_array = np.genfromtxt(cell_file_path)
        return cell_array, "cell_array", 0
    elif args.mode == "extended":
        logging.error(f"Extended requested but no --cell_file or --lattice provided.")
        return None, None, 1
    elif args.mode == "copy":
        return True, "copy", 0
    else:
        return None, "nothing", 0


def main(args):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    input_xyz = Path(args.input)
    output_xyz = Path(args.output)

    # Check input file existence
    if not input_xyz.is_file():
        logging.error(f"{input_xyz} file not found.")
        return 1

    # Prompt before overwriting output file
    if output_xyz.is_file():
        while True:
            user_input = (
                input(
                    f"File '{output_xyz}' already exists. Delete it (Y) or abort (N)? "
                )
                .strip()
                .upper()
            )
            if user_input == "Y":
                output_xyz.unlink()
                logging.info(f"Deleted '{output_xyz}'.")
                break
            elif user_input == "N":
                logging.info("Operation aborted.")
                return 0
            else:
                logging.warning("Invalid input. Please enter 'Y' or 'N'.")

    # Handle mode types and lattice information
    comment_line, mode_type, error_num = handle_mode_type(args)
    if error_num != 0:
        logging.error("Aborting...")
        return 1

    # Validate stride and skip_frames values
    if args.stride <= 0 or args.skip < 0:
        logging.error(
            "Stride should be a positive integer, and skip count should be non-negative."
        )
        return 1

    num_atoms, atom_symbols, atom_coords, read_comment_line = read_xyz_trajectory(
        input_xyz
    )
    if args.stride > num_atoms.size:
        logging.error(
            "Stride value cannot be greater than the total number of frames in the trajectory."
        )
        return 1
    if mode_type == "copy":
        comment_line = read_comment_line

    num_saved_frames = 0
    for frame_idx in range(args.skip, num_atoms.size, args.stride):
        if frame_idx >= num_atoms.size:
            continue
        write_xyz_frame(
            output_xyz,
            frame_idx,
            num_atoms,
            atom_coords,
            atom_symbols,
            comment_line,
            mode_type,
        )
        num_saved_frames += 1

    logging.info("Processing complete without errors.")
    logging.info(f"{num_saved_frames} frames saved.")


if __name__ == "__main__":
    arguments = process_arguments()
    main(arguments)

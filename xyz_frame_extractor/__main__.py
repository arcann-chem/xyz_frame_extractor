"""
#----------------------------------------------------------------------------------------------------#
#   ArcaNN: xyz_frame_extractor                                                                      #
#   Copyright 2023-2024 ArcaNN developers group <https://github.com/arcann-chem>                     #
#                                                                                                    #
#   SPDX-License-Identifier: AGPL-3.0-only                                                           #
#----------------------------------------------------------------------------------------------------#
Created: 2023/07/17
Last modified: 2024/05/15

This script extracts individual frames from a trajectory file in XYZ format and saves them to a new trajectory file.
"""

# Standard library modules
import argparse
import logging
from pathlib import Path

# Third-party modules
import numpy as np

# Local modules
from xyz_frame_extractor.xyz import parse_xyz_trajectory_file, write_xyz_frame
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
        "output",
        type=str,
        nargs="?",
        default=None,
        help=(
            "Path to the output trajectory XYZ file. If omitted, the output file name "
            "is generated as '<input_stem>_<begin>_<end>_<stride>.xyz'."
        ),
    )
    parser.add_argument(
        "--begin",
        type=int,
        default=0,
        help="Start frame index (0-based, default: 0)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="End frame index (0-based, inclusive; use -1 for last frame; default: last frame)",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Stride value: a positive integer specifying the frame extraction interval (default: 1)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="nothing",
        choices=["nothing", "copy", "extended"],
        help="Mode type for the mode line (default: 'nothing', choices: 'nothing', 'copy', 'extended')",
    )
    parser.add_argument(
        "--per_frame",
        action="store_true",
        help=(
            "Write one frame per file named '<output_stem>_00000.xyz' "
            "(frame number zero-padded)."
        ),
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

    if args.mode == "extended" and args.lattice:
        lattice_array = None
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
            return lattice_array, None, 1

    elif args.mode == "extended" and args.cell_file:
        cell_array = None
        cell_file_path = Path(args.cell_file)
        if not cell_file_path.is_file():
            logging.error(f"Cell information file '{cell_file_path}' not found.")
            return cell_array, None, 1
        cell_array = np.genfromtxt(cell_file_path)
        return cell_array, "cell_array", 0

    elif args.mode == "extended":
        return True, "extended", 0

    elif args.mode == "copy":
        return True, "copy", 0

    else:
        return None, "nothing", 0


def main(args=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args is None:
        args = process_arguments()

    input_xyz = Path(args.input)
    # Check input file existence
    if not input_xyz.is_file():
        logging.error(f"{input_xyz} file not found.")
        return 1

    # Handle mode types and lattice information
    comments, mode_type, error_num = handle_mode_type(args)
    is_extended = False
    if mode_type == "extended":
        is_extended = True

    if error_num != 0:
        logging.error("Aborting...")
        return 1

    atom_counts, atomic_symbols, atomic_coordinates, in_comments, is_extended = (
        parse_xyz_trajectory_file(input_xyz, is_extended)
    )

    # Validate begin/end/stride values
    if args.stride <= 0:
        logging.error("Stride should be a positive integer.")
        return 1
    if args.begin < 0:
        logging.error("Begin index should be non-negative.")
        return 1
    if args.begin >= atom_counts.size:
        logging.error(
            "Begin index cannot be greater than or equal to the total number of frames."
        )
        return 1
    if args.end is not None and args.end < args.begin:
        if args.end == -1:
            pass
        else:
            logging.error("End index cannot be less than the begin index.")
            return 1
    logging.info(f"Trajectory contains {atom_counts.size} frames.")

    if args.end is None or args.end == -1:
        end_idx = atom_counts.size - 1
    else:
        if args.end >= atom_counts.size:
            logging.warning(
                "End index exceeds total number of frames; using last frame instead."
            )
            end_idx = atom_counts.size - 1
        else:
            end_idx = args.end

    if args.output is None:
        output_name = f"{input_xyz.stem}_{args.begin}_{end_idx}_{args.stride}.xyz"
        output_xyz = Path.cwd() / output_name
    else:
        output_xyz = Path(args.output)

    # Prompt before overwriting output file
    if args.per_frame:
        existing_files = list(output_xyz.parent.glob(f"{output_xyz.stem}_*.xyz"))
        if existing_files:
            while True:
                user_input = (
                    input(
                        "Per-frame output files already exist. Delete them (Y) or abort (N)? "
                    )
                    .strip()
                    .upper()
                )
                if user_input == "Y":
                    for file_path in existing_files:
                        file_path.unlink()
                    logging.info(
                        f"Deleted {len(existing_files)} existing per-frame files."
                    )
                    break
                elif user_input == "N":
                    logging.info("Operation aborted.")
                    return 0
                else:
                    logging.warning("Invalid input. Please enter 'Y' or 'N'.")
    else:
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

    if mode_type == "copy":
        comments = in_comments
    elif mode_type == "extended" and is_extended:
        comments = in_comments

    num_saved_frames = 0
    for frame_idx in range(args.begin, end_idx + 1, args.stride):
        if frame_idx >= atom_counts.size:
            continue
        if args.per_frame:
            output_path = output_xyz.with_name(
                f"{output_xyz.stem}_{frame_idx:05d}.xyz"
            )
        else:
            output_path = output_xyz
        write_xyz_frame(
            output_path,
            frame_idx,
            atom_counts,
            atomic_symbols,
            atomic_coordinates,
            comments,
            mode_type,
        )
        num_saved_frames += 1

    logging.info("Processing complete without errors.")
    logging.info(f"{num_saved_frames} frames saved.")


if __name__ == "__main__":
    main()

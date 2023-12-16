#!/bin/bash

python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_2_1_nothing.xyz --stride 2 --skip 1 --mode nothing
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_2_1_copy.xyz --stride 2 --skip 1 --mode copy
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_2_1_lattice_3.xyz --stride 2 --skip 1 --mode extended --lattice "19.734 19.734 19.734"
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_2_1_lattice_9.xyz --stride 2 --skip 1 --mode extended --lattice "19.734 0.0 0.0 0.0 19.734 0.0 0.0 0.0 19.734"
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_2_1_cell.xyz --stride 2 --skip 1 --mode extended --cell_file original_trajectories/water-MD_NVT-Cell.cell

python -m xyz_frame_extractor original_trajectories/water-MD_NPT-Trajectory.xyz water-MD_NPT-Trajectory_2_1_nothing.xyz --stride 2 --skip 1 --mode nothing
python -m xyz_frame_extractor original_trajectories/water-MD_NPT-Trajectory.xyz water-MD_NPT-Trajectory_2_1_copy.xyz --stride 2 --skip 1 --mode copy
python -m xyz_frame_extractor original_trajectories/water-MD_NPT-Trajectory.xyz water-MD_NPT-Trajectory_2_1_cell.xyz --stride 2 --skip 1 --mode extended --cell_file original_trajectories/water-MD_NPT-Cell.cell

for file in water-MD_NVT-Trajectory_2_1_nothing.xyz water-MD_NVT-Trajectory_2_1_copy.xyz water-MD_NVT-Trajectory_2_1_lattice_3.xyz water-MD_NVT-Trajectory_2_1_lattice_9.xyz water-MD_NVT-Trajectory_2_1_cell.xyz water-MD_NPT-Trajectory_2_1_nothing.xyz water-MD_NPT-Trajectory_2_1_copy.xyz water-MD_NPT-Trajectory_2_1_cell.xyz
do
    diff $file ref_trajectories/$file
done
#!/bin/bash

python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_1_-1_2_nothing.xyz --begin 1 --end -1 --stride 2 --mode nothing
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_1_-1_2_copy.xyz --begin 1 --end -1 --stride 2 --mode copy
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_1_-1_2_lattice_3.xyz --begin 1 --end -1 --stride 2 --mode extended --lattice "19.734 19.734 19.734"
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_1_-1_2_lattice_9.xyz --begin 1 --end -1 --stride 2 --mode extended --lattice "19.734 0.0 0.0 0.0 19.734 0.0 0.0 0.0 19.734"
python -m xyz_frame_extractor original_trajectories/water-MD_NVT-Trajectory.xyz water-MD_NVT-Trajectory_1_-1_2_cell.xyz --begin 1 --end -1 --stride 2 --mode extended --cell_file original_trajectories/water-MD_NVT-Cell.cell

python -m xyz_frame_extractor original_trajectories/water-MD_NPT-Trajectory.xyz water-MD_NPT-Trajectory_1_-1_2_nothing.xyz --begin 1 --end -1 --stride 2 --mode nothing
python -m xyz_frame_extractor original_trajectories/water-MD_NPT-Trajectory.xyz water-MD_NPT-Trajectory_1_-1_2_copy.xyz --begin 1 --end -1 --stride 2 --mode copy
python -m xyz_frame_extractor original_trajectories/water-MD_NPT-Trajectory.xyz water-MD_NPT-Trajectory_1_-1_2_cell.xyz --begin 1 --end -1 --stride 2 --mode extended --cell_file original_trajectories/water-MD_NPT-Cell.cell

for file in water-MD_NVT-Trajectory_1_-1_2_nothing.xyz water-MD_NVT-Trajectory_1_-1_2_copy.xyz water-MD_NVT-Trajectory_1_-1_2_lattice_3.xyz water-MD_NVT-Trajectory_1_-1_2_lattice_9.xyz water-MD_NVT-Trajectory_1_-1_2_cell.xyz water-MD_NPT-Trajectory_1_-1_2_nothing.xyz water-MD_NPT-Trajectory_1_-1_2_copy.xyz water-MD_NPT-Trajectory_1_-1_2_cell.xyz
do
    diff $file ref_trajectories/$file
done

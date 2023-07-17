# ArcaNN XYZ Trajectory Processor

The ArcaNN XYZ Trajectory Processor is a command-line tool that processes trajectory files in the XYZ format. It allows you to extract frames from a trajectory file based on specified options and write them to a new trajectory file.

## Features

- Extract frames from an XYZ trajectory file
- Specify the frame extraction interval using the `--stride` option
- Skip a certain number of frames from the beginning using the `--skip` option
- Process large trajectory files efficiently

## Requirements

- Python 3.x
- Additional Python dependencies can be installed using the `requirements.txt` file

## Installation

1. Clone the ArcaNN XYZ Trajectory Processor repository:

   ```bash
   git clone https://github.com/arcann-chem/xyz-trajectory-processor.git
   ```

2. Navigate to the project directory:

   ```bash
   cd xyz-trajectory-processor
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python xyz_trajectory_processor.py input.xyz output.xyz --stride 2 --skip 10
```

- `input.xyz` is the path to the input XYZ trajectory file.
- `output.xyz` is the path to the output XYZ trajectory file.
- `--stride` (optional) specifies the frame extraction interval (default: 1).
- `--skip` (optional) specifies the number of frames to skip from the beginning of the trajectory (default: 0).

**Note:** The input and output file paths are required parameters, while `--stride` and `--skip` are optional.

## Examples

1. Extract frames from `input.xyz` with a stride of 2, skipping the first 10 frames:

   ```bash
   python xyz_trajectory_processor.py input.xyz output.xyz --stride 2 --skip 10
   ```

2. Extract frames from `input.xyz` without skipping any frames:

   ```bash
   python xyz_trajectory_processor.py input.xyz output.xyz
   ```

## License

Distributed under the GNU Affero General Public License v3.0. See `LICENSE` for more information.

## Contact

For any questions or inquiries, please contact the ArcaNN developers group at [https://github.com/arcann-chem](https://github.com/arcann-chem).

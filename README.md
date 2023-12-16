# ArcaNN XYZ Frame Extractor

The ArcaNN XYZ Frame Extractor is a command-line tool that processes trajectory files in the XYZ format. It allows you to extract frames from a trajectory file based on specified options and write them to a new trajectory file.

## Features

- Extract frames from an XYZ trajectory file
- Specify frame extraction interval (`--stride`)
- Skip initial frames (`--skip`)
- Mode options for comment lines (`--mode`): `nothing`, `copy`, `extended`
- Can use a CP2K cell file using the `--cell_file` option
- Can write extended xyz as output

## Requirements

- Python >= 3.6
- Additional Python dependencies can be installed using the `requirements.txt` file

## Installation

1. Download the ArcaNN XYZ Frame Extractor

    Option a. Clone the ArcaNN XYZ Frame Extractor repository:

    ```bash
    git clone https://github.com/arcann-chem/xyz_frame_extractor.git
    ```

    Option b. Download the archive by clicking on the green Code button and then download zip

    ```bash
    unzip xyz_frame_extractor-main.zip -d xyz_frame_extractor
    ```

2. Navigate to the project directory:

    ```bash
    cd xyz_frame_extractor
    ```

3. Install the dependencies and the module (please do not forget the dot at the end):

    ```bash
    pip install -r requirements.txt .
    ```

## Usage

Go to the directory where the trajectory is located or otherwise specify the absolute path of the file of the trajectory, then

```bash
python -m xyz_frame_extractor input.xyz output.xyz --stride 2 --skip 10 --mode extended --cell_file input.cell
```

- `input.xyz` is the name of the input XYZ trajectory file (if not in the directory specify the absolute path)
- `output.xyz` is the name of the output XYZ trajectory file (if needed, specify the absolute path where you want to locate your file)
- `--stride` (optional) specifies the frame extraction interval (default: 1).
- `--skip` (optional) specifies the number of frames to skip from the beginning of the trajectory (default: 0).
- `--mode` (optional) specifies the comment line (default: frame): frame, cp2k or cell.
  - `nothing` write the comment line as `Frame: {step_number}`
  - `copy` copy the comment line from the input to the output
  - `extended` write the comment as extended xyz. If no other argument is provided, it will assume your input xyz is in extended format and copy the comment line (but it will not copy the auxiliaries properties !)
    - use `--cell_file` to provide a CP2K cell file to write extended xyz format (CP2K format is Frame Time xx xy xz yx yy yz zx zy zz)
    - use `--lattice` and provide a string either in the format `A B C` or `xx xy xz yx yy yz zx zy zz` to write extended xyz format (but constant cell)

**Note:** The input and output file paths are required parameters, while `--stride`, `--skip`, `--mode`, `--cell_file` and `--lattice` are optional.

## Examples

1. Extract frames from `input.xyz` with a stride of 2, skipping the first 10 frames:

    ```bash
    python -m xyz_frame_extractor input.xyz output.xyz --stride 2 --skip 10
    ```

2. Extract frames from `input.xyz` with a stride of 50 without skipping any frames:

    ```bash
    python -m xyz_frame_extractor $HOME/inputs/input.xyz  $HOME/outputs/output.xyz --stride 50
    ```

## License

Distributed under the GNU Affero General Public License v3.0. See `LICENSE` for more information.

## Contact

For any questions or inquiries, please contact the ArcaNN developers group at [https://github.com/arcann-chem](https://github.com/arcann-chem).

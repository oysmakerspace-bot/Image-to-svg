# Image to SVG Converter

A simple command-line tool to convert PNG and JPEG images to SVG format.

## Installation

It is highly recommended to install this tool in a virtual environment to avoid conflicts with system packages and permission issues.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the tool:**
    The following command will install the package and its dependencies from `setup.py`.
    ```bash
    pip install .
    ```

## Usage

Once installed, you can use the tool from your terminal:

```bash
img-to-svg <input_file> <output_file>
```

### Example

```bash
img-to-svg my_image.png my_image.svg
```

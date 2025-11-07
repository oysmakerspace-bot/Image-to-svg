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

## API Usage

This project also provides a web service API for converting images to SVG. The API is built with Flask and can be run using Docker.

### Running the API with Docker

1.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```

2.  **The API will be available at `http://localhost:80`**

### Endpoints

-   `POST /upload`: Upload an image and get a job ID.
-   `GET /status/<job_id>`: Get the status of a job.
-   `GET /result/<job_id>`: Get the SVG result of a completed job.

### Worker Configuration

The background worker has a configurable sleep time, which can be set using the `WORKER_SLEEP_TIME` environment variable. The default value is 60 seconds.

You can set this variable in the `docker-compose.yml` file:

```yaml
worker:
  environment:
    - WORKER_SLEEP_TIME=30
```

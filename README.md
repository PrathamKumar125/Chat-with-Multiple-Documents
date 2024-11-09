# Chat-with-Multiple-Documents
## Docker Image

- **Docker Image Name**: `prathamkumars125/chat-with-multiple-document`
- **Docker Hub**: [prathamkumars125/chat-with-multiple-document](https://hub.docker.com/r/prathamkumars125/chat-with-multiple-document)
  
## Deployed Link: https://huggingface.co/spaces/pratham0011/Chat_with_Multiple_Documents
![image](https://github.com/user-attachments/assets/2b5ba953-d0b7-4d20-ac8e-ff3cfb8145dc)



### Description of Files

- **Notebooks/Chat_with_Multiple_Documents.ipynb**: Jupyter notebook for exploring and interacting with multiple documents.
- **static/app.py**: Streamlit application file.
- **static/man-kddi.png**: Image file used in the Streamlit app.
- **static/robot.png**: Another image file used in the Streamlit app.
- **README.md**: This file.
- **index.py**: FastAPI application file.
- **main.py**: Entry point for running both Streamlit and FastAPI.
- **requirements.txt**: Lists the Python dependencies required for the project.

## Setup and Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/PrathamKumar125/Chat-with-Multiple-Documents.git
    cd Chat-with-Multiple-Documents
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

The application can be run individually using: FastAPI app, Streamlit app, Or Both using main.py.

## Running the Application

### Start FastAPI : **Run the FastAPI application (`index.py`):**

    ```bash
    uvicorn index:app --reload
    ```

    By default, the FastAPI app will be available at `http://127.0.0.1:8000/docs`.

### Start Streamlit :  **Run the Streamlit application (`static/app.py`):**

    ```bash
    streamlit run streamlit_app.py
    ```

    By default, the Streamlit app will be available at `http://localhost:8501`.

### Start Both FastAPI and Streamlit via `main.py` : **Run the combined application (`main.py`):**

    ```bash
    streamlit run main.py
    ```

    This will start both the FastAPI server and the Streamlit application. By default:
    
    - The FastAPI app will be available at `http://127.0.0.1:8000`.
    - The Streamlit app will be available at `http://localhost:8501`.

    **Note:** Ensure that `main.py` is configured to handle starting both services properly. 
    Typically, `main.py` should manage the execution of both FastAPI and Streamlit applications, possibly using threading or multiprocessing.

## Requirements

The required Python packages are listed in `requirements.txt`. Ensure all dependencies are installed as described in the "Setup and Installation" section.


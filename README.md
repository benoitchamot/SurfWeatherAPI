# Weather API
API providing weather information for a surfing holiday in Hawaii

## File structure
- Resources dictionary includes all the data (CSV files with raw data and sqlite database)
- `app.py` is used to run the Flask server (please see note below)
- `climate_starter.ipynb` is a Jupyter notebook used for a preliminary exploration of the data

## Important note about `app.py`
At this stage, there are some issues with running the engine from a different folder. To run `app.py`:
1. First navigate to the `SurfsUp` directory
2. Run `> python app.py` from within the directory

An error will be returned if the script is run from outside its directory.

## Coding conventions
The coding conventions from the requirements have been followed. There are however some repetitions between the Jupyter notebook and the `app.py` script. While these could be moved to a module to be used as functions or classes for both the script and the notebook, it was decided to follow an explicit approach instead so the full code is visible from within a file.

Functions internal to the files were used to follow the DRY principles within that file.

## Using the API
Once running, the server will indicate the URL that can be used to reach the API. For instance: `http://127.0.0.1:5000/`. Navigate to this address in a browser or write code to connect to the API directly. The landing page (root `/`) of the API provides information about each available route. 


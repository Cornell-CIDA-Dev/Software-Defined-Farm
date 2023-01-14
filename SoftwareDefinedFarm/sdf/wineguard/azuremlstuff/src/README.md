# Classifying GLRaV incidence

## Install anaconda virtual environment

1. Install anaconda environment with the provided 'GLRaV.yml' file

## Running classification_pipeline.py

1. With Python run the script classification_pipeline.py accordingly:

python classification_pipeline.py -m <pickled model filepath> -r <image filepath> -p <polygon boundary filepath> -o <output directory filepath>

1.a. Note: the polygon must be a .shp, .geojson, or .kml filepath; only standard data-structures are currently accepted.

2. The script will run and output a .geotiff for both the discrete classificaitons and a probability map should you choose a different threshold for disease detection.

3. Drop .geotiffs into your favorite Geospatial Software to see the results.

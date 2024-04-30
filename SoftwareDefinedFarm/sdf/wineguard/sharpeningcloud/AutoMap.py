import folium, io
import plotly.express as px
import numpy as np
import rasterio as rio
import pandas as pd
import geopandas as gpd

from shapely.geometry import box
from branca.element import Figure
from jinja2 import Template
from matplotlib.colors import rgb2hex, LinearSegmentedColormap
from matplotlib.cm import get_cmap
from PIL import Image

__author__ = "Fernando Emiliano Romero Galvan"
__email__ = "fer36@cornell.edu"
__credits__ = ["Fernando Emiliano Romero Galvan"]

class AutoMap:
    '''Class to generate maps from raster files.'''
    def __init__(self,
                 mapbox_api_key : str,
                 metric : str,
                 statistic : str,
                 rio_obj : rio.DatasetReader) :
        
        self.mapbox_api_key = mapbox_api_key
        self.raster_array = rio_obj.read(masked = True)

        self.bbox = AutoMap.extract_boundingbox(rio_obj.bounds)
        self.bbox = AutoMap.reproject_boundingbox(self.bbox,
                                                  rio_obj.crs,
                                                  'EPSG:4326')
        self.centroid = AutoMap.extract_bbox_centroid(self.bbox.values[0])

        self.metric = metric
        self.statistic = statistic.capitalize()

        self.COLOR_RAMPS = {
                        'NDVI' : AutoMap.custom_cmap([
                                                '#D7bE69',
                                                '#A47E4f',
                                                '#5C6B28',
                                                '#424A26',
                                                '#2A3019'
                                                ],
                                               n = 100),
                        'FAPAR' : 'viridis',
                        'PET' : AutoMap.custom_cmap([
                                                '#9A3DD9',
                                                '#FFA500',
                                                '#2B308C',
                                                '#173673',
                                                '#25A6D9'
                                                ],
                                                n = 100),
                        'E' : AutoMap.custom_cmap([
                                              '#f6e8c3',
                                              '#d8b365',
                                              '#99974a',
                                              '#53792d',
                                              '#6bdfd2',
                                              '#1839c5',
                                              ],
                                              n = 100)
                        }

    ### Color Stuff
    @staticmethod
    def custom_cmap(colors : list,
                    n : int = 100,
                    reverse : bool = False) -> LinearSegmentedColormap :
        '''Creates a custom colormap.
        input:
            - colors: list of tuples
        output:
            - cmap: matplotlib.colors.LinearSegmentedColormap
        '''
        if reverse:
            colors = colors[::-1]
        cmap = LinearSegmentedColormap.from_list("", colors, N=n)
        return cmap


    @staticmethod
    def normalize_minmax(array : np.ndarray) -> np.ndarray :
        '''Normalizes an array between 0 and 1.
        input:
            - array: np.array
        output:
            - normalized_array: np.array
        '''
        mask = np.ma.array(array, mask=np.isnan(array))
        min_val = np.nanmin(mask.data)
        max_val = np.nanmax(mask.data)
        normalized_array = (mask.data - min_val) / (max_val - min_val)

        return normalized_array


    @staticmethod
    def get_color(x : float,
                  ramp : str = 'viridis') -> list[int]:
        '''Returns a color from a color ramp.
        input:
            - x: float
            - ramp: string
        output:
            - color: tuple
        '''
        decimals = 2
        x = np.around(x, decimals=decimals)
        ls = np.linspace(0,1,10**decimals+1)
        if 0 <= x <= 1:
            color = get_cmap(ramp)(x)
            return tuple((int(255 * color[0]), int(255 * color[1]), int(255 * color[2]), int(255 * color[3])))
        elif np.isnan(x):
            return (0, 0, 0, 0)
        else:
            raise ValueError()


    ### Bounding Box Stuff
    @staticmethod
    def reproject_boundingbox(bbox : list[float],
                              source_crs : 'str' ,
                              target_crs : str = 'EPSG:4326') -> list[float]:
        '''Reprojects a bounding box.
        Input:
            - bbox: list
            - source_crs: string
            - target_crs: string
        Output:
            - bbox: tuple
        '''
        bbox_df = pd.DataFrame({'geometry': [box(*bbox)]})
        bbox_gdf = gpd.GeoDataFrame(bbox_df, geometry='geometry')
        bbox_gdf.crs = {'init' : source_crs}
        bbox_gdf = bbox_gdf.to_crs(target_crs)
        bbox = bbox_gdf.geometry.bounds

        return bbox


    @staticmethod
    def extract_boundingbox(bounds : list[float]) -> list[float] :
        '''Extracts the bounding box from a raster file.
        Input:
            - bounds: list
            - source_crs: string
            - target_crs: string
            - reproject: boolean
        Output:
            - bbox: tuple
        '''
        minx, miny, maxx, maxy = bounds
        return minx, miny, maxx, maxy


    @staticmethod
    def extract_bbox_centroid(bbox : list[float]) -> list[float, float] :
        '''Extracts the centroid of a bounding box.
        Input:
            - bbox: list
        Output:
            - centroid: tuple'''
        return (bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2


    def custom_colorbar(self,
                        colorbar_params : dict) -> str :
        '''Generates a custom colorbar for the map.
        Input:
            - colorbar_params: dict
        Output:
            - html: string
        '''
        html = """
            <head>
                <meta charset="UTF-8">
                <style>
                    .label-container {
                        width: {{ width }}px;
                        height: {{ height }}px;

                        background: linear-gradient(to right, 
                        {% for hex in hex_codes %}
                            {{ hex }}
                            {% if not loop.last %},{% endif %}
                        {% endfor %}
                        );
                        border-radius: 5px;
                        border: 0px solid #000;
                        justify-content: space-between;
                        align-items: center;
                        display: flex;
                        padding: 0px;
                        margin: 0 auto;
                        position: fixed;
                        z-index: 1000;
                        bottom: 0px;
                        left: 50%;
                        transform: translate(-50%, -50%);
                    }

                    .label {
                        color: {{ font_color }};
                        font-size: 22px;
                        font-weight: bold;
                        padding: 0px 10px;
                        margin: 0px;
                        border: none;
                    }
                </style>
            </head>
            <body>
                <div class="label-container">
                    <div class="label">{{ min }}</div>
                    <div class="label">{{ label }}</div>
                    <div class="label">{{ max }}</div>
                </div>
            </body>
        """
        my_templ = Template(html)
        with open('temp.html', 'w') as f:
            return my_templ.render(**colorbar_params)


    # TODO: Complete
    def make_histogram(self) -> px.histogram :
        pass


    # TODO: Complete
    def make_timeseries_graph(self) -> px.scatter_mapbox :
        pass


    def make_map(self) -> folium.Map :
        '''Generates a map from a raster file.
        Input:
            - raster_filepath: string, path to raster file
            - output_dir: string, path to output directory
        Output:
            - folium.Map
        '''
        palette = self.COLOR_RAMPS[self.metric.upper()]
        if not isinstance(palette, list) :
            cmap = get_cmap(palette, 100)

        px.set_mapbox_access_token(self.mapbox_api_key)
        mapboxTilesetId = 'mapbox.satellite'

        fig = Figure(width=500, height=500)

        m = folium.Map(
            location = [self.centroid[1], self.centroid[0]],
            zoom_start=18,
            zoom_control=False,
            tiles='https://api.tiles.mapbox.com/v4/' + mapboxTilesetId + '/{z}/{x}/{y}.png?access_token=' + self.mapbox_api_key,
            attr='mapbox.com'
        )

        fig.add_child(m)

        min, max = np.min(self.raster_array), np.max(self.raster_array)
        raster_arr = self.raster_array.reshape(-1, self.raster_array.shape[-1])
        norm_raster_arr = AutoMap.normalize_minmax(raster_arr)

        folium.raster_layers.ImageOverlay(norm_raster_arr,
                            bounds = [[self.bbox.miny.min(),
                                       self.bbox.minx.min()],
                                      [self.bbox.maxy.max(),
                                       self.bbox.maxx.max()]],
                            colormap = lambda x: AutoMap.get_color(x, ramp=palette),
                            ).add_to(m)
        m.fit_bounds([[self.bbox.miny.min(), self.bbox.minx.min()],
                      [self.bbox.maxy.max(), self.bbox.maxx.max()]])

        if self.statistic is None :
            label = self.metric.upper()
        else :
            label = f"{self.metric.upper()} - {self.statistic.capitalize()}"

        colorbar_params = {
            'label' : label,
            'max': "{0:.2f}".format(max),
            'min': "{0:.2f}".format(min),
            'hex_codes' : [rgb2hex(c) for c in cmap(np.linspace(0, 1, 100))],
            'width': 600,
            'height': 50,
            'font_color' : 'black'
        }

        colorbar_html = self.custom_colorbar(colorbar_params)
        m.get_root().html.add_child(folium.Element(colorbar_html))

        # Weird conversion to JPG
        map_fig = m._to_png()
        map_fig = Image.open(io.BytesIO(map_fig))
        map_fig = map_fig.convert('RGB')
        # Return seek
        img = io.BytesIO()
        map_fig.save(img, "JPEG")
        img.seek(0)
        return img
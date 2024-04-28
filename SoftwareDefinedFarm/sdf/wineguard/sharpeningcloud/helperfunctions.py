from datetime import datetime
from re import compile, search, IGNORECASE
from os.path import join
from shutil import copy, move

from matplotlib.colors import rgb2hex, LinearSegmentedColormap
from matplotlib.cm import get_cmap

import rasterio as rio
import numpy as np
import geopandas as gpd
import pandas as pd

from shapely.geometry import box
from rasterio.io import MemoryFile
from rasterio.mask import mask

def is_valid_date(date : str) -> bool :
    '''Checks if a string is a valid date.
    input:
        - date: string
    output:
        - bool
    '''
    try:
        datetime.strptime(date, '%Y%m%d')
        return True
    except ValueError:
        return False


def extract_timestamp(filepath : str) -> datetime :
    '''Extracts the timestamp from a file path.
    input:
        - filepath: string
    output:
        - timestamp: datetime.datetime
    '''
    timestamp_pattern = r'(\d{8})'
    match = search(timestamp_pattern, filepath)
    if match:
        timestamp_str = match.group(0)
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d')
        return timestamp
    else:
        return None


def extract_vegetationmetric(filepath : str) -> str :
    '''Extracts the vegetation index from a file path.
    input:
        - filepath: string
    output:
        - vegetation_index: string
    '''
    vi_pattern = r'(E|FAPAR|PET)'
    vegetation_index_pattern = compile(vi_pattern, IGNORECASE)
    match = search(vegetation_index_pattern, filepath)
    if match:
        vegetation_index = match.group(0)
        return vegetation_index
    else:
        return None


def custom_cmap(colors : list, n = 100, reverse = False) -> LinearSegmentedColormap :
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
    # Perform normalization
    normalized_array = (mask.data - min_val) / (max_val - min_val)

    return normalized_array


def get_color(x : float, ramp : str = 'viridis') -> tuple[int]:
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


# TODO: obsolete function
def raster_poly_crs_check(raster : rio.DatasetReader,
                          polygons : gpd.GeoDataFrame) -> gpd.GeoDataFrame :
    '''Checks if the CRS of a raster and a polygon are the same.
    input:
        - raster: rasterio.io.DatasetReader
        - polygons: geopandas.GeoDataFrame
    output:
        - polygons: geopandas.GeoDataFrame
    '''
    imagery_crs = raster.crs
    # Check if CRS are different
    if polygons.crs != imagery_crs:
        # Reproject polygons to imagery CRS
        polygons = polygons.to_crs(imagery_crs)

    return polygons


def raster_to_stats(raster : rio.io.DatasetReader,
                    metric : str) -> pd.DataFrame :
    '''Calculates statistics of a raster.'''
    mask = np.ma.array(raster.read(), mask=np.nan)
    index = raster.descriptions
    
    min_val = np.nanmin(mask.data, axis=(1, 2))
    max_val = np.nanmax(mask.data, axis=(1, 2))
    mean_val = np.nanmean(mask.data, axis=(1, 2))
    std_val = np.nanstd(mask.data, axis=(1, 2))
    lq_val = np.nanquantile(mask.data, 0.25, axis=(1, 2))
    mq_val = np.nanquantile(mask.data, 0.5, axis=(1, 2))
    uq_val = np.nanquantile(mask.data, 0.75, axis=(1, 2))
    
    df_stats = pd.DataFrame({
        'date': index,
        'metric': metric,
        'min': min_val,
        'max': max_val,
        'mean': mean_val,
        'std': std_val,
        'lq': lq_val,
        'mq': mq_val,
        'uq': uq_val
    })
    return df_stats


def raster_stack_statistics(raster : rio.DatasetReader,
                            stat : str,
                            nodata : int | float = np.nan) -> np.array :
    '''Calculates statistics specificed in the statistics list.'''
    raster_array = raster.read()
    raster_meta = raster.meta
    raster_meta.update({"nodata": nodata,
                        "dtype": np.float64,
                        "count": 1,
                        "height": raster_array.shape[1],
                        "width": raster_array.shape[2],
                        "descriptions": [stat]})
    raster_array = np.ma.masked_equal(raster_array, nodata)
    if stat == 'mean':
        result = np.mean(raster_array.data, axis=0)
    elif stat == 'median':
        result = np.median(raster_array.data, axis=0)
    elif stat == 'std':
        result = np.std(raster_array.data, axis=0)
    elif stat == 'min':
        result = np.min(raster_array.data, axis=0)
    elif stat == 'max':
        result = np.max(raster_array.data, axis=0)
    elif stat == 'sum':
        result = np.sum(raster_array.data, axis=0)
    else:
        raise ValueError("Invalid statistic")

    result = np.ma.filled(result, fill_value=nodata)
    result = np.expand_dims(result, axis=0)

    yield memory_raster(result, raster_meta)


def merge_rasters(raster_list : list[str],
                  nodata : np.nan = np.nan) :
    '''Merges a list of rasters into a single raster.
    Input:
        - raster_list: list of rasterio.io.DatasetReader
        - output_filepath: filepath to save the merged raster
    Output:
        - None
    '''
    rasters = [rio.open(raster) for raster in raster_list]

    merged_raster, merged_transform = rio.merge.merge(rasters)

    merged_meta = rasters[0].meta.copy()
    merged_meta.update({"transform": merged_transform,
                        "nodata": nodata,
                        "dtype": np.float64,
                        "count": merged_raster.shape[0],
                        "height": merged_raster.shape[1],
                        "width": merged_raster.shape[2]})
    # Clean up; lambda function to close all rasters
    list(map(lambda r: r.close(), rasters))

    merged_raster = merged_raster.astype(np.float64)
    merged_raster[merged_raster == 0] = np.nan

    # TODO: complete writing merged raster to memory file and returning rio object
    return memory_raster(merged_raster, merged_meta)


def stack_rasters(rasters : list,
                  index : list[str] | list[int],
                  nodata : np.nan = np.nan) :
    '''Stacks a list of rasters into a single raster.
    Input:
        - rasters : list of rasterio.io.DatasetReader
        - index : list of strings or integers representing the band index
        - nodata: pixel value representing no data
    Output:
        - stacked_raster: rasterio.io.DatasetReader
    '''
    for raster in rasters:
        if raster.count > 1:
            raise ValueError("Rasters must have only one band.")
    
    stacked_raster = np.stack([raster.read(1) for raster in rasters], axis=0)
    stacked_meta = rasters[0].meta.copy()

    stacked_meta.update({"count": len(index),
                         "dtype": np.float64,
                         "nodata": nodata,
                         "height": stacked_raster.shape[1],
                         "width": stacked_raster.shape[2]
                         })
    index = [datetime.strptime(i, "%Y%m%d").strftime("%Y-%m-%d") for i in index]
    return memory_raster(stacked_raster, stacked_meta, index)


def clip_raster(raster : rio.DatasetReader,
                polygons : gpd.GeoDataFrame,
                nodata = np.nan) -> tuple[np.array, dict] :
    '''Masks a raster with a polygon.
    Input:
        - raster: Rasterio.io.DatasetReader
        - polygon: 
    Output:
        - clipped_raster: numpy.ndarray
        - clipped_meta: dict
    '''
    polygons = raster_poly_crs_check(raster, polygons)

    clipped_raster, clipped_transform = mask(raster, [polygons.geometry[0]], crop=True)
    clipped_raster = np.where(clipped_raster==0, np.nan, clipped_raster)
    clipped_meta = raster.meta.copy()
    clipped_meta.update({
                        "transform": clipped_transform,
                        "nodata": nodata,
                        "dtype": np.float64,
                        "height": clipped_raster.shape[1],
                        "width": clipped_raster.shape[2]
                        })
    return memory_raster(clipped_raster, clipped_meta)


def memory_raster(raster : np.array,
                  meta_data : dict,
                  band_names : list[str] | list[int] = None) -> rio.io.DatasetReader :
    '''Creates a raster in memory.
    input:
        - raster: numpy.ndarray
        - meta_data: dict
    output:
        - raster: rasterio.io.DatasetReader
    '''
    with MemoryFile() as memfile:
        with memfile.open(**meta_data) as dataset :
            if band_names is not None :
                dataset.descriptions = band_names
            dataset.write(raster)
        return memfile.open()


def write_raster(raster : rio.io.DatasetReader, meta_data : dict,
                 output_filepath : str) -> None:
    '''Writes a raster to a file.
    input:
        - raster: numpy.ndarray
        - meta_data: dict
        - output_filepath: string
    output:
        - None
    '''
    with rio.open(output_filepath, 'w', **meta_data) as dst:
        dst.write(raster)


def extract_boundingbox(bounds : list[float],
                        source_crs : str = '',
                        target_crs : str  = '',
                        reproject = False) -> tuple[float] :
    '''Extracts the bounding box from a raster file.
    Input:
        - bounds: list
        - source_crs: string
        - target_crs: string
        - reproject: boolean
    Output:
        - bbox: tuple
    '''
    def reproject_boundingbox(bbox : list[float], source_crs : 'str' ,
                              target_crs : str = 'EPSG:4326') -> tuple [float]:
        '''Reprojects a bounding box.
        Input:
            - bbox: list
            - source_crs: string
            - target_crs: string
        Output:
            - bbox: tuple'''
        # bbox_df = pd.DataFrame({'geometry': [box(*bbox)]})
        bbox_gdf = gpd.GeoDataFrame({'geometry' : [box(*bbox)]}, geometry='geometry')
        bbox_gdf.crs = {'init' : source_crs}
        bbox_gdf = bbox_gdf.to_crs(target_crs)
        bbox = bbox_gdf.geometry.bounds
        return bbox

    if reproject :
        minx, miny, maxx, maxy = reproject_boundingbox(bounds, source_crs,  target_crs)
    minx, miny, maxx, maxy = bounds
    return minx, miny, maxx, maxy


def extract_bbox_centroid(bbox : list[float]) -> tuple[float, float] :
    return (bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2


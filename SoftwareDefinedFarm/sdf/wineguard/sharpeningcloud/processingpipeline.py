### Local Packages
# Local packages - image processing
import helperfunctions as hf
# Local packages - storage
from sdf.storage.awswrappers.aws_dynamodb_wrapper import DynamoDBService
from sdf.storage.awswrappers.aws_s3_wrapper import S3Service 


### Third party packages
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import pandas as pd
import rasterio as rio
from rasterio.io import MemoryFile
from datetime import datetime
from shapely.geometry import Polygon, Point
from io import BytesIO
from AutoMap import AutoMap

__author__ = "Fernando Emiliano Romero Galvan"
__email__ = "fer36@cornell.edu"
__credits__ = ["Fernando Emiliano Romero Galvan"]

class ProcessingPipeline() :
    '''Class to process raster files.'''
    def __init__(self,
                 date_range: tuple[datetime, datetime],
                 polygon_filepath : str,
                 api_keys : dict,
                 dynamodb : str = "Images_TestTable",
                 s3bucket : str = "sharpenedhlsimagery",
                 output_s3bucket : str = "testvineyardmaps") :
        
        self.dynamodb = dynamodb
        self.polygon_filepath = polygon_filepath
        self.api_keys = api_keys
        self.date_range = date_range
        self.dynamodb_items = self.get_images_dynamodb()
        self.bucket = s3bucket
        self.output_bucket = output_s3bucket


    def get_s3_imagestream(self,
                           object_name : str) :
        '''Gets a stream of an image from an S3 bucket.'''
        s3 = S3Service("test")
        blob = s3.get_filestream(self.bucket, object_name)
        blob = MemoryFile(blob)

        return blob.open()


    def get_images_dynamodb(self) -> list[str]:
        '''Gets a list of images from a dynamodb table.
        Example JSON:
        {'timestamp': 1595142000,
        'image_id': 'lodi_1',
        'Metrics': {'E': {'images': ['data/E_20200719.tif']}}}
        '''
        dynamodb_Table = self.dynamodb
        ddb = DynamoDBService("test")
        date_start, date_end = self.date_range

        scan_filter = f"Key('timestamp').between({date_start}, {date_end})"
        response = ddb.scan_table(dynamodb_Table, scan_filter)

        return response['Items']


    @staticmethod
    def extract_raster_centroids(raster : rio.io.DatasetReader) -> gpd.GeoDataFrame :
        '''Extracts the centroids of a raster.'''
        band = raster.read(1)
        height = band.shape[0]
        width = band.shape[1]

        cols, rows = np.meshgrid(np.arange(width), np.arange(height))
        xs, ys = rio.transform.xy(raster.transform, rows, cols)
        lons = np.array(xs)
        lats = np.array(ys)

        points = gpd.GeoSeries(
            list(zip(lons.flatten(), lats.flatten()))).map(Point)
        
        # use the feature loop in case shp is multipolygon
        geoms = points.values
        features = [i for i in range(len(geoms))]

        centroid_gdf = gpd.GeoDataFrame(
        {'feature': features, 'geometry': geoms}, crs=raster.crs)

        return centroid_gdf


    @staticmethod
    def generate_grid(points : gpd.GeoDataFrame,
                      target_resolution : int | float) -> gpd.GeoDataFrame :
        '''Resamples the point's spatial distribution to the raster resolution.
        Intput:
            - points : geopandas dataframe, points to resample
            - target_resolution : int | float, resolution to resample to
        Output:
            - geopandas dataframe, resampled points to target resolution
        '''
        bounds = points.total_bounds
        minx, miny, maxx, maxy = bounds
        res = target_resolution
        
        w, l = res, res

        cols = list(np.arange(minx, maxx + w, w))
        rows = list(np.arange(miny, maxy + l, l))

        polygons = []
        for x in cols[:-1] :
            for y in rows[:-1] :
                polygons.append(Polygon([(x,y), (x+w, y), (x+w, y+l), (x, y+l)]))

        grid = gpd.GeoDataFrame({'geometry':polygons})
        grid.crs = points.crs
        
        return grid


    @staticmethod
    def point_spatial_sample(sampling_points : gpd.GeoDataFrame,
                             data : rio.io.DatasetReader,
                             column_headers : list = None,
                             ) -> gpd.GeoDataFrame:
        """
        Extracts raster values at point locations from a vector file.
        Input
            - rio_obj : rasterio object, Raster file to extract values from.
            - geopandas_obj : geopandas object
        Output:
            - geopandas dataframe, Dataframe with point locations and raster values.
        """
        points = sampling_points.geometry
        xy = [xy for xy in zip(points.x, points.y)]        
        sampler = rio.sample.sample_gen(data,
                                        xy,
                                        indexes=None,
                                        masked=True)
        spec_df = pd.DataFrame(sampler, columns=column_headers)

        spec_df.columns = spec_df.columns.map(str)
        spec_df = sampling_points.merge(spec_df, left_index=True, right_index=True)

        spec_df = spec_df[(spec_df[str(column_headers[0])] != "--") & (spec_df[str(column_headers[0])] != 0)]

        return spec_df


    def image_collection(self) :
        '''Generates a collection of images.'''
        for record in self.dynamodb_items :
            record_timestamp = datetime.fromtimestamp(int(record['timestamp'])).strftime('%Y%m%d')
            for metric, images in record['Metrics'].items() :
                for image in images['images'] :
                    raster_filestream = self.get_s3_imagestream(image)
                    yield record_timestamp, metric, raster_filestream


    def upload_image_to_s3_bucket(self,
                                    bucket : str,
                                    output_fname : str,
                                    image : plt) :
            '''Uploads the results to Google Cloud Storage.
            Input:
                - bucket : str, name of the bucket to upload the image to.
                - output_fname : str, name of the file to save the image as.
                - image : plt, image to upload to the bucket.
            '''
            s3 = S3Service("test")
            s3.write_from_filestream(image, bucket, output_fname)


    def metrics_grapher(self,
                        df : pd.DataFrame,
                        title : str,
                        y_label : str,
                        savefig_output : str) -> None :
        
        plt.figure(figsize=(9, 4))

        t = df.reset_index()
        t = t.sort_values(by='date')

        plt.plot(t['date'], t['mean'], label='Mean', color='red')
        plt.plot(t['date'], t['mq'], label='Median', color='cyan', linestyle='dashed')
        plt.fill_between(t['date'], t['lq'], t['uq'], alpha=0.3, color='blue', label = 'IQR')
        plt.fill_between(t['date'], t['min'], t['max'], alpha=0.1, color='blue', label = 'Min/Max')

        tick_labels = tuple(t['date'])
        plt.xticks(tick_labels, rotation=90, fontsize=12)
        plt.title(title)
        plt.xlabel('Dates')
        plt.ylabel(y_label)
        plt.legend(loc="upper left")
        plt.grid(True)
        plt.tight_layout()

        img = BytesIO()
        # plt.savefig(img, format='jpg', dpi=1200)
        plt.savefig(img, format='pdf', dpi=1200)
        img.seek(0)
        return img


    def process_images(self) :
        polygons = gpd.read_file(self.polygon_filepath)
        ic = self.image_collection()
        image_count = 0

        clipped_images = {}
        for t, m, filestream in ic :
            image_count += 1
            raster = hf.clip_raster(filestream, polygons)

            if m in clipped_images.keys() :
                clipped_images[m].append((t, raster))
            else :
                clipped_images[m] = [(t, raster)]

        if image_count == 1:
            return clipped_images

        stacked_rasters = {}
        for metric, images in clipped_images.items():
            timestamps, rasters = zip(*images)
            stacked_raster = hf.stack_rasters(rasters, timestamps)
            stacked_rasters[metric] = stacked_raster

        # TODO: Only uncomment if we want to store processing results
        ### Start
        # centroids = self.extract_raster_centroids(stacked_rasters['E'])
        # grid = self.generate_grid(centroids, 0.01)
        ### END

        statistical_summary_rasters = {}
        for metrics, stacked_raster in stacked_rasters.items() :
            if metrics in ('E', 'PET') :
                statistics = ['mean', 'median', 'std', 'min', 'max','sum']
            elif metrics in ('FAPAR', 'ESI', 'LST') :
                statistics = ['mean', 'median', 'std', 'min', 'max']

            df = hf.raster_to_stats(stacked_raster, metrics)
            graph = self.metrics_grapher(df, metric.upper(), 'Values', f'{metrics}_graph.jpg')
            dates = f"{datetime.fromtimestamp(self.date_range[0]).strftime("%Y%m%d")}_to_{datetime.fromtimestamp(self.date_range[1]).strftime("%Y%m%d")}"
            output_fname = f'Timeseries_{metrics}_{dates}.jpg'
            self.upload_image_to_s3_bucket(self.output_bucket, output_fname, graph)

            statistical_summary_rasters[metrics] = {}
            for stat in statistics:
                stat_o_raster = [result for result in hf.raster_stack_statistics(stacked_raster, stat)]
                statistical_summary_rasters[metrics][stat] = stat_o_raster[0]
 
        for metric, statistics in statistical_summary_rasters.items() :
            for stat, raster in statistics.items() :
                dates = f"{datetime.fromtimestamp(self.date_range[0]).strftime("%Y%m%d")}_to_{datetime.fromtimestamp(self.date_range[1]).strftime("%Y%m%d")}"
                output_fname = f"Map_{metric}_{stat}_{dates}.jpg"
                map = AutoMap(self.api_keys['mapbox']['api_token'],
                              metric,
                              stat,
                              raster).make_map()
                self.upload_image_to_s3_bucket(self.output_bucket,
                                               output_fname,
                                               map)


def main() :
    import argparse, json

    parser = argparse.ArgumentParser(description='ET Satellite Imgagery Processing Pipeline.')

    parser.add_argument('-p', '--vineyard_polygon_filepath', type = str, help = "Filepath to (.geojson) vineyard boundaries.")
    parser.add_argument('-s', '--date_start', type = str, help = 'Date range for satellite imagery. Format: YYYYMMDD')
    parser.add_argument('-e', '--date_end', type = str, help = 'Date range for satellite imagery. Format: YYYYMMDD')
    parser.add_argument('-a', '--api_keys_json', type=str, help='JSON file holding API keys')

    args = parser.parse_args()

    with open(args.api_keys_json) as f :
        api_keys_json = json.load(f)

    if args.date_start and args.date_end :
        if not hf.is_valid_date(args.date_start) or not hf.is_valid_date(args.date_end) :
            raise ValueError('Invalid date range.')
        elif args.date_start > args.date_end :
            raise ValueError('Invalid date range.')
        else :
            date_range = (int(datetime(args.date_start).timestamp()),
                          int(datetime(args.date_end).timestamp()))

    ProcessingPipeline(date_range,
                       args.vineyard_polygon_filepath,
                       api_keys_json).process_images()

if __name__ == '__main__' :
    main()
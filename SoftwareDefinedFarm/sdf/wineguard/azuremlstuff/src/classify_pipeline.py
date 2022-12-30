import re, os, sys, getopt, time
import pandas as pd
import rasterio as rio
import numpy as np
import fiona
from rasterio.mask import mask
from pathlib import Path


class ClassificationPipeline :

    def __init__(self, rfm_pk_filepath, hsi_aviris, polygon, outputdir) :
        '''
        self.rfm_pk_filepath : filepath to the pickled random-forest model
        self.hsi : filepath to the aviris spectroscopic image
        self.poly : filepath to the vineyard polygon boundary
        self.outputdir :
        '''
        self.rfm_pk_filepath = rfm_pk_filepath
        self.hsi = hsi_aviris
        self.poly = polygon
        self.outputdir = outputdir

        self.unpickle_rf_model()
        self.load_overlapping_spectra()


    def clean_wl(self, src_wls) :
        '''
        '''
        src_wls = src_wls.values()
        wls = [re.findall('\d+\.\d+',wl)[0] for wl in src_wls]
        float_wls = [round(float(wl),6) for wl in wls if wl.replace('.','','1').isdigit()]

        return sorted(float_wls)


    def remove_bb(self, wls) :
        '''
        '''
        bb = [[300,400],[1320,1430],[1800,1960],[2450,2600]]

        np_wls = np.array(wls)
        for bb in bbs :
            np_wls = np_wls[(np_wls <= bb[0]) | (np_wls >= bb[1])]

        return np_wls


    def load_overlapping_spectra(self) :
        ''' Clips the spectra according to the boundaries of the polygon.
        '''
        with fiona.open(self.poly, "r") as geometries :
            geom = [feature["geometry"] for feature in geometries]

        with rio.open(self.hsi) as src:
            self.spectra, self.geog_transform = rio.mask.mask(src, geom, crop=True)
            self.meta = src.meta
            self.wls = self.clean_wl(src.tags()) # sorted list of wls; e.g [300.0, ... , 2500.0]
            self.bbs = self.remove_bb(wls) # filtered list of wls; e.g. [405.0, ..., 2445]

            meta.update({
                "height" : self.spectra.shape[1],
                "width" : self.spectra.shape[2],
                "transform" : self.geog_transform
                })

        return out_image, out_meta


    def unpickle_rf_model(self) :
        '''unpickle_rf_model loads and unpickles a random-forest model trained
        on spectral residuals and disease incidence points.
        rfm_pj - expected to be a filepath to a pickled (.pkl) random-forest model.

        returns the unpickled random-forest model
        '''
        with open(self.rfm_pk_filepath, 'rb') as unpickled_model :
            rf_model = pickle.load(unpickled_model)


    def null_nodata_pixels(self) :
        band_count = self.meta['count'] # this might be bugged
        cols = self.meta['width']
        rows = self.meta['height']

        self.nulled_image = np.empty((band_count,cols,rows), np.float64)

        for band_position in range(band_count) :
            band = self.spectra[band_position]
            band[band == -9999] = np.nan
            nulled_image[band_position,:,:] = band

        return 


    def mask(self) :
        
        masked_image = 

        return masked_image


    # def apply_mask(self) :
    #


    def spec_mixture_res(self, endmembers='filepath') :
        ''' unmix veg. vs soil
        '''
        local_bbs = np.in1d(self.wls, self.bbs)

        w = 1 # set unit sum constraint weight
        D = self.nulled_image
        d = np.reshape(D, [D.shape[0], D.shape[1]*D.shape[2]])
        G = pd.read_csv(endmembers, sep="[,|\t]", header = None).to_numpy()
        wavelength = G[:,0]
        G = G[: ,1:G.shape[1]]

        d = d[local_bbs]
        G = G[local_bbs]

        d_constraint = np.array(w*np.ones(d.shape[1]))
        G_constraint = np.array(w*np.ones(G.shape[1]))

        d = np.vstack([d,d_constraint])
        G = np.vstack([G,G_constraint])

        mixtureResidual_alt = d-(G.dot(np.linalg.inv(G.transpose().dot(G)).dot(G.transpose()))).dot(d)
        self.smr = np.reshape(mixtureResidual_alt,[d.shape[0],D.shape[1],D.shape[2]])


    def classify_raster(self) :
        ''' Apply RF model to the clipped and spectrally unmixed aviris image
        '''
        f = Path(self.hsi).stem

        output = ('%s%s_predictions.tif' % (self.outputdir,f))
        output_classes = ('%s%s_class_probability.tif' % (self.outputdir,f))

        classEncoder = LabelEncoder()

        colWLHeaders = self.bbs.astype(str)

        cleanSpectra = self.smr
        b,h,w = cleanSpectra.shape # Band, Height, Width 

    # numpy-nd array > df
        local_df = pd.DataFrame(cleanData.reshape([b,-1]).T, columns= colWLHeaders)
        local_df_nn = local_df.dropna()

        local_df_nn['classifications'] = rf_model.predict(local_df_nn[colWLHeaders])

        # Class-Probabilities
        class_probas = rf_model.predict_proba(local_df_nn[colWLHeaders])
        class_count = len(class_probas[1])
        classes = list(map(str,range(1,class_count+1)))

        local_df_nn[classes] = class_probas

        classEncoder.fit(local_df_nn['classifications'])
        classValues = classEncoder.transform(local_df_nn['classifications'])
        local_df_nn['classifications'] = classValues

        local_df_j = local_df.join(local_df_nn[['classifications']+classes])

        local_df_arr = np.array(local_df_j['classifications'])
        output_raster = local_df_arr.reshape((1,h,w))

        output_probs_raster = np.zeros((len(classes),h,w))
        for i,c in enumerate(classes) :
            local_df_probs_arr = np.array(local_df_j[c])
            output_probs_raster[i] = local_df_probs_arr.reshape(1,h,w)

        metadata.update({'count': 1,'drive':'GTiff'})
        with rio.open(output,'w',**metadata) as dest :
            dest.write(output_raster)

        metadata.update({'count':len(classes),'drive':'GTiff'})
        with rio.open(output_classes,'w',**metadata) as dest :
            dest.write(output_probs_raster)


def pipeline(model, raster, poly, outputdir) :
    


def main(argv) :
    long_input = ["--help","--model","--raster","--polygon","--output_directory"]
    short_input = "hm:r:p:o:"

    asked_for_help = False
    model = None
    raster = None
    poly = None
    outputdir = './'

    try :
        options, current_values = getopt.getopt(argv, short_input, long_input)

        for option, current_value in options :
            if option == "-h" :
                print("classification_pipeline.py -m <model filepath> -r
                        <raster filepath> -p <polygon filepath> -o <output
                        directory>")
                asked_for_help = True
            elif option in ('-m','--model') :
                model = current_value
            elif option in ('-r', '--raster') :
                raster = current_value
            elif option in ('-p', '--polygon') :
                poly = current_value
            elif option in ('-o','--output_directory') :
                outputdir = current_value


    except getopt.GetoptError as e :
        print(">>> ERROR: %s" % str(e))

    if not asked_for_help :
        pipeline(model, raster, poly, outputdir)


if __name__ == "__main__" :
    main(sys.argv[1:])

from contextlib import contextmanager
from pathlib import Path
import re, os, sys, getopt, time, pickle
import pandas as pd
import numpy as np
import fiona
import rasterio as rio
from rasterio.mask import mask
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling


def generate_mask(frac_w, threshold = 0.5) :

    veg = frac_w[0,:,:]
    soil = frac_w[1,:,:]

    mask = np.divide(veg, (veg+soil), np.zeros_like(veg), where=(veg+soil)!=0)

    mask[mask >= threshold] = 1
    mask[mask < threshold] = 0

    return mask


def apply_mask(si, mask_raster) :

    bands = si.shape[0]
    rows = mask_raster.shape[0]
    cols = mask_raster.shape[1]

    masked_si = np.empty((bands,rows,cols,), np.float32)

    for band in range(bands):
        applied_mask = si[band] * mask_raster
        applied_mask[applied_mask == 0] = np.nan
        masked_si[band,:,:] = applied_mask

    return masked_si


def unpickle_rf_model(rfm_pk_filepath) :
    '''unpickle_rf_model loads and unpickles a random-forest model trained
    on spectral residuals and disease incidence points.
    rfm_pj - expected to be a filepath to a pickled (.pkl) random-forest model.

    returns the unpickled random-forest model
    '''
    with open(rfm_pk_filepath, 'rb') as unpickled_model :
        rf_model = pickle.load(unpickled_model)

    return rf_model


def clean_wl(src_wls) :
    '''
    '''
    src_wls = src_wls.values()
    wls = [re.findall('\d+\.\d+',wl)[0] for wl in src_wls if len(re.findall('\d+\.\d+',wl)) != 0]
    float_wls = [round(float(wl),6) for wl in wls if wl.replace('.','',1).isdigit()]

    return sorted(float_wls)


def remove_bb(wls) :
    '''
    '''
    bbs = [[0,400],[1310,1470],[1750,2000],[2400,2600]]
    #bbs = [[300,400],[1320,1430],[1800,1960],[2450,2600]]

    np_wls = np.array(wls)
    for bb in bbs :
        np_wls = np_wls[(np_wls <= bb[0]) | (np_wls >= bb[1])]

    return np_wls


def null_nodata_pixels(src_img) :
    band_count, cols, rows = src_img.shape

    nulled_image = np.empty((band_count,cols,rows), np.float64)

    for band_position in range(band_count) :
        band = src_img[band_position]
        band[band == -9999] = np.nan
        nulled_image[band_position,:,:] = band

    return nulled_image


def clip_imagery(poly_filepath, si_filepath) :
    ''' Clips the spectra according to the boundaries of the polygon.
    '''
    with fiona.open(poly_filepath, "r") as geometries :
        geom = [feature["geometry"] for feature in geometries]

    with rio.open(si_filepath) as src:
        spectra, geog_transform = rio.mask.mask(src, geom, crop=True)
        out_meta = src.meta
        wls = clean_wl(src.tags()) # sorted list of wls; e.g [300.0, ... , 2500.0]
        bbs = remove_bb(wls) # filtered list of wls; e.g. [405.0, ..., 2445]

        out_meta.update({
            "height" : spectra.shape[1],
            "width" : spectra.shape[2],
            "transform" : geog_transform,
            "wls" : wls,
            "bbs" : bbs
            })

    return spectra, out_meta


def smr_vegsoil(si, wls, wls_f, endmembers="endmembers.csv") :
    ''' unmix veg. vs soil
    si - numpy nd array holding spectra
    wls - numpy list of wavelengths
    wls_f - numpy list of filtered wavelengths
    '''

    wls_filter = np.in1d(wls, wls_f)

    w = 1 # set unit sum constraint weight
    D = si
    d = np.reshape(D, [D.shape[0], D.shape[1]*D.shape[2]])
    G = pd.read_csv(endmembers, sep="[,|\t]", header = None).to_numpy()
    wavelength = G[:,0]
    G = G[: ,1:G.shape[1]]

    d = d[wls_filter]
    G = G[wls_filter]

    d_constraint = np.array(w*np.ones(d.shape[1]))
    G_constraint = np.array(w*np.ones(G.shape[1]))

    d = np.vstack([d,d_constraint])
    G = np.vstack([G,G_constraint])

    # Fractional Weights
    frac_ws = np.linalg.inv(G.transpose().dot(G)).dot(G.transpose().dot(d))
    # Spectral residuals
    res = (d - G.dot(frac_ws))

    #M_alt = d-(G.dot(np.linalg.inv(G.transpose().dot(G)).dot(G.transpose()))).dot(d)

    frac_w_res = np.reshape(frac_ws,[G.shape[1],D.shape[1],D.shape[2]])

    smr_res = np.reshape(res,[d.shape[0],D.shape[1],D.shape[2]])
    smr_res = smr_res[:-1,:,:]

    return smr_res, frac_w_res


def classify_raster(image, meta, model, outputdir, output_filename="GLRaV") :
    ''' Apply RF model to the clipped and spectrally unmixed aviris image
    '''

    output = ('%s%s_predictions.tif' % (outputdir, output_filename))
    output_classes = ('%s%s_class_probability.tif' % (outputdir,output_filename))

    colWLHeaders = meta['bbs'].astype(str)

    cleanSpectra = image
    b,h,w = cleanSpectra.shape # Band, Height, Width

    # numpy-nd array > df
    local_df = pd.DataFrame(image.reshape([b,-1]).T, columns= colWLHeaders)
    local_df_nn = local_df.dropna()

    local_df_nn['classifications'] = model.predict(local_df_nn[colWLHeaders])

    # Class-Probabilities
    class_probas = model.predict_proba(local_df_nn[colWLHeaders])
    class_count = len(class_probas[1])
    classes = list(map(str,range(1,class_count+1)))

    local_df_nn[classes] = class_probas

    classValues = local_df_nn['classifications']
    local_df_nn['classifications'] = classValues

    local_df_j = local_df.join(local_df_nn[['classifications']+classes])

    local_df_arr = np.array(local_df_j['classifications'])
    output_raster = local_df_arr.reshape((1,h,w))

    output_probs_raster = np.zeros((len(classes),h,w))
    for i,c in enumerate(classes) :
        local_df_probs_arr = np.array(local_df_j[c])
        output_probs_raster[i] = local_df_probs_arr.reshape(1,h,w)

    meta.update({'count': 1,'drive':'GTiff'})
    with rio.open(output,'w',**meta) as dest :
        dest.write(output_raster)

    meta.update({'count':len(classes),'drive':'GTiff'})
    with rio.open(output_classes,'w',**meta) as dest :
        dest.write(output_probs_raster)


def pipeline(model_filepath, si_filepath, poly_filepath, outputdir) :
    # Step 1: unpickle the model
    model = unpickle_rf_model(model_filepath)

    # Step 2: Clip AVIRIS-NG Imagery
    vineyard_si, meta = clip_imagery(poly_filepath, si_filepath)

    # Step 3: remove -9999s from Imagery and replace with NA
    vineyard_si = null_nodata_pixels(vineyard_si)

    # Step 3: calculate spectral mixture residual weights
    vineyard_si, frac_ws = smr_vegsoil(vineyard_si, meta['wls'], meta['bbs'])

    # Step 4: Generate vegetation mask
    mask = generate_mask(frac_ws)

    # Step 5: Apply vegetation mask to Step 3 output
    vineyard_si = apply_mask(vineyard_si, mask)

    # Step 6: Apply model to SMR
    vineyard_GLRaV = classify_raster(vineyard_si, meta, model, outputdir, output_filename="GLRaV")



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
                print("classification_pipeline.py -m <model filepath> -r \
                        <raster filepath> -p <polygon filepath> -o <output \
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


if __name__ == '__main__' :
    main(sys.argv[1:])

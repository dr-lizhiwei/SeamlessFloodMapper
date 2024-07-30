'''
Main Function: Seamless flood mapping using HLS imagery
'''

import argparse
from functions_config import *
from visualization_RGB import RGBTIFF, RGBgrey, RGBTIFF_cld
from water_extraction import inference_on_files
from cloud_reconstruction import *
from spatiotemporalMRF_refinement import cnsstncy_filter
from postprocessing import floodHighlight


def parse_args():
    parser = argparse.ArgumentParser(
        description="Beyond clouds: reconstructing cloud-covered areas for seamless flood mapping using the Harmonized Landsat and Sentinel-2 data")
    parser.add_argument('-DataPath', help='path to experimental data', default=r".\TestData")
    parser.add_argument('-Bands_Folder', help='folder of bands downloaded from HLS', default=r"HLS")

    # step 1 preprocess HLS data
    # If TIFF data and Cloud data are already available, set the following 2 step to False to save time
    parser.add_argument('-Bandfusion', help='fusion six bands to an multi-band image', default=True)
    parser.add_argument('-RenderHLS', help='pseudo-color visualization of remote sensing images', default=True)
    parser.add_argument('-Fmask2Cloud', help='convert Fmask to binary and extract cloud', default=True)

    # step 2 Water extraction in HLS image
    parser.add_argument('-config', help='path to model configuration file', default=r".\sen1floods11_Prithvi_100M.py")
    parser.add_argument('-ckpt', help='path to model checkpoint', default=r".\epoch_320.pth")
    parser.add_argument('-bands', help='bands in the file where to find the relevant data', default="[0,1,2,3,4,5]")
    parser.add_argument('-SemanticSegment', help='whether to use semantic segmentation to extract water', default=True)

    parser.add_argument('-Water_Occur_path', help='path to water occurrence', default=r".\TestData\WaterOccurrence.tif")
    parser.add_argument('-CloudRemoval',
                        help='whether to remove clouds from semantic segment results and generate initial water map',
                        default=True)
    parser.add_argument('-InitialWaterMaps', help='visualize initial water map', default=True)

    # step 3  Cloud reconstruction
    parser.add_argument('-WaterReconstruction', help='global/Local', default='Global')
    parser.add_argument('-ReconstructedWaterMaps', help='visualize reconstructed water map', default=True)

    # step 4  Time series refinement
    parser.add_argument('-floodDay', help='specific days of the year on which the floods occurred', default=213)
    parser.add_argument('-RefinedWaterMaps', help='refine the reconstructed water map', default=True)
    parser.add_argument('-HightlightFlood', help='mark flooded areas of refined water map in red', default=True)

    args = parser.parse_args()
    return args


def create_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def FloodMapping(args):
    """
    HLS_Folder: multi-band images
    HLS_RGB： Pseudo-color visualization of Image
    Fmask_Folder： Fmask bands
    Bina_Folder: Binary image generated by Fmask（1：Cloud, 0: No Cloud)
    Mask_Folder： 1：No Data, 0: Data
    Cloud_Folder: 1：Cloud & No Data, 0: Valid Data
    """
    # step 1 preprocess HLS data
    Rootpath = args.DataPath
    Bands_Folder = os.path.join(Rootpath, args.Bands_Folder)
    HLS_Folder = os.path.join(Rootpath, "1_HLS")
    Fmask_Folder = os.path.join(Bands_Folder, "Fmask")
    Bina_Folder = os.path.join(Bands_Folder, "Bina")
    Mask_Folder = os.path.join(Bands_Folder, "Mask")
    Cloud_Folder = os.path.join(Rootpath, "2_Mask")
    if args.Bandfusion:
        create_directory(Fmask_Folder)
        create_directory(HLS_Folder)
        multibandsincoprate(Bands_Folder, HLS_Folder, Fmask_Folder)
    if args.RenderHLS:
        HLS_RGB = os.path.join(HLS_Folder, "RGB")
        create_directory(HLS_RGB)
        RGBTIFF(HLS_Folder, HLS_RGB)
    if args.Fmask2Cloud:
        create_directory(Bina_Folder)
        create_directory(Mask_Folder)
        create_directory(Cloud_Folder)
        F2Bpath(Fmask_Folder, Bina_Folder)
        TIFFmask(HLS_Folder, Bina_Folder, Mask_Folder, Cloud_Folder)

    # step 2 Semantic segmentation of downloaded HLS data
    """
    HLS_Segment:output path of semantic segment results (1: Water, 0: No Water, -1: No data)
    Cloud_Removal: TIFF image of Initial Water Map  (0: No water, 1: Water, 2: Cloud)
    Cloud_Removal_RGB：RGB image of Initial Water Map 
    Water_Occur_removal: De-cloud Water Occurrence data in preparation for calculating reconstruction thresholds
    """
    config_path = args.config
    ckpt = args.ckpt
    bands = args.bands
    HLS_Segment = os.path.join(Rootpath, "3_HLSSegmentResult")
    if args.SemanticSegment:
        inference_on_files(config_path, ckpt, "tif", HLS_Folder + '\\', HLS_Segment + '\\', bands)

    Water_Occur_path = args.Water_Occur_path
    Cloud_Removal = os.path.join(Rootpath, "4_InitialWaterMap")
    Water_Occur_removal = os.path.join(Rootpath, "5_CloudRemovalOccurrence")
    if args.CloudRemoval:
        create_directory(Cloud_Removal)
        create_directory(Water_Occur_removal)
        cloud_detection(HLS_Segment, Cloud_Folder, Cloud_Removal, Water_Occur_path, Water_Occur_removal)
    if args.InitialWaterMaps:
        Cloud_Removal_RGB = os.path.join(Cloud_Removal, "RGB")
        create_directory(Cloud_Removal_RGB)
        RGBgrey(Cloud_Removal, Cloud_Removal_RGB)

    # step 3 calculate Rate curve (= Ws&Wo/Wo) and reconstruct water map
    # The first Occurrence value whose Rate>0.35 is used as the threshold for water reconstruction.
    """ 
    Rate_file: Calculate the Rate curve for each image and save all curve to a csv file
    WaterMap_Recons: Reconstructed Water Map(0: No Water, 1: Water, 3: Reconstructed Water, 10: Reconstructed No Water)
    WaterMap_Recons_RGB : RGB Reconstructed Images
    """
    Rate_file = os.path.join(Rootpath, "Rates_file_Occurrence.csv")
    WR(Water_Occur_removal, Cloud_Removal, Rate_file)

    WaterMap_Recons = os.path.join(Rootpath, "6_ReconstructedWaterMaps")
    WaterMap_Recons_RGB = os.path.join(WaterMap_Recons, "RGB")
    create_directory(WaterMap_Recons)
    create_directory(WaterMap_Recons_RGB)

    if args.WaterReconstruction == 'Global':
        water_reconstruction_Globle_Rate(Cloud_Removal, Water_Occur_removal, Water_Occur_path, Rate_file, WaterMap_Recons)
    if args.WaterReconstruction == 'Local':
        water_reconstruction_Globle_Local(Cloud_Removal, Water_Occur_removal, Water_Occur_path, Rate_file, WaterMap_Recons,
                                          0.35)
    if args.ReconstructedWaterMaps:
        RGBgrey(WaterMap_Recons, WaterMap_Recons_RGB)

    # step 4 spatio-temporal filter & generate Refined Water Map
    # highlight flood inundation areas
    """
    WaterMap_Refine： Refined Water Map (0 no water 1 reconstructed no water; 3 reconstructed water 4 water;
                                   7 refined water;  6 refined no water)
    WaterMap_Refine_flood: (0：no water, 1: flood, 3,4: permanent water)
    WaterMap_Refine_RGB：RGB refined flood map
    """

    WaterMap_Refine = os.path.join(Rootpath, "7_RefinedWaterMaps")
    WaterMap_Refine_flood = os.path.join(WaterMap_Refine, "Flood")
    WaterMap_Refine_RGB = os.path.join(WaterMap_Refine, "RGB")
    create_directory(WaterMap_Refine)
    create_directory(WaterMap_Refine_flood)
    create_directory(WaterMap_Refine_RGB)

    # divide into pre-flood and post-flood
    if args.RefinedWaterMaps:
        cnsstncy_filter(WaterMap_Recons, WaterMap_Refine, args.floodDay)
    if args.HightlightFlood:
        period = []
        for file in os.listdir(WaterMap_Recons):
            if file.split('.')[-1] == "tif" and int(file.split('.')[1][4:7]) < args.floodDay:
                period.append(file)
        floodHighlight(WaterMap_Refine, period, WaterMap_Refine_flood, recns=False)
        RGBgrey(WaterMap_Refine_flood, WaterMap_Refine_RGB, flood=True)
    if not args.HightlightFlood:
        RGBgrey(WaterMap_Refine, WaterMap_Refine_RGB, filter=True)


def main():
    # unpack args
    args = parse_args()
    FloodMapping(args)


if __name__ == '__main__':
    main()

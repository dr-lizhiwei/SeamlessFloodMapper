Authors:
Shaofen Xu, xv.sfen@gmail.com  
Zhiwei Li, dr.lizhiwei@gmail.com
The Hong Kong Polytechnic University

#################################
Zhiwei Li, Shaofen Xu, Qihao Weng, 2024. Beyond Clouds: Beyond clouds: Seamless flood mapping using Harmonized Landsat and Sentinel-2 time series imagery and water occurrence data. ISPRS Journal of Photogrammetry and Remote Sensing. (In Revision)

Zhiwei Li, Shaofen Xu, Qihao Weng, 2024. Can we reconstruct cloud-covered flooding areas in harmonized Landsat and Sentinel-2 image time series?, IEEE International Geoscience and Remote Sensing Symposium (IGARSS). pp. 3686-3688. Athens, Greece.
#################################


########## Setup ################
1. Download the code, and required pretrained model and test data.
2. Download the HLS image of cloud-covered water map to be reconstructed and the corresponding GSW Water Occurrence data. Make sure all data have the same georeference and projection.
2. Set the parameters in the parse_args function in _Flood_Mapping_HLS.py as nedded.
3. Run _Flood_Mapping_HLS.py
#################################


########## Key Packages ##########
torch
mmcv
mmseg
gdal
rasterio
tifffile
argparse
os
datetime
cv2
PIL
shutil
numpy
collections
pandas

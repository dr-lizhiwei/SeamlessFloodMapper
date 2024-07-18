##########Flood Mapping################
1. Download the code, and required pretrained model and test data.
2. Download the HLS image of cloud-covered water map to be reconstructed and the corresponding GSW Water Occurrence data. Make sure all data have the same georeference and projection.
2. Set the parameters in the parse_args function in _Flood_Mapping_HLS.py as nedded.
3. Run _Flood_Mapping_HLS.py


##########key package##################
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

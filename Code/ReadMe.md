**Contributors:**
Shaofen Xu, xv.sfen@gmail.com, The Hong Kong Polytechnic University
Zhiwei Li, dr.lizhiwei@gmail.com, The Hong Kong Polytechnic University
Send an email to Shaofen Xu and copy Dr. Zhiwei Li for any issues with the use of the code and datasets.





**Relevant publications:**
Zhiwei Li, Shaofen Xu, Qihao Weng, 2024. Beyond Clouds: Beyond clouds: Seamless flood mapping using Harmonized Landsat and Sentinel-2 time series imagery and water occurrence data. *ISPRS Journal of Photogrammetry and Remote Sensing*. (Accepted)

Zhiwei Li, Shaofen Xu, Qihao Weng, 2024. Can we reconstruct cloud-covered flooding areas in harmonized Landsat and Sentinel-2 image time series?, IEEE International Geoscience and Remote Sensing Symposium (IGARSS). pp. 3686-3688. Athens, Greece.





**Setup**: 

1. Download the code, and the required pretrained model and test data.
2. Download the HLS image of the cloud-covered water map to be reconstructed and the corresponding GSW Water Occurrence data. Make sure all data have the same georeference and projection.
3. Set the parameters in the parse_args function in _Flood_Mapping_HLS.py as needed.
4. Run _Flood_Mapping_HLS.py





**Notes:**

**1. Preparing Data**

- **Root Path**: Set a root directory for the study area. Specify it in the variable `-DataPath`. All processing and resulting data will be saved and managed in this root directory.

**2. Settings**

Depending on the format of input data, consider the following settings:

- a. If the existing data consists of separate bands such as Blue, Green, Red, Narrow NIR, SWIR1, SWIR2, and Fmask, create a new folder under the Root Path to store the BANDs data and declare it in the variable `-Bands_Folder`. Set the `-CombineBands` variable to **True** and the `-Fmask2Cloud` variable to **True**.
- b. If there are existing binary cloud mask files, create a folder named "2_Mask" under the Root Path to store these files. Set the `-Fmask2Cloud` variable to **False**.
- c. If there are multiband HLS remote sensing images and Fmask bands, create a new folder under the Root Path to store the BANDs data and declare it under the variable `-Bands_Folder`. Inside this folder, create another folder named "Fmask" to store the Fmask bands. Additionally, create a folder named "1_HLS" under the Root Path to manage all the multiband remote sensing image files. Set the `-CombineBands` variable to **False** and the `-Fmask2Cloud` variable to **True**.
- d. If there are multiband HLS remote sensing images and binary cloud mask files, create a folder named "1_HLS" and another named "2_Mask" under the Root Path to store the respective files. Set the `-CombineBands` variable to **False** and the `-Fmask2Cloud` variable to **False**.

**3. File Naming Conversion**

- Naming the files uniformly as "YearMonthDate_SensorType.YearMonthDay.tif" (e.g., 20200524.2020145.tif or 20200524_S.2020145).

  SensorType: S (Sentinel), L (Landsat)





**Key Packages:**
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
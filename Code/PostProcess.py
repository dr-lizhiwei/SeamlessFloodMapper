import cv2
from osgeo import gdal
import os
import numpy as np


def BiReclassFile(image, recns, before=False):
    if recns:
        if before:
            NoWater_org = np.where((image[:, :] == 10) | (image[:, :] == 0) | (image[:, :] == 2))
        else:
            NoWater_org = np.where((image[:, :] == 10) | (image[:, :] == 0))
        Water_org = np.where((image[:, :] == 3) | (image[:, :] == 1) | (image[:, :] == 254))
    else:
        NoWater_org = np.where((image[:, :] == 3) | (image[:, :] == 0) | (image[:, :] == 6))
        Water_org = np.where((image[:, :] == 4) | (image[:, :] == 4) | (image[:, :] == 7))
        # Perm_pixels = np.where(image[:, :] == 3)
    image[NoWater_org] = 0
    image[Water_org] = 1
    return image


def floodHighlight(inpath, period, labeldpath, recns):
    beforefiles = period
    waters = []
    for bfile in beforefiles:
        b_img = gdal.Open(os.path.join(inpath, bfile)).ReadAsArray()
        img = BiReclassFile(b_img.copy(), recns=recns) + 3
        cv2.imwrite(os.path.join(labeldpath, bfile), img)
        b_img = BiReclassFile(b_img, recns=recns, before=True)
        waters.append(b_img)

    waterall = waters[0]
    for i in range(1, len(waters)):
        waterall += waters[i]

    water_extent = np.where(waterall > 0)
    # perm_water = np.where(waterall==4)

    images = os.listdir(inpath)

    period2 = []
    for img in images:
        if img.split('.')[-1] == 'tif' or img.split('.')[-1] == 'png':
            if img not in period:
                fld_img = gdal.Open(os.path.join(inpath, img)).ReadAsArray()
                fld_img = BiReclassFile(fld_img, recns=recns)
                fld_img[water_extent] += 3
                # fld_img[perm_water] += 2
                # +2 0 no water 1 flood  2 3 permanent water
                # +3 0 no water 1 flood, 2 cloud 3 no water 4 permanent water 5 cloud
                cv2.imwrite(os.path.join(labeldpath, img), fld_img)

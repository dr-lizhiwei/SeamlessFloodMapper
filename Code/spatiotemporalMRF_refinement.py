import os
from osgeo import gdal
import cv2
import numpy as np


def Reclasspath(recons_path):
    files = os.listdir(recons_path)
    for file in files:
        if file.split('.')[-1] == 'png':
            img_dir = os.path.join(recons_path, file)
            imgMulti = gdal.Open(img_dir)
            image = imgMulti.ReadAsArray()

            # Water_Rcns = np.where(image[:, :] == 254)
            # NoWater_Rcns = np.where(image[:, :] == 10)
            Water_org = np.where(image[:, :] == 1)
            NoWater_org = np.where(image[:, :] == 0)
            # Perm_pixels = np.where(image[:, :] == 3)
            image[Water_org] = 4
            # image[Water_Rcns] = 3
            # image[NoWater_Rcns] = 1
            # image[NoWater_org] = 0

            cv2.imwrite(os.path.join(recons_path, file), image)


def Reclass(image, filter = False):
    if filter:
        Water_Rcns = np.where((image == 3) | (image == 254) | (image == 7) | (image == 253))  #
        NoWater_Rcns = np.where(image[:, :] == 6)

        image[Water_Rcns] = 3
        image[NoWater_Rcns] = 1
    else:
        Water_Rcns = np.where((image == 3) | (image == 254) | (image == 7) | (image == 253))  #
        NoWater_Rcns = np.where(image[:, :] == 10)
        Water_org = np.where(image[:, :] == 1)
        NoWater_org = np.where((image == 0) | (image == 2) | (image == 4) | (image == 6))

        # image[Water_org] = 10
        image[Water_org] = 4
        image[Water_Rcns] = 3
        # image[Water_Rcns] = 9
        image[NoWater_Rcns] = 1
        image[NoWater_org] = 0

    return image


def Reclassfilter(image):
    Water_Rcns = np.where(image == 7)  #
    NoWater_Rcns = np.where(image[:, :] == 6)

    image[Water_Rcns] = 3
    image[NoWater_Rcns] = 1

    return image


def TmprlSptlFilter(imagegroup, Consist_path):
    # For each graph to be processed, find 5 days of data, forward and backward.
    # Assign weights to the data by length of time

    targetimage = imagegroup[0][1]
    weight = imagegroup[0][0]
    sumimage = targetimage * weight
    for i in range(1, len(imagegroup)):
        image = imagegroup[i][1] * (imagegroup[i][0])
        sumimage = sumimage + image
        weight += imagegroup[i][0]
    weightimage = sumimage / weight

    shp = targetimage.shape
    for i in range(4, shp[0] - 5):
        for j in range(4, shp[1] - 5):
            window3 = weightimage[i - 1:i + 2, j - 1:j + 2]
            value3 = sum(map(sum, window3))
            value = (weightimage[i, j] + value3) / 10

            if targetimage[i][j] == 0 or targetimage[i][j] == 1:
                # In pixels that were not water originally,
                # if there is a large portion of pixels around that were originally water
                if value > 2:
                    targetimage[i][j] = 7
            elif targetimage[i][j] == 3 or targetimage[i][j] == 4:
                # In pixels that wer water originally,
                # if there is a large portion of pixels around that were originally not water
                if value < 2:
                    targetimage[i][j] = 6
            else:
                print(targetimage[i][j])
    cv2.imwrite(Consist_path, targetimage)


def GroupFilter(period, Rcns_dir, Consist_path, ):
    widths = []
    heights = []
    for img in period:
        image = gdal.Open(os.path.join(Rcns_dir, img)).ReadAsArray()
        widths.append(image.shape[0])
        heights.append(image.shape[1])
    # unify size
    w = int(np.min(widths))
    h = int(np.min(heights))

    datadir = {}
    for i in range(len(period)):
        data = int(period[i].split('.')[1][4:7])
        if data in datadir.keys():
            datadir[data].append(period[i])
        else:
            datadir[data] = []
            datadir[data].append(period[i])

    imagedir = {}
    for i in range(len(period)):  #
        keys = datadir.keys()
        data = int(period[i].split('.')[1][4:7])
        imagedir[period[i]] = []
        flood_img = gdal.Open(os.path.join(Rcns_dir, period[i])).ReadAsArray()
        flood_img = flood_img[0:w, 0:h]
        flood_img = Reclass(flood_img)
        imagedir[period[i]].append([6, flood_img])
        for key in range(data - 5, data + 5):
            if key in keys and key != data:
                for l in range(len(datadir[key])):
                    name = datadir[key][l]
                    if name == period[i]:
                        continue
                    flood_img = gdal.Open(os.path.join(Rcns_dir, name)).ReadAsArray()
                    flood_img = flood_img[0:w, 0:h]
                    flood_img = Reclass(flood_img)
                    imagedir[period[i]].append([6 - abs(key - data), flood_img])
    for itm in imagedir.keys():
        filterdir = os.path.join(Consist_path, itm)
        print(itm)
        TmprlSptlFilter(imagedir[itm], filterdir)


def cnsstncy_filter(Rcns_dir, Consist_path,floodDay ):
    images = os.listdir(Rcns_dir)
    period = []
    period2 = []
    for img in images:
        if img.split('.')[-1] == 'tif' or img.split('.')[-1] == 'png':
            if int(img.split('.')[1][4:7]) < floodDay:
                period.append(img)
            else:
                period2.append(img)
    if len(period)>0:
        GroupFilter(period, Rcns_dir, Consist_path)
    if len(period2) > 0:
        GroupFilter(period2, Rcns_dir, Consist_path)


'''
cloud remval and water reconstruction
'''

import numpy as np
import os
import cv2
from osgeo import gdal
from collections import Counter
import pandas as pd


def WR(Water_Occur_removal, Cloud_Removal, fileName):

    rates = []
    for i in range(0,101):
        rates.append([])
        # rates[i].append(i)
    '''
    Water Reconstruction
    '''
    cfiles = os.listdir(Cloud_Removal)
    for file in cfiles:
        if file.split('.')[-1] =='tif' or file.split('.')[-1] =='png':
            rates[0].append(file.split('.')[0])
            img_dir = os.path.join(Cloud_Removal, file)
            imgMulti = gdal.Open(img_dir)
            image = imgMulti.ReadAsArray()

            # cloud removal
            Cloud_pixels = np.where(image[:, :] == 2)
            image[Cloud_pixels] = 0

            Water_path = os.path.join(Water_Occur_removal, file.split('.')[0]+'.tif')
            waterimg = gdal.Open(Water_path)
            water_img = waterimg.ReadAsArray()
            all_pixels = np.where(water_img[:, :] != 0)

            # Water_Occur = gdal.Open(Water_Occur_path).ReadAsArray()
            # validpix = np.where((Water_Occur >= 0) & (Water_Occur <= 100))
            # Water_Occur = Water_Occur[min(validpix[0]):max(validpix[0]), min(validpix[1]):max(validpix[1])]
            # Water_Occur = np.where(Water_Occur == 128, 0, Water_Occur)
            # Water_Occur = cv2.resize(Water_Occur, (height, width))


            # get (i, j) positions of predicted water pixels
            Seg_pixels = np.where(image[:, :] == 1)
            result = Counter(water_img[Seg_pixels])
            result1 = Counter(water_img[all_pixels])
            dic = dict(result)
            dic1 = dict(result1)
            for key in range(1,101):
                if key in dic.keys() and key in dic1.keys() and int(dic1[key])!= 0:
                    rates[int(key)].append(int(dic[key])/int(dic1[key]))
                else:
                    rates[int(key)].append(0)
    # rates to .csv
    array = np.array(rates)
    pd.DataFrame(array).to_csv(fileName,header=None)
    # [f.write('{0},{1}\n'.format(key, value)) for key, value in rates.items()]

def water_Rate_Global(Water_Occur_removal, Cloud_Removal, fileName):
    '''
        method of Zhao and Gao
    '''
    rates = []
    for i in range(0,2):
        rates.append([])
        # rates[i].append(i)

    cfiles = os.listdir(Cloud_Removal)
    for file in cfiles:
        if file.split('.')[-1] =='tif' or file.split('.')[-1] =='png':
            rates[0].append(file.split('.')[0])
            img_dir = os.path.join(Cloud_Removal, file)
            imgMulti = gdal.Open(img_dir)
            image = imgMulti.ReadAsArray()

            # cloud removal
            Cloud_pixels = np.where(image[:, :] == 2)
            image[Cloud_pixels] = 0

            Water_path = os.path.join(Water_Occur_removal, file.split('.')[0]+'.tif')
            waterimg = gdal.Open(Water_path)
            water_img = waterimg.ReadAsArray()


            # get (i, j) positions of predicted water pixels
            Seg_pixels = np.where(image[:, :] == 1)
            result1 = Counter(water_img[Seg_pixels])

            dic1 = dict(result1)
            sum = 0
            for key in range(1,101):
                if key in dic1.keys() :
                    sum+=int(dic1[key])
            threshold = sum * 0.17 / 100
            count = 0
            for key in range(1, 101):
                # if key in dic1.keys():
                #     count += int(dic1[key])
                if dic1[key] >threshold:
                    rates[1].append(key)
                    break
                #     rates[int(key)].append(int(dic1[key]))
                # else:
                #     rates[int(key)].append(0)
    #rates to .csv
    array = np.array(rates)
    pd.DataFrame(array).to_csv(fileName,header=None)
    # [f.write('{0},{1}\n'.format(key, value)) for key, value in rates.items()]

def water_Rate(seg_img, water_img, rt):
    '''
    Local threshold
    '''
    rates = []
    for i in range(0, 256):
        rates.append([])
        # rates[i].append(i)
    '''
    Water Reconstruction
    '''

    all_pixels = np.where(water_img[:, :] != 0)

    # get (i, j) positions of predicted water pixels
    Seg_pixels = np.where(seg_img[:, :] == 1)
    result = Counter(water_img[Seg_pixels])
    result1 = Counter(water_img[all_pixels])
    dic = dict(result)
    dic1 = dict(result1)
    for key in dic.keys():
        if key != 0 and key in dic1.keys():
            if int(dic1[key]) != 0:
                rates[int(key)].append(int(dic[key]) / int(dic1[key]))

    for i in range(len(rates)):
        if len(rates[i]) > 0:
            # if rates[i][0]> 0.4:
            if rates[i][0] > rt:  # 0.2:
                return i
                break
        else:
            return 0


def Water_Reconstruction_Gradually(Cloud_Removal, Water_Occur_removal, Water_Occur_path, rate_path,
                                   Water_reconstruction):
    # set threshold for rate
    widths = []
    heights = []

    # Semantic Segmentation Result
    images = [img for img in os.listdir(Cloud_Removal) if img.endswith(('tif', 'png'))]
    for img in images:
        img_dir = os.path.join(Cloud_Removal, img)
        imgMulti = gdal.Open(img_dir)
        image = imgMulti.ReadAsArray()
        widths.append(image.shape[0])
        heights.append(image.shape[1])
    # unify size
    width = int(np.min(widths))
    height = int(np.min(heights))
    pansize = int(max(width, height) / 2)
    pansize1 = int(min(width, height) / 2)

    Water_Occur = gdal.Open(Water_Occur_path).ReadAsArray()
    validpix = np.where((Water_Occur >= 0) & (Water_Occur <= 100))
    Water_Occur = Water_Occur[min(validpix[0]):max(validpix[0]), min(validpix[1]):max(validpix[1])]
    Water_Occur = np.where(Water_Occur == 128, 0, Water_Occur)
    Water_Occur = cv2.resize(Water_Occur, (height, width))

    NoWaterPixs = np.where(Water_Occur == 0)

    # for each image
    cfiles = [file for file in os.listdir(Cloud_Removal) if file.endswith(('tif', 'png'))]
    cols = [file.split('.')[0] for file in cfiles]
    datas = pd.read_csv(rate_path, usecols=cols)

    for file in cfiles:
        rcns_dir = os.path.join(Water_reconstruction, file)
        if os.path.exists(rcns_dir):
            continue

        img_dir = os.path.join(Cloud_Removal, file)
        seg_img = gdal.Open(img_dir).ReadAsArray()
        # seg_img = cv2.resize(seg_img, (im_width, im_height))
        seg_img_pad = np.pad(seg_img, ((pansize, pansize), (pansize, pansize)), 'constant', constant_values=(0, 0))

        Water_path = os.path.join(Water_Occur_removal, file.split('.')[0] + '.tif')
        waterimg = gdal.Open(Water_path).ReadAsArray()
        # waterimg = cv2.resize(waterimg, (im_width, im_height))
        water_img_pad = np.pad(waterimg, ((pansize, pansize), (pansize, pansize)), 'constant', constant_values=(0, 0))

        # water reconstruction
        # threshold for water
        thrWater = 70
        thrRate = 0.40
        for i, rate in enumerate(datas[file.split('.')[0]]):
            if rate > thrRate:
                thrWater = i
                break

        cloud_pixels = set(map(tuple, np.column_stack(np.where((seg_img == 2) | (seg_img == -1)))))
        no_water_pixels = set(map(tuple, np.column_stack(NoWaterPixs)))
        intersection = cloud_pixels.intersection(no_water_pixels)
        res0, res1 = np.array(list(zip(*intersection)))
        seg_img[res0, res1] = 10

        # calculate local threshold using slide window
        gap_pixels = np.column_stack(np.where((seg_img == 2) | (seg_img == -1)))

        count = len(gap_pixels)
        num = 0
        out = 0
        for pnt in gap_pixels:
            num += 1
            tmp = round(num / count, 1)
            if tmp != out:
                print(tmp)
                out = tmp

            ptx, pty = pnt
            wo = Water_Occur[ptx, pty]
            if wo == 0:
                seg_img[ptx, pty] = 0
            else:
                # initial size and iter step
                WindowSize = 25
                exp = 1
                ValidPixs = 0
                Seg_Wndw = []

                while ValidPixs < WindowSize * WindowSize / 4.5 and WindowSize < pansize1:
                    # pansize is the effective fill size. Since the largest window is the one that contains the
                    # entire image, when the window edges are already larger than the image edges, jump out of the
                    # loop and rebuild directly using global thresholding

                    Seg_Wndw = seg_img_pad[ptx + pansize - WindowSize: ptx + pansize + WindowSize,
                               pty + pansize - WindowSize: pty + pansize + WindowSize]
                    ValidPixs = np.sum(Seg_Wndw == 1)
                    WindowSize = int(WindowSize * (2 ** exp))
                    exp += 1

                if WindowSize >= pansize1:
                    thrsh_pix = thrWater
                else:
                    Water_Wndw = water_img_pad[ptx + pansize - WindowSize:ptx + pansize + WindowSize,
                                 pty + pansize - WindowSize:pty + pansize + WindowSize]
                    thrsh_pix = water_Rate(Seg_Wndw, Water_Wndw)

                # To give less credit to the reconstructed part, the reciprocal will be taken
                seg_img[ptx, pty] = 3 if wo > thrsh_pix else 10

        # Under normal circumstances, there would be no clouds on the reconstructed image.
        Cloud_pixels = np.where(seg_img[:, :] == 2)
        seg_img[Cloud_pixels] = 0
        Cloud_pixels = np.where(seg_img[:, :] == -1)
        seg_img[Cloud_pixels] = 0

        # 0 no water, 1 water, 2 cloud, 3 reconstructed water,  10 reconstructed no water
        cv2.imwrite(rcns_dir, seg_img)
        print(file.split('.')[0])


def water_reconstruction_Globle(Cloud_Removal, Water_Occur_path, rate_path, Water_reconstruction):
    # Zhao and Gao
    # set threshold for rate
    thrRate = 0.40

    widths = []
    heights = []

    # Semantic Segmentation Result
    images = os.listdir(Cloud_Removal)
    for img in images:
        if img.split('.')[-1] == 'tif' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(Cloud_Removal, img)
            imgMulti = gdal.Open(img_dir)
            image = imgMulti.ReadAsArray()
            widths.append(image.shape[0])
            heights.append(image.shape[1])
    # unify size
    width = int(np.min(widths))
    height = int(np.min(heights))

    Water_Occur = gdal.Open(Water_Occur_path).ReadAsArray()
    validpix = np.where(Water_Occur != 128)
    Water_Occur = Water_Occur[min(validpix[0]):max(validpix[0]), min(validpix[1]):max(validpix[1])]
    Water_Occur = np.where(Water_Occur == 128, 0, Water_Occur).astype(float)
    Water_Occur = cv2.resize(Water_Occur, (height, width))

    # for each image
    cfiles = os.listdir(Cloud_Removal)
    col = []
    for file in cfiles:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            col.append(file.split('.')[0])
    datas = pd.read_csv(rate_path, usecols=col)
    for file in cfiles:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            img_dir = os.path.join(Cloud_Removal, file)
            seg_img = gdal.Open(img_dir).ReadAsArray()

            thrWater = datas[file.split('.')[0]][0]

            cloud_pixels = set(map(tuple, np.column_stack(np.where((seg_img == 2) | (seg_img == -1)))))
            water_pixels = np.where((Water_Occur[:, :] > thrWater))
            water_pixels = set(map(tuple, np.column_stack(water_pixels)))
            intersection = cloud_pixels.intersection(water_pixels)
            res0, res1 = np.array(list(zip(*intersection)))
            seg_img[res0, res1] = 1

            # water_pixels = np.where((Water_Occur[:, :] > thrWater))

            # seg_img[water_pixels] = 1

            seg_img = np.where(seg_img == 2, 0, seg_img)
            seg_img = np.where(seg_img == -1, 0, seg_img)
            # 0 no water, 1 water, 2 cloud, 3 reconstructed water,  10 reconstructed no water
            rcns_dir = os.path.join(Water_reconstruction, file.split('.')[0] + '.' + file.split('.')[1] + '.tif')
            cv2.imwrite(rcns_dir, seg_img)
            print(file.split('.')[0])

def water_reconstruction_Globle_Rate(Cloud_Removal, Water_Occur_removal, Water_Occur_path, rate_path, Water_reconstruction):

    # set threshold for rate
    thrRate = 0.40

    widths = []
    heights = []

    # Semantic Segmentation Result
    images = os.listdir(Cloud_Removal)
    for img in images:
        if img.split('.')[-1] == 'tif' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(Cloud_Removal, img)
            imgMulti = gdal.Open(img_dir)
            image = imgMulti.ReadAsArray()
            widths.append(image.shape[0])
            heights.append(image.shape[1])
    # unify size
    width = int(np.min(widths))
    height = int(np.min(heights))

    Water_Occur = gdal.Open(Water_Occur_path).ReadAsArray()
    validpix = np.where(Water_Occur != 128)
    Water_Occur = Water_Occur[min(validpix[0]):max(validpix[0]), min(validpix[1]):max(validpix[1])]
    Water_Occur = np.where(Water_Occur == 128, 0, Water_Occur).astype(float)
    Water_Occur = cv2.resize(Water_Occur, (height, width))

    cfiles = os.listdir(Cloud_Removal)
    col = []
    for file in cfiles:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            col.append(file.split('.')[0])
    datas = pd.read_csv(rate_path, usecols=col)
    for file in cfiles:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            img_dir = os.path.join(Cloud_Removal, file)
            seg_img = gdal.Open(img_dir).ReadAsArray()

            thrWater = 70
            for i in range(0, len(datas[file.split('.')[0]])):
                if datas[file.split('.')[0]][i] > thrRate:
                    thrWater = i
                    break

            cloud_pixels = set(map(tuple, np.column_stack(np.where((seg_img == 2) | (seg_img == -1)))))
            water_pixels = np.where((Water_Occur[:, :] > thrWater))
            water_pixels = set(map(tuple, np.column_stack(water_pixels)))
            intersection = cloud_pixels.intersection(water_pixels)
            res0, res1 = np.array(list(zip(*intersection)))
            seg_img[res0, res1] = 1

            seg_img = np.where(seg_img == 2, 0, seg_img)
            seg_img = np.where(seg_img == -1, 0, seg_img)
            # 0 no water, 1 water, 2 cloud, 3 reconstructed water,  10 reconstructed no water
            rcns_dir = os.path.join(Water_reconstruction, file.split('.')[0] + '.' + file.split('.')[1] + '.tif')
            cv2.imwrite(rcns_dir, seg_img)
            print(file.split('.')[0])


def water_reconstruction_Globle_Local(Cloud_Removal, Water_Occur_removal, Water_Occur_path, rate_path,
                                      Water_reconstruction, rt):
    """
    The most important function for local reconstruction of a water body
    Obtain global reconstruction thresholds from files
    Perform local threshold calculation and reconstruction
    """
    # set threshold for rate
    # thrRate = 0.40
    thrRate = rt  # 0.20

    widths = []
    heights = []

    # Semantic Segmentation Result
    images = os.listdir(Cloud_Removal)
    for img in images:
        if img.split('.')[-1] == 'tif' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(Cloud_Removal, img)
            imgMulti = gdal.Open(img_dir)
            image = imgMulti.ReadAsArray()
            widths.append(image.shape[0])
            heights.append(image.shape[1])
    # unify size
    width = int(np.min(widths))
    height = int(np.min(heights))
    # im_width = 6687  # imgMulti.RasterXSize
    # im_height = 3088  # imgMulti.RasterYSize

    Water_Occur = gdal.Open(Water_Occur_path).ReadAsArray()
    validpix = np.where((Water_Occur >= 0) & (Water_Occur <= 100))
    Water_Occur = Water_Occur[min(validpix[0]):max(validpix[0]), min(validpix[1]):max(validpix[1])]
    Water_Occur = np.where(Water_Occur == 128, 0, Water_Occur)
    Water_Occur = cv2.resize(Water_Occur, (height, width))

    NoWaterPixs = np.where(Water_Occur == 0)

    # for each image
    cfiles = os.listdir(Cloud_Removal)
    col = []
    for file in cfiles:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            col.append(file.split('.')[0])
    datas = pd.read_csv(rate_path, usecols=col)
    for file in cfiles:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            rcns_dir = os.path.join(Water_reconstruction, file.split('.')[0] + '.' + file.split('.')[1] + '.tif')
            if os.path.exists(rcns_dir):
                continue
            img_dir = os.path.join(Cloud_Removal, file)
            seg_img = gdal.Open(img_dir).ReadAsArray()
            # seg_img = cv2.resize(seg_img, (height, width))
            seg_img_pad150 = np.pad(seg_img, ((75, 75), (75, 75)), 'constant', constant_values=(0, 0))

            Water_path = os.path.join(Water_Occur_removal, file.split('.')[0] + '.tif')
            waterimg = gdal.Open(Water_path).ReadAsArray()
            # waterimg = cv2.resize(waterimg, (im_width, im_height))
            water_img_pad150 = np.pad(waterimg, ((75, 75), (75, 75)), 'constant', constant_values=(0, 0))

            # water reconstruction
            # threshold for water
            thrWater = 70
            for i in range(0, len(datas[file.split('.')[0]])):
                if datas[file.split('.')[0]][i] > thrRate:
                    thrWater = i
                    break

            # Local reconstruction after obtaining global thresholds
            # Fill the missing part first with values where OW is 0, it is impossible to fill it with water again
            # Traverse only the regions where water has appeared to reduce computation
            cloud_pixels = np.where(seg_img[:, :] == 2)
            c = set((tuple([cloud_pixels[0][i], cloud_pixels[1][i]]) for i in range(len(cloud_pixels[0]))))
            n = set((tuple([NoWaterPixs[0][i], NoWaterPixs[1][i]]) for i in range(len(NoWaterPixs[0]))))
            inter = c.intersection(n)
            res0 = np.array([x[0] for x in inter])
            res1 = np.array([x[1] for x in inter])

            seg_img[tuple(res0), tuple(res1)] = 10

            # calculate local threshold
            gap_pixels = np.where((seg_img[:, :] == 2) | (seg_img[:, :] == -1))
            g_array = np.array(gap_pixels).transpose(1, 0)

            count50 = 0
            count100 = 0
            count150 = 0

            for pnt in g_array:
                ptx = pnt[0]
                pty = pnt[1]
                wo = Water_Occur[ptx, pty]
                if wo == 0:
                    seg_img[ptx, pty] = 0
                # 3 fit size of window
                else:
                    seg50 = seg_img_pad150[pnt[0] + 50:pnt[0] + 100, pnt[1] + 50:pnt[1] + 100]
                    valid1_50 = np.where((seg50 == 1) | (seg50 == 0))

                    if len(valid1_50[0]) > 1250:
                        water50 = water_img_pad150[pnt[0] + 50:pnt[0] + 100, pnt[1] + 50:pnt[1] + 100]
                        thrsh_pix = water_Rate(seg50, water50, rt)
                        count50 += 1
                    else:
                        seg100 = seg_img_pad150[pnt[0] + 25:pnt[0] + 125, pnt[1] + 25:pnt[1] + 125]
                        valid1_100 = np.where((seg100 == 1) | (seg100 == 0))
                        if len(valid1_100[0]) > 5000:
                            water100 = water_img_pad150[pnt[0] + 25:pnt[0] + 125, pnt[1] + 25:pnt[1] + 125]
                            thrsh_pix = water_Rate(seg100, water100, rt)
                            count100 += 1
                        else:
                            seg150 = seg_img_pad150[pnt[0]:pnt[0] + 150, pnt[1]:pnt[1] + 150]
                            valid1_150 = np.where((seg150 == 1) | (seg150 == 0))
                            if len(valid1_150[0]) > 11250:
                                water150 = water_img_pad150[pnt[0]:pnt[0] + 150, pnt[1]:pnt[1] + 150]
                                thrsh_pix = water_Rate(seg150, water150, rt)
                                count150 += 1
                            else:
                                thrsh_pix = thrWater

                    seg_img[ptx, pty] = 3 if wo > thrsh_pix else 10

            print(count50, count100, count150)

            # cloud removal
            Cloud_pixels = np.where(seg_img[:, :] == 2)
            seg_img[Cloud_pixels] = 0
            nodata = np.where(seg_img[:, :] == -1)
            seg_img[nodata] = 0

            # 0 no water, 1 water, 2 cloud, 3 reconstructed water,  10 reconstructed no water
            cv2.imwrite(rcns_dir, seg_img)
            print(file.split('.')[0])




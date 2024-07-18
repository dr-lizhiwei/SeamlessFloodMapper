'''
turn HLS name into calender
'''
import os
from osgeo import gdal
import datetime
import cv2
import numpy as np
import shutil


def out_date_by_day(year,day):
    first_day=datetime.datetime(year,1,1)
    add_day=datetime.timedelta(days=day-1)
    return datetime.datetime.strftime(first_day+add_day,"%Y%m%d")
def out_day_by_date(year,month,day):
    months=[0,31,59,90,120,151,181,212,243,273,304,334]
    if 0<month<=12:
        sum=months[month-1]
    else:
        print("month error")
    sum+=day
    leap=0
    if(year%400==0) or ((year%4)==0) and (year%100!=0):
        leap=1
    if(leap==1) and (month>2):
        sum+=1
    return sum


# rename HLS bands
def renameHLS(File_path):
    files = os.listdir(File_path)
    for fl in files:
        #判断传感器
        if len(fl.split('.')) >4 and fl.split('.')[-1] == 'tif':
            mode = fl.split('.')[1][0]
            band = fl.split('.')[-2]
            prefix = fl.split('.')[3][0:7]

            year = fl.split('.')[3][0:4]
            days = fl.split('.')[3][4:7]
            data = out_date_by_day(int(year), int(days))

            oldname = File_path + os.sep + fl
            newname = File_path + os.sep + f"{data}_{mode}.{prefix}.{band}.tif"

            if os.path.exists(newname):
                continue
            else:
                os.rename(oldname, newname)

def multibandsincoprate(RootPath, TIFFPath, CloudPath):
    # 重命名 YearMonthDate.YearDays.tif
    renameHLS(RootPath)
    # 读取文件夹中的文件，获得单独的文件名
    files = os.listdir(RootPath)
    scenes = set()
    for file in files:
        name_parts = file.split('.')
        if len(name_parts) > 3:
            datam, days = name_parts[0], name_parts[1]
            scenes.add((datam, days))
    # Iterate over the filenames, taking only the 6 bands needed for the semantic segmentation model
    # Bands of S30：[ "B2", "B3", "B4", "B8A", "B11", "B12"]
    # Bands of L30：[ "B2", "B3", "B4", "B5", "B6", "B7"]
    for datam, days in scenes:
        filename = f"{datam}.{days}"
        is_sentinel = datam.split('_')[-1] == 'S'

        bands = [
            f"{filename}.B02.tif",
            f"{filename}.B03.tif",
            f"{filename}.B04.tif",
            f"{filename}.B8A.tif" if is_sentinel else f"{filename}.B05.tif",
            f"{filename}.B11.tif" if is_sentinel else f"{filename}.B06.tif",
            f"{filename}.B12.tif" if is_sentinel else f"{filename}.B07.tif"
        ]

    tiff = gdal.Open(os.path.join(RootPath, bands[0]))
    x, y = tiff.RasterXSize, tiff.RasterYSize
    datatype = tiff.GetRasterBand(1).DataType

    in_bands = [gdal.Open(os.path.join(RootPath, band)).ReadAsArray() for band in bands]

    gtif_driver = gdal.GetDriverByName("GTiff")
    out_ds = gtif_driver.Create(os.path.join(TIFFPath, f"{filename}.tif"), x, y, 6, datatype)

    out_ds.SetProjection(tiff.GetProjection())
    out_ds.SetGeoTransform(tiff.GetGeoTransform())

    for i, in_band in enumerate(in_bands, start=1):
        out_ds.GetRasterBand(i).WriteArray(in_band)

    out_ds.FlushCache()
    print("FlushCache succeed")

    del out_ds

    BFmask = f"{filename}.Fmask.tif"
    cloud_dir = os.path.join(RootPath, BFmask)
    Fmask_dir = os.path.join(CloudPath, BFmask)
    shutil.copyfile(cloud_dir,Fmask_dir)



def F2Bpath(Cloud_path,Binary_path):
    files = [file for file in os.listdir(Cloud_path) if file.endswith('.tif')]
    for file in files:
        name_parts = file.split('.')
        bina_path = os.path.join(Binary_path, f"{name_parts[0]}.{name_parts[1]}.tif")
        cloud_dir = os.path.join(Cloud_path, file)

        if not os.path.isfile(cloud_dir):
            print(f"{cloud_dir} doesn't exist")
            continue
        else:
            cloud_img = gdal.Open(cloud_dir).ReadAsArray()
            Fbi = np.zeros_like(cloud_img)

            # 0 representing no data in the FMask band
            zero_pix = np.where(cloud_img[:,:]==0)

            cloud_pix = np.where((cloud_img >= 64) & ((cloud_img & 0b10) | (cloud_img & 0b1000)))

            Fbi[cloud_pix] = 1
            Fbi[zero_pix] = 1
            cv2.imwrite(bina_path,Fbi)

def TIFFmask(TIFFpath,Binary_path,Mask_Folder,maskpath):
    files = [file for file in os.listdir(TIFFpath) if file.endswith('.tif')]
    for file in files:
        image = gdal.Open(os.path.join(TIFFpath, file)).ReadAsArray()
        channels, height, width = image.shape

        # 创建遮罩
        mask = np.zeros((height, width))
        for i in range(channels):
            pix = np.where((image[i] == 32767) | (image[i] == -9999))
            mask[pix] = 1

        NpKernel = np.uint8(np.ones((30, 30)))
        dilated = cv2.dilate(mask, NpKernel)
        cv2.imwrite(os.path.join(Mask_Folder, file), dilated)

        if os.path.isfile(os.path.join(Binary_path, file) ):
            cld_dir = os.path.join(Binary_path, file)
        else:
            print("no cloud!")

        cloud = gdal.Open(cld_dir).ReadAsArray()
        cloud = cv2.resize(cloud, (width, height))
        cloud[np.where(dilated == 1)] = 1
        cv2.imwrite(os.path.join(maskpath, file), cloud)


def cloud_detection (Seg_path, Cloud_path, Cloud_Removal, Water_Occur_path, Water_Occur_removal):
    # Due to projection or data cropping, there may be a few pixels of error in the data SIZE
    # using Semantic Segmentation Result to unify size

    widths = []
    heights = []
    images = os.listdir(Seg_path)
    for img in images:
        if img.split('.')[-1] == 'tif' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(Seg_path, img)
            image = gdal.Open(img_dir).ReadAsArray()
            widths.append(image.shape[0])
            heights.append(image.shape[1])
    width = int(np.min(widths))
    height = int(np.min(heights))

    files = os.listdir(Seg_path)
    for file in files:
        if file.split('.')[-1] == 'tif' or file.split('.')[-1] == 'png':
            img_dir = os.path.join(Seg_path, file)
            image = gdal.Open(img_dir).ReadAsArray()
            cutImg =cv2.resize(image, (height, width))

            water_img = gdal.Open(Water_Occur_path).ReadAsArray()
            validpix = np.where((water_img >= 0) & (water_img <= 100))
            water_img = water_img[min(validpix[0]):max(validpix[0]),min(validpix[1]):max(validpix[1])]
            water_img = np.where((water_img < 0) | (water_img > 100),0,water_img).astype(float)
            water_img = cv2.resize(water_img, (height, width))

            cloud_dir = os.path.join(Cloud_path, file.split('-')[0] + '.tif') # file.split('_')[0][0:8] + '.tif'))#
            if not os.path.isfile(cloud_dir):
                cloud_dir = os.path.join(Cloud_path, file.split('.')[0] + '.tif')
                if not os.path.isfile(cloud_dir):
                        print(cloud_dir + " doesn't exist")

            cloud_img = gdal.Open(cloud_dir).ReadAsArray()
            cloud_resz = cv2.resize(cloud_img, (height, width))
            print(cloud_resz.shape)

            if 'L7' in file or 'L8' in file or 'L9' in file:
                cloud_pix= np.where(cloud_resz[:, :] == 0)
            else:
                cloud_pix = np.where(cloud_resz[:, :] == 1)

            # cloud detection
            cutImg[cloud_pix] = 2
            c_dir = os.path.join(Cloud_Removal, file.split('-')[0] + '.tif')#file.split('_')[0][0:8]+ '_clean.png')
            cv2.imwrite(c_dir, cutImg)

            #Occurrence
            water_img[cloud_pix] = 0
            Water_removal_dir = os.path.join(Water_Occur_removal,file.split('.')[0] + '.tif')#file.split('_')[0][0:8]+ '.png' )
            cv2.imwrite(Water_removal_dir, water_img)
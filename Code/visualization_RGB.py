from PIL import Image
import cv2
import numpy as np
from osgeo import gdal
import os


def stretch(band, lower_percent=2, higher_percent=95): #2和95表示分位数
    band=np.array(band,dtype=np.float32)
    # band[band < 0] = 0
    c = np.percentile(band[(band!=32767.0)&(band!=-9999.0)], lower_percent)*1.0
    d = np.percentile(band[(band!=32767.0)&(band!=-9999.0)], higher_percent)*1.0
    band[band<c] = c
    band[band>d] = d
    out =  (band - c)  / (d - c)

    return out.astype(np.float32)

def stretch_n(data,cloudper = 2, n_band=3):  #该操作将改变原始数据，因此data用.copy，不对原始数据进行更改
    data=np.array(data,dtype=np.float32)
    for k in range(n_band):
            data[:,:,k] = stretch(data[:,:,k],cloudper)
    return data
def rgb(img_data,iftran=True):
    img_data_3b = img_data[[1,2,3],:,:]                  # 取前三个波段 B02,B03,B04
    if iftran:
        img_data_3b = img_data_3b[::-1,:,:]             # 将B02,B03,B04转成B04,B03,B02 (BGR转RGB)
    img_data = img_data_3b.transpose(1,2,0)     # C,H,W -> H,W,C
    return img_data
color_dict = {"white": [255, 255, 255],
              "green": [0, 255, 0],

              "blue": [255, 0, 0],
              # "deepblue":[168,77,0],
              "deepblue":[200,90,10],
              "dogerblue4":[139, 78, 16],
              "lightblue":[255,112,0],
              "picblue":[204,139,61],

              "red": [0, 0, 255],
              "brown":[102,102,205],
              "darkred":[0,0,139],
              "indiared":[85 ,85, 205],
              "picred":[70,71,196],
              # "deepred":[0,0,192],
              "deepred":[20,20,212],

              "grey": [204, 204, 204],
              "black":[0,0,0]
              }

def render(gray):

    rgb_image = np.zeros(shape=(*gray.shape, 3))
    rgb_image[:, :, :] = color_dict["grey"]

    # 0 背景；1 水体； 2/4 云层/重建后的云层（不显示）； 3 重建的水体  10 重建的背景;
    pixel1 = np.where(gray == 1)
    pixel2 = np.where(gray == 2)
    rgb_image[pixel1[0],pixel1[1],:] = color_dict["deepblue"]
    rgb_image[pixel2[0],pixel2[1],:] = color_dict["white"]

    return rgb_image.astype(np.uint8)

def renderfilter(gray):
    rgb_image = np.zeros(shape=(*gray.shape, 3))
    rgb_image[:, :, :] = color_dict["grey"]

    # 0/1 背景； 3/4 水； 7 滤波出的水  6 滤波没的背景;
    pixel7 = np.where(gray == 7)
    pixel254 = np.where(gray == 254)
    # pixel6 = np.where(gray == 6)
    pixel4 = np.where(gray == 4)
    pixel3 = np.where(gray == 3)
    rgb_image[pixel7[0], pixel7[1], :] = color_dict["deepblue"]
    rgb_image[pixel4[0], pixel4[1], :] = color_dict["deepblue"]
    rgb_image[pixel3[0], pixel3[1], :] = color_dict["deepblue"]
    rgb_image[pixel254[0], pixel254[1], :] = color_dict["deepblue"]

    return rgb_image.astype(np.uint8)


def renderflood(gray):
    rgb_image = np.zeros(shape=(*gray.shape, 3))
    rgb_image[:, :, :] = color_dict["grey"]

    # +3 0 no water 1 flood 2,5 cloud 3 no 4 water
    pixel1 = np.where(gray == 1)
    pixel2 = np.where(gray == 2)
    pixel3 = np.where(gray == 3)
    pixel4 = np.where(gray == 4)
    pixel5 = np.where(gray == 5)
    rgb_image[pixel1[0], pixel1[1], :] = color_dict["deepred"]
    rgb_image[pixel2[0], pixel2[1], :] = color_dict["white"]
    # rgb_image[pixel3[0], pixel3[1], :] = color_dict["deepblue"]
    rgb_image[pixel4[0], pixel4[1], :] = color_dict["deepblue"]
    rgb_image[pixel5[0], pixel5[1], :] = color_dict["white"]

    return rgb_image.astype(np.uint8)

def RGBgrey(img_path, rgb_path, filter=False, flood=False, Fig8=False):
    img_list = os.listdir(img_path)
    for img in img_list:
        if img.split('.')[-1] == 'png' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(img_path, img)
            image = gdal.Open(img_dir).ReadAsArray()
            rgb_dir = os.path.join(rgb_path, img.split('.')[0] + '-rgb.tif')

            # 灰度图拉伸成彩色显示
            if filter:
                imagergb = renderfilter(image)
            elif flood:
                imagergb = renderflood(image)
            else:
                imagergb = render(image)
            font = cv2.FONT_HERSHEY_DUPLEX  # 设置字体
            # 图片对象、文本、位置像素、字体、字体大小、颜色、字体粗细
            label = img.split('.')[0][0:11]  # 不论是否两个字母标记都可囊括
            if img.split('_')[0].__contains__('S1'):
                label = img.split('_')[4][0:8]
            # imgzi = cv2.putText(imagergb, label, (100, 100), font, 3, (0, 0, 255), 2)
            # imagergb = Image.fromarray(imagergb)
            # imagergb.save(rgb_dir)
            cv2.imwrite(rgb_dir, imagergb)
            print(img)

def RGBTIFF_cld(img_path, cloud_path, rgb_path):
    img_list = os.listdir(img_path)
    for img in img_list:
        if img.split('.')[-1] == 'png' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(img_path, img)
            imgMulti = gdal.Open(img_dir)
            # meta = get_meta(img_dir)
            image = imgMulti.ReadAsArray()
            cloud_dir = os.path.join(cloud_path,img)
            if not os.path.exists(cloud_dir):
                cloud_dir = os.path.join(cloud_path,img.split('.')[0]+'.tif')
            cloud = gdal.Open(cloud_dir).ReadAsArray()
            cloudper = len(np.where(cloud == 1)[0])/cloud.size*20
            rgb_dir = os.path.join(rgb_path, img.split('.')[0]+ '-rgb.png')

            img_data_r = rgb(image)
            imagergb = np.uint8(stretch_n(img_data_r.copy(), 100 - cloudper) * 255)

            font = cv2.FONT_HERSHEY_DUPLEX
            # Image object, text, position pixels, font, font size, color, font thickness
            imagergb = cv2.putText(imagergb, img.split('.')[0], (100, 100), font, 3, (0, 0, 255), 2)
            imagergb = Image.fromarray(imagergb)
            imagergb.save(rgb_dir)

def RGBTIFF(img_path, rgb_path):
    img_list = os.listdir(img_path)
    for img in img_list:
        if img.split('.')[-1] == 'png' or img.split('.')[-1] == 'tif':
            img_dir = os.path.join(img_path, img)
            imgMulti = gdal.Open(img_dir)
            # meta = get_meta(img_dir)
            image = imgMulti.ReadAsArray()
            rgb_dir = os.path.join(rgb_path, img.split('.')[0]+ '-rgb.png')

            # # Multi-band TIFF map saved as tri-band RGB display
            img_data_r = rgb(image)
            imagergb = np.uint8(stretch_n(img_data_r.copy()) * 255)

            # font = cv2.FONT_HERSHEY_DUPLEX
            # Image object, text, position pixels, font, font size, color, font thickness
            # imagergb = cv2.putText(imagergb, img.split('.')[0], (100, 100), font, 3, (255, 0, 0), 2)
            imagergb = Image.fromarray(imagergb)
            imagergb.save(rgb_dir)

# SeamlessFloodMapper: Seamless Flood Mapping Using Harmonized Landsat and Sentinel-2 Image Time Series
Earth observation satellites provide data for continuous and extensive flood monitoring, yet limitations exist when using optical images due to cloud cover. Gap-filling methods have been developed for reconstructing cloud-covered areas in water maps. However, the existing methods are not tailored for and validated in cloudy and rainy flooding scenarios with rapid water extent changes and limited clear-sky observations. To overcome these limitations, we developed a novel method for seamless time series flood mapping under varying cloud cover conditions.

**📝Publications:**

Zhiwei Li, Shaofen Xu, Qihao Weng, 2024. Beyond Clouds: Beyond clouds: Seamless flood mapping using Harmonized Landsat and Sentinel-2 time series imagery and water occurrence data. *ISPRS Journal of Photogrammetry and Remote Sensing*, 216, 185-199. [**[PDF]**](https://zhiweili.net/assets/pdf/2020.4_ISPRS%20P&RS_Thick%20cloud%20and%20cloud%20shadow%20removal%20in%20multitemporal%20imagery%20using%20progressively%20spatio-temporal%20patch%20group%20deep%20learning.pdf) [**[Appendix]**](https://zhiweili.net/assets/pdf/2024.10_ISPRS%20P&RS_Seamless%20flood%20mapping_Appendix%20A%20Supplementary%20data.pdf) (Featured in ’**Select Landsat Publications**’ by NASA Landsat Science⭐)

Zhiwei Li, Shaofen Xu, Qihao Weng, 2024. Can we reconstruct cloud-covered flooding areas in harmonized Landsat and Sentinel-2 image time series?, *IEEE* *International Geoscience and Remote Sensing Symposium (IGARSS)*. pp. 3686-3688. Athens, Greece. [**[PDF]**](https://zhiweili.net/assets/pdf/Conference%20Papers/2024_IGARSS_Can%20we%20reconstruct%20cloud-covered%20flooding%20areas%20in%20harmonized%20Landsat%20and%20Sentinel-2%20image%20time%20series.pdf) [**[Poster]**](https://zhiweili.net/assets/pdf/Poster/2024_IGARSS_Poster_Flood%20Mapping_Zhiwei%20Li.pdf)

<img src="https://raw.githubusercontent.com/dr-lizhiwei/SeamlessFloodMapper/main/2024_IGARSS_Poster_Flood Mapping_Preview.png" style="zoom:100%;" />

<br>

**💻Code**:

Source code for seamless time series flood mapping using harmonized Landsat and Sentinel-2 images is available now. 

- The required pretrained model to run the code are available at [[Link]](https://drive.google.com/drive/folders/1c57gKA1L6q0v36gaPfBn0a3XnN1cYjwF?usp=sharing).

- The test data containing only one HLS image is used only for the cloud reconstruction step. Download the full datasets below, which include HLS image time series and cloud masks, to test the whole method introduced in our paper.

Contributors:<br>
Shaofen Xu, xv.sfen@gmail.com, The Hong Kong Polytechnic University<br>
[**Zhiwei Li**](https://zhiweili.net/), dr.lizhiwei@gmail.com, The Hong Kong Polytechnic University<br>
Send an email to Shaofen Xu and copy Dr. Zhiwei Li for any issues with the use of the code and datasets.

<br>

**🗂️Datasets**:

Datasets including HLS image time series and cloud masks over the four study sites are available now. [[Link]](https://drive.google.com/drive/folders/1c57gKA1L6q0v36gaPfBn0a3XnN1cYjwF?usp=sharing)

<img src="https://raw.githubusercontent.com/dr-lizhiwei/SeamlessFloodMapper/main/Datasets_StudyArea.png" style="zoom:100%;" />

<br>





<!--<img src="https://raw.githubusercontent.com/dr-lizhiwei/SeamlessFloodMapper/main/Pakistan_2022_flood.png" style="zoom:50%;" />-->

<!--**Fig. 1.** Example reconstruction results of the proposed method for seamless time series flood extent mapping over Sindh, Pakistan in 2022 flood event.-->

<!--<img src="https://raw.githubusercontent.com/dr-lizhiwei/SeamlessFloodMapper/main/floodwater%26daily%20precipitation.png" style="zoom:50%;" />-->

<!--**Fig. 2.** Comparison of areas of identified floodwater (red bar) with daily precipitation (blue background) over Sindh, Pakistan in 2022 flood event.-->


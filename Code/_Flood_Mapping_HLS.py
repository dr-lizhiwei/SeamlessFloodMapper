                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                on of downloaded HLS data
    """
    TIFF_Segment:output_path of semantic segment results (1: Water, 0: No Water, -1: No data)
    TIFF_Segment_RGB: visualization of semantic segment results
    Cloud_Removal: TIFF image of Initial Water Map  (0: No water, 1: Water, 2: Cloud)
    Cloud_Removal_RGB：RGB image of Initial Water Map 
    Water_Occur_removal: De-cloud Water Occurrence data in preparation for calculating reconstruction thresholds
    """
    config_path = args.config
    ckpt = args.ckpt
    TIFF_Segment = os.path.join(Rootpath, "3_TIFFSegment")
    if args.SemanticSegment:
        inference_on_files(config_path, ckpt, "tif", TIFF_Folder + '\\', TIFF_Segment + '\\', "[0,1,2,3,4,5]")

    Water_Occur_path = args.Water_Occur_path
    Cloud_Removal = os.path.join(Rootpath, "4_CloudRemoval")
    Water_Occur_removal = os.path.join(Rootpath, "5_OccurenceRemoval")
    if args.CloudRemoval:
        create_directory(Cloud_Removal)
        create_directory(Water_Occur_removal)
        cloud_detection(TIFF_Segment, Cloud_Folder, Cloud_Removal, Water_Occur_path, Water_Occur_removal)
    if args.OriginalWaterMap:
        Cloud_Removal_RGB = os.path.join(Cloud_Removal, "RGB")
        create_directory(Cloud_Removal_RGB)
        RGBgrey(Cloud_Removal, Cloud_Removal_RGB)

    # step 3 calculate Rate curve (= Ws&Wo/Wo) and reconstruct water map
    # The first Occurrence value whose Rate>0.35 is used as the threshold for water reconstruction.
    """ 
    Rate_file: Calculate the Rate curve for each image and save all curve to a csv file
    Local_Recons: Reconstructed Water Map(0: Not Water, 1: Water, 3: Reconstructed Water, 10: Reconstructed No Water)
    Local_Recons_RGB : RGB Reconstructed Images
    """
    Rate_file = Cloud_Removal = os.path.join(Rootpath, "Rates_file_Occurrence.csv")
    WR(Water_Occur_removal, Cloud_Removal, Rate_file)

    Local_Recons = os.path.join(Rootpath, "6_WaterRecons")
    Local_Recons_RGB = os.path.join(Local_Recons, "RGB")
    create_directory(Local_Recons)

    if args.WaterReconstruction == 'Global':
        water_reconstruction_Globle_Rate(Cloud_Removal, Water_Occur_removal, Water_Occur_path, Rate_file, Local_Recons)
    if args.WaterReconstruction == 'Local':
        water_reconstruction_Globle_Local(Cloud_Removal, Water_Occur_removal, Water_Occur_path, Rate_file, Local_Recons,
                                          0.35)
    if args.RecnsWaterMap:
        create_directory(Local_Recons_RGB)
        RGBgrey(Local_Recons, Local_Recons_RGB)

    # step 4 spatio-temporal filter & generate Refined Water Map
    # highlight flood inundation areas
    """
    Filter_Path： Refined Water Map (0 No Water 1 reconstructed no water; 3 reconstructed Water 4 water;
                                   7 Refined water;  6 Refined no water)
    Filter_Path_flood: (0：Not Water, 1: Flood, 3,4: Permanent Water)
    Filter_Path_RGB：RGB refined flood map
    """

    Filter_Path = os.path.join(Rootpath, "7_SptlTmprlFilter")
    Filter_Path_flood = os.path.join(Filter_Path, "Flood")
    Filter_Path_RGB = os.path.join(Filter_Path, "RGB")
    create_directory(Filter_Path)
    create_directory(Filter_Path_flood)
    create_directory(Filter_Path_RGB)

    # divide into pre-flood and post-flood
    if args.RefinedWater:
        cnsstncy_filter(Local_Recons, Filter_Path, args.floodDay)
    if args.HightlightFlood:
        period = []
        for file in os.listdir(Local_Recons):
            if file.split('.')[-1] == "tif" and int(file.split('.')[1][4:7]) < args.floodDay:
                period.append(file)
        floodHighlight(Filter_Path, period, Filter_Path_flood, recns=False)
        RGBgrey(Filter_Path_flood, Filter_Path_RGB, flood=True)
    if not args.HightlightFlood:
        RGBgrey(Filter_Path, Filter_Path_RGB, filter=True)


def main():
    # unpack args
    args = parse_args()
    FloodMapping(args)


if __name__ == '__main__':
    main()

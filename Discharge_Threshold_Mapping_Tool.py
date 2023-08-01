# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 17:46:53 2023

@author: pmosh
"""

###############################################################################
#######################################################################
# Final Project: Discharge Threshold Mapping Tool Using Rational Method
#######################################################################
###############################################################################
# Import packages 
import arcpy as ap
import sys


# Define input feature classes and search fields
shapefile=ap.GetParameterAsText(0)
DEM=ap.GetParameterAsText(1)
outDir=ap.GetParameterAsText(2)
discharge=ap.GetParameter(3)
pointRainDepth=ap.GetParameter(4)
stormDuration=ap.GetParameter(5)
stormReturn=ap.GetParameterAsText(6)
soilType1=ap.GetParameterAsText(7)
soilPerc1=ap.GetParameter(8)
soilType2=ap.GetParameterAsText(9)
soilPerc2=ap.GetParameter(10)
soilType3=ap.GetParameterAsText(11)
soilPerc3=ap.GetParameter(12)
landCoverType1=ap.GetParameterAsText(13)
landCoverPerc1=ap.GetParameter(14)
landCoverType2=ap.GetParameterAsText(15)
landCoverPerc2=ap.GetParameter(16)
landCoverType3=ap.GetParameterAsText(17)
landCoverPerc3=ap.GetParameter(18)
landCoverType4=ap.GetParameterAsText(19)
landCoverPerc4=ap.GetParameter(20)
# Establish working environment
ap.env.workspace = outDir
ap.env.overwriteOutput = True

# Define tool prompts
ap.AddMessage("Area of Interest: {}".format(shapefile))
ap.AddMessage("Elevation Data: {}".format(DEM))
ap.AddMessage("Output Location: {}".format(outDir))
ap.AddMessage("Discharge Value of Interest: {}".format(discharge))
ap.AddMessage("Point Rainfall Depth (Inches): {}".format(pointRainDepth))
ap.AddMessage("Storm Duration (Minutes): {}".format(stormDuration))
ap.AddMessage("Storm Return Period: {}".format(stormReturn))
ap.AddMessage("Predominant Soil Type 1: {}".format(soilType1))
ap.AddMessage("Predominant Soil Type 1 Percentage: {}".format(soilPerc1))
ap.AddMessage("Predominant Soil Type 2: {}".format(soilType2))
ap.AddMessage("Predominant Soil Type 2 Percentage: {}".format(soilPerc3))
ap.AddMessage("Predominant Soil Type 3: {}".format(soilType3))
ap.AddMessage("Predominant Soil Type 3 Percentage: {}".format(soilPerc3))
ap.AddMessage("Predominant Land Cover Type 1: {}".format(landCoverType1))
ap.AddMessage("Predominant Land Cover Type 1 Percentage: {}".format(landCoverPerc1))
ap.AddMessage("Predominant Land Cover Type 2: {}".format(landCoverType2))
ap.AddMessage("Predominant Land Cover Type 2 Percentage: {}".format(landCoverPerc2))
ap.AddMessage("Predominant Land Cover Type 3: {}".format(landCoverType3))
ap.AddMessage("Predominant Land Cover Type 3 Percentage: {}".format(landCoverPerc3))
ap.AddMessage("Predominant Land Cover Type 4: {}".format(landCoverType4))
ap.AddMessage("Predominant Land Cover Type 4 Percentage: {}".format(landCoverPerc4))

# Set up try-except error handling for whole tool:
try:
# Rainfall Intensity workflow: calculates rainfall intensity using equation 
# from Mile High Flood District Criteria Manual. User is encouraged in tool 
# prompt to look at their area for appropriate storm duration/point rainfall
# depth for their area of interest. 
    denom = 10.0+stormDuration
    Intensity = (28.5*pointRainDepth)/(pow(denom,0.786))

# Establishes a list of land cover types and their percent coverage to be
# evaluated for calculating the percent imperviousness of the study area. 
    landCoverList=[landCoverType1,
                   landCoverType2,
                   landCoverType3,
                   landCoverType4]
    landCoverPercents=[landCoverPerc1*.01,
                       landCoverPerc2*.01,
                       landCoverPerc3*.01,
                       landCoverPerc4*.01]

# Error Check: verifies that the total user land cover percentage input is 
# equal to 100%. If not, the tool terminates and an error message is thrown
    if sum(landCoverPercents) != 1:
        ap.AddError("Total Land Cover Percentage Doesn't Equal 100%, Tool Has Been Terminated.")
        sys.exit()
    else:
        pass

# Error Check: verifies that there are no duplicate land cover types selected
# by the user. If so, the tool terminates and an error message is thrown
    for x in landCoverList:
        index = landCoverList.index(x)
        del landCoverList[index]
        if x in landCoverList:
            ap.AddError("Duplicate Land Cover Types Detected, Script Has Been Terminated.")
            sys.exit() 
        else:
            pass
        landCoverList.insert(index, x)


# Creates a land cover/percent impervious dictionary based on table 6-3 from 
# the Mile High Flood District criteria manual.
    landcoverPercImpervDictionary = {'Downtown Areas':.95,
                                     'Suburban Areas':.75,
                                     'Single-family (2.5 acre or larger lots)':.12,
                                     'Single-family (0.75-2.5 acre lots)':.20,
                                     'Single-family (0.25-0.75 acre lots)':.30,
                                     'Single-family (0.25 acre or less lots)':.45,
                                     'Apartments':.75,
                                     'Light Industrial Area':.80,
                                     'Heavy Industrial Area':.90,
                                     'Park Land':.10,
                                     'Playgrounds':.25,
                                     'Schools':.55,
                                     'Railroad Yard Area':.50,
                                     'Undeveloped historic flowpath':.02,
                                     'Greenbelts, Agricultural':.02,
                                     'Undefined Land Use Type':.45,
                                     'Paved Road':1,
                                     'Packed Gravel Road':.45,
                                     'Driveway/Paved Walkway':.9,
                                     'Roof':.9,
                                     'Lawn, Sandy Soil':.02,
                                     'Lawn, Clayey Soil':.02}
# For loop extracts the percent impervious value from the landcover/imperviousness 
# dictionary given the user input land cover type. The results are multiplied
# and appended to a weighted percent imperviousness list and then summed to get a 
# final area weighted percent imperviousness value for the study area.       
    weightedImpervious=[]
    for LC in landCoverList:
        i = landcoverPercImpervDictionary[LC]
        weightedImpervious.append(i*landCoverPercents[landCoverList.index(LC)])
    finalImperviousness=sum(weightedImpervious)
    
# Creates a nested dictionary based off of table 6-4 from the Mile High Flood
# District criteria manual. The nested dictionary relates soil type, storm 
# return period, and corresponding runoff coefficient calculation. The dictionary
# utilizes the previously calculated final percent imperviousness       
    RunoffCoeffDictionary ={'A':{'2-year':0.84*pow(finalImperviousness,1.302),
                                 '5-year':0.86*pow(finalImperviousness,1.276),
                                 '10-year':0.87*pow(finalImperviousness,1.232),
                                 '25-year':0.88*pow(finalImperviousness,1.124),
                                 '50-year':0.85*(finalImperviousness)+0.025,
                                 '100-year':0.78*(finalImperviousness)+0.110,
                                 '500-year':0.65*(finalImperviousness)+0.254},
                            'B':{'2-year':0.84*pow(finalImperviousness,1.169),
                                 '5-year':0.86*pow(finalImperviousness,1.088),
                                 '10-year':0.81*(finalImperviousness)+0.057,
                                 '25-year':0.63*(finalImperviousness)+0.249,
                                 '50-year':0.56*(finalImperviousness)+0.328,
                                 '100-year':0.47*(finalImperviousness)+0.426,
                                 '500-year':0.37*(finalImperviousness)+0.536},
                            'C/D':{'2-year':0.83*pow(finalImperviousness,1.122),
                                   '5-year':0.82*(finalImperviousness)+0.035,
                                   '10-year':0.74*(finalImperviousness)+0.132,
                                   '25-year':0.56*(finalImperviousness)+0.319,
                                   '50-year':0.49*(finalImperviousness)+0.393,
                                   '100-year':0.41*(finalImperviousness)+0.484,
                                   '500-year':0.32*(finalImperviousness)+0.588}}

# Establishes a list of soil types and percentages to be evaluated for 
# calculating the runoff coefficient. 
    soilTypeList=[soilType1,
                  soilType2,
                  soilType3]
    soilTypePercents=[soilPerc1*.01,
                      soilPerc2*.01,
                      soilPerc3*.01]

# Error Check: verifies that the total user soil type percentage input is 
# equal to 100%. If not, the tool terminates and an error message is thrown
    if sum(soilTypePercents) != 1:
        ap.AddError("Total Soil Type Percentage Doesn't Equal 100%, Tool Has Been Terminated")
        sys.exit() 
    else:
        pass

# Error Check: verifies that there are no duplicate soil types selected
# by the user. If so, the tool terminates and an error message is thrown
    for x in soilTypeList:
        index = soilTypeList.index(x)
        del soilTypeList[index]
        if x in soilTypeList:
            ap.AddError("Duplicate Soil Types Detected, Script Has Been Terminated.")
            sys.exit() 
        else:
            pass
        soilTypeList.insert(index, x)
    weightedRC=[]
    for soilType in soilTypeList:
        rc = RunoffCoeffDictionary[soilType][stormReturn]
        weightedRC.append(rc*soilTypePercents[soilTypeList.index(soilType)])    
    finalRC = sum(weightedRC)

# Calculate flow accumulation threshold value, note that the additional 
# multiplications/divisions tacked onto the end of the 
# threshold calculation area applied to assure the correct units are obtained:
#
# Threshold needs to be in Acres while discharge divided by runoff coefficient
# and Intensity give the the following units: ((ft**3)(hr))/((sec)(inch)).
# To convert units:
# 1) Multiply by 12 to convert inches to feet, gives ((ft**2)(hr))/(sec).
# 2) Multiply by 3600 seconds in an hour to get ft**2.
# 3) Divide by 43560 ft**2 in an acre to get acres
# 4) lastly, multiply by 4 to take into account the 2x2 foot cell size of the 
#    DEM.

    threshold=(discharge/(finalRC*Intensity))*(12)*(3600)*(1/43560)*(4)
    ap.AddMessage("Calculated Threshold values: {}".format(threshold))
# Workflow for Discharge Exceedence Area:
#   1) Extract by mask DEM using input shapefile to get DEM of area of interest
#   2) Fill DEM to prevent sinks from under estimating flow accumulation
#   3) Create flow direction raster to be used in flow accumulation
#   4) Run flow accumulation tool and extract cells that exceed the threshold 
#      value
#   5) Select and save portions of the flow accumulation polygon that exceed 
#      the threshold. The shapefile "DischargeExceedanceAreas.shp" is the final
#      result. 
    maskedDEM=ap.sa.ExtractByMask(DEM,shapefile)
    fillDEM=ap.sa.Fill(maskedDEM)
    flowDir=ap.sa.FlowDirection(fillDEM,'','','D8')
    flowAcc=ap.sa.FlowAccumulation(flowDir,
                                   '','INTEGER','D8')
    threshFlowAcc=ap.sa.ExtractByAttributes(flowAcc,'VALUE > '+str(threshold))
    ap.conversion.RasterToPolygon(threshFlowAcc,'DischargeExceedanceAreas.shp','SIMPLIFY',
                                  'VALUE','SINGLE_OUTER_PART')
except:
    ap.GetMessages()





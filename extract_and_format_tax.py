import os
import zipfile
import pandas as pd
import numpy as np
import geopandas as gp
import shapely as sh
import fiona

dataFile = ['university_of_michigan_hatcher_library_hist_property_basic1_300000403632468_05_20220624_154500_data.zip']   

dataFileIndex = 0
count = 1
sampleList = []
with zipfile.ZipFile(dataFile[dataFileIndex], 'r') as z:            
    fileList = z.infolist()
    with z.open(fileList[0], 'r') as f:
        for line in f:
            line = line.decode(encoding='utf-8', errors='strict')
            intermediary_object=line.strip().split("|")
            sampleList.append(intermediary_object)
            count=count+1
            if count==10:
               break

#Display sample records 
df1 = pd.DataFrame(sampleList[1:9], columns = sampleList[0]) 
pd.set_option('display.max_columns', None)
df1

def searchField(fieldString):
    strIndex = [i for i in sampleList[0] if fieldString in i.lower()] 
    indexLat = [sampleList[0].index(i) for i in strIndex]
    print((strIndex,indexLat))


fieldNameStr = ['original apn', 'fips code', 'situs zip code', 
                'total value calculated', 'property indicator code']

indexList = [searchField(i) for i in fieldNameStr]



FIPS_CODE_CUYAHOGA = '39035'

def process_line(line):
    try:
        line = line.decode(encoding='utf-8', errors='strict')
    except UnicodeDecodeError:
        line = line.decode(encoding='utf-8', errors='replace')  # Adjust error handling here
    line = line.strip().replace('|', ',')
    line = line.split(',')
    line = ['NA' if x == '' else x for x in line]
    return line


with open("output_2022_tax.csv", 'w') as resultFile:
    resultFile.write(
        'fips code [2], situs zip code [59], total value calculated [112], property indicator code [39]'
    )

with open("output_2022_tax.csv", 'a') as resultFile:
    with zipfile.ZipFile(dataFile[dataFileIndex], 'r') as z:
        fileList = z.infolist()
        with z.open(fileList[0], 'r') as f:
            for _ in range(1):  # Skip header
                next(f)
            for line in f:
                line = process_line(line)
                if line[2][:5] == FIPS_CODE_CUYAHOGA and (line[39][:2] == '10' or line[39][:2] == '11' or line[39][:2] == '21' or line[39][:2] == '22'):
                    relevantData = [line[2]] + [line[59][:5]] + [line[112]] + [line[39]]
                    relevantData = ','.join(relevantData)
                    resultFile.write(relevantData)
                    resultFile.write('\n')



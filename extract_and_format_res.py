import os
import zipfile
import pandas as pd
import numpy as np
import geopandas as gp
import shapely as sh
import fiona
import csv

dataFile = ['university_of_michigan_hatcher_library_ownertransfer_v3_300000403632475_20220624_100835_data.zip']   

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

print(sampleList[0])
print('THERE ARE %d FIELDS' % len(sampleList[0]))

#Display sample records 
df1 = pd.DataFrame(sampleList[1:9], columns = sampleList[0]) 
pd.set_option('display.max_columns', None)

# Create a function to search field strings 
def searchField(fieldString):
    strIndex = [i for i in sampleList[0] if fieldString in i.lower()] 
    indexLat = [sampleList[0].index(i) for i in strIndex]
    print((strIndex,indexLat))


fieldNameStr = ['original apn', 'fips code', 'deed situs zip code - static', 
                'sale derived date', 'sale derived recording date', 'sale amount', 
                'transaction batch date', 'property indicator code - static',
                'cash purchase indicator', 'mortgage purchase indicator',
                'investor purchase indicator', 'residential indicator',
                'buyer 1 full name', 'buyer 2 full name', 
                'buyer 3 full name', 'buyer 4 full name', 'corporate indicator',
                'foreclosure reo indicator', 'foreclosure reo sale indicator',
                'interfamily related indicator']

indexList = [searchField(i) for i in fieldNameStr]

#indexList = [searchField(i) for i in sampleList[0]]

FIPS_CODE_CUYAHOGA = '39035'


def process_line(line):
    try:
        line = line.decode(encoding='utf-8', errors='strict')
    except UnicodeDecodeError:
        line = line.decode(encoding='utf-8', errors='replace')
    line = line.strip().replace('|', ',')
    line = line.split(',')
    line = ['NA' if x == '' else x for x in line]
    return line


def is_valid_year(date_str):
    try:
        return int(date_str[:4]) >= 2000
    except (ValueError, TypeError):
        return False


#Open the result file to write results
with open("output_2022.csv", 'w') as resultFile:
    resultFile.write(
         'original apn [6], fips code [2],transaction fips code [33],deed situs zip code - static [28],' 
         'sale derived date [43],sale derived recording date [44],sale amount [42],transaction batch date [35],'
         'property indicator code - static [14],cash purchase indicator [52],mortgage purchase indicator [53],'
         'investor purchase indicator [55],residential indicator [58],'
         'buyer 1 full name [62],buyer 1 last name [63],buyer 1 firt name and middle initial [64],'
         'buyer 2 full name [65],buyer 2 last name [66],buyer 2 firt name and middle initial [67],'
         'buyer 3 full name [70],buyer 3 last name [71],buyer 4 firt name and middle initial [72],'
         'buyer 4 full name [74],buyer 1 last name [75],buyer 1 firt name and middle initial [76],'
         'buyer 1 corporate indicator [68],buyer 2 corporate indicator [69],'
         'buyer 3 corporate indicator [73],buyer 4 corporate indicator [77],' 
         'foreclosure reo indicator [60],foreclosure reo sale indicator [61],' 
         'interfamily related indicator [54],buyer occupancy code [82],'
        )

#Open the input file to read data
with open("output_2022.csv", 'a') as resultFile:
    with zipfile.ZipFile(dataFile[dataFileIndex], 'r') as z:
        fileList = z.infolist()
        with z.open(fileList[0], 'r') as f:
            for _ in range(1):  # Skip header
                next(f)
            for line in f:
                line = process_line(line)
                if line[2][:5] == FIPS_CODE_CUYAHOGA or line[33][:5] == FIPS_CODE_CUYAHOGA:
                    #Check for valid years
                    date1_valid = line[43] != 'NA' and is_valid_year(line[43])
                    date2_valid = line[44] != 'NA' and is_valid_year(line[44])
                    
                    if date1_valid or date2_valid:
                        
                        relevantData = [line[6]] + [line[2]] + [line[33]] + [line[28]] + line[43:45] + [line[42]] + [line[35]] \
                                        + [line[14]] + line[52:54] + [line[55]] + [line[58]] \
                                        + line[62:68] + line[70:73] + line[74:77] \
                                        + line[68:70] + [line[73]] + [line[77]] \
                                        + line[60:62] + [line[54]] + [line[82]]

                        relevantData = ','.join(relevantData)
                        resultFile.write(relevantData)
                        resultFile.write('\n')
import sys
import csv
import os
import glob

def printUsage():
    print(sys.argv[0] + ' Usage\n')
    print('\t-bizDir businessReportPath ')
    print('\t-popFile populationMappingFile (zip,population) ')
    print('\t-o outputFilePath (omit for stdout) ')
    print('\t-state stateToUse (omit to use all data available) ')

def main():

    bizDirFilename = ''
    popFilename = ''
    outputFilename = ''
    writeToFile = False

    stateToUse = ''
    filterByState = False;

    if '-bizDir' in sys.argv:
        bizDirFilename = sys.argv[sys.argv.index('-bizDir') + 1]
    else:
        printUsage()
        sys.exit('Need bizDir filename.')

    if '-popFile' in sys.argv:
        popFilename = sys.argv[sys.argv.index('-popFile') + 1]
    else:
        printUsage()
        sys.exit('Need population data filename.')

    if '-o' in sys.argv:
        outputFilename = sys.argv[sys.argv.index('-o') + 1]
        writeToFile = True

    if '-state' in sys.argv:
        stateToUse = sys.argv[sys.argv.index('-state') + 1]
        filterByState = True

    print('Using biz data from: ' + bizDirFilename)

    bizData = processBizData(bizDirFilename, filterByState, stateToUse)

    zipToPopMap = loadPopulationData(popFilename)

    lines = assembleOutput(bizData, zipToPopMap)

    if(writeToFile):
        writeLinesToFile(outputFilename, lines)
    else:
        print(lines)

def loadPopulationData(populationFilename):
    #Zip Code ZCTA
    #2010 Census Population

    zipToPopMap = {}

    with open(populationFilename) as csvfile:
        popReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in popReader:
            zipToPopMap[row['Zip Code ZCTA']] = row['2010 Census Population']

    return zipToPopMap

def writeLinesToFile(filename, lines):
    outputFile = open(filename,'w')

    for line in lines:
        outputFile.write(line + '\n')

    outputFile.close()

def assembleOutput(bizData, zipToPopMap):

    lines = ['zip,newBusinessCount,exampleCity,2010 Census Population,Biz to Pop Ratio']

    for k, v in bizData['zipBusinessCountMap'].items():

        popCount = 0;

        if(k in zipToPopMap):
            popCount = int(zipToPopMap[k])

        popToBusRatio = 0

        if(popCount > 0):
            popToBusRatio = round(int(v) / popCount, 4)

        lines.append(str(k) + "," + str(v) + "," + str(bizData['zipToCityMap'][k]) + "," + str(popCount) + "," + str(popToBusRatio))

    return lines

def processBizData(bizDirFilename, filterByState = False, stateToUse = ''):

    bizSummary = {}
    zipToCity = {}

    for filename in glob.glob(os.path.join(bizDirFilename, '*.csv')):
        with open(filename) as csvfile:
            print('Filename: ' + filename)
            bizReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in bizReader:

                #Filters
                if(row['Associated Name Type'].strip() == 'PRINCIPAL PLACE OF BUSINESS'
                    and ( not filterByState or row['State'] == stateToUse)):

                    print(row['Business Name'])

                    #keep the last one
                    zipToCity[row['Zip Code']] = row['City']

                    if(row['Zip Code'] in bizSummary):
                        bizSummary[row['Zip Code']] = bizSummary[row['Zip Code']] + 1;
                    else:
                        bizSummary[row['Zip Code']] = 1

    return {
        'zipBusinessCountMap': bizSummary,
        'zipToCityMap': zipToCity
    }

if __name__== "__main__":
    main()

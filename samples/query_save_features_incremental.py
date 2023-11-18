"""
   This sample shows how to query a layer based on a sql expression
   and retrieve features since the last run of this model.  It is designed
   to be scheduled to run and get incremental updates.  A date field that is
   tracking the changes is required.  A file is created that stores the last
   run time.  This value is appened to the query.  The results can be saved
   as csv, json, or a feature class.  A sample is include to show how to loop
   through the results in case you want to add logic to handle them in the 
   same scripts

   Python 2.x/3.x
   ArcREST 3.5.4
"""
from __future__ import print_function
import arcrest

import csv
import datetime
import os
import arcresthelper
from arcresthelper import common
from arcresthelper import featureservicetools

def validate(date_text,dateTimeFormat):
    try:
        datetime.datetime.strptime(date_text, dateTimeFormat)
        return True
    except ValueError:
        return False
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    import traceback, inspect, sys
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile(inspect.currentframe())
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def main():
    #Path and name of file to store log
    logFile = r"c:\temp\log.log"
    logFile = common.init_log(logFile)
    try:
        proxy_port = None
        proxy_url = None

        securityinfo = {
            'security_type': 'Portal',
            'username': "",
            'password': "",
            'org_url': "http://www.arcgis.com",
            'proxy_url': proxy_url,
            'proxy_port': proxy_port,
            'referer_url': None,
            'token_url': None,
            'certificatefile': None,
            'keyfile': None,
            'client_id': None,
            'secret_id': None,
        }
        #Date time format of the service, example'2016-04-26 04:00:00'
        dateTimeFormat = "%Y/%m/%d %H:%M:%S"
        #log file to store details

        print ("###### Date Extraction Process Started ######")
        print ("\tStarted at {0}".format(datetime.datetime.now().strftime(dateTimeFormat)))

        fst = featureservicetools.featureservicetools(securityinfo)

        """Settings"""
        #URL to service
        url = ''#url to feature layer, make sure it ends in \layer number 

        #Base sql expression to find features of a type
        sql = "1=1"

        #Fields to save to the output CSV, format Field1,Field2,...
        out_fields ='OBJECTID,GIS_ID,Nickname'

        """The location and file name to save the results to"""
        #File with the date of the last run, if it does not exist, all features are returned and file is created for next run
        lastRunDetails = r"c:\temp\lastrundate.txt"

        lastQueryDate = None

        #Open the file with the last run date
        if os.path.isfile(lastRunDetails):
            print("\tLast run file exist")
            with open(lastRunDetails, 'r') as configFile:
                lastQueryDate = configFile.read()
                configFile.close()
            print("\t\tLast query date: {0}".format(lastQueryDate))

        #If the last query date file was found and value is a date
        queryDate = datetime.datetime.now().strftime(dateTimeFormat)
        if lastQueryDate is not None and validate(date_text=lastQueryDate, dateTimeFormat=dateTimeFormat):
            #Field used to restrict query to only records since last query
            statusUpdateField = 'Laststatusupdate'
            sql = f"{sql} AND {statusUpdateField} >= '{lastQueryDate}'"
            #Add current time to query
            sql = f"{sql} AND {statusUpdateField} <= '{queryDate}'"

        print("\tSQL: {0}".format(sql))

        #query the layer
        featureSet  = fst.QueryAllFeatures(url=url,
                            where=sql,
                            out_fields=out_fields,
                            chunksize=300,
                            printIndent="\t")
        if (isinstance(featureSet,arcrest.common.general.FeatureSet)):
            if len(featureSet.features) == 0:
                print ("\tNo features matching the query where found")
            else:
                print("\t{0} feature(s) returned".format(len(featureSet.features)))
                #Option are a folder or a GDB
                outputLocation = r"c:\temp"

                #Output filename
                #  Options:
                #    *.csv - output is a csv file, outputLocation must be a folder
                #    *.json - output is a json text file, outputLocation must be a folder
                #    * - output is a Shapefile or GDB featureclass depending on outputLocation
                outputFileName = "results.csv" 

                #Create a new output writer
                saveLocation = os.path.join(outputLocation, outputFileName)
                if (len(featureSet.features) == 0):
                    if os.path.isfile(saveLocation):
                        os.remove(saveLocation)
                else:
                    #Save the results to a file
                    result = featureSet.save(saveLocation=outputLocation, outName=outputFileName)
                    print ("\t{0} created".format(result))
                    """
                    If you want to process the results of the query without saving to a file
                    uncomment the process below and add your code.  The example below loops
                    through each field in a feature in a featureset.
                    
                    """
                    #for feature in featureSet:
                        #print ("\t----------------------")
                        #for field in featureSet.fields:
                            #print ("\t\tField Name: {0} | Field Value: {1}".format(field['name'],feature.get_value(field['name'])))
                        #print ("\t######################")
        else:
            print ("\tNo features matching the query where found")

        #Update the last run file
        with open(lastRunDetails, 'w') as configFile:
            configFile.write(queryDate)
            configFile.close()
            print("\t{0} saved to last run file".format(queryDate))
        print ("\tCompleted at {0}".format(datetime.datetime.now().strftime(dateTimeFormat)))
        print ("###### Completed ######")
    except common.ArcRestHelperError as e:
        print(f"error in function: {e[0]['function']}")
        print(f"error on line: {e[0]['line']}")
        print(f"error in file name: {e[0]['filename']}")
        print(f"with error message: {e[0]['synerror']}")
        if 'arcpyError' in e[0]:
            print(f"with arcpy message: {e[0]['arcpyError']}")
    except:
        line, filename, synerror = trace()
        print(f"error on line: {line}")
        print(f"error in file name: {filename}")
        print(f"with error message: {synerror}")
    finally:
        if (logFile):
            common.close_log(logFile)
if __name__ == "__main__":
    main()
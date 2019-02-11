import json, requests, time, datetime, sys, getopt, csv
from datetime import datetime, timedelta


# Usage
# python3 client-ap-report.py --endpoint https://https://domain.nyansa.com/api/v2/graphql --apikey <API_Key> --numHours 24 --jsonoutput output.json --csvoutput output.csv 

# if on OnPrem please disable SSL-Validation with:
# --validation false (only if on onprem)


# -------------------------------------------------------------
# Start
# -------------------------------------------------------------
def start(argv):
    try:
        endpoint = ''
        apikey = ''
        jsonoutput = ''
        csvoutput= ''
        numDays = ''
        validation = True
        try:
            if (argv == []):
                print('client-ap-report.py -e <endpoint> -a <apikey> -n <numHours> -j <jsonoutput> -c <csvoutput>')
                sys.exit(2)

            opts, args = getopt.getopt(argv,"he:a:s:t:n:j:c:v:",["endpoint=","apikey=","numHours=","jsonoutput=","csvoutput=","validation="])
        except getopt.GetoptError:
            print('client-ap-report.py -e <endpoint> -a <apikey> -n <numHours> -j <jsonoutput> -c <csvoutput>')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-j", "--jsonoutput"):
                jsonoutput = arg
            elif opt in ("-c", "--csvoutput"):
                csvoutput = arg
            elif opt in ("-e", "--endpoint"):
                endpoint = arg
            elif opt in ("-a", "--apikey"):
                apikey = arg
            elif opt in ("-n", "--numHours"):
                numHours = arg
            elif opt in ("-v", "--validation"):
                if (arg == "0" or arg == "False" or arg == "false"):
                    requests.packages.urllib3.disable_warnings()
                    validation = False
   
        # create report
        print (jsonoutput)
        print (csvoutput)
        get_ap_macaddr2name_mapping(endpoint, apikey, numHours, validation)
        get_device_list(endpoint, apikey, jsonoutput, csvoutput, numHours, validation)

    except:
        print("")

# -------------------------------------------------------------
# Device List
# -------------------------------------------------------------
query = { "query": "{ deviceList (sortBy:\"macAddr\", fromDate:\"<<DATE>>\", pageSize:500, page:<<PAGENUMBER>> ) { page pageSize pageCount totalCount devices { ipAddress macAddr description hostname userName deviceTypeDetails { osAndVersion deviceClass model }relatedAttributes(name: \"apMacAddr\") { name value timestamp } } } }" }
apQuery = { "query": "{ accessPointList (sortBy:\"macAddr\", fromDate:\"<<DATE>>\", pageSize:500, page:<<PAGENUMBER>>) { pageSize pageCount totalCount accessPoints { description macAddr } } }" }
apNamelist = {}
result = []
devicesAnalyzed = 0
devicesFound = 0

def get_ap_macaddr2name_mapping(endpoint, apikey, numHours, validation):
    try:
        current_datetime = datetime.now()
        date_today = current_datetime.date()
        fromDate = date_today - timedelta(days=14)
        apQuery["query"] = apQuery["query"].replace("<<DATE>>", str(fromDate))    
        fetch(endpoint, apikey, "accessPointList", "accessPoints", apQuery, numHours, validation)
        
    except Exception as e: 
        print("get_ap_macaddr2name_mapping:", e)

def get_device_list(endpoint, apikey, jsonoutput, csvoutput, numHours, validation):
    try:
        current_datetime = datetime.now()
        date_today = current_datetime.date()
        fromDate = date_today - timedelta(days=14)
        print ("From Date: ", fromDate)
        query["query"] = query["query"].replace("<<DATE>>", str(fromDate))

        current_datetime = datetime.now()
        current_datetimeutc = datetime.utcnow()
        numHoursInt=int(numHours)
        fromTime =  current_datetime - timedelta(hours=numHoursInt)
        fromTimeutc = current_datetimeutc - timedelta(hours=numHoursInt)
        print ("Report From ", fromTime, "To", current_datetime)
        print ("Report From ", fromTimeutc, "(UTC) To", current_datetimeutc,"UTC")
        
        fetch(endpoint, apikey, "deviceList", "devices", query, numHours, validation)
        save_textfile(jsonoutput, json.dumps(result, sort_keys=False, indent=4))
        inputFile = open(jsonoutput) #open json file
        outputFile = open(csvoutput, 'w') #load csv file
        data = json.load(inputFile) #load json content
        inputFile.close() #close the input file
        output = csv.writer(outputFile) #create a csv.write
        output.writerow(data[0].keys())  # header row
        numRows=0
        for row in data:
            output.writerow(row.values()) #values row
        print ("Total Devices Analyzed: ", devicesAnalyzed)
    except Exception as e: 
        print("get_device_list:", e)

def process_ap_data(data, fieldname):
    try:
            global apNamelist

            for accessPoint in data:
                apNamelist[accessPoint["macAddr"]]= accessPoint["description"]
            
    except Exception as e: 
        print("process_ap_data:", e)

def agg_device_data(data, fieldname, numHours):
    try:
            current_datetime = datetime.utcnow()
            numHoursInt=int(numHours)
            fromTime =  current_datetime - timedelta(hours=numHoursInt)
            formattedfromTime = fromTime.isoformat()

            global devicesAnalyzed
            global devicesFound
            
            for client in data:
                if (client != None):
                    devicesAnalyzed = devicesAnalyzed + 1
                    apJoinedlist = []
                    timestamp = []
                    osAndVersion = ''
                    deviceClass = ''
                    model = ''
                    if (client["deviceTypeDetails"] != None):
                        osAndVersion = client["deviceTypeDetails"]["osAndVersion"]
                        deviceClass = client["deviceTypeDetails"]["deviceClass"]
                        model = client["deviceTypeDetails"]["model"]
                    for apJoined in client["relatedAttributes"]:
                        if (apJoined["timestamp"] > str(formattedfromTime)):
                            apJoinedlist.append(apNamelist[apJoined["value"]])
                            timestamp.append(apJoined["timestamp"])
                    if (len(apJoinedlist) > 0):
                        result.append({ "ipAddress": client["ipAddress"], "macAddr": client["macAddr"], "description": client["description"], "userName": client["userName"], "hostname": client["hostname"], "osAndVersion": osAndVersion, "deviceType": deviceClass, "model": model, "APs" : apJoinedlist, "Timestamps" : timestamp })
    except Exception as e: 
        print("agg_device_data:", e)

# -------------------------------------------------------------
# Fetcher
# -------------------------------------------------------------
def fetch(endpoint, apikey, fieldname, listname, query, numHours, validation):
    try:
        query_temp = query.copy()
        query_temp["query"] = query_temp["query"].replace("<<PAGENUMBER>>", str(1))
        response = requests.post(endpoint, headers={'api-token': apikey}, data=query_temp, verify=validation)
        if (response.status_code == 200):
            if ("data" in response.text):
                if (fieldname in response.text):
                    response = json.loads(response.text)["data"][fieldname]
                    pageCount = response["pageCount"]
                    for page in range(1, pageCount+1):
                        query_temp = query.copy()
                        query_temp["query"] = query_temp["query"].replace("<<PAGENUMBER>>", str(page))
                        response = fetch_page(endpoint, apikey, fieldname, listname, query_temp, page, validation)
                        if (len(response) > 0):
                            print(fieldname, "page", page, "of", pageCount)
                            if (fieldname == "deviceList"):
                                agg_device_data(response, fieldname, numHours)
                            elif (fieldname == "accessPointList"):
                                process_ap_data(response, fieldname)
        else:
            print(fieldname, "fetch:", response.status_code)
            print(fieldname, "fetch:", response.reason)
    except Exception as e: 
        print(fieldname, "fetch:", e)

def fetch_page(endpoint, apikey, fieldname, listname, query, page, validation):
    try:
        response = requests.post(endpoint, headers={'api-token': apikey}, data=query, verify=validation)
        if(response.status_code == 200):
            if ("data" in response.text):
                if (fieldname in response.text):
                    response = json.loads(response.text)["data"][fieldname]
                    return response[listname]
        else:
            print(fieldname, "fetch_page:", response.status_code)
            print(fieldname, "fetch_page:", response.reason)
    except Exception as e: 
        print(fieldname, "fetch_page:", e)
    return []

# -------------------------------------------------------------
# helper
# -------------------------------------------------------------
def save_textfile(_filename, _filecontent):
    with open(_filename, "w") as outfile:
        print(_filecontent, file=outfile)

# -------------------------------------------------------------
# entry point
# -------------------------------------------------------------
start(sys.argv[1:])

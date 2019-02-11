import json, requests, time, datetime, sys, getopt, csv
from datetime import datetime, timedelta

# Usage
# python3 ap-suspicious-rogue.py --endpoint https://https://domain.nyansa.com/api/v2/graphql --apikey <API_Key> --jsonoutput output.json --csvoutput output.csv

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
        validation = True
        try:
            if (argv == []):
                print('ap-suspicious-rogue.py -e <endpoint> -a <apikey> -j <jsonoutput> -c <csvoutput>')
                sys.exit(2)

            opts, args = getopt.getopt(argv,"he:a:j:c:v:",["endpoint=","apikey=","jsonoutput=","csvoutput=","validation="])
        except getopt.GetoptError:
            print('ap-suspicious-rogue.py -e <endpoint> -a <apikey> -n <numHours> -j <jsonoutput> -c <csvoutput>')
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
            elif opt in ("-v", "--validation"):
                if (arg == "0" or arg == "False" or arg == "false"):
                    requests.packages.urllib3.disable_warnings()
                    validation = False
   
        # create report
        get_suspicious_rogues(endpoint, apikey, jsonoutput, csvoutput, validation)

    except:
        print("")

# -------------------------------------------------------------
# Neighbor List
# -------------------------------------------------------------
query = { "query": "{ accessPointList (sortBy:\"macAddr\", fromDate:\"<<DATE>>\", pageSize:500, page:<<PAGENUMBER>>) { pageSize pageCount totalCount accessPoints { macAddr apName apModel apRadios { radioChannel rfBand radioNumber essids rogueList { bssidMacAddr essid snrDb} } } } }" }
result = []
devicesAnalyzed = 0

def get_suspicious_rogues(endpoint, apikey, jsonoutput, csvoutput, validation):
    try:
        current_datetime = datetime.now()
        date_today = current_datetime.date()
        fromDate = date_today - timedelta(days=14)
        print ("From Date: ", fromDate)
        query["query"] = query["query"].replace("<<DATE>>", str(fromDate))
        fetch(endpoint, apikey, "accessPointList", "accessPoints", query, validation)
        print ("Total APs Analyzed: ", devicesAnalyzed)
        if (len(result)):
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
            print ("Suspicious rogues FOUND")
        else:
            print ("Suspicious rogues NOT FOUND")
    except Exception as e: 
        print("get_suspicious_rogues:", e)

def agg_rogue_data(data, fieldname):
    try:
        apNamelist = {}
        for accessPoint in data:
            apNamelist[accessPoint["macAddr"]]= accessPoint["apName"]

        global devicesAnalyzed
                    
        for accessPoint in data:
            devicesAnalyzed = devicesAnalyzed + 1
            for apRadio in accessPoint["apRadios"]:
                if (apRadio != None):
                    for rogue in apRadio["rogueList"]:
                        if (rogue != None):
                            suspiciousRogue = False
                            overlappingSSID = []
                            for apSSID in apRadio["essids"]:
                                if (apSSID == rogue["essid"]):
                                    suspiciousRogue = True
                                    overlappingSSID.append(apSSID)
                            if (suspiciousRogue == True):
                                result.append({ "apName": accessPoint["apName"], "radioNumber": apRadio["radioNumber"], "rfBand": apRadio["rfBand"], "radioChannel": apRadio["radioChannel"], "rogueMacAddr": rogue["bssidMacAddr"], "roguesnrDB": rogue["snrDb"], "overlappingSSID": overlappingSSID})
    except Exception as e: 
        print("agg_rogue_data:", e)

# -------------------------------------------------------------
# Fetcher
# -------------------------------------------------------------
def fetch(endpoint, apikey, fieldname, listname, query, validation):
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
                        print (query_temp)
                        response = fetch_page(endpoint, apikey, fieldname, listname, query_temp, page, validation)
                        if (len(response) > 0):
                            print(fieldname, "page", page, "of", pageCount)
                            agg_rogue_data(response, fieldname)
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

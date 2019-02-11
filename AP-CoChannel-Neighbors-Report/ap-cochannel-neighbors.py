import json, requests, time, datetime, sys, getopt, csv
from datetime import datetime, timedelta

# Usage
# python3 ap-cochannel-neighbors.py --endpoint https://https://domain.nyansa.com/api/v2/graphql --apikey <API_Key> --jsonoutput output.json --csvoutput output.csv

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
                print('ap-cochannel-neighbors.py -e <endpoint> -a <apikey> -j <jsonoutput> -c <csvoutput>')
                sys.exit(2)

            opts, args = getopt.getopt(argv,"he:a:j:c:v:",["endpoint=","apikey=","jsonoutput=","csvoutput=","validation="])
        except getopt.GetoptError:
            print('ap-cochannel-neighbors.py -e <endpoint> -a <apikey> -n <numHours> -j <jsonoutput> -c <csvoutput>')
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
        get_cochannel_neighbors(endpoint, apikey, jsonoutput, csvoutput, validation)

    except:
        print("")

# -------------------------------------------------------------
# Neighbor List
# -------------------------------------------------------------
query = { "query": "{ accessPointList (sortBy:\"macAddr\", fromDate:\"<<DATE>>\", pageSize:500, page:<<PAGENUMBER>>) { pageSize pageCount totalCount accessPoints { macAddr apName apModel apRadios { radioChannel rfBand radioNumber neighborList { apMacAddr channel snrDb} } } } }" }
result = []
devicesAnalyzed = 0

def get_cochannel_neighbors(endpoint, apikey, jsonoutput, csvoutput, validation):
    try:
        current_datetime = datetime.now()
        date_today = current_datetime.date()
        fromDate = date_today - timedelta(days=14)
        print ("From Date: ", fromDate)
        query["query"] = query["query"].replace("<<DATE>>", str(fromDate))
        
        fetch(endpoint, apikey, "accessPointList", "accessPoints", query, validation)
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
        print ("Total APs Analyzed: ", devicesAnalyzed)
    except Exception as e: 
        print("get_cochannel_neighbors:", e)

def agg_neighbor_data(data, fieldname):
    try:
        apNamelist = {}
        for accessPoint in data:
            apNamelist[accessPoint["macAddr"]]= accessPoint["apName"]

        global devicesAnalyzed
                    
        for accessPoint in data:
            devicesAnalyzed = devicesAnalyzed + 1
            for apRadio in accessPoint["apRadios"]:
                coChannelneighbors = []
                for neighbor in apRadio["neighborList"]:
                    if (neighbor["channel"] == apRadio["radioChannel"]):
                        if (apNamelist[neighbor["apMacAddr"]]):
                            apName = apNamelist[neighbor["apMacAddr"]] 
                        else:
                            apName = " "
                            print ("apName is NULL", neighbor["apMacAddr"]) 
                        coChannelneighbors.append(apName + " snrDb:" + str(neighbor["snrDb"]))
                if (len(coChannelneighbors)):
                    result.append({ "apName": accessPoint["apName"], "radioNumber": apRadio["radioNumber"], "rfBand": apRadio["rfBand"], "radioChannel": apRadio["radioChannel"], "coChannelneighborr:snrDb": coChannelneighbors })
    except Exception as e: 
        print("agg_neighbor_data:", e)

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
                        response = fetch_page(endpoint, apikey, fieldname, listname, query_temp, page, validation)
                        if (len(response) > 0):
                            print(fieldname, "page", page, "of", pageCount)
                            agg_neighbor_data(response, fieldname)
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

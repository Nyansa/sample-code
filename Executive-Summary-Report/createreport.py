import json, requests, time, datetime, sys, getopt
from utils.helper import *


# Usage
# python3 createreport.py --endpoint https://domain.nyansa.com/api/v2/graphql --apikey PutApiKeyHere --report [devices|applications|accesspoints|issues|custom|combined] --outputfile output/FileName.html --company Name  

# if in OnPrem please disable SSL-Validation with:
# --validation false (only if on onprem)


# -------------------------------------------------------------
# Start
# -------------------------------------------------------------
Company = {"name": ""}
def start(argv):
    try:
        endpoint = ''
        apikey = ''
        outputfile = ''
        report = ''
        validation = True
        company = ''
        try:
            if (argv == []):
                print('createreport.py -e <endpoint> -a <apikey> -r <report> -o <outputfile> -c <company>')
                sys.exit(2)

            opts, args = getopt.getopt(argv,"he:a:r:o:v:c:",["endpoint=","apikey=","report=","outputfile=","validation=", "company="])
        except getopt.GetoptError:
            print('createreport.py -e <endpoint> -a <apikey> -r <report> -o <outputfile> -c <company>')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-r", "--report"):
                report = arg
            elif opt in ("-o", "--outputfile"):
                outputfile = arg
            elif opt in ("-e", "--endpoint"):
                endpoint = arg
            elif opt in ("-a", "--apikey"):
                apikey = arg
            elif opt in ("-c", "--company"):
                company = arg
            elif opt in ("-v", "--validation"):
                if (arg == "0" or arg == "False" or arg == "false"):
                    requests.packages.urllib3.disable_warnings()
                    validation = False
   
        Company["name"] = company

        # create reports
        if (report == "devices"):
            create_devices_report(endpoint, apikey, outputfile, validation)
        elif (report == "issues"):
            create_issues_report(endpoint, apikey, outputfile, validation)
        elif (report == "applications"):
            create_applications_report(endpoint, apikey, outputfile, validation)
        elif (report == "accesspoints"):
            create_accesspoints_report(endpoint, apikey, outputfile, validation)
        elif (report == "custom"):
            create_custom_report(endpoint, apikey, outputfile, validation)
        elif (report == "combined"):
            create_combined_report(endpoint, apikey, outputfile, validation)
        else:
            print("Unknown Report:", report)
            print("Known Reports are:", "applications", "devices", "issues", "accesspoints", "custom", "combined")
    except:
        print("")


# -------------------------------------------------------------
# create Reports
# -------------------------------------------------------------
def create_applications_report(endpoint, apikey, outputfile, validation):
    try:
        get_applications_data(endpoint, apikey, validation)

        create_viewer("applications", outputfile)
    except Exception as e: 
        print("create_applications_report:", e)


def create_devices_report(endpoint, apikey, outputfile, validation):
    try:
        get_devices_data(endpoint, apikey, validation)

        create_viewer("devices", outputfile)
    except Exception as e: 
        print("create_devices_report:", e)


def create_issues_report(endpoint, apikey, outputfile, validation):
    try:
        get_issues_data(endpoint, apikey, validation)

        create_viewer("issues", outputfile)
    except Exception as e: 
        print("create_issues_report:", e)


def create_accesspoints_report(endpoint, apikey, outputfile, validation):
    try:
        get_accesspoints_data(endpoint, apikey, validation)

        create_viewer("accesspoints", outputfile)
    except Exception as e: 
        print("create_accesspoints_report:", e)


def create_custom_report(endpoint, apikey, outputfile, validation):
    try:
        get_custom_data(endpoint, apikey, validation)

        create_viewer("custom", outputfile)
    except Exception as e: 
        print("create_custom_report:", e)


def create_combined_report(endpoint, apikey, outputfile, validation):
    try:
        get_applications_data(endpoint, apikey, validation)
        get_issues_data(endpoint, apikey, validation)
        get_accesspoints_data(endpoint, apikey, validation)
        get_devices_data(endpoint, apikey, validation)
        get_custom_data(endpoint, apikey, validation)

        create_viewer("combined", outputfile)
    except Exception as e: 
        print("create_combined_report:", e)

        
# -------------------------------------------------------------
# Applications
# -------------------------------------------------------------
applications_performance_query = { "query": "{ affectedClientHoursDistribution ( metricCategory:apps aggFields:\"metricId\") { pageSize pageCount totalCount affectedClientHours { affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }
applications_traffic_users_query = { "query": "{ applicationList ( aggWindow:last24h ) { pageSize pageCount totalCount applications { appName userCount totalBytes } } }" }

applications_Performance = []
applications_Traffic = []
applications_Users = []

App_Beautifier = json.loads(load_textfile("data/app_beautifier.json"))
App_Blacklist = json.loads(load_textfile("data/app_blacklist.json"))


def get_applications_data(endpoint, apikey, validation):
    try:
        fetch(endpoint, apikey, "applications", "affectedClientHoursDistribution", "affectedClientHours", applications_performance_query, validation)
        fetch(endpoint, apikey, "applications", "applicationList", "applications", applications_traffic_users_query, validation)
    except Exception as e: 
        print("get_applications_data:", e)


def insert_applications_Data(template):
    try:
        template = insert_Data(sorted(getTopN(applications_Performance, 10, True), key=lambda k: k.get('value', 0), reverse=False), template, "barchart-vertical-application-performance")
        template = insert_Data(getTopN(applications_Traffic, 5, False), template, "barchart-horizontal-top-5-applications-traffic")
        template = insert_Data(getTopN(applications_Users, 5, False), template, "barchart-horizontal-top-5-applications-users")
    except Exception as e: 
        print("insert_applications_Data:", e)
    return template


def agg_applications_Data(data, report, fieldname):
    try:
        if (report == "applications" and fieldname == "affectedClientHoursDistribution"):
            for row in data:
                AppName = row["metricDescription"].replace("Client ", "").replace(" performance", "")
                if (AppName not in App_Blacklist):
                    if (AppName in App_Beautifier):
                        AppName = App_Beautifier[AppName]
                    applications_Performance.append({ "label": AppName, "value": row["affectedRatio"] })
        elif (report == "applications" and fieldname == "applicationList"):
            for row in data:
                AppName = row["appName"]
                if (AppName not in App_Blacklist):
                    if (AppName in App_Beautifier):
                        AppName = App_Beautifier[AppName]
                    applications_Traffic.append({ "label": get_bytes_label(AppName, row["totalBytes"]), "value": row["totalBytes"] })
                    applications_Users.append({ "label": get_count_label(AppName, row["userCount"]), "value": row["userCount"] })
    except Exception as e: 
        print("agg_applications_Data:", e)


# -------------------------------------------------------------
# Devices
# -------------------------------------------------------------
devices_query = { "query": "{deviceList (pageSize:500 sortBy:\"macAddr\" fromDate:\"<<DATE>>\" page:<<PAGENUMBER>>) { pageSize pageCount totalCount devices { macAddr hostname userName essid is5ghzCapable isDfsCapable isIotDevice deviceTypeDetails { osAndVersion deviceClass model osVersion os } } } }" }

devices_DeviceType = []
devices_OS = []
devices_IOS = []
devices_Android = []
devices_Mac = []
devices_Windows = []

devices_total = {"value": 0}
devices_is5ghzCapable = {"value": 0}
devices_isDfsCapable = {"value": 0}


def get_devices_data(endpoint, apikey, validation):
    try:
        devices_query["query"] = devices_query["query"].replace("<<DATE>>", str(date).replace(" 00:00:00", ""))

        fetch(endpoint, apikey, "devices", "deviceList", "devices", devices_query, validation)
    except Exception as e: 
        print("get_devices_data:", e)


def insert_devices_Data(template):
    try:
        template = insert_Data_Total(getTopN(devices_DeviceType, 5, True), 0, template, "donutchart-horizontal-device-types")
        template = insert_Data_Total(getTopN(devices_OS, 5, True), 0, template, "donutchart-horizontal-top5-os-distribution")
        template = insert_Data(getTopN(devices_IOS, 5, True), template, "barchart-horizontal-ios")
        template = insert_Data(getTopN(devices_Android, 5, True), template, "barchart-horizontal-android")
        template = insert_Data(getTopN(devices_Mac, 5, True), template, "barchart-horizontal-osx")
        template = insert_Data(getTopN(devices_Windows, 5, True), template, "barchart-horizontal-windows")
        template = insert_info(str("{:,}".format(devices_total["value"])), "", template, "info-total-clients")
        template = insert_info(str(get_total_percentage(devices_total["value"], devices_is5ghzCapable["value"])), str("{:,}".format(devices_is5ghzCapable["value"])), template, "info-5-ghz-capable-clients")
        template = insert_info(str(get_total_percentage(devices_total["value"], devices_isDfsCapable["value"])), str("{:,}".format(devices_isDfsCapable["value"])), template, "info-dfs-capable-clients")
    except Exception as e: 
        print("insert_devices_Data:", e)
    return template


def agg_devices_Data(data, report, fieldname):
    try:
        if (report == "devices" and fieldname == "deviceList"):
            for row in data:
                devices_total["value"] += 1
                if (row["is5ghzCapable"] == True):
                    devices_is5ghzCapable["value"] += 1
                if (row["isDfsCapable"] == True):
                    devices_isDfsCapable["value"] += 1
                if (row["deviceTypeDetails"] != None):
                    if (row["deviceTypeDetails"]["deviceClass"] != None):
                        agg_devices_value(row, devices_DeviceType, "deviceClass")
                        agg_devices_value(row, devices_OS, "os")
                        if (row["deviceTypeDetails"]["os"] == "iOS"):
                            agg_devices_value(row, devices_IOS, "osVersion")
                        elif (row["deviceTypeDetails"]["os"] == "Android"):
                            agg_devices_value(row, devices_Android, "osVersion")
                        elif (row["deviceTypeDetails"]["os"] == "OS X"):
                            agg_devices_value(row, devices_Mac, "osVersion")
                        elif (row["deviceTypeDetails"]["os"] == "Windows"):
                            agg_devices_value(row, devices_Windows, "osVersion")
    except Exception as e: 
        print("agg_devices_Data:", e)


def agg_devices_value(row, array, fieldname):
    try:
        if (row["deviceTypeDetails"][fieldname] != None):
            found = False
            for item in array:
                if (item["label"] == row["deviceTypeDetails"][fieldname]):
                    item["value"] += 1
                    found = True
            if (found == False):
                array.append({ "label": row["deviceTypeDetails"][fieldname], "value": 0 })
    except Exception as e: 
        print(fieldname, "agg_devices_value:", e)


# -------------------------------------------------------------
# Issues
# -------------------------------------------------------------
issues_wifi_query = { "query": "{affectedClientHoursDistribution ( metricCategory:wifi ) { pageSize pageCount totalCount affectedClientHours { affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }
issues_dhcp_query = { "query": "{affectedClientHoursDistribution ( metricCategory:dhcp ) { pageSize pageCount totalCount affectedClientHours { affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }
issues_web_query = { "query": "{affectedClientHoursDistribution ( metricCategory:web ) { pageSize pageCount totalCount affectedClientHours { affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }
issues_dns_query = { "query": "{affectedClientHoursDistribution ( metricCategory:dns ) { pageSize pageCount totalCount affectedClientHours { affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }
issues_radius_query = { "query": "{affectedClientHoursDistribution ( metricCategory:radius ) { pageSize pageCount totalCount affectedClientHours { affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }

issues = []

issues_wifi = {"affectedRatio": 0 }
issues_dhcp = {"affectedRatio": 0 }
issues_web = {"affectedRatio": 0 }
issues_dns = {"affectedRatio": 0 }
issues_radius = {"affectedRatio": 0 }


def get_issues_data(endpoint, apikey, validation):
    try:
        fetch(endpoint, apikey, "issues_wifi", "affectedClientHoursDistribution", "affectedClientHours", issues_wifi_query, validation)
        fetch(endpoint, apikey, "issues_dhcp", "affectedClientHoursDistribution", "affectedClientHours", issues_dhcp_query, validation)
        fetch(endpoint, apikey, "issues_web", "affectedClientHoursDistribution", "affectedClientHours", issues_web_query, validation)
        fetch(endpoint, apikey, "issues_dns", "affectedClientHoursDistribution", "affectedClientHours", issues_dns_query, validation)
        fetch(endpoint, apikey, "issues_radius", "affectedClientHoursDistribution", "affectedClientHours", issues_radius_query, validation)
    except Exception as e: 
        print("get_issues_data:", e)


def insert_issues_Data(template):
    try:
        template = insert_Data_Total(getTopN(calc_issues(), 5, True), 0, template, "donutchart-horizontal-client-device-issues")
    except Exception as e: 
        print("insert_issues_Data:", e)
    return template


def agg_issues_Data(data, report, fieldname):
    try:
        if (report == "issues_wifi"):
            for row in data:
                if (row["affectedRatio"] != None):
                    issues_wifi["affectedRatio"] = row["affectedRatio"]
        elif (report == "issues_dhcp"):
            for row in data:
                if (row["affectedRatio"] != None):
                    issues_dhcp["affectedRatio"] = row["affectedRatio"]
        elif (report == "issues_web"):
            for row in data:
                if (row["affectedRatio"] != None):
                    issues_web["affectedRatio"] = row["affectedRatio"]
        elif (report == "issues_dns"):
            for row in data:
                if (row["affectedRatio"] != None):
                    issues_dns["affectedRatio"] = row["affectedRatio"]
        elif (report == "issues_radius"):
            for row in data:
                if (row["affectedRatio"] != None):
                    issues_radius["affectedRatio"] = row["affectedRatio"]
    except Exception as e: 
        print("agg_issues_Data:", e)


def calc_issues():
    try:        
        issues.append({ "label": "Wi-Fi perf", "value": issues_wifi["affectedRatio"] })
        issues.append({ "label": "DHCP", "value": issues_dhcp["affectedRatio"] })
        issues.append({ "label": "Web", "value": issues_web["affectedRatio"] })
        issues.append({ "label": "DNS", "value": issues_dns["affectedRatio"] })
        issues.append({ "label": "RADIUS", "value": issues_radius["affectedRatio"] })
        return issues
    except Exception as e: 
        print("calc_issues:", e)
    return []


# -------------------------------------------------------------
# Access Points
# -------------------------------------------------------------
accesspoints_query = { "query": "{ accessPointList (pageSize:500 sortBy:\"apName\" page:<<PAGENUMBER>>) { pageSize pageCount totalCount accessPoints { apName apModel } } }" }
accesspoints_worst_aps_wifi_query = { "query": "{affectedClientHoursDistribution ( aggFields:\"apMacAddr\" metricCategory:wifi ) { pageSize pageCount totalCount affectedClientHours { apDescriptions apMacAddr affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }
accesspoints_worst_aps_web_query = { "query": "{affectedClientHoursDistribution ( aggFields:\"apMacAddr\" metricCategory:web ) { pageSize pageCount totalCount affectedClientHours { apDescriptions apMacAddr affectedRatio clientHours usageHours rootCause metricDescription metricId } } }" }

accesspoints_models = []
accesspoints_capabilities = []
accesspoints_worst_aps_wifi = []
accesspoints_worst_aps_web = []

accesspoints_Total = {"value": 0}
accesspoints_mumimo_capable = {"value": 0}

AP_Capabilities = json.loads(load_textfile("data/ap_capabilities.json"))
MuMiMoAPModels = []


def get_accesspoints_data(endpoint, apikey, validation):
    try:
        for ap in AP_Capabilities:
            if ("MIMO" in ap['capabilities']):
                MuMiMoAPModels.append(ap['apModel'])

        fetch(endpoint, apikey, "accesspoints", "accessPointList", "accessPoints", accesspoints_query, validation)
        fetch(endpoint, apikey, "accesspoints_worst_aps_wifi", "affectedClientHoursDistribution", "affectedClientHours", accesspoints_worst_aps_wifi_query, validation)
        fetch(endpoint, apikey, "accesspoints_worst_aps_web", "affectedClientHoursDistribution", "affectedClientHours", accesspoints_worst_aps_web_query, validation)
    except Exception as e: 
        print("get_accesspoints_data:", e)


def insert_accesspoints_Data(template):
    try:
        top10_accesspoints_models = getTopN(accesspoints_models, 10, False)
        for row in top10_accesspoints_models:
            row["label"] = row["label"] + " (" + str("{:,}".format(row["value"])) + ")"

        top5_accesspoints_capabilities = getTopN(accesspoints_capabilities, 5, True)
        accesspoints_capabilities_count = get_total_count(top5_accesspoints_capabilities)

        top10_accesspoints_worst_aps_wifi = getTopN(accesspoints_worst_aps_wifi, 10, True)
        top10_accesspoints_worst_aps_web = getTopN(accesspoints_worst_aps_web, 10, True)

        template = insert_Data(top10_accesspoints_models, template, "barchart-horizontal-top10-apmodels")
        template = insert_Data(top10_accesspoints_worst_aps_wifi, template, "barchart-horizontal-top10-worst-aps-wifi")
        template = insert_Data(top10_accesspoints_worst_aps_web, template, "barchart-horizontal-top10-worst-aps-web")
        template = insert_info(str(get_total_percentage(accesspoints_Total["value"], accesspoints_mumimo_capable["value"])), str("{:,}".format(accesspoints_mumimo_capable["value"])), template, "info-mu-mimo-capable-aps")
        template = insert_info(str("{:,}".format(accesspoints_Total["value"])), "", template, "info-total-aps")
        template = insert_Data_Total(top5_accesspoints_capabilities, get_total_percentage(accesspoints_Total["value"], accesspoints_capabilities_count), template, "donutchart-vertical-ap-capabilities")
    except Exception as e: 
        print("insert_accesspoints_Data:", e)
    return template


def agg_accesspoints_Data(data, report, fieldname):
    try:
        if (report == "accesspoints"):
            for row in data:
                accesspoints_Total["value"] += 1
                if (row["apModel"] in MuMiMoAPModels):
                    accesspoints_mumimo_capable["value"] += 1
                if (row["apModel"] != None):
                    agg_value(row["apModel"], accesspoints_models)
                capability = list(filter(lambda item: item['apModel'] == row['apModel'], AP_Capabilities))
                if (len(capability) > 0):
                    agg_value(capability[0]["capabilities"], accesspoints_capabilities)
                else:
                    add_unkown_ap(row['apModel'])
        elif (report == "accesspoints_worst_aps_wifi"):
            for row in data:
                if (row["affectedRatio"] != None):
                    accesspoints_worst_aps_wifi.append({ "label": row["apDescriptions"], "value": row["affectedRatio"] })
        elif (report == "accesspoints_worst_aps_web"):
            for row in data:
                if (row["affectedRatio"] != None):
                    accesspoints_worst_aps_web.append({ "label": row["apDescriptions"], "value": row["affectedRatio"] })

    except Exception as e: 
        print("agg_accesspoints_Data:", e)


def agg_value(label, array):
    try:
        found = False
        for item in array:
            if (item["label"] == label):
                item["value"] += 1
                found = True
        if (found == False):
            array.append({ "label": label, "value": 1 })
    except Exception as e: 
        print("agg_accesspoints_value:", e)


# -------------------------------------------------------------
# Custom
# -------------------------------------------------------------
custom_wifi_query = { "query": "{ customGroupList ( pageSize:500 page:<<PAGENUMBER>>) { pageSize pageCount totalCount customGroups { name groupType affectedClientHours (metricCategory:wifi) { clientHours usageHours affectedRatio } } } }" }
custom_web_query = { "query": "{ customGroupList ( pageSize:500 page:<<PAGENUMBER>>) { pageSize pageCount totalCount customGroups { name groupType affectedClientHours (metricCategory:web) { clientHours usageHours affectedRatio } } } }" }
custom_dns_query = { "query": "{ customGroupList ( pageSize:500 page:<<PAGENUMBER>>) { pageSize pageCount totalCount customGroups { name groupType affectedClientHours (metricCategory:dns) { clientHours usageHours affectedRatio } } } }" }
custom_dhcp_query = { "query": "{ customGroupList ( pageSize:500 page:<<PAGENUMBER>>) { pageSize pageCount totalCount customGroups { name groupType affectedClientHours (metricCategory:dhcp) { clientHours usageHours affectedRatio } } } }" }
custom_radius_query = { "query": "{ customGroupList ( pageSize:500 page:<<PAGENUMBER>>) { pageSize pageCount totalCount customGroups { name groupType affectedClientHours (metricCategory:radius) { clientHours usageHours affectedRatio } } } }" }
custom_apps_query = { "query": "{ customGroupList ( pageSize:500 page:<<PAGENUMBER>>) { pageSize pageCount totalCount customGroups { name groupType affectedClientHours (metricCategory:apps) { clientHours usageHours affectedRatio } } } }" }

custom_wifi = []
custom_web = []
custom_dns = []
custom_dhcp = []
custom_radius = []
custom_apps = []


def get_custom_data(endpoint, apikey, validation):
    try:
        fetch(endpoint, apikey, "custom_wifi", "customGroupList", "customGroups", custom_wifi_query, validation)
        fetch(endpoint, apikey, "custom_web", "customGroupList", "customGroups", custom_web_query, validation)
        fetch(endpoint, apikey, "custom_dns", "customGroupList", "customGroups", custom_dns_query, validation)
        fetch(endpoint, apikey, "custom_dhcp", "customGroupList", "customGroups", custom_dhcp_query, validation)
        fetch(endpoint, apikey, "custom_radius", "customGroupList", "customGroups", custom_radius_query, validation)
        fetch(endpoint, apikey, "custom_apps", "customGroupList", "customGroups", custom_apps_query, validation)
    except Exception as e: 
        print("get_custom_data:", e)


def insert_custom_Data(template):
    try:
        top10_custom_wifi = getTopN(custom_wifi, 10, False)
        for row in top10_custom_wifi:
            row["label"] = row["label"] + " (" + str(row["value"]) + "%)"

        top10_custom_web = getTopN(custom_web, 10, False)
        for row in top10_custom_web:
            row["label"] = row["label"] + " (" + str(row["value"]) + "%)"

        top10_custom_dns = getTopN(custom_dns, 10, False)
        for row in top10_custom_dns:
            row["label"] = row["label"] + " (" + str(row["value"]) + "%)"

        top10_custom_dhcp = getTopN(custom_dhcp, 10, False)
        for row in top10_custom_dhcp:
            row["label"] = row["label"] + " (" + str(row["value"]) + "%)"

        top10_custom_radius = getTopN(custom_radius, 10, False)
        for row in top10_custom_radius:
            row["label"] = row["label"] + " (" + str(row["value"]) + "%)"

        top10_custom_apps = getTopN(custom_apps, 10, False)
        for row in top10_custom_apps:
            row["label"] = row["label"] + " (" + str(row["value"]) + "%)"

        template = insert_Data(top10_custom_wifi, template, "barchart-horizontal-top10-custom-wifi")
        template = insert_Data(top10_custom_web, template, "barchart-horizontal-top10-custom-web")
        template = insert_Data(top10_custom_dns, template, "barchart-horizontal-top10-custom-dns")
        template = insert_Data(top10_custom_dhcp, template, "barchart-horizontal-top10-custom-dhcp")
        template = insert_Data(top10_custom_radius, template, "barchart-horizontal-top10-custom-radius")
        template = insert_Data(top10_custom_apps, template, "barchart-horizontal-top10-custom-apps")
    except Exception as e: 
        print("insert_custom_Data:", e)
    return template


def agg_custom_Data(data, report, fieldname):
    try:
        if (report == "custom_wifi"):
            for row in data:
                agg_custom_value(row, custom_wifi)
        if (report == "custom_web"):
            for row in data:
                agg_custom_value(row, custom_web)
        if (report == "custom_dns"):
            for row in data:
                agg_custom_value(row, custom_dns)
        if (report == "custom_dhcp"):
            for row in data:
                agg_custom_value(row, custom_dhcp)
        if (report == "custom_radius"):
            for row in data:
                agg_custom_value(row, custom_radius)
        if (report == "custom_apps"):
            for row in data:
                agg_custom_value(row, custom_apps)

    except Exception as e: 
        print("agg_custom_Data:", e)


def agg_custom_value(row, array):
    try:
        if (row["affectedClientHours"] != None):
            if (row["affectedClientHours"]["affectedRatio"] != None):
                array.append({ "label": row["name"], "value": round(row["affectedClientHours"]["affectedRatio"] * 10, 2) })
    except Exception as e: 
        print("agg_custom_value:", e)


# -------------------------------------------------------------
# Fetcher
# -------------------------------------------------------------
def fetch(endpoint, apikey, report, fieldname, listname, query, validation):
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
                        response = fetch_page(endpoint, apikey, report, fieldname, listname, query_temp, page, validation)
                        if (len(response) > 0):
                            print(report, fieldname, "page", page, "of", pageCount)
                            if (report == "applications"):
                                agg_applications_Data(response, report, fieldname)
                            elif (report == "devices"):
                                agg_devices_Data(response, report, fieldname)
                            elif (report.startswith("accesspoints")):
                                agg_accesspoints_Data(response, report, fieldname)
                            elif (report.startswith("issues")):
                                agg_issues_Data(response, report, fieldname)
                            elif (report.startswith("custom")):
                                agg_custom_Data(response, report, fieldname)
        else:
            print(report, fieldname, "fetch:", response.status_code)
            print(report, fieldname, "fetch:", response.reason)
    except Exception as e: 
        print(report, fieldname, "fetch:", e)


def fetch_page(endpoint, apikey, report, fieldname, listname, query, page, validation):
    try:
        response = requests.post(endpoint, headers={'api-token': apikey}, data=query, verify=validation)
        if(response.status_code == 200):
            if ("data" in response.text):
                if (fieldname in response.text):
                    response = json.loads(response.text)["data"][fieldname]
                    return response[listname]
        else:
            print(report, fieldname, "fetch_page:", response.status_code)
            print(report, fieldname, "fetch_page:", response.reason)
    except Exception as e: 
        print(report, fieldname, "fetch_page:", e)
    return []


# -------------------------------------------------------------
# create viewer
# -------------------------------------------------------------
def create_viewer(report, outputfile):
    try:
        Template = get_template(report)
        Template["company"] = Company["name"]
        Template["date"] = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        if (Template != ""):

            if (report == "applications" or report == "combined"):
                Template = insert_applications_Data(Template)

            if (report == "devices" or report == "combined"):
                Template = insert_devices_Data(Template)

            if (report == "issues" or report == "combined"):
                Template = insert_issues_Data(Template)

            if (report.startswith("accesspoints") or report == "combined"):
                Template = insert_accesspoints_Data(Template)

            if (report.startswith("custom") or report == "combined"):
                Template = insert_custom_Data(Template)

            Header_Links = []
            for section in Template["sections"]:
                Header_Links.append(section["link"])

            save_viewer(outputfile, Template, Header_Links)
    except Exception as e: 
        print(report, "create_viewer:", e)

    
def get_template(report):
    try:
        if (report == "combined"):
            return create_combined_template()
        if (report == "applications"):
            return json.loads(load_textfile("templates/applications.json"))
        if (report == "devices"):
            return json.loads(load_textfile("templates/devices.json"))
        if (report == "issues"):
            return json.loads(load_textfile("templates/issues.json"))
        if (report.startswith("accesspoints")):
            return json.loads(load_textfile("templates/accesspoints.json"))
        if (report.startswith("custom")):
            return json.loads(load_textfile("templates/custom.json"))
    except Exception as e: 
        print(report, "get_template:", e)
    return ""


def create_combined_template():
    try:
        Combined_Template = json.loads(load_textfile("templates/combined.json"))
        sections = []
        for Combined_Section in Combined_Template["sections"]:
            Template_Sections = get_Template_Sections(Combined_Section)
            for Template_Section in Template_Sections:
                sections.append(Template_Section)
        Combined_Template["sections"] = sections 

        return Combined_Template
    except Exception as e: 
        print("create_combined_template:", e)
    return {}


def get_Template_Sections(templatefile):
    try:
        Partial_Template = json.loads(load_textfile(templatefile))
        return Partial_Template["sections"]
    except Exception as e: 
        print("get_Template_Sections:", e)
    return []


# -------------------------------------------------------------
# entry point
# -------------------------------------------------------------
date = datetime.datetime.today().replace(microsecond=0, second=0, minute=0, hour=0)-datetime.timedelta(days=14)
start(sys.argv[1:])

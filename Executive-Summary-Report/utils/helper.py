import os, json, datetime, requests
from dateutil import parser


def load_textfile(_filename):
    if os.path.exists(_filename):
        return open(_filename,'r').read()
    return ""


def save_textfile(_filename, _filecontent):
    with open(_filename, "w") as outfile:
        print(_filecontent, file=outfile)


def getTopN(array, count, convertToPercentage):
    try:
        sortedResult = sorted(array, key=lambda k: k.get('value', 0), reverse=True)
        result = []
        for row in sortedResult:
            if (row['label'] != ""):
                if (len(result) < count):
                    result.append(row)
        if (convertToPercentage == True):
            result = convertValueToPercentage(result)
        return result
    except:
        print("getTopN: something went wrong!")
    return []


def convertValueToPercentage(_list, _total=0):
    if (len(_list) > 0):    
        if (_total == 0):
            for row in _list:
                _total = _total + row['value']    
        totalPercentage = 0
        for row in _list:
            rowPercentage = 1
            if (row['value'] > (_total / 100)):
                rowPercentage = int(100 / (_total / row['value']))
            row['value'] = rowPercentage
            totalPercentage = totalPercentage + rowPercentage
        _list[0]['value'] = _list[0]['value'] - (totalPercentage - 100)
    return _list


def save_viewer(filename, data, header_links):
    try:
        Viewer = load_textfile("templates/viewer.html")
        Viewer = Viewer.replace("<<HEADER>>", create_header(header_links))
        Viewer = Viewer.replace("<<JAVASCRIPT>>", load_textfile("templates/viewer.min.js").replace("REPORTDATA", json.dumps(data)))
        save_textfile(filename, Viewer)
    except:
        print("save_viewer: something went wrong!")


def create_header(header_links):
    try:
        Header = load_textfile("templates/header.html")

        items = ''
        for item in header_links:
            items = items + '<li class="nav-item" style="margin-right: 30px; margin-top: 3px">'
            items = items + '   <a class="nav-link lead" href="#{{item}}" style="color: #27293b;">{{item}}</a>'.replace("{{item}}", item)
            items = items + '</li>'

        Header = Header.replace("<<HEADERITEMS>>", items)

        return Header
    except:
        print("create_header: something went wrong!")
    return ""


def get_total_count(data):
    result = 0
    try:
        for row in data:
            result += row["value"]
    except Exception as e: 
        print("get_total_count:", e)
    return result


def get_total_percentage(total, count):
    result = 0
    try:
        result = int(100 / (total / count))
    except: 
        print("")
    return result


def get_bytes_label(label, totalbytes):
    try:
        if (totalbytes >= 1000000000000000000000000):
            return label + " (" + str(round(totalbytes / 1000000000000000000000000, 2)) + " YB)"
        elif (totalbytes >= 1000000000000000000000):
            return label + " (" + str(round(totalbytes / 1000000000000000000000, 2)) + " ZB)"
        elif (totalbytes >= 1000000000000000000):
            return label + " (" + str(round(totalbytes / 1000000000000000000, 2)) + " EB)"
        elif (totalbytes >= 1000000000000000):
            return label + " (" + str(round(totalbytes / 1000000000000000, 2)) + " PB)"
        elif (totalbytes >= 1000000000000):
            return label + " (" + str(round(totalbytes / 1000000000000, 2)) + " TB)"
        elif (totalbytes >= 1000000000):
            return label + " (" + str(round(totalbytes / 1000000000, 2)) + " GB)"
        elif (totalbytes >= 1000000):
            return label + " (" + str(round(totalbytes / 1000000, 2)) + " MB)"
        elif (totalbytes >= 1000):
            return label + " (" + str(round(totalbytes / 1000, 2)) + " KB)"
    except Exception as e: 
        print("get_bytes_label:", e)
    return label + " (" + str(totalbytes) + " B)"


def get_count_label(label, totalcount):
    try:
        if (totalcount >= 1000000000000000000000000):
            return label + " (" + str(round(totalcount / 1000000000000000000000000, 2)) + " Y)"
        elif (totalcount >= 1000000000000000000000):
            return label + " (" + str(round(totalcount / 1000000000000000000000, 2)) + " Z)"
        elif (totalcount >= 1000000000000000000):
            return label + " (" + str(round(totalcount / 1000000000000000000, 2)) + " E)"
        elif (totalcount >= 1000000000000000):
            return label + " (" + str(round(totalcount / 1000000000000000, 2)) + " P)"
        elif (totalcount >= 1000000000000):
            return label + " (" + str(round(totalcount / 1000000000000, 2)) + " T)"
        elif (totalcount >= 1000000000):
            return label + " (" + str(round(totalcount / 1000000000, 2)) + " G)"
        elif (totalcount >= 1000000):
            return label + " (" + str(round(totalcount / 1000000, 2)) + " M)"
        elif (totalcount >= 1000):
            return label + " (" + str(round(totalcount / 1000, 2)) + " K)"
    except Exception as e: 
        print("get_count_label:", e)
    return label + " (" + str(totalcount) + ")"


def APName_beautifier(vendor, array):
    try:
        for row in array:
            if (vendor == "Aruba"):
                AP_Name = row['label'].replace("AP-AIR-", "").replace("ap-air-", "").replace("Aruba ", "")
            if (vendor == "Cisco"):
                AP_Name = AP_Name.replace("CAP", "").replace("cap", "").replace("Cisco ", "")
                AP_Name = AP_Name.replace("AP", "").replace("ap", "")
                AP_Name = AP_Name.split("-")[0]
            row['label'] = AP_Name
    except Exception as e: 
        print("APName_beautifier:", e)
    return array


def add_unkown_ap(apModel):
    try:
        unknown_aps = json.loads(load_textfile("data/unknown_aps.json"))
        if (apModel not in unknown_aps):
            unknown_aps.append(apModel)
            save_textfile("data/unknown_aps.json", json.dumps(unknown_aps, sort_keys=False, indent=4))
    except Exception as e: 
        print("add_unkown_ap:", e)


def insert_Data(data, template, reportid):
    try:
        for section in template["sections"]:
            for report in section["reports"]:
                if (report["id"] == reportid):
                    report["data"] = data
    except Exception as e: 
        print(reportid, "insert_Data:", e)
    return template


def insert_Data_Total(data, total, template, reportid):
    try:
        for section in template["sections"]:
            for report in section["reports"]:
                if (report["id"] == reportid):
                    report["data"]["data"] = data
                    report["data"]["total"] = total
    except Exception as e: 
        print(reportid, "insert_Data_Total:", e)
    return template


def insert_info(value, count, template, reportid):
    try:
        for section in template["sections"]:
            for report in section["reports"]:
                if (report["id"] == reportid):
                    if (value != ""):
                        report["config"]["value"] = report["config"]["value"].replace("<<VALUE>>", value)
                    if (count != ""):
                        report["config"]["count"] = report["config"]["count"].replace("<<COUNT>>", count)
    except Exception as e: 
        print(reportid, "insert_info:", e)
    return template

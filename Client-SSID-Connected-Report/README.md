#  Nyansa — 24-hour report of all clients on the network and the SSIDs they have connected to

## Setup

```
$ pip install -r requirements.txt
```

## Usage

```
python3 client-ssid-report.py --endpoint https://https://domain.nyansa.com/api/v2/graphql --apikey <API_Key> --numHours 24 --jsonoutput output.json --csvoutput output.csv --validation true
```

## Arguments
--endpoint https://domain.nyansa.com/api/v2/graphql

--apikey 000000000000000000 (API Key for the used Endpoint). Generate this in the Voyance application

--numHours Number of Hours from current time the report should be generated for. For last 24 hours, use '24'

--jsonoutput folder/FileName.json 

--csvoutput folder/FileName.csv

--validation true/false (optional - only needed if the used endpoint uses a self signed certificate)

#  Nyansa — List of all access points with co-channel neighbors

## Setup

```
$ pip install -r requirements.txt
```

## Usage

```
python3 ap-cochannel-neighbors.py --endpoint https://https://domain.nyansa.com/api/v2/graphql --apikey <API_Key> --jsonoutput output.json --csvoutput output.csv --validation true

```

## Arguments
--endpoint https://domain.nyansa.com/api/v2/graphql

--apikey 000000000000000000 (API Key for the used Endpoint). Generate this in the Voyance application

--jsonoutput folder/FileName.json 

--csvoutput folder/FileName.csv

--validation true/false (optional - only needed if the used endpoint uses a self signed certificate)

#  Nyansa — List of rogue access points that are broadcasting SSIDs that are visible to the access points that make up the corporate wireless infrastructure

## Setup

```
$ pip install -r requirements.txt
```

## Usage

```
python3 ap-suspicious-rogue.py --endpoint https://https://domain.nyansa.com/api/v2/graphql --apikey <API_Key> --jsonoutput output.json --csvoutput output.csv --validation true
```

## Arguments
--endpoint https://domain.nyansa.com/api/v2/graphql

--apikey 000000000000000000 (API Key for the used Endpoint)

--report [devices|applications|accesspoints|issues|custom|combined] 

--jsonoutput folder/FileName.json 

--csvoutput folder/FileName.csv

--validation true/false (optional - only needed if the used endpoint uses a self signed certificate)

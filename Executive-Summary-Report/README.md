#  Nyansa — 2-week Executive Summary report including insights about Applications, Devices, Access point performance

## Setup

```
$ pip install -r requirements.txt
```

## Usage

```
python createreport.py --endpoint https://domain.nyansa.com/api/v2/graphql --apikey 000000000000000000 --report [devices|applications|accesspoints|issues|custom|combined] --outputfile output/FileName.html --validation false
```

## Arguments
--endpoint https://domain.nyansa.com/api/v2/graphql

--apikey 000000000000000000 (API Key for the used Endpoint)

--report [devices|applications|accesspoints|issues|custom|combined] 

--outputfile folder/FileName.html 

--validation false (only needed if the used endpoint uses a self signed certificate)

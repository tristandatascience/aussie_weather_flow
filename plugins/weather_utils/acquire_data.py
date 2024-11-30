import argparse
import os.path

import datetime as dt
import requests

import csv
import pprint

app_description = "Scraping of Weather Data from the Australian Bureau of Meteorology."
data_path = './data'



def init_argparser() -> argparse.ArgumentParser:
    """
    Initialise the arguments parser.
    """
    parser = argparse.ArgumentParser(description = app_description)

    parser.add_argument('--data_path', help="Data path", default='../data')

    return parser


def digest(raw_path:str, digest_path:str, csv_file_name:str):
    """
    Convert raw CSV files to digest ones that can be read using Pandas.
    """
    Lines = []

    file_path = os.path.join(raw_path, csv_file_name)
    try:
        with open(file_path, mode='r', encoding="cp1252") as file:

            header_found = False
            for line in file:
                # Skip leading comments and empty lines
                if line[0] == "\"" or line[0] == "\n":
                    continue
                # Skip header
                if line[0] == "," and header_found == False:
                    header_found = True
                    continue
                Lines.append(line)

        file_path = os.path.join(digest_path, csv_file_name)
        try:
            with open(file_path, mode='w', encoding="utf_8") as file:
                for line in Lines:
                    file.write(line)
                print("File {file_path} created.".format(file_path=file_path))
        except Exception as exc :
            print("Failed to open {}".format(file_path))
            print(exc)

    except Exception as exc :
        print("Failed to open {}".format(file_path))
        print(exc)


def get_data(data_id:str, period:str, data_path:str,
             refresh:bool = False):
    """
    Checks existence of data file and retrieves it if needed.
    """
    file_name = '{data_id}.{period}.csv'.format(data_id=data_id, period=period)
    raw_path = os.path.join(data_path, 'raw')
    raw_file_path = os.path.join(raw_path, file_name)

    if os.path.isfile(raw_file_path):
        print("File {file_path} exists.".format(file_path=raw_file_path))
        if not refresh:
            return

    # Request
    # ex : https://reg.bom.gov.au/climate/dwo/202409/text/IDCJDW2124.202409.csv
    url='https://reg.bom.gov.au/climate/dwo/{period}/text/{data_id}.{period}.csv'

    response = requests.get(url=url.format(data_id=data_id, period=period)
    )

    # Request status
    status_code = response.status_code

    if status_code == 200:
        try:
            with open(raw_file_path, 'wb') as file:
                file.write(response.content)
                print("File {file_path} created.".format(file_path=raw_file_path))

            digest_path = os.path.join(data_path, 'digest')
            digest(raw_path, digest_path, file_name)

        except Exception as exc :
            print("Failed to open {}".format(raw_file_path))
            print(exc)
    else:
        print('Got error :', status_code)


def get_stations(file_path:str = 'data/CodeVilleClimat.csv') -> list:
    """"
    Get stations from CSV file.
    Indeed we are interested in the station code only.
    """
    rows = []
    try:
        with open(file_path, newline='') as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                rows.append(row['Code'])

    except Exception as exc :
        print("Failed to open {}".format(file_path))
        print(exc)

    return rows


def get_data_id(station_id:str) -> str:
    """
    Get the data identifier for the considered station.
    """
    data_id = ''

    # Request
    # ex : https://reg.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=201&p_display_type=dwo&p_startYear=&p_c=&p_stn_num=066214
    url='https://reg.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=201&p_display_type=dwo&p_startYear=&p_c=&p_stn_num={}'

    response = requests.get(url=url.format(station_id)
    )

    # Request status
    status_code = response.status_code

    if status_code == 200:
        content = str(response.content)

        start_delimiter = 'URL=/climate/dwo/'
        start_delimiter_first = content.find(start_delimiter)

        if start_delimiter_first == -1:
            print('{} - Start delimiter not found !'.format(station_id))
        else:
            end_delimiter = '.latest'
            end_delimiter_first = content.find(end_delimiter)

            if end_delimiter_first == -1:
                print('{} - End delimiter not found !'.format(station_id))
            else:
                start_data_id = start_delimiter_first + len(start_delimiter)
                data_id = content[start_data_id:end_delimiter_first]
    else:
        print('{} - Request got error :{}'.format(station_id, status_code))

    return data_id

def get_data_ids(stations:list, file_path:str = 'data/DataIds.csv') -> list:
    """
    Get the data identifiers for the considered stations.
    """
    rows = []

    if not os.path.isfile(file_path):
        print("File {file_path} does not exist.".format(file_path=file_path))

        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['station_id', 'data_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for station_id in stations:
                    row = {
                        'station_id': station_id,
                        'data_id': get_data_id(station_id)
                    }
                    rows.append(row)
                    writer.writerow(row)
                    print(row)

                print("File {file_path} created.".format(file_path=file_path))

        except Exception as exc :
            print("Failed to open {}".format(file_path))
            print(exc)

        return rows

    print("File {file_path} exists.".format(file_path=file_path))
    try:
        with open(file_path, newline='') as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                rows.append(row)

        return rows

    except Exception as exc :
        print("Failed to open {}".format(file_path))
        return rows

def acquire():

    print("Processing to : {}".format(data_path))

    stations = get_stations(os.path.join(data_path, 'CodeVilleClimat.csv'))
    print("Stations list :")
    pprint.pprint(stations)

    station_data_ids = get_data_ids(stations,
                                    os.path.join(data_path, 'DataIds.csv'))
    print("Data Identifiers and Stations list :")
    pprint.pprint(station_data_ids)

    #today = dt.datetime.now(tz = dt.UTC).strftime("%Y%m%d")
    today_year_month = dt.datetime.now(dt.timezone.utc).strftime("%Y%m")

    today_year = int(today_year_month[:4])
    today_month = int(today_year_month[-2:])

    year, month = today_year, today_month
    dates = [(year, month)]

    for i in range(1, 14):
        month -= 1
        if month == 0:
            year -= 1
            month = 12
        dates.append((year, month))

    for station_data_id in station_data_ids:
        for date in dates:
            period = "{year}{month:02d}".format(year=date[0], month=date[1])
            refresh = (today_year == date[0]) and (today_month == date[1])
            get_data(station_data_id['data_id'], period, data_path, refresh)

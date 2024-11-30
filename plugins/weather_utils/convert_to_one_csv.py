import argparse
import os.path

import pandas as pd

app_description = "CSV Conversion of monthly Weather Data from the Australian Bureau of Meteorology."

def init_argparser() -> argparse.ArgumentParser:
    """
    Initialise the arguments parser.
    """
    parser = argparse.ArgumentParser(description = app_description)

    parser.add_argument('--data_path', help="Data path", default='../data')

    return parser


# weatherAUS.csv fields
"""
Date,
Location,
MinTemp,
MaxTemp,
Rainfall,
Evaporation,
Sunshine,
WindGustDir,
WindGustSpeed,
WindDir9am,
WindDir3pm,
WindSpeed9am,
WindSpeed3pm,
Humidity9am,
Humidity3pm,
Pressure9am,
Pressure3pm,
Cloud9am,
Cloud3pm,
Temp9am,
Temp3pm,
RainToday,
RainTomorrow
"""

# Column names from data acquisition
weatherAUS_names_pre = \
[
    'Date',
    'MinTemp',
    'MaxTemp',
    'Rainfall',
    'Evaporation',
    'Sunshine',
    'WindGustDir',
    'WindGustSpeed',
    'WindDir9am',
    'WindDir3pm',
    'WindSpeed9am',
    'WindSpeed3pm',
    'Humidity9am',
    'Humidity3pm',
    'Pressure9am',
    'Pressure3pm',
    'Cloud9am',
    'Cloud3pm',
    'Temp9am',
    'Temp3pm',
]

acquisition_names = \
[
    'Comment',
    'Date',
    'MinTemp',
    'MaxTemp',
    'Rainfall',
    'Evaporation',
    'Sunshine',
    'WindGustDir',
    'WindGustSpeed',
    'Time of maximum wind gust',
    'Temp9am',
    'Humidity9am',
    'Cloud9am',
    'WindDir9am',
    'WindSpeed9am',
    'Pressure9am',
    'Temp3pm',
    'Humidity3pm',
    'Cloud3pm',
    'WindDir3pm',
    'WindSpeed3pm',
    'Pressure3pm',
]

# Column names with added data : Location, RainToday and RainTomorrow
weatherAUS_names_post = \
[
    'Date',
    'Location',
    'MinTemp',
    'MaxTemp',
    'Rainfall',
    'Evaporation',
    'Sunshine',
    'WindGustDir',
    'WindGustSpeed',
    'WindDir9am',
    'WindDir3pm',
    'WindSpeed9am',
    'WindSpeed3pm',
    'Humidity9am',
    'Humidity3pm',
    'Pressure9am',
    'Pressure3pm',
    'Cloud9am',
    'Cloud3pm',
    'Temp9am',
    'Temp3pm',
    'RainToday',
    'RainTomorrow'
]


def merge_cvc_dids(data_path: str) -> pd.DataFrame:
    """
    Merges CodeVilleClimat.csv and DataIds.csv
    """

    cvc = pd.read_csv(os.path.join(data_path, 'CodeVilleClimat.csv'),
                      sep =',')

    dids = pd.read_csv(os.path.join(data_path, 'DataIds.csv'),
                       sep =',')

    cvc = cvc.rename(columns = {'Code':'station_id'})

    # Left merge between CodeVilleClimat and DataIds on column 'station_id'
    return cvc.merge(right = dids, on = 'station_id', how = 'left')


def convert(data_path='./data'):

    """
    "CSV Conversion of monthly Weather Data from the Australian Bureau of Meteorology."
    """

    
    # Merges CodeVilleClimat.csv and DataIds.csv
    cvc_dids = merge_cvc_dids(data_path)

    digest_path = os.path.join(data_path, 'digest')

    pandas_path = os.path.join(data_path, 'pandas')
    pandas_file_name = "weatherAUS.csv"
    pandas_file_path = os.path.join(pandas_path, pandas_file_name)

    csv_list = os.listdir(digest_path)
    csv_list.sort()

    df_total = pd.DataFrame()

    for csv_file_name in csv_list:

        if csv_file_name[-4:] != '.csv':
            continue

        csv_file_path = os.path.join(digest_path, csv_file_name)
        print("Processing {}".format(csv_file_name))

        data_id = csv_file_name[:csv_file_name.find('.')]

        location = cvc_dids.loc[cvc_dids['data_id'] == data_id]['Location'].values[0]

        df = pd.read_csv(filepath_or_buffer = csv_file_path,
                        sep = ',',
                        encoding='utf_8',
                        header = None,
                        names = acquisition_names,
                        index_col = None,
                        skip_blank_lines = True)[weatherAUS_names_pre]

        # Reformat the date so that sorting gives appropriate result
        df['Date'] = df.apply(lambda row:
                              row['Date'][0:-2] +  '-0' + row['Date'][-1]
                              if row['Date'][-2] == '-'
                              else row['Date'], axis=1)
        df['Location'] = location
        df['RainToday'] = df.apply(lambda row: 'Yes' if row['Rainfall'] >= 1.0 else 'No', axis=1)

        df['RainTomorrow'] = df['RainToday'].shift(-1)

        df = df[weatherAUS_names_post]

        df_total = pd.concat([df_total, df], axis=0, ignore_index=True)

    df_total.sort_values(by=['Location', 'Date'], ascending=[True, True], inplace=True)
    df_total.reset_index(drop=True, inplace=True)

    # Print some information
    print('\n''df_total information :\n')
    print(df_total.info())
    print('\n''df_total head :\n')
    print(df_total.head(10))
    print('\n''df_total tail :\n')
    print(df_total.tail(10))

    # Save final CSV file
    df_total.to_csv(path_or_buf=pandas_file_path,
              index=False)


import pytest
from unittest.mock import patch, Mock, call
import datetime as dt
from weather_utils.acquire_data import acquire, get_stations, get_data_id, get_data, digest

import pytest
from unittest.mock import patch, mock_open
from weather_utils.acquire_data import get_data_id
import csv
from weather_utils.acquire_data import get_stations

def test_get_data_id_success():
  station_id = '066214'
  expected_data_id = 'IDCJDW2124'

  # Contenu simulé de la réponse HTTP
  fake_response_content = (
      'some irrelevant content URL=/climate/dwo/'
      f'{expected_data_id}.latest.txt more irrelevant content'
  ).encode('utf-8')

  with patch('requests.get') as mock_get:
      # Configure le mock pour retourner un objet response avec le contenu simulé
      mock_get.return_value.status_code = 200
      mock_get.return_value.content = fake_response_content

      data_id = get_data_id(station_id)

      assert data_id == expected_data_id
      mock_get.assert_called_once()

def test_get_data_id_no_delimiter():
  station_id = '066214'

  # Contenu simulé sans les délimiteurs attendus
  fake_response_content = 'no delimiters here'.encode('utf-8')

  with patch('requests.get') as mock_get:
      mock_get.return_value.status_code = 200
      mock_get.return_value.content = fake_response_content

      data_id = get_data_id(station_id)

      assert data_id == ''
      mock_get.assert_called_once()

def test_get_data_id_http_error():
  station_id = '066214'

  with patch('requests.get') as mock_get:
      mock_get.return_value.status_code = 404
      mock_get.return_value.content = b''

      data_id = get_data_id(station_id)

      assert data_id == ''
      mock_get.assert_called_once()


def test_get_stations():
  # Données CSV simulées
  fake_csv_content = 'Code,SomeOtherField\n12345,some_value\n67890,another_value\n'

  with patch('builtins.open', mock_open(read_data=fake_csv_content)) as mocked_file:
      with patch('csv.DictReader', wraps=csv.DictReader) as mock_csv_reader:
          stations = get_stations('fake_file_path.csv')

          assert stations == ['12345', '67890']
          mocked_file.assert_called_with('fake_file_path.csv', newline='')
          mock_csv_reader.assert_called()


import os
from weather_utils.acquire_data import get_data

def test_get_data_file_exists():
  data_id = 'IDCJDW2124'
  period = '202309'
  data_path = '/fake_data_path'

  with patch('os.path.isfile') as mock_isfile:
      mock_isfile.return_value = True

      get_data(data_id, period, data_path)

      raw_file_path = os.path.join(data_path, 'raw', f'{data_id}.{period}.csv')
      mock_isfile.assert_called_with(raw_file_path)

def test_get_data_download_and_digest():
  data_id = 'IDCJDW2124'
  period = '202309'
  data_path = '/fake_data_path'
  fake_content = b'some,csv,content\n1,2,3'

  with patch('os.path.isfile') as mock_isfile, \
       patch('requests.get') as mock_get, \
       patch('builtins.open', mock_open()) as mocked_file, \
       patch('weather_utils.acquire_data.digest') as mock_digest:

      mock_isfile.return_value = False
      mock_get.return_value.status_code = 200
      mock_get.return_value.content = fake_content

      get_data(data_id, period, data_path)

      raw_file_path = os.path.join(data_path, 'raw', f'{data_id}.{period}.csv')
      digest_path = os.path.join(data_path, 'digest')

      mock_isfile.assert_called_with(raw_file_path)
      mock_get.assert_called_once()
      mocked_file.assert_called_with(raw_file_path, 'wb')
      mocked_file().write.assert_called_with(fake_content)
      mock_digest.assert_called_with(os.path.join(data_path, 'raw'), digest_path, f'{data_id}.{period}.csv')


def test_digest():
  raw_path = '/fake_raw_path'
  digest_path = '/fake_digest_path'
  csv_file_name = 'test.csv'

  fake_raw_content = (
      '"Some header info"\n'
      '\n'
      ',Header1,Header2,Header3\n'
      'Data1,Data2,Data3\n'
  )

  expected_digest_content = 'Data1,Data2,Data3\n'

  # Simuler l'ouverture de fichiers pour lecture et écriture
  with patch('builtins.open', mock_open(read_data=fake_raw_content)) as mocked_file:
      digest(raw_path, digest_path, csv_file_name)

      # Vérifier que le fichier a été lu correctement
      mocked_file.assert_any_call(os.path.join(raw_path, csv_file_name), mode='r', encoding="cp1252")
      # Vérifier que le fichier a été écrit correctement
      mocked_file.assert_any_call(os.path.join(digest_path, csv_file_name), mode='w', encoding="utf_8")
      handle = mocked_file()
      handle.write.assert_called_with(expected_digest_content)


from weather_utils.acquire_data import acquire

def test_acquire():
  with patch('weather_utils.acquire_data.get_stations') as mock_get_stations, \
       patch('weather_utils.acquire_data.get_data_ids') as mock_get_data_ids, \
       patch('weather_utils.acquire_data.get_data') as mock_get_data:

      mock_get_stations.return_value = ['12345']
      mock_get_data_ids.return_value = [{'station_id': '12345', 'data_id': 'IDCJDW2124'}]

      acquire()

      mock_get_stations.assert_called_once()
      mock_get_data_ids.assert_called_once_with(['12345'], os.path.join('./data', 'DataIds.csv'))
      assert mock_get_data.call_count == 14  # Si vous récupérez 14 mois de données
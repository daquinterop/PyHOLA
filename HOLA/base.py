'''
Diego Quintero - 2021
University of Nevada, Reno
Water and Irrigation Management Lab

Base Classes to download data ussing HOLOGRAM API 
(https://www.hologram.io/references/http#/introduction/authentication)
The project is structured in modules so that it can be easily handled by
any desktop or web-based app
'''

import base64
import requests
from datetime import datetime, timedelta
import json
import base64
import os 
from collections import Counter
import dateutil.parser

class Hologram():
    '''
    Hologram class handles the required data to access to the API,
    and has the methods to retrieve the data.
    --------------------------------------
    '''

    def __init__(self, deviceID, apiKey, orgID, startTime, endTime, recordLimit=1000, isLive=False):
        '''  
        Args:
            recordLimit: int    | Maximum number of records to be obtained
            deviceID: str       | Device ID for 'VRAlfGate'
            isLive: bool        | Only get usage data from live devices (true) or not (false)
            apiKey: str         | API key to use
            orgID: str          | Organization ID 
            startTime: datetime | Start time of the time serie to retrieve
            endTime = datetime  | End time of the time serie to retrieve
        '''
        self.recordLimit = recordLimit
        self.deviceID = deviceID
        self.isLive = isLive
        self.apiKey = apiKey
        self.orgID = orgID
        self.startTime = startTime
        self.endTime = endTime
        self.records = []
        return None
    
    def _urlBuild(self):
        ''' Build the URL to request based on init attributes'''
        self._posix_startTime = int(self.startTime.timestamp())
        self._posix_endTime = int(self.endTime.timestamp())
        return f'https://dashboard.hologram.io/api/1/csr/rdm?orgid={self.orgID}' \
            f'&deviceid={self.deviceID}&timestart={self._posix_startTime}&timeend={self._posix_endTime}' \
            f'&apikey={self.apiKey}&islive={str(self.isLive).lower()}&limit={self.recordLimit}'

    def retrieve(self):
        ''' Retrieve the data for the requested period'''
        # Start downloading data and in case not all the data was retrieve, it'll continue downloading data
        self._data_records = []
        unique_ids = [] # To store ids
        continues = True
        while continues:
            self._response = requests.get(self._urlBuild())
            if self._response.status_code != 200: # Verify if we get a OK status
                raise requests.exceptions.RequestException('Something failed during the requests, make sure all init parameters are well defined')
            self.response_dict = json.loads(self._response.text)
            for record in self.response_dict['data']:
                id = record['record_id']
                if id in unique_ids: # If record is already appended, then continue
                    continue
                else:
                    self._data_records.append(json.loads(record['data']))
                    self._data_records[-1]['data'] = base64.b64decode(self._data_records[-1]['data']).decode('utf8').split('~')
                    self._data_records[-1]['data'].append(id)
                    unique_ids.append(id)
            continues = self.response_dict['continues']
            if continues: # If there is still more data to download
                former_date = self.endTime
                self.endTime = datetime.strptime(self._data_records[-1]['received'][:10], '%Y-%m-%d')
                print(f'Downloaded from {self._data_records[-1]["received"][:10]} to {former_date}')

        # Create a real record object i.e. list of dicts, assigning a number to any of the fields but the id
        for record in self._data_records:
            tmp_data_list = record['data']
            self.records.append(dict(zip(range(len(tmp_data_list) - 1), tmp_data_list[:-1])))
            self.records[-1]['_id'] = tmp_data_list[-1]
        
        # Define the number of fields as the most common number of fields among all the records 
        # (_id not included) and drop records that doesn't match n_records
        self._n_fields = Counter(map(len, self.records)).most_common(1)[0][0] - 1
        self.records = [i for i in self.records[:] if len(i) == (self._n_fields + 1)]

        print(f'Succesfully requested {len(self.records)} records')
        return None

    def save_records(self, filepath, sep=',', colnames=None, append=False, dateSort=None, timeDelta=0, dateFormat='%Y-%m-%d %H:%M:%S'):
        '''
        Save records to a text file.
        Args:
            - filepath: str  | File to write
            - sep: str       | Column separator string
            - colnames: list | Names of the columns or None
            - append: bool   | True if the data will be appended to an existing file
            - dateSort: int  | None or index of the date column to perform sorting
            - timeDelta: int | Hours to add to the raw date in case it's not local time
            - dateFormat str | format to print dates
        '''
        # Raise exception if there are no records to save
        if len(self.records) <= 0:
            raise AttributeError("No record has ben downloaded yet")
        # Raise exception if the file to append to does not exist
        if append:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f'{filepath} does not exist and can not append records to')
        else: # Raise if file exists and append is False
            if os.path.exists(filepath):
                raise FileExistsError(f'{filepath} already exists, enter a different name or append to existing file')
        # Raise exception if the number of columns does not match the existing fields
        if colnames != None:
            if not hasattr(colnames, '__len__'):
                raise TypeError('colnames arg must be a list, tuple, set or any iterable')
            if len(colnames) != self._n_fields:
                raise IndexError(f'colnames does not match with number {self._n_fields} of fields')

        # TODO: Raise exception if the number of fields does not match the columns of the existing file (append mode)

        # Perform sorting
        if dateSort != None:
            if not isinstance(dateSort, int):
                raise TypeError('dateSort argument must be an integer')
            for n, record in enumerate(self.records):
                self.records[n][dateSort] =  dateutil.parser.parse(record[dateSort].replace('_', ' '))
            self.records = sorted(self.records, key=lambda x: x[dateSort])
        
        # Add the timeDelta and convert datetime to string
        for n, record in enumerate(self.records):
            self.records[n][dateSort] =  (record[dateSort] + timedelta(hours=timeDelta)).strftime(dateFormat)
        # Lines to write on the file
        lines = []
        if not append: # If not append, create columns headers
            if colnames == None:
                colnames = list(map(str, self.records[0].keys()))
                colnames = f'{sep}'.join(colnames)
                colnames += '\n'
                lines.append(colnames)
            else:
                colnames = list(map(str, colnames))
                colnames.append('_id\n')
                lines.append(f'{sep}'.join(colnames))

        # All downloaded lines
        lines += list(map(lambda x: f'{sep}'.join(list(x.values())) + '\n', self.records))
        
        # If append, then open file to get existing records, so as not overwrite
        if append:
            f = open(filepath, 'r')
            file_lines = f.readlines()
            f.close()
            # New lines in the file
            lines = [line for line in lines if line not in file_lines]
        # Open and write file
        f = open(filepath, 'a')
        f.writelines(lines)
        f.close()
        print(f'{len(lines)} records written to {filepath}')
        return None
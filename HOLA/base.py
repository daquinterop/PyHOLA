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
from datetime import datetime 
import json
import base64

class Hologram():
    '''
    Hologram class handles the required data to access to the API,
    and has the methods to retrieve the data.
    --------------------------------------
    '''

    def __init__(self, deviceID, apiKey, orgID, startTime, endTime, recordLimit=1000, isLive=False):
        '''  
        Attributes:
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
        self.records = []
        for record in self._data_records:
            tmp_data_list = record['data']
            self.records.append(dict(zip(range(len(tmp_data_list) - 1), tmp_data_list[:-1])))
            self.records[-1]['_id'] = tmp_data_list[-1]

        print(f'Succesfully requested {len(self.records)} records')
        return None


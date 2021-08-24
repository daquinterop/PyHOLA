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
import time 
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
        # Verify if the url is well defined and we get a OK status
        self._response = requests.get(self._urlBuild())
        if self._response.status_code != 200:
            requests.exceptions.RequestException('Something failed during the requests, make sure all init parameters are well defined')
        
        # Download first batch of data
        self.response_dict = json.loads(self._response.text)
        self.data_records = []
        for record in self.response_dict['data']:
            self.data_records.append(json.loads(record['data']))
            self.data_records[-1]['data'] = base64.b64decode(self.data_records[-1]['data']).decode('utf8').split('~') # Get data as a list
            self.data_records[-1]['data'].append(record['record_id']) # Append record id
        
        # In case not all the data was retrieve, it'll continue downloading data
        while self.response_dict['continues']:
            self.startTime = datetime.strptime(self.data_records[0]['received'][:10], '%Y-%m-%d')
            self._response = requests.get(self._urlBuild())
            self.response_dict = json.loads(self._response.text)
            for record in self.response_dict['data']:
                self.data_records.append(json.loads(record['data']))
                self.data_records[-1]['data'] = base64.b64decode(self.data_records[-1]['data']).decode('utf8').split('~')
                self.data_records[-1]['data'].append(record['record_id'])

        self.final_records = []
        for record in self.data_records:
            self.final_records.append(record['data'])

        print(f'Succesfully requested {len(self.final_records)} records')
        

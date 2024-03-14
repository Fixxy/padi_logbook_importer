import requests, json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm

from utils.helpers import get_data_param

LOGIN_HEADERS = {
    "Host": "www.padi.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8,ru;q=0.7,ja;q=0.6,jv;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none"
}
REGULAR_HEADERS = { 'Content-Type': 'application/json' }
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"

class PADI_API:
    def __init__(self):
        self.session = requests.session()
        self.client_id = None
        self.bearer_token = None
        self.affiliate_id = None

        # get client id
        r = self.session.get('https://www.padi.com/', headers=LOGIN_HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        drupal_settings = soup.find_all(attrs={"data-drupal-selector": "drupal-settings-json"})[0]
        drupal_settings_json = json.loads(drupal_settings.text)
        self.client_id = drupal_settings_json['padi_sso']['ssoClientId']

    def __get_auth_header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.bearer_token),
        }

    def __error(self, message):
        print('ERROR: {0}'.format(message))
        quit()

    def __get_affiliation_id(self):
        headers = self.__get_auth_header()
        r = self.session.get('https://ecard.global-prod.padi.com/api/eCard/GeteCardListConsumer', headers=headers, allow_redirects=True)
        json_response = json.loads(r.content)
        if (r.status_code != 200):
            self.__error(json_response['message'])
        return json_response['affiliateSummary']['affiliateID']

    def login(self, username, password):
        login_payload = {
            'clientId':  self.client_id,
            'extraData':  '',
            'password':  password,
            'username':  username,
        }
        r = self.session.post(
            'https://api.global-prod.padi.com/auth/api/oauth/login',
            headers=REGULAR_HEADERS,
            data=json.dumps(login_payload),
            allow_redirects=True
        )
        json_response = json.loads(r.content)

        if (r.status_code != 200):
            self.__error(json_response['message'])

        self.bearer_token = json_response['tokens']['idToken']
        self.affiliate_id = self.__get_affiliation_id()

    # creating an empty base entry
    def __create_basic_dive_entry(self, data):
        created_date = datetime.now().strftime(DATE_FORMAT)
        minimum_dive_data = {"query":"mutation insert_logbook_logs($general: [logbook_logs_insert_input!]!) {\n  insert_logbook_logs(objects: $general) {\n    affected_rows\n    returning {\n      id\n      affiliate_id\n      dive_title\n      dive_type\n      dive_location\n      log_type\n      log_course\n      dive_date\n      created_date\n      status\n      adventure_dive\n    }\n  }\n}","variables":{"general":{"affiliate_id":self.affiliate_id,"log_type":"Recreational","created_date":created_date,"dive_type":data.dive_type,"dive_title":data.dive_title,"dive_location":data.dive_location,"dive_date":data.date,"status":"Publish"}}}
        r = self.session.post(
            'https://logbook.global-prod.padi.com/api/Logbook',
            headers=self.__get_auth_header(),
            data=json.dumps(minimum_dive_data),
            allow_redirects=True
        )

        response = json.loads(r.content)
        if 'errors' in response:
            self.__error(response['errors'][0]['message'])

        created_entry_data = response['data']['insert_logbook_logs']['returning'][0]
        self.last_dive_entry_id = int(created_entry_data['id'])

    # populating empty entry with data
    def __populate_dive_entry(self, data):
        data_structure = {
            'depthTime': ["bottom_time", "max_depth"],
            'conditions': ["water_type", "body_of_water", "weather", "air_temp", "surface_water_temp", "bottom_water_temp", "visibility", "visibility_distance", "wave_condition", "current", "surge"],
            'equipment': ["starting_pressure","ending_pressure","suit_type","weight","weight_type","additional_equipment","cylinder_type","cylinder_size","gas_mixture","oxygen","nitrogen","helium"],
            'experience': ["feeling", "notes", "buddies", "dive_center"]
        }

        variables = {}

        for key in data_structure:
            if key not in variables: variables[key] = {}
            columns = data_structure[key]
            variables[key]['logs_id'] = self.last_dive_entry_id # default param, which should be in every section
            for el in columns:
                value = get_data_param(data, el)
                if (el == 'additional_equipment'): value = '{%s}' % value # edge case for additional equipment array
                if value != None and str(value) != 'nan': variables[key][el] = value

        all_dive_data = {"query":"mutation RemainingSection($depthTime: [logbook_depth_time_insert_input!]!, $conditions: [logbook_conditions_insert_input!]!, $equipment: [logbook_equipment_insert_input!]!, $experience: [logbook_experience_insert_input!]!) {\n  insert_logbook_depth_time(objects: $depthTime) {\n    affected_rows\n  }\n  insert_logbook_conditions(objects: $conditions) {\n    affected_rows\n  }\n  insert_logbook_equipment(objects: $equipment) {\n    affected_rows\n  }\n  insert_logbook_experience(objects: $experience) {\n    affected_rows\n  }\n}","variables":variables}

        r = self.session.post(
            'https://logbook.global-prod.padi.com/api/Logbook',
            headers=self.__get_auth_header(),
            data=json.dumps(all_dive_data),
            allow_redirects=True
        )
        response = json.loads(r.content)
        if 'errors' in response:
            self.__error(response['errors'][0]['message'])

    # add a single dive entry
    def __add_dive(self, data):
        self.__create_basic_dive_entry(data)
        self.__populate_dive_entry(data)

    # add all the dives from the log file
    def add_dives(self, file_path, data_format):
        if (data_format == 'custom_csv'):
            df = pd.read_csv(file_path) 
            # reformat date into padi format
            df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y').dt.strftime('%m/%d/%Y')

            for index, data in tqdm(df.iterrows(), total=df.shape[0]):
                self.__add_dive(data)
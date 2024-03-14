import requests, json
from bs4 import BeautifulSoup

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

class PADI_API:
    def __init__(self, data_format):
        self.session = requests.session()
        self.client_id = None
        self.bearer_token = None
        self.data_format = data_format

        # get client id
        r = self.session.get('https://www.padi.com/', headers=LOGIN_HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        drupal_settings = soup.find_all(attrs={"data-drupal-selector": "drupal-settings-json"})[0]
        drupal_settings_json = json.loads(drupal_settings.text)
        self.client_id = drupal_settings_json['padi_sso']['ssoClientId']

    def __error(self, message):
        print('ERROR: {0}'.format(message))
        quit()

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

    def __create_basic_dive_entry(self, headers):

        #TODO: affiliate_id?
        #TODO: created_date?

        # first request to create a new entry
        minimum_dive_data = {"query":"mutation insert_logbook_logs($general: [logbook_logs_insert_input!]!) {\n  insert_logbook_logs(objects: $general) {\n    affected_rows\n    returning {\n      id\n      affiliate_id\n      dive_title\n      dive_type\n      dive_location\n      log_type\n      log_course\n      dive_date\n      created_date\n      status\n      adventure_dive\n    }\n  }\n}","variables":{"general":{"affiliate_id":"28140789","log_type":"Recreational","created_date":"2024-03-14T09:09:43.449Z","dive_type":"Boat","dive_title":"dive title","dive_location":"dive site","dive_date":"03/14/2024","status":"Publish"}}}
        r = self.session.post(
            'https://logbook.global-prod.padi.com/api/Logbook',
            headers=headers,
            data=json.dumps(minimum_dive_data),
            allow_redirects=True
        )

        response = json.loads(r.content)
        if 'errors' in response:
            self.__error(response['errors'][0]['message'])

        created_entry_data = response['data']['insert_logbook_logs']['returning'][0]
        self.last_dive_entry_id = int(created_entry_data['id'])

    def __populate_dive_entry(self, headers):
        # second request to populate it with data
        minimum_dive_data = {"query":"mutation RemainingSection($depthTime: [logbook_depth_time_insert_input!]!, $conditions: [logbook_conditions_insert_input!]!, $equipment: [logbook_equipment_insert_input!]!, $experience: [logbook_experience_insert_input!]!) {\n  insert_logbook_depth_time(objects: $depthTime) {\n    affected_rows\n  }\n  insert_logbook_conditions(objects: $conditions) {\n    affected_rows\n  }\n  insert_logbook_equipment(objects: $equipment) {\n    affected_rows\n  }\n  insert_logbook_experience(objects: $experience) {\n    affected_rows\n  }\n}","variables":{"depthTime":{"bottom_time":"50","max_depth":"39","logs_id":self.last_dive_entry_id},"conditions":{"water_type":"Salt","body_of_water":"Ocean","weather":"Sunny","air_temp":"32","surface_water_temp":None,"bottom_water_temp":"27","visibility":"Average","visibility_distance":"20","wave_condition":"MediumWaves","current":"MediumCurrent","surge":None,"logs_id":self.last_dive_entry_id},"equipment":{"starting_pressure":"210","ending_pressure":"50","suit_type":"FullSuit_5mm","weight":"10","weight_type":"Good","additional_equipment":"{Gloves,Boots}","cylinder_type":"Aluminum","cylinder_size":"12","gas_mixture":"Enriched","oxygen":"32","nitrogen":"68","helium":"0","logs_id":self.last_dive_entry_id},"experience":{"feeling":"Good","notes":"here is a diving note","buddies":"Marina","dive_center":"Sadko","logs_id":self.last_dive_entry_id}}}
        r = self.session.post(
            'https://logbook.global-prod.padi.com/api/Logbook',
            headers=headers,
            data=json.dumps(minimum_dive_data),
            allow_redirects=True
        )
        response = json.loads(r.content)
        if 'errors' in response:
            self.__error(response['errors'][0]['message'])
        print(r.content)

    def add_dive(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.bearer_token),
        }
        self.__create_basic_dive_entry(headers)
        self.__populate_dive_entry(headers)
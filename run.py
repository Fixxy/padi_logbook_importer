from argparse import ArgumentParser
from padi.api import PADI_API

parser = ArgumentParser()
parser.add_argument("-u", "--username", required=True, help="username / email address")
parser.add_argument("-p", "--password", required=True, help="password")
parser.add_argument("-f", "--file", required=True, help="spreadsheet to be imported")
parser.add_argument("-t", "--type", help="data type", choices=['custom_csv'], default='custom_csv')
args = parser.parse_args()

padi_api = PADI_API()
padi_api.login(args.username, args.password)
padi_api.add_dives(args.file, args.type)
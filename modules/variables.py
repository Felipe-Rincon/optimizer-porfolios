import os 

path_core = os.getcwd().replace("\\","/")

class Variables_user:
    route_yaml = path_core + "/modules/user_data.yaml"
    authentication_status = 'authentication_status'
    credentials = 'credentials'
    usernames = 'usernames'
    username = 'username'
    password = 'password'
    name = 'name'

class Variables_asset_values:
    historical_returns = 'historical_returns'
    expected_return = 'expected_return'
    name = 'name'
    day = 'day'


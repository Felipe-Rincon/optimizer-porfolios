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
    performance = 'Return'
    volatility = 'Volatility'
    downside_risk = 'Downside Risk'
    portfolios = 'portfolios'
    portfolio = 'portfolio'

class Variables_user_management:
    authentication_status = 'authentication_status'
    username = 'username'
    totp_verified = 'totp_verified'
    totp_secret = 'totp_secret'
    secret_key = 'secret_key'
    qr_png = 'qr.png'
    show_qr = 'show_qr'

class Variables_front:
    name_app = 'Asset Optimizer'
    login = 'Login'
    user = 'User'
    password = 'Password'
    firt_loging_qr = 'It\'s your first time logging in. Scan the QR code with Google Authenticator.'
    logout = 'Logout'
    scan_qr = 'Scan this QR code with Google Authenticator'
    valid_totp = 'Valid code. Successful login!'
    invalid_totp = 'Invalid code.'
    enter_code = 'Please enter the Google Authenticator code.'
    verification_code = 'Verification code:'
    verify_code = 'Verify Code'
    optimize = 'Optimize'
    optimizing = 'Optimizing...'
    upload_excel_file = 'Upload Excel file'
    upload_data = 'Upload Data'
    values_title = 'Values'
    singular_constrains_title = 'Singular Constrains'
    grouped_constrains_title = 'Grouped Constrains'
    values_constrains_title = 'Values Constrains'
    optimization_results_title= 'Optimization Results.'
    two_dimensions_graphics_title = '2D Graphics'
    three_dimensions_graphics_title = '3D Graphics'
    portfolio_weights_title = 'Portfolio Weights:'
    portfolio_metrics_title = 'Portfolio Metrics:'
    incorrect_credentials = 'Incorrect username or password'
    try_again = 'Try again.' 
    welcome_to = 'Welcome to'


class Variables_data_up:
    values_name_sheet = 'values'
    singular_constrains_name_sheet = 'singular_constrains'
    grouped_constrains_name_sheet = 'grouped_constrains'
    values_constrains_name_sheet = 'values_constrains'


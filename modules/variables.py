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
    duration = 'duration'
    expected_return_forecast = 'expected_return_forecast'

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
    portfolio_all_metrics_title = 'Portfolio All Metrics:'
    incorrect_credentials = 'Incorrect username or password'
    try_again = 'Try again.' 
    welcome_to = 'Welcome to'
    variable_x ='Variable X'
    variable_y ='Variable Y'
    variable_z ='Variable Z'
    metric_variable_x = 'Metric for Variable X'
    metric_variable_y = 'Metric for Variable Y'
    metric_variable_z = 'Metric for Variable Z'
    select_metrics ='Select the metrics for each variable'
    portofolio_yield_base_100 = 'Portfolio Yield (NAV base 100)'
    upload_weights_porfolios= 'Upload weights of portfolios'
    upload_asset_prices = 'Upload asset prices'
    backtesting_title = "Backtesting"
    select_portfolio = 'Select a portfolio'
    start_backtesting = 'Start Backtesting'
    date = 'Date'
    frequency = 'Frequency'
    yield_histograms_title = 'Yield Histograms'
    portfolio_drawdown_title = 'Portfolio Drawdown'
    daily_histogram_title = '**Daily Histogram**'
    distribution_daily_yields = 'Distribution of Daily Yields (%)'
    yield_label = 'Yield (%)'
    monthly_histogram_title= '**Monthly Histogram**'
    distribution_monthly_yields = 'Distribution of Monthly Yields (%)'
    quarterly_histogram_title = '**Quarterly Histogram**'
    distribution_quarterly_yields = 'Quarterly Yield Distribution (%)'
    annual_histogram_title = '**Annual Histogram**'
    distribution_annual_yields = 'Distribution of Annual Returns (%)'

    names_to_front = {
        "Expected Return": "Expected Return",
        "Expected Return Forecast": "Expected Return Forecast",
        "Volatility": "Volatility",
        "Downside Risk": "Downside Risk",
        "Maximum Drawdown": "Maximum Drawdown",
        "Duration": "Duration",
        "Sharpe Ratio" : "Sharpe Ratio",
        "Sortino Ratio": "Sortino Ratio"
    }

class Variables_data_up:
    values_name_sheet = 'values'
    singular_constrains_name_sheet = 'singular_constrains'
    grouped_constrains_name_sheet = 'grouped_constrains'
    values_constrains_name_sheet = 'values_constrains'
    other_info_name_sheet = 'other_info'

class Variables_mapping_optimization:

    names_to_mapping = {
        "Expected Return": "ExpectedReturnFunction()",
        "Volatility": "VolatilityFunction()",
        "Downside Risk": "DownsideRiskFunction()",
        "Maximum Drawdown": "MaxDrawdownFunction()",
        "Sortino Ratio": "SortinoRatioFunction()",
        "Sharpe Ratio": "SharpeRatioFunction()"
    }


class Variables_mapping_optimization_blacklitterman:

    names_to_mapping = {
        "Expected Return Forecast": "ExpectedReturnForecastFunction()",
        "Volatility": "VolatilityFunction()",
        "Downside Risk": "DownsideRiskFunction()",
        "Maximum Drawdown": "MaxDrawdownFunction()",
        "Sortino Ratio": "SortinoRatioFunction()",
        "Sharpe Ratio": "SharpeRatioFunction()"
    }


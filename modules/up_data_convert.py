import pandas as pd

from modules.variables import Variables_asset_values

def asset_values_generator(df, df_metrics):

    if df_metrics.index.name != 'metric':
        df_metrics.set_index('metric', inplace=True)

    df.set_index(Variables_asset_values.day, inplace=True)

    returns = df.pct_change().dropna()

    assetValues = []
    for column in df.columns:
        expected_return = (1 + returns[column].mean()) ** 365 - 1
        duration = df_metrics.loc['duration', column]
        expected_return_forecast = df_metrics.loc['expected_return_forecast', column]
        asset_data = {
            Variables_asset_values.name: column,
            Variables_asset_values.expected_return: expected_return,
            Variables_asset_values.historical_returns: returns[column].tolist(),
            Variables_asset_values.duration: duration,
            Variables_asset_values.expected_return_forecast: expected_return_forecast
        }
        assetValues.append(asset_data)
    
    return assetValues

def asset_values_generator_2(df):

    df.set_index(Variables_asset_values.day, inplace=True)

    returns = df.pct_change().dropna()

    assetValues = []
    for column in df.columns:
        expected_return = (1 + returns[column].mean()) ** 365 - 1

        asset_data = {
            Variables_asset_values.name: column,
            Variables_asset_values.expected_return: expected_return,
            Variables_asset_values.historical_returns: returns[column].tolist(),

        }
        assetValues.append(asset_data)
    
    return assetValues

def constrains_generator(df_singular_contrains, df_grouped_constrains, df_values_constrains):

    asset_to_index = {asset: i for i, asset in enumerate(df_singular_contrains['asset'])}

    # Construcción del diccionario final
    portfolioConstraints = {
        'single': [
            {'asset': row['asset'], 
            'min_weight': df_values_constrains.loc[df_values_constrains['constrains'] == row['r'], 'min'].values[0], 
            'max_weight': df_values_constrains.loc[df_values_constrains['constrains'] == row['r'], 'max'].values[0]}
            for _, row in df_singular_contrains.iterrows()
        ],
        'grouped': []
    }

    # Construcción de restricciones conjuntas
    for rc, group in df_grouped_constrains.groupby('rc'):
        min_w = df_values_constrains.loc[df_values_constrains['constrains'] == rc, 'min'].values[0]
        max_w = df_values_constrains.loc[df_values_constrains['constrains'] == rc, 'max'].values[0]
        indexes = [asset_to_index[asset] for asset in group['asset']]
        portfolioConstraints['grouped'].append({
            'indexes': indexes, 
            'min_weight': min_w, 
            'max_weight': max_w
        })

    # Resultado final
    return portfolioConstraints
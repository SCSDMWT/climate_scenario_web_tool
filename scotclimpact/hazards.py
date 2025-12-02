from . import extreme_temp

'''
A dictionary containing functions that calculate hazard data.
The values are names used by routes.py and db.py to find a relavant
function. Values are dictionaries and must contain the following:

'''
hazards = {
    'extreme_temp_intensity': dict(
        function=extreme_temp.intensity_from_return_time,
        ci_report_function=extreme_temp.intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=54, y=54),
    ),
    'extreme_temp_intensity_change': dict(
        function=extreme_temp.change_in_intensity,
        ci_report_function=extreme_temp.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        arg_names=['return_time', 'covariate', 'covariate_comp'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
    ),
    'extreme_temp_return_time': dict(
        function=extreme_temp.return_time_from_intensity,
        ci_report_function=extreme_temp.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(30, 41)),
        ],
        result_grid_size=dict(x=54, y=54),
    ),
    'extreme_temp_frequency_change': dict(
        function=extreme_temp.change_in_frequency,
        ci_report_function=extreme_temp.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        arg_names=['intensity', 'covariate', 'covariate_comp'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(30, 41)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
    ),
}

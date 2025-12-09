from . import developing_process


ui_selection = {
    "extreme_temp": dict(
        ui_label="Extreme Temperature",
        calculations=dict(
            intensity="extreme_temp_intensity",
            intensity_change="extreme_temp_intensity_change",
            return_time="extreme_temp_return_time",
            frequency_change="extreme_temp_frequency_change",
        ),
    ),
}

'''
A dictionary containing functions that calculate hazard data.
The values are names used by routes.py and db.py to find a relavant
function. Values are dictionaries and must contain the following:

'''
hazards = {
    ## Extreme temperatures
    'extreme_temp_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        calculation_dropdown_label="Hottest temperature expected to be exceeded in # years.",
        calculation_description_template="<p>Intensity shows the hottest temperature that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Set the return time (in years) to visualise the 1-in-# year extreme:'],
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[25, 27, 29, 31, 33, 35, 37, 39],
            # Colorbrewer YlOrBr-9
            colors=["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#993404", "#662506"],
            endpoint_type="out_of_range",
            decimal_places=0,
            label="Legend (in °C):",
        ),
    ),
    'extreme_temp_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in hottest temperature expected in # years.",
        calculation_description_template="<p>Change in Intensity shows the change in the hottest temperature that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to a global warming level of +{covariate_comp} °C.</p>",
        arg_labels=['Set the return time (in years) to visualise the 1-in-# year extreme:', '', ''],
        arg_names=['return_time', 'covariate', 'covariate_comp'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            colors=["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            endpoint_type="lower_in_range",
            decimal_places=1,
            label="Legend:",
        ),
    ),
    'extreme_temp_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        calculation_dropdown_label="Expected return time of hottest temperature.",
        arg_labels=['', 'Hottest temperature (in °C):'],
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(30, 41)),
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[0, 10, 25, 50, 100, 200],
            # Colorbrewer YlOrBr-6
            colors=list(reversed(["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ])),
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (in years):",
        ),
    ),
    'extreme_temp_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in frequency of hottest temperature.",
        arg_labels=['Hottest temperature (in °C):', '', ''],
        arg_names=['intensity', 'covariate', 'covariate_comp'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(30, 41)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            # Colorbrewer YlOrBr-6
            colors=["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ],
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend:",
        ),
    ),
    ## Sustained cold temperatures
    'sustained_3day_Tmin_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/3day_Tmin_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
    ),
    'sustained_3day_Tmin_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/3day_Tmin_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        arg_names=['return_time', 'covariate', 'covariate_comp'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
    ),
    'sustained_3day_Tmin_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/3day_Tmin_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(14, 21)),
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
    ),
    'sustained_3day_Tmin_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/3day_Tmin_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        arg_names=['intensity', 'covariate', 'covariate_comp'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(14, 21)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
    ),
    ## Extreme 1 day precipitation
    'extreme_1day_precip_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    'extreme_1day_precip_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        arg_names=['return_time', 'covariate', 'covariate_comp'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    'extreme_1day_precip_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(50, 175, 25)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    'extreme_1day_precip_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        arg_names=['intensity', 'covariate', 'covariate_comp'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            #list(range(30, 41)),
            list(range(50, 175, 25)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    ## Extreme 3 day precipitation
    'extreme_3day_precip_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    'extreme_3day_precip_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        arg_names=['return_time', 'covariate', 'covariate_comp'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    'extreme_3day_precip_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(50, 175, 25)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
    'extreme_3day_precip_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        arg_names=['intensity', 'covariate', 'covariate_comp'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(50, 175, 25)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Comparitave Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
    ),
}


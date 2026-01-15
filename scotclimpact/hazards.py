from . import developing_process


ui_selection = {
    "extreme_temp": dict(
        ui_label="Extreme Heat",
        calculations=dict(
            intensity="extreme_temp_intensity",
            intensity_change="extreme_temp_intensity_change",
            return_time="extreme_temp_return_time",
            frequency_change="extreme_temp_frequency_change",
        ),
    ),
    "sustained_3day_Tmin": dict(
        ui_label="Sustained heat threshold for hot nights",
        calculations=dict(
            intensity="sustained_3day_Tmin_intensity",
            intensity_change="sustained_3day_Tmin_intensity_change",
            return_time="sustained_3day_Tmin_return_time",
            frequency_change="sustained_3day_Tmin_frequency_change",
        ),
    ),
    "extreme_1day_precip": dict(
        ui_label="Highest 1-day rainfall",
        calculations=dict(
            intensity="extreme_1day_precip_intensity",
            intensity_change="extreme_1day_precip_intensity_change",
            return_time="extreme_1day_precip_return_time",
            frequency_change="extreme_1day_precip_frequency_change",
        ),
    ),
    "extreme_3day_precip": dict(
        ui_label="Highest 3-day rainfall",
        calculations=dict(
            intensity="extreme_3day_precip_intensity",
            intensity_change="extreme_3day_precip_intensity_change",
            return_time="extreme_3day_precip_return_time",
            frequency_change="extreme_3day_precip_frequency_change",
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
        intensityUnits=u"\u00b0C",
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
        arg_names=['return_time', 'covariate_comp', 'covariate'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='GEV_covaraite_fit_%s_tasmax_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            colors=["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            endpoint_type="lower_in_range",
            decimal_places=1,
            label="Legend (in °C):",
        ),
    ),
    'extreme_temp_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_temp_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        calculation_dropdown_label="Expected return time of hottest temperature.",
        calculation_description_template="<p>Shows the number of years in which the hottest temperature of {intensity} °C is expected to be exceeded at least once at a global temperature anomaly of +{covariate} °C compared to the pre-industrial average.</p>",
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
        calculation_description_template="<p>Change in Frequency shows how many times more frequent the hottest temperature of {intensity} °C is expected to be seen at a global temperature anomaly of +{covariate_comp) °C compared to a global temperature anomaly +{covariate} °C.</p>",
        arg_labels=['Hottest temperature (in °C):', '', ''],
        arg_names=['intensity', 'covariate_comp', 'covariate'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(30, 41)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
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
            label="Legend (times more frequent):",
        ),
    ),
    ## Sustained cold temperatures
    'sustained_3day_Tmin_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/sustained_3day_Tmin_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        calculation_dropdown_label="Highest 3-day sustained heat expected to be exceeded in # years.",
        calculation_description_template="<p>Intensity shows the highest 3-day sustained haet that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Set the return time (in years) to visualise the 1-in-# year extreme:'],
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='exclude_GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        intensityUnits=u"\u00b0C",
        legend=dict(
            edges=[14, 15, 16, 17, 18, 19, 20, 21],
            # Colorbrewer YlOrBr-9
            colors=["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#993404", "#662506"],
            endpoint_type="out_of_range",
            decimal_places=0,
            label="Legend (in °C):",
        ),
    ),
    'sustained_3day_Tmin_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/sustained_3day_Tmin_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in highest 3-day sustained heat expected in # years",
        calculation_description_template="<p>Change in Intensity shows the change in the highest 3-day sustained heat that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to a global warming level of +{covariate_comp} °C.</p>",
        arg_labels=['Set the return time (in years) to visualise the 1-in-# year extreme:', '', ''],
        arg_names=['return_time', 'covariate_comp', 'covariate'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='exclude_GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            colors=["#ffffe5", "#fff7bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
            endpoint_type="lower_in_range",
            decimal_places=1,
            label="Legend (in °C):",
        ),
    ),
    'sustained_3day_Tmin_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/sustained_3day_Tmin_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        calculation_dropdown_label="Expected return time of highest 3-day sustained heat.",
        calculation_description_template="<p>Shows the number of years in which the highest 3-day sustained heat of {intensity} °C is expected to be exceeded at least once at a global temperature anomaly of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Highest 3-day sustained heat (in °C):'],
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(14, 21)),
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='exclude_GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[0, 10, 25, 50, 100, 200],
            # Colorbrewer YlOrBr-7
            colors=list(reversed(["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ])),
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (in years):",
        ),
    ),
    'sustained_3day_Tmin_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/sustained_3day_Tmin_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in frequency of highest 3-day sustained heat.",
        calculation_description_template="<p>Change in Frequency shows how many times more frequent the highest 3-day sustained heat of {intensity} °C is expected to be seen at a global temperature anomaly of +{covariate_comp) °C compared to a global temperature anomaly +{covariate} °C.</p>",
        arg_labels=['Highest 3-day sustained heat (in °C):', '', ''],
        arg_names=['intensity', 'covariate_comp', 'covariate'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(14, 21)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=54, y=54),
        model_file='exclude_GEV_covaraite_fit_%s_max_3day_tasmin_linear_loc_log_scale_nFits_1000_parametric_False.nc',
        grid_size=12,
        legend=dict(
            edges=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            # Colorbrewer YlOrBr-7
            colors=["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#d95f0e", "#993404" ],
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (times more frequent):",
        ),
    ),
    ## Extreme 1 day precipitation
    'extreme_1day_precip_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        calculation_dropdown_label="Highest 1-day rainfall expected to be exceeded in # years.",
        calculation_description_template="<p>Intensity shows the highest 1-day rainfall that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Set the return time (in years) to visualise the 1-in-# year extreme:'],
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        intensityUnits="mm",
        legend=dict(
            edges=[50, 75, 100, 125, 150],
            # Colorbrewer PuBu-6
            colors=['#f1eef6', '#d0d1e6', '#a6bddb', '#74a9cf', '#2b8cbe', '#045a8d'],
            endpoint_type="out_of_range",
            decimal_places=0,
            label="Legend (in mm):",
        ),
    ),
    'extreme_1day_precip_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in highest 1-day rainfall expected in # years.",
        calculation_description_template="<p>Change in Intensity shows the change in the highest 1-day rainfall that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to a global warming level of +{covariate_comp} °C.</p>",
        arg_labels=['Set the return time (in years) to visualise the 1-in-# year extreme:', '', ''],
        arg_names=['return_time', 'covariate_comp', 'covariate'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        legend=dict(
            edges=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            # Colorbrewer PuBu-8
            colors=["#fff7fb", "#ece7f2", "#d0d1e6", "#a6bddb", "#74a9cf", "#3690c0", "#0570b0", "#034e7b"],
            endpoint_type="lower_in_range",
            decimal_places=1,
            label="Legend (in mm):",
        ),
    ),
    'extreme_1day_precip_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        calculation_dropdown_label="Expected return time of highest 1-day rainfall.",
        calculation_description_template="<p>Shows the number of years in which the highest 1-day rainfall of {intensity} mm is expected to be exceeded at least once at a global temperature anomaly of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Highest 1-day rainfall (in mm):'],
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(50, 175, 25)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        legend=dict(
            edges=[0, 10, 25, 50, 100, 200],
            # Colorbrewer PuBu-6
            colors=list(reversed(["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"])),
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (in years):",
        ),
    ),
    'extreme_1day_precip_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/extreme_1day_precip_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in frequency of highest 1-day rainfall.",
        calculation_description_template="<p>Change in Frequency shows how many times more frequent the highest 1-day rainfall of {intensity} mm is expected to be seen at a global temperature anomaly of +{covariate_comp) °C compared to a global temperature anomaly +{covariate} °C.</p>",
        arg_labels=['Highest 1-day rainfall (in mm):', '', ''],
        arg_names=['intensity', 'covariate_comp', 'covariate'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            #list(range(30, 41)),
            list(range(50, 175, 25)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_1day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        legend=dict(
            edges=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            # Colorbrewer PuBu-6
            colors=["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"],
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (times more frequent):",
        ),
    ),
    ## Extreme 3 day precipitation
    'extreme_3day_precip_intensity': dict(
        function=developing_process.intensity_from_return_time,
        ci_report_function=developing_process.intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_intensity/{x}/{y}?covariate={covariate}&return_time={return_time}',
        calculation_dropdown_label="Highest 3-day rainfall expected to be exceeded in # years.",
        calculation_description_template="<p>Intensity shows the highest 3-day rainfall that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Set the return time (in years) to visualise the 1-in-# year extreme:'],
        arg_names=['covariate', 'return_time'],
        arg_types=dict(covariate=float, return_time=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(10, 110, 10)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        intensityUnits="mm",
        legend=dict(
            edges=[50, 75, 100, 125, 150],
            # Colorbrewer PuBu-6
            colors=['#f1eef6', '#d0d1e6', '#a6bddb', '#74a9cf', '#2b8cbe', '#045a8d'],
            endpoint_type="out_of_range",
            decimal_places=0,
            label="Legend (in mm):",
        ),
    ),
    'extreme_3day_precip_intensity_change': dict(
        function=developing_process.change_in_intensity,
        ci_report_function=developing_process.change_in_intensity_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_intensity_change/{x}/{y}?covariate={covariate}&return_time={return_time}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in highest 3-day rainfall expected in # years.",
        calculation_description_template="<p>Change in Intensity shows the change in the highest 3-day rainfall that is expected to be seen in {return_time} years at a global warming level of +{covariate} °C compared to a global warming level of +{covariate_comp} °C.</p>",
        arg_labels=['Set the return time (in years) to visualise the 1-in-# year extreme:', '', ''],
        arg_names=['return_time', 'covariate_comp', 'covariate'],
        arg_types=dict(return_time=int, covariate=float, covariate_comp=float),
        args=[
            list(range(10, 110, 10)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        legend=dict(
            edges=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            # Colorbrewer PuBu-8
            colors=["#fff7fb", "#ece7f2", "#d0d1e6", "#a6bddb", "#74a9cf", "#3690c0", "#0570b0", "#034e7b"],
            endpoint_type="lower_in_range",
            decimal_places=1,
            label="Legend (in mm):",
        ),
    ),
    'extreme_3day_precip_return_time': dict(
        function=developing_process.return_time_from_intensity,
        ci_report_function=developing_process.return_time_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_return_time/{x}/{y}?covariate={covariate}&intensity={intensity}',
        calculation_dropdown_label="Expected return time of highest 3-day rainfall.",
        calculation_description_template="<p>Shows the number of years in which the highest 3-day rainfall of {intensity} mm is expected to be exceeded at least once at a global temperature anomaly of +{covariate} °C compared to the pre-industrial average.</p>",
        arg_labels=['', 'Highest 3-day rainfall (in mm):'],
        arg_names=['covariate', 'intensity'],
        arg_types=dict(covariate=float, intensity=int),
        args=[
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
            list(range(100, 275, 25)),
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        legend=dict(
            edges=[0, 10, 25, 50, 100, 200],
            # Colorbrewer PuBu-6
            colors=list(reversed(["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"])),
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (in years):",
        ),
    ),
    'extreme_3day_precip_frequency_change': dict(
        function=developing_process.change_in_frequency,
        ci_report_function=developing_process.change_in_frequency_ci_report,
        ci_report_url = 'data/ci_report/extreme_3day_precip_frequency_change/{x}/{y}?covariate={covariate}&intensity={intensity}&covariate_comp={covariate_comp}',
        calculation_dropdown_label="Change in frequency of highest 3-day rainfall.",
        calculation_description_template="<p>Change in Frequency shows how many times more frequent the highest 3-day rainfall of {intensity} mm is expected to be seen at a global temperature anomaly of +{covariate_comp) °C compared to a global temperature anomaly +{covariate} °C.</p>",
        arg_labels=['Highest 3-day rainfall (in mm):', '', ''],
        arg_names=['intensity', 'covariate_comp', 'covariate'],
        arg_types=dict(intensity=int, covariate=float, covariate_comp=float),
        args=[
            list(range(100, 275, 25)),
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5], # Comparitave Covariate/Global temperature anomaly
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], # Covariate/Global temperature anomaly
        ],
        result_grid_size=dict(x=120, y=170),
        model_file='smoothed_GEV_covaraite_fit_%s_3day_precip_max_log_loc_scale_nFits_1000_parametric_False.nc',
        grid_size=5,
        legend=dict(
            edges=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            # Colorbrewer PuBu-6
            colors=["#f1eef6", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe", "#045a8d"],
            endpoint_type="lower_in_range",
            decimal_places=0,
            label="Legend (times more frequent):",
        ),
    ),
}


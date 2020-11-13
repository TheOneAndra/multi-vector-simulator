import pandas as pd
import pytest

import multi_vector_simulator.C0_data_processing as C0

from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    ENERGY_PROVIDERS,
    ENERGY_STORAGE,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    ENERGY_CONVERSION,
    ENERGY_BUSSES,
    OUTFLOW_DIRECTION,
    INFLOW_DIRECTION,
    PROJECT_DURATION,
    DISCOUNTFACTOR,
    OPTIMIZE_CAP,
    MAXIMUM_CAP,
    INSTALLED_CAP,
    FILENAME,
    PEAK_DEMAND_PRICING,
    AVAILABILITY_DISPATCH,
    OEMOF_ASSET_TYPE,
    INFLOW_DIRECTION,
    OUTFLOW_DIRECTION,
    EFFICIENCY,
    TAX,
    AGE_INSTALLED,
    VALUE,
    LABEL,
    DISPATCH_PRICE,
    SPECIFIC_COSTS_OM,
    DEVELOPMENT_COSTS,
    SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
    SPECIFIC_COSTS,
    LIFETIME,
    SIMULATION_SETTINGS,
    EVALUATED_PERIOD,
    START_DATE,
    END_DATE,
    TIMESTEP,
    TIME_INDEX,
    ANNUITY_FACTOR,
    SIMULATION_ANNUITY,
    LIFETIME_SPECIFIC_COST,
    TIMESERIES_PEAK,
    CRF,
    ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
    LIFETIME_SPECIFIC_COST_OM,
    LIFETIME_PRICE_DISPATCH,
    PERIODS,
    UNIT_MINUTE,
    ENERGY_VECTOR,
    ASSET_DICT,
)


def test_add_economic_parameters():
    economic_parameters = {
        PROJECT_DURATION: {VALUE: 20},
        DISCOUNTFACTOR: {VALUE: 0.15},
    }
    C0.add_economic_parameters(economic_parameters)
    # the actual value of the annuity factor should have been checked in C2
    for k in (ANNUITY_FACTOR, CRF):
        assert (
            k in economic_parameters.keys()
        ), f"Function does not add {k} to the economic parameters."


settings = {EVALUATED_PERIOD: {VALUE: 365}}

economic_data = {
    PROJECT_DURATION: {VALUE: 20},
    ANNUITY_FACTOR: {VALUE: 1},
    CRF: {VALUE: 1},
    DISCOUNTFACTOR: {VALUE: 0},
    TAX: {VALUE: 0},
}

dict_asset = {
    SPECIFIC_COSTS_OM: {VALUE: 1, UNIT: "a_unit"},
    CRF: {VALUE: 1},
    SPECIFIC_COSTS: {VALUE: 1, UNIT: "a_unit"},
    DISPATCH_PRICE: {VALUE: 1},
    DEVELOPMENT_COSTS: {VALUE: 1},
    LIFETIME: {VALUE: 20},
    UNIT: "a_unit",
    AGE_INSTALLED: {VALUE: 0},
}


def test_evaluate_lifetime_costs_adds_all_parameters():
    C0.evaluate_lifetime_costs(settings, economic_data, dict_asset)
    for k in (
        LIFETIME_SPECIFIC_COST,
        ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
        LIFETIME_SPECIFIC_COST_OM,
        LIFETIME_PRICE_DISPATCH,
        SIMULATION_ANNUITY,
        SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
        SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    ):
        assert (
            k in dict_asset.keys()
        ), f"Function does not add {k} to the asset dictionary."


start_date = pd.Timestamp("2018-01-01 00:00:00")
dict_test_avilability = {
    SIMULATION_SETTINGS: {
        TIME_INDEX: pd.date_range(
            start=start_date, periods=8760, freq=str(60) + UNIT_MINUTE
        ),
        START_DATE: start_date,
        TIMESTEP: {VALUE: 60},
    }
}


def test_define_availability_of_peak_demand_pricing_assets_yearly():
    dict_availability_timeseries = C0.define_availability_of_peak_demand_pricing_assets(
        dict_test_avilability, 1, 12
    )
    assert (
        len(dict_availability_timeseries) == 1
    ), f"Function does not create a single availability_timeseries for the whole year."
    assert (
        dict_availability_timeseries[1].values.sum() == 8760
    ), f"Availablity of a single dict_availability_timeseries is not ensured for every hour of the year."


def test_define_availability_of_peak_demand_pricing_assets_monthly():
    dict_availability_timeseries = C0.define_availability_of_peak_demand_pricing_assets(
        dict_test_avilability, 12, 1
    )
    assert (
        len(dict_availability_timeseries) == 12
    ), f"Function does not create 12 individual availability_timeseries for the whole year."
    assert (
        dict_availability_timeseries[1].values.sum() == 31 * 24
    ), f"Availability timeseries that is supposed to be 1 for January alone has an unexpected number of available hours."
    total = 0
    for key in dict_availability_timeseries:
        total += dict_availability_timeseries[key].values.sum()
    assert (
        total == 8760
    ), f"Availablity of all 12 availability_timeseries does not insure availability every hour of the year."


def test_define_availability_of_peak_demand_pricing_assets_quarterly():
    dict_availability_timeseries = C0.define_availability_of_peak_demand_pricing_assets(
        dict_test_avilability, 4, 3
    )
    assert (
        len(dict_availability_timeseries) == 4
    ), f"Function does not create 4 individual availability_timeseries for the whole year."
    total = 0
    for key in dict_availability_timeseries:
        total += dict_availability_timeseries[key].values.sum()
    assert (
        total == 8760
    ), f"Availablity of all 12 availability_timeseries does not insure availability every hour of the year."


def test_define_transformer_for_peak_demand_pricing():
    dict_test = {
        ENERGY_CONVERSION: {},
        ENERGY_PROVIDERS: {
            "dso": {
                LABEL: "a_label",
                INFLOW_DIRECTION: "a_direction",
                OUTFLOW_DIRECTION: "b_direction",
                PEAK_DEMAND_PRICING: {VALUE: 60},
                UNIT: "unit",
                ENERGY_VECTOR: "a_vector",
            }
        },
    }
    dict_test_dso = dict_test[ENERGY_PROVIDERS]["dso"].copy()
    transformer_name = "a_name"
    timeseries_availability = pd.Series()
    C0.define_transformer_for_peak_demand_pricing(
        dict_test, dict_test_dso, transformer_name, timeseries_availability
    )
    assert transformer_name in dict_test[ENERGY_CONVERSION]
    for k in [
        LABEL,
        OPTIMIZE_CAP,
        INSTALLED_CAP,
        INFLOW_DIRECTION,
        OUTFLOW_DIRECTION,
        AVAILABILITY_DISPATCH,
        DISPATCH_PRICE,
        SPECIFIC_COSTS,
        DEVELOPMENT_COSTS,
        SPECIFIC_COSTS_OM,
        OEMOF_ASSET_TYPE,
        INFLOW_DIRECTION,
        OUTPUT_BUS_NAME,
        EFFICIENCY,
        ENERGY_VECTOR,
    ]:
        assert (
            k in dict_test[ENERGY_CONVERSION][transformer_name]
        ), f"Function does not add {k} to the asset dictionary of the {transformer_name}."
    assert (
        dict_test[ENERGY_CONVERSION][transformer_name][SPECIFIC_COSTS_OM][VALUE]
        == dict_test[ENERGY_PROVIDERS]["dso"][PEAK_DEMAND_PRICING][VALUE]
    ), f"The {SPECIFIC_COSTS_OM} of the newly defined {transformer_name} is not equal to the {PEAK_DEMAND_PRICING} of the energy provider it is defined from."


def test_define_energyBusses():
    asset_names = ["asset_name_" + str(i) for i in range(0, 6)]
    in_bus_names = ["in_bus_name_" + str(i) for i in range(0, 6)]
    out_bus_names = ["out_bus_name_" + str(i) for i in range(0, 6)]
    energy_vector = "Electricity"
    dict_test = {
        ENERGY_PROVIDERS: {
            asset_names[0]: {
                LABEL: asset_names[0],
                OUTFLOW_DIRECTION: out_bus_names[0],
                INFLOW_DIRECTION: in_bus_names[0],
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_STORAGE: {
            asset_names[1]: {
                LABEL: asset_names[1],
                OUTFLOW_DIRECTION: out_bus_names[1],
                INFLOW_DIRECTION: in_bus_names[1],
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_CONSUMPTION: {
            asset_names[2]: {
                LABEL: asset_names[2],
                INFLOW_DIRECTION: in_bus_names[2],
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            asset_names[3]: {
                LABEL: asset_names[3],
                OUTFLOW_DIRECTION: out_bus_names[2],
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_CONVERSION: {
            asset_names[4]: {
                LABEL: asset_names[4],
                OUTFLOW_DIRECTION: out_bus_names[3],
                INFLOW_DIRECTION: in_bus_names[3],
                ENERGY_VECTOR: energy_vector,
            },
            asset_names[5]: {
                LABEL: asset_names[5],
                OUTFLOW_DIRECTION: [out_bus_names[4], out_bus_names[5]],
                INFLOW_DIRECTION: [in_bus_names[4], in_bus_names[5]],
                ENERGY_VECTOR: energy_vector,
            },
        },
    }

    C0.define_busses(dict_test)
    assert (
        ENERGY_BUSSES in dict_test.keys()
    ), f"Parameter {ENERGY_BUSSES} is not added to the dictionary."
    for k in in_bus_names:
        assert (
            k  in dict_test[ENERGY_BUSSES].keys()
        ), f"Bus {k} of the input busses is not added to the {ENERGY_BUSSES}."
    for k in out_bus_names:
        assert (
            k in dict_test[ENERGY_BUSSES].keys()
        ), f"Bus {k} of the output busses is not added to the {ENERGY_BUSSES}."


def test_add_busses_of_asset_depending_on_in_out_direction_single():
    bus_names = ["bus_name_" + str(i) for i in range(1, 3)]
    asset_name = "asset"
    asset_label = "asset_label"
    energy_vector = "Electricity"
    dict_test = {
        ENERGY_BUSSES: {},
        ENERGY_CONVERSION: {
            asset_name: {
                LABEL: asset_label,
                OUTFLOW_DIRECTION: bus_names[0],
                INFLOW_DIRECTION: bus_names[1],
                ENERGY_VECTOR: energy_vector,
            }
        },
    }
    C0.add_busses_of_asset_depending_on_in_out_direction(
        dict_test, dict_test[ENERGY_CONVERSION][asset_name], asset_name
    )
    for k in bus_names:
        assert (
            k in dict_test[ENERGY_BUSSES].keys()
        ), f"Bus {k} is not added to the {ENERGY_BUSSES}."

    for bus in dict_test[ENERGY_BUSSES].keys():
        assert (
            asset_name in dict_test[ENERGY_BUSSES][bus][ASSET_DICT].keys()
        ), f"Asset {asset_name} is not included in the asset list of {bus}."
        assert (
            dict_test[ENERGY_BUSSES][bus][ASSET_DICT][asset_name] == asset_label
        ), f"The asset label of asset {asset_name} in the asset list of {bus} is of unexpected value."


def test_update_bus():
    bus_name = "bus_name"
    asset_name = "asset"
    asset_label = "asset_label"
    energy_vector = "Electricity"
    dict_test = {
        ENERGY_BUSSES: {},
        ENERGY_CONVERSION: {
            asset_name: {
                LABEL: asset_label,
                OUTFLOW_DIRECTION: bus_name,
                ENERGY_VECTOR: energy_vector,
            }
        },
    }
    C0.add_asset_to_asset_dict_of_bus(
        dict_values=dict_test,
        bus=bus_name,
        asset_key=asset_name,
        asset_label=asset_label,
    )
    assert (
        bus_name in dict_test[ENERGY_BUSSES]
    ), f"The {bus_name} is not added to the {ENERGY_BUSSES}."
    assert (
        asset_name in dict_test[ENERGY_BUSSES][bus_name][ASSET_DICT]
    ), f"The asset {asset_name} is not added to the list of assets attached to the bus."
    assert (
        dict_test[ENERGY_BUSSES][bus_name][ASSET_DICT][asset_name] == asset_label
    ), f"The asset {asset_name} is not added with its {LABEL} to the list of assets attached to the bus."
    assert (
        dict_test[ENERGY_BUSSES][bus_name][ENERGY_VECTOR] == energy_vector
    ), f"The {ENERGY_VECTOR} of the added bus is not of the expected value."

def test_apply_function_to_single_or_list_apply_to_single():
    def multiply(parameter):
        parameter_processed = 2 * parameter
        return parameter_processed

    parameter = 1
    parameter_processed = C0.apply_function_to_single_or_list(multiply, parameter)
    assert parameter_processed == 2, f"The multiplication with a single value fails."


def test_apply_function_to_single_or_list_apply_to_list():
    def multiply(parameter):
        parameter_processed = 2 * parameter
        return parameter_processed

    parameter = [1, 1]
    parameter_processed = C0.apply_function_to_single_or_list(multiply, parameter)
    assert parameter_processed == [2, 2], f"The multiplication with a list fails."


def test_determine_months_in_a_peak_demand_pricing_period_not_valid():
    with pytest.raises(C0.InvalidPeakDemandPricingPeriods):
        C0.determine_months_in_a_peak_demand_pricing_period(
            5, 365
        ), f"No C0.InvalidPeakDemandPricingPeriods is raised eventhough an invalid number of pricing periods is requested."


def test_determine_months_in_a_peak_demand_pricing_period_valid():
    months_in_a_period = C0.determine_months_in_a_peak_demand_pricing_period(4, 365)
    assert (
        months_in_a_period == 3
    ), f"The duration, ie. months of the peak demand pricing periods, are calculated incorrectly."

def test_evaluate_lifetime_costs():
    settings = {EVALUATED_PERIOD: {VALUE: 10}}
    economic_data = {
        PROJECT_DURATION: {VALUE: 20},
        DISCOUNTFACTOR: {VALUE: 0.1},
        TAX: {VALUE: 0},
        CRF: {VALUE: 0.1},
        ANNUITY_FACTOR: {VALUE: 7},
    }

    dict_asset = {
        SPECIFIC_COSTS_OM: {VALUE: 5, UNIT: "unit"},
        SPECIFIC_COSTS: {VALUE: 100, UNIT: "unit"},
        DISPATCH_PRICE: {VALUE: 1, UNIT: "unit"},
        LIFETIME: {VALUE: 10},
        UNIT: UNIT,
        AGE_INSTALLED: {VALUE: 0},
    }

    C0.evaluate_lifetime_costs(settings, economic_data, dict_asset)

    # Note: Only the relevant keys are tested here. The valid calculation of the costs is tested with test_benchmark_KPI.py, Test_Economic_KPI.test_benchmark_Economic_KPI_C2_E2()
    for k in [
        LIFETIME_SPECIFIC_COST,
        LIFETIME_SPECIFIC_COST_OM,
        ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
        SIMULATION_ANNUITY,
        LIFETIME_PRICE_DISPATCH,
        SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
        SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
    ]:
        assert k in dict_asset, f"Function does not add {k} to the asset dictionary."


def test_check_if_energy_carrier_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS_pass():
    # Function only needs to pass
    C0.check_if_energy_carrier_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS(
        "Electricity", "asset_group", "asset"
    )
    assert (
        1 == 1
    ), f"The energy carrier `Electricity` is not recognized to be defined in `DEFAULT_WEIGHTS_ENERGY_CARRIERS`."


def test_check_if_energy_carrier_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS_fail():
    with pytest.raises(C0.UnknownEnergyCarrier):
        C0.check_if_energy_carrier_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS(
            "Bio-Diesel", "asset_group", "asset"
        ), f"The energy carrier `Bio-Diesel` is recognized in the `DEFAULT_WEIGHTS_ENERGY_CARRIERS`, eventhough it should not be defined."


group = "GROUP"
asset = "ASSET"
subasset = "SUBASSET"
unit = "kW"
installed_cap = 50


def test_process_maximum_cap_constraint_maximumCap_undefined():
    """If no maximum cap is defined previously, it is defined as none."""
    dict_values = {group: {asset: {UNIT: unit}}}
    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
    assert (
        MAXIMUM_CAP in dict_values[group][asset]
    ), f"The function does not add a MAXIMUM_CAP to the asset dictionary."
    assert (
        dict_values[group][asset][MAXIMUM_CAP][VALUE] is None
    ), f"Eventhough there is no limit imposed to the asset capacity, its maximumCap is defined to be {dict_values[group][asset][MAXIMUM_CAP][VALUE]}."
    assert (
        dict_values[group][asset][MAXIMUM_CAP][UNIT] == unit
    ), f"The maximumCap is in {dict_values[group][asset][MAXIMUM_CAP][UNIT]}, while the asset itself has unit {dict_values[group][asset][UNIT]}."


def test_process_maximum_cap_constraint_maximumCap_is_None():
    """The asset has a maximumCap==None, and a unit is added."""
    dict_values = {group: {asset: {UNIT: unit, MAXIMUM_CAP: {VALUE: None}}}}
    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
    assert (
        dict_values[group][asset][MAXIMUM_CAP][VALUE] is None
    ), f"Eventhough there is no limit imposed to the asset capacity, its maximumCap is defined to be {dict_values[group][asset][MAXIMUM_CAP][VALUE]}."
    assert (
        dict_values[group][asset][MAXIMUM_CAP][UNIT] == unit
    ), f"The maximumCap is in {dict_values[group][asset][MAXIMUM_CAP][UNIT]}, while the asset itself has unit {dict_values[group][asset][UNIT]}."


def test_process_maximum_cap_constraint_maximumCap_is_int():
    """The asset has a maximumCap of int, and a unit is added."""
    maxCap = 100
    dict_values = {
        group: {
            asset: {
                UNIT: unit,
                INSTALLED_CAP: {VALUE: installed_cap},
                MAXIMUM_CAP: {VALUE: maxCap},
            }
        }
    }
    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
    assert (
        dict_values[group][asset][MAXIMUM_CAP][VALUE] == maxCap
    ), f"The initial maximumCap defined by the end-user ({maxCap}) is overwritten by a different value ({dict_values[group][asset][MAXIMUM_CAP][VALUE]})."
    assert (
        dict_values[group][asset][MAXIMUM_CAP][UNIT] == unit
    ), f"The maximumCap is in {dict_values[group][asset][MAXIMUM_CAP][UNIT]}, while the asset itself has unit {dict_values[group][asset][UNIT]}."


def test_process_maximum_cap_constraint_maximumCap_is_float():
    """The asset has a maximumCap of float, and a unit is added"""
    maxCap = 100.1
    dict_values = {
        group: {
            asset: {
                UNIT: unit,
                INSTALLED_CAP: {VALUE: installed_cap},
                MAXIMUM_CAP: {VALUE: maxCap},
            }
        }
    }
    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
    assert (
        dict_values[group][asset][MAXIMUM_CAP][VALUE] == maxCap
    ), f"The initial maximumCap defined by the end-user ({maxCap}) is overwritten by a different value ({dict_values[group][asset][MAXIMUM_CAP][VALUE]})."
    assert (
        dict_values[group][asset][MAXIMUM_CAP][UNIT] == unit
    ), f"The maximumCap is in {dict_values[group][asset][MAXIMUM_CAP][UNIT]}, while the asset itself has unit {dict_values[group][asset][UNIT]}."


def test_process_maximum_cap_constraint_maximumCap_is_0():
    """The asset has no maximumCapacity, and the entry is translated into a unit-value pair."""
    maxCap = 0

    dict_values = {
        group: {
            asset: {
                UNIT: unit,
                INSTALLED_CAP: {VALUE: installed_cap},
                MAXIMUM_CAP: {VALUE: maxCap},
            }
        }
    }
    with pytest.warns(UserWarning):
        C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
        assert (
            dict_values[group][asset][MAXIMUM_CAP][VALUE] is None
        ), f"The initial maximumCap defined by the end-user ({maxCap}) is overwritten by a different value ({dict_values[group][asset][MAXIMUM_CAP][VALUE]})."


def test_process_maximum_cap_constraint_maximumCap_is_int_smaller_than_installed_cap():
    """"The asset has a maximumCap < installedCap which is invalid and being ignored."""
    maxCap = 10
    dict_values = {
        group: {
            asset: {
                UNIT: unit,
                INSTALLED_CAP: {VALUE: installed_cap},
                MAXIMUM_CAP: {VALUE: maxCap},
            }
        }
    }
    with pytest.warns(UserWarning):
        C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
        assert (
            dict_values[group][asset][MAXIMUM_CAP][VALUE] is None
        ), f"The invalid input is not ignored by defining maximumCap as None."


def test_process_maximum_cap_constraint_group_is_ENERGY_PRODUCTION_fuel_source():
    """The asset belongs to the energy production group, but is a dispatchable fuel source. The maximumCap is processed as usual."""
    group = ENERGY_PRODUCTION
    maxCap = 100
    dict_values = {
        group: {
            asset: {
                LABEL: asset,
                UNIT: unit,
                INSTALLED_CAP: {VALUE: installed_cap},
                MAXIMUM_CAP: {VALUE: maxCap},
                FILENAME: None,
            }
        }
    }
    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
    assert (
        dict_values[group][asset][MAXIMUM_CAP][VALUE] == maxCap
    ), f"The initial maximumCap defined by the end-user ({maxCap}) is overwritten by a different value ({dict_values[group][asset][MAXIMUM_CAP][VALUE]})."


def test_process_maximum_cap_constraint_group_is_ENERGY_PRODUCTION_non_dispatchable_asset():
    """The asset belongs to the energy production group, and is a non-dispatchable asset.
    As the maximumCap is used to define the maximum capacity of an asset, but used in oemof-solph to limit a flow, the value has to be translated."""
    timeseries_peak = 0.8
    group = ENERGY_PRODUCTION
    maxCap = 100
    dict_values = {
        group: {
            asset: {
                LABEL: asset,
                UNIT: unit,
                INSTALLED_CAP: {VALUE: installed_cap},
                MAXIMUM_CAP: {VALUE: maxCap},
                FILENAME: "a_name",
                TIMESERIES_PEAK: {VALUE: timeseries_peak},
            }
        }
    }
    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=None)
    assert (
        dict_values[group][asset][MAXIMUM_CAP][VALUE] == maxCap * timeseries_peak
    ), f"The initial maximumCap defined by the end-user ({maxCap}) is overwritten by a different value ({dict_values[group][asset][MAXIMUM_CAP][VALUE]})."


def test_process_maximum_cap_constraint_subasset():
    """For storages, the subassets have to be processes. This tests the procedure examplary."""
    dict_values = {
        group: {
            asset: {subasset: {LABEL: asset, UNIT: unit, MAXIMUM_CAP: {VALUE: None},}}
        }
    }

    C0.process_maximum_cap_constraint(dict_values, group, asset, subasset=subasset)
    assert (
        dict_values[group][asset][subasset][MAXIMUM_CAP][VALUE] is None
    ), f"The function does not change the previously defined MAXIMUM_CAP."
    assert (
        dict_values[group][asset][subasset][MAXIMUM_CAP][UNIT] == unit
    ), f"The maximumCap is in {dict_values[group][asset][subasset][MAXIMUM_CAP][UNIT]}, while the asset itself has unit {dict_values[group][asset][subasset][UNIT]}."


"""
def test_asess_energyVectors_and_add_to_project_data():
    C2.identify_energy_vectors(dict_values)
    assert 1 == 0
    # assert "sector" in dict_values[PROJECT_DATA].keys()

#Create a sink for each energyVector (this actually might be changed in the future - create an excess sink for each bus?)
def test_create_excess_sinks_for_each_energyVector():
    assert 1 == 0

#- Add demand sinks to energyVectors (this should actually be changed and demand sinks should be added to bus relative to input_direction, also see issue #179)
def test_adding_demand_sinks_to_energyVectors():
    assert 1 == 0

def test_naming_busses():
    assert 1 == 0

def test_check_for_missing_data():
    assert 1 == 0

def test_add_missing_data_to_automatically_generated_objects():
    assert 1 == 0

def test_reading_timeseries_of_assets_one_column():
    assert 1 == 0

def test_reading_timeseries_of_assets_multi_column_csv():
    assert 1 == 0

def test_reading_timeseries_of_assets_delimiter_comma():
    assert 1 == 0

def test_reading_timeseries_of_assets_delimiter_semicolon():
    assert 1 == 0

# Read timeseries for parameter of an asset, eg. efficiency
def test_reading_timeseries_of_asset_for_parameter():
    assert 1 == 0

def test_parse_list_of_inputs_one_input():
    assert 1 == 0

def test_parse_list_of_inputs_two_inputs():
    assert 1 == 0

def test_parse_list_of_inputs_one_output():
    assert 1 == 0

def test_parse_list_of_inputs_two_outputs():
    assert 1 == 0

def test_parse_list_of_inputs_two_inputs_two_outputs():
    assert 1 == 0

def test_raise_error_message_multiple_inputs_not_multilpe_parameters():
    assert 1 == 0

def test_raise_error_message_multiple_outputs_multilpe_parameters():
    assert 1 == 0

# Define dso sinks, soures, transformer stations (this will be changed due to bug #119), also for peak demand pricing
def test_generation_of_dso_side():
    assert 1 == 0

# Add a source if a conversion object is connected to a new input_direction (bug #186)
def test_add_source_when_unknown_input_direction():
    assert 1 == 0

# Define all necessary energyBusses and add all assets that are connected to them specifically with asset name and label
def test_defined_energyBusses_complete():
    assert 1 == 0

def test_verification_executing_C1():
    assert 1 == 0
"""

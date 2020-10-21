"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import argparse
import os
import shutil

import mock
import pandas as pd
import pytest

from multi_vector_simulator.cli import main
from multi_vector_simulator.B0_data_input_json import load_json
import multi_vector_simulator.C2_economic_functions as C2

from _constants import (
    JSON_WITH_RESULTS,
    TEST_REPO_PATH,
    CSV_EXT,
    TIME_SERIES,
)


from multi_vector_simulator.utils.constants_json_strings import (
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
    VALUE,
    FLOW,
    LIFETIME_SPECIFIC_COST_OM,
    LIFETIME_PRICE_DISPATCH,
    LIFETIME_SPECIFIC_COST,
    ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
    SIMULATION_ANNUITY,
    SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
    OPTIMIZED_ADD_CAP,
    ANNUITY_OM,
    ANNUITY_TOTAL,
    COST_TOTAL,
    COST_OPERATIONAL_TOTAL,
    COST_OM,
    COST_DISPATCH,
    COST_INVESTMENT,
    COST_UPFRONT,
    COST_REPLACEMENT,
    LCOE_ASSET,
    CURR,
    DISCOUNTFACTOR,
    PROJECT_DURATION,
    ANNUITY_FACTOR,
    CRF,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    ENERGY_BUSSES,
    ENERGY_PROVIDERS,
    KPI,
    KPI_SCALARS_DICT,
)


TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")

DICT_ECONOMIC = {
    CURR: "Euro",
    DISCOUNTFACTOR: {VALUE: 0.08},
    PROJECT_DURATION: {VALUE: 20},
}

DICT_ECONOMIC.update(
    {
        ANNUITY_FACTOR: {
            VALUE: C2.annuity_factor(
                project_life=DICT_ECONOMIC[PROJECT_DURATION][VALUE],
                discount_factor=DICT_ECONOMIC[DISCOUNTFACTOR][VALUE],
            )
        },
        CRF: {
            VALUE: C2.crf(
                project_life=DICT_ECONOMIC[PROJECT_DURATION][VALUE],
                discount_factor=DICT_ECONOMIC[DISCOUNTFACTOR][VALUE],
            )
        },
    }
)


class Test_Economic_KPI:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_Economic_KPI_C2_E2(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, we evaluate the performance of the economic pre- and post-processing in C2 and E2.
        Values that have to be compared for each asset
        - LIFETIME_SPECIFIC_COST_OM
        - LIFETIME_PRICE_DISPATCH
        - LIFETIME_SPECIFIC_COST
        - ANNUITY_SPECIFIC_INVESTMENT_AND_OM
        - SIMULATION_ANNUITY
        - SPECIFIC_REPLACEMENT_COSTS_INSTALLED
        - SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED
        - OPTIMIZED_ADD_CAP != 0, as we are not optimizing any asset
        - ANNUITY_OM
        - ANNUITY_TOTAL
        - COST_TOTAL
        - COST_OPERATIONAL_TOTAL
        - COST_OM
        - COST_DISPATCH
        - COST_INVESTMENT
        - COST_UPFRONT
        - COST_REPLACEMENT
        - LCOE_ASSET

        Overall economic values of the project:
        - NPV
        - Annuity

        """
        use_case = "Economic_KPI_C2_E2"

        # Execute the script
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        # read json with results file
        data = load_json(os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS))

        # Read expected values from file. To edit the values, please use the .xls file first and convert the first tab to csv.
        expected_value_file = "test_data_economic_expected_values.csv"
        expected_values = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, use_case, expected_value_file),
            sep=",",
            index_col=0,
        )

        KEYS_TO_BE_EVALUATED = [
            LIFETIME_SPECIFIC_COST_OM,
            LIFETIME_PRICE_DISPATCH,
            LIFETIME_SPECIFIC_COST,
            ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
            SIMULATION_ANNUITY,
            SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
            SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
            OPTIMIZED_ADD_CAP,
            COST_INVESTMENT,
            COST_UPFRONT,
            COST_REPLACEMENT,
            COST_OM,
            COST_DISPATCH,
            COST_OPERATIONAL_TOTAL,
            COST_TOTAL,
            ANNUITY_OM,
            ANNUITY_TOTAL,
            LCOE_ASSET,
        ]

        # # Derive expected values dependent on actual dispatch of the asset(s)
        # for asset in expected_values.columns:
        #     # determine asset dictionary (special for storages)
        #     result_key = expected_values[asset]["group"]
        #
        #     if asset in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
        #         asset_data = data[result_key]["storage_01"][asset]
        #     else:
        #         asset_data = data[result_key][asset]
        #
        #     # Get dispatch of the assets
        #     expected_values[asset][FLOW] = asset_data[FLOW]
        #
        #     # Calculate cost parameters that are dependent on the flow
        #     expected_values[asset][COST_DISPATCH] = expected_values[asset][
        #         LIFETIME_PRICE_DISPATCH
        #     ] * sum(expected_values[asset][FLOW])
        #     expected_values[asset][COST_OPERATIONAL_TOTAL] = (
        #         expected_values[asset][COST_DISPATCH] + expected_values[asset][COST_OM]
        #     )
        #     expected_values[asset][COST_TOTAL] = (
        #         expected_values[asset][COST_OPERATIONAL_TOTAL]
        #         + expected_values[asset][COST_INVESTMENT]
        #     )
        #
        #     # Process cost
        #     expected_values[asset][ANNUITY_OM] = (
        #         expected_values[asset][COST_OPERATIONAL_TOTAL]
        #         * DICT_ECONOMIC[CRF][VALUE]
        #     )
        #     expected_values[asset][ANNUITY_TOTAL] = (
        #         expected_values[asset][COST_TOTAL] * DICT_ECONOMIC[CRF][VALUE]
        #     )
        #     if sum(expected_values[asset][FLOW]) == 0:
        #         expected_values[asset][LCOE_ASSET] = 0
        #     else:
        #         expected_values[asset][LCOE_ASSET] = expected_values[asset][
        #             ANNUITY_TOTAL
        #         ] / sum(expected_values[asset][FLOW])
        #
        # # Store to csv to enable manual check, eg. of LCOE_A. Only previously empty rows have been changed.
        # expected_values.drop("flow").to_csv(
        #     os.path.join(TEST_OUTPUT_PATH, use_case, expected_value_file), sep=","
        # )

        # Compare asset costs calculated in C2 and E2 with benchmark data from csv file
        for asset in expected_values.index:

            asset_group = expected_values.loc[asset, "group"]

            # determine asset dictionnary (special for storages)
            if asset in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                asset_data = data[asset_group]["storage_01"][asset]
            else:
                asset_data = data[asset_group][asset]
            # assertion
            for key in KEYS_TO_BE_EVALUATED:
                assert expected_values.loc[asset, key] == pytest.approx(
                    asset_data[key][VALUE], rel=1e-3
                ), f"Parameter {key} of asset {asset} is not of expected value."

        demand = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, use_case, TIME_SERIES, "demand.csv"), sep=",",
        )
        aggregated_demand = demand.sum()[0]

        # Compute the aggregated annuity and costs (NPC)
        aggregated_annuity = 0
        aggregated_costs = 0

        for asset_group in (ENERGY_CONSUMPTION, ENERGY_PRODUCTION, ENERGY_STORAGE):
            for asset in data[asset_group]:
                # for storage we look at the annuity of the in and out flows and storage capacity
                if asset_group == ENERGY_STORAGE:
                    for storage_type in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                        asset_data = data[asset_group][asset][storage_type]
                        aggregated_annuity += asset_data[ANNUITY_TOTAL][VALUE]
                        aggregated_costs += asset_data[COST_TOTAL][VALUE]
                else:
                    asset_data = data[asset_group][asset]
                    aggregated_annuity += asset_data[ANNUITY_TOTAL][VALUE]
                    aggregated_costs += asset_data[COST_TOTAL][VALUE]

        # Compute the lcoe for this simple case (single demand)
        lcoe = aggregated_annuity / aggregated_demand
        mvs_lcoe = data[KPI][KPI_SCALARS_DICT][
            "Levelized costs of electricity equivalent"
        ]
        assert lcoe == pytest.approx(
            mvs_lcoe, rel=1e-2
        ), f"Parameter {LCOE_ASSET} of system is not of expected value (benchmark of {lcoe} versus computed value of {mvs_lcoe}."

        mvs_costs = data[KPI][KPI_SCALARS_DICT]["costs_total"]
        assert aggregated_costs == pytest.approx(
            mvs_costs, rel=1e-2
        ), f"Parameter {COST_TOTAL} of system is not of expected value (benchmark of {aggregated_costs} versus computed value of {mvs_costs}."

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)

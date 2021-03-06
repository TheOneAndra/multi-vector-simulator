class MissingParameterError(ValueError):
    """Exception raised for missing parameters of a csv input file."""

    pass


class MissingParameterWarning(UserWarning):
    """Exception raised for missing new parameters of a csv input file, which will be set to default."""

    pass


class WrongParameterWarning(UserWarning):
    """Exception raised for errors in the parameters of a csv input file."""

    pass


class CsvParsingError(ValueError):
    """Exception raised for errors in the parameters of a csv input file."""

    pass


class WrongStorageColumn(ValueError):
    """Exception raised for wrong column name in "storage_xx" input file."""

    pass


class InvalidPeakDemandPricingPeriodsError(ValueError):
    # Exeption if an input is not valid
    pass


class UnknownEnergyCarrierError(ValueError):
    # Exception if an energy carrier is not in DEFAULT_WEIGHTS_ENERGY_CARRIERS
    pass

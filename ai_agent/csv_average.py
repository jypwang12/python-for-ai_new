import pandas as pd


class CSVAverageCalculator:
    """Read a CSV file and calculate averages using pandas.

    Methods
    -------
    read()
        Loads the CSV into a DataFrame.
    column_averages()
        Returns a dict with averages for numeric columns.
    row_averages()
        Returns a pandas Series with the per-row average across numeric columns.
    overall_average()
        Returns the mean of all numeric values in the DataFrame.
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None

    def read(self) -> pd.DataFrame:
        """Load the CSV file into a pandas DataFrame.

        Raises FileNotFoundError if the file does not exist, or
        pd.errors.EmptyDataError / pd.errors.ParserError for bad CSVs.
        """
        try:
            self.df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            raise
        except Exception:
            # Propagate pandas errors (EmptyDataError, ParserError) to the caller
            raise
        return self.df

    def _ensure_df(self):
        if self.df is None:
            self.read()

    def column_averages(self) -> dict:
        """Return averages for numeric columns as a dict {col: avg}.

        Raises ValueError if there are no numeric columns.
        """
        self._ensure_df()
        numeric = self.df.select_dtypes(include="number")
        if numeric.empty:
            raise ValueError("No numeric columns available to average")
        return numeric.mean(axis=0).to_dict()

    def row_averages(self) -> pd.Series:
        """Return a Series with per-row averages across numeric columns.

        Index matches the original DataFrame index.
        Raises ValueError if there are no numeric columns.
        """
        self._ensure_df()
        numeric = self.df.select_dtypes(include="number")
        if numeric.empty:
            raise ValueError("No numeric columns available to average")
        return numeric.mean(axis=1)

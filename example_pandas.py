"""Example module showing simple pandas usage and plotting.

Provides `DataProcessor` and `Plotter` classes and a runnable demo that
creates two PNG plots in the `plots/` folder.
"""

from __future__ import annotations
import os
from typing import Iterable, Optional

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class DataProcessor:
    def __init__(
        self, data: Optional[Iterable[float]] = None, csv_path: Optional[str] = None
    ):
        self.csv_path = csv_path
        self.data = list(data) if data is not None else None
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        if self.csv_path:
            self.df = pd.read_csv(self.csv_path)
        else:
            if self.data is None:
                raise ValueError("No data provided")
            self.df = pd.DataFrame({"value": self.data})
        return self.df

    def summary(self) -> pd.DataFrame:
        if self.df is None:
            raise RuntimeError("Data not loaded")
        return self.df.describe()

    def add_rolling_mean(self, window: int = 2, column: str = "value") -> pd.Series:
        if self.df is None:
            raise RuntimeError("Data not loaded")
        rm = self.df[column].rolling(window=window, min_periods=1).mean()
        self.df[f"rolling_{window}"] = rm
        return rm

    def compute_clv(
        self,
        arpu_column: str = "value",
        churn_rate: float = 0.1,
        discount_rate: float = 0.0,
        periods: Optional[int] = None,
    ) -> float:
        """Compute a simple Customer Lifetime Value (CLV) estimate.

        - If `discount_rate` is 0.0, uses simple CLV = ARPU / churn_rate.
        - Otherwise uses discounted CLV over `periods` (or 100 if None) as
          sum_{t=0..T-1} ARPU * (1 - churn_rate)^t / (1+discount_rate)^t.

        The method uses the mean of `arpu_column` as ARPU.
        """
        if self.df is None:
            raise RuntimeError("Data not loaded")
        if churn_rate <= 0:
            raise ValueError("churn_rate must be > 0")
        arpu = float(self.df[arpu_column].mean())
        if discount_rate <= 0:
            # simple steady-state CLV
            clv = arpu / churn_rate
            return clv

        # discounted CLV over finite horizon
        if periods is None:
            periods = 100
        retention = 1.0 - churn_rate
        clv = 0.0
        for t in range(periods):
            clv += arpu * (retention**t) / ((1.0 + discount_rate) ** t)
        return clv


class Plotter:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def plot_histogram(
        self, column: str = "value", bins: int = 10, out_path: str = "plots/hist.png"
    ) -> str:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.figure()
        self.df[column].hist(bins=bins)
        plt.title(f"Histogram of {column}")
        plt.xlabel(column)
        plt.ylabel("count")
        plt.savefig(out_path)
        plt.close()
        return out_path

    def plot_time_series(
        self, column: str = "value", out_path: str = "plots/series.png"
    ) -> str:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.figure()
        self.df.reset_index(drop=True)[column].plot(marker="o")
        plt.title(f"Time series of {column}")
        plt.xlabel("index")
        plt.ylabel(column)
        plt.grid(True)
        plt.savefig(out_path)
        plt.close()
        return out_path


def demo():
    sample = [80, 82, 85, 90, 95]
    dp = DataProcessor(data=sample)
    df = dp.load()
    print("Summary:\n", dp.summary())
    dp.add_rolling_mean(window=2)
    # Compute CLV examples (simple and discounted)
    clv_simple = dp.compute_clv(churn_rate=0.1, discount_rate=0.0)
    clv_discounted = dp.compute_clv(churn_rate=0.1, discount_rate=0.05, periods=20)
    print(f"CLV (simple, churn=0.1): {clv_simple:.2f}")
    print(f"CLV (discounted 5%, 20 periods, churn=0.1): {clv_discounted:.2f}")
    plotter = Plotter(df)
    hist = plotter.plot_histogram()
    series = plotter.plot_time_series()
    print(f"Saved plots: {hist}, {series}")


if __name__ == "__main__":
    demo()

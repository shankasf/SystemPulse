#!/usr/bin/env python3
import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_metrics(url="http://127.0.0.1:8000/metrics"):
    """Fetch JSON metrics from the FastAPI endpoint and return a DataFrame."""
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()["data"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    return df

def pivot_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot so each field is its own column, indexed by timestamp."""
    pivot = df.pivot(index="time", columns="field", values="value").sort_index()
    return pivot

def plot_cpu_and_load(pivot: pd.DataFrame):
    """Plot CPU % and load averages on the same chart with two y‑axes."""
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Primary axis: CPU usage %
    ax1.plot(
        pivot.index,
        pivot["usage_percent"],
        label="CPU Usage (%)",
        linewidth=2
    )
    ax1.set_xlabel("Time")
    ax1.set_ylabel("CPU Usage (%)")
    ax1.legend(loc="upper left")

    # Secondary axis: load averages
    ax2 = ax1.twinx()
    ax2.plot(
        pivot.index,
        pivot["load_avg_1m"],
        linestyle="--",
        label="Load 1m"
    )
    ax2.plot(
        pivot.index,
        pivot["load_avg_5m"],
        linestyle=":",
        label="Load 5m"
    )
    ax2.plot(
        pivot.index,
        pivot["load_avg_15m"],
        linestyle="-.",
        label="Load 15m"
    )
    ax2.set_ylabel("Load Average")
    ax2.legend(loc="upper right")

    plt.title("CPU Usage and Load Averages Over Time")
    plt.tight_layout()

def plot_memory(pivot: pd.DataFrame):
    """Plot used vs. total memory on a separate chart."""
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        pivot.index,
        pivot["used_memory_mb"],
        label="Used Memory (MB)",
        linewidth=2
    )
    ax.plot(
        pivot.index,
        pivot["total_memory_mb"],
        label="Total Memory (MB)",
        linestyle="--"
    )

    ax.set_xlabel("Time")
    ax.set_ylabel("Memory (MB)")
    ax.legend()
    plt.title("Memory Usage Over Time")
    plt.tight_layout()

def main():
    df = fetch_metrics()
    pivot = pivot_metrics(df)
    plot_cpu_and_load(pivot)
    plot_memory(pivot)
    plt.show()

if __name__ == "__main__":
    main()

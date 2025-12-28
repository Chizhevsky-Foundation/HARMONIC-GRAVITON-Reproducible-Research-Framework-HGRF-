#!/usr/bin/env python3
"""
src/stats.py

Likelihood fit (Gaussian), bootstrap confidence intervals, and toy-MC generator.

Input: a CSV (e.g. results/angles_summary.csv) with a numeric column (default: mean_angle_deg).
Outputs: JSON report, PNG figures, optional CSVs of bootstrap/toy draws.

Author: ChatGPT (implementation)
Reviewed by: Benjamin Cabeza Durán (method)
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy import optimize, stats
import matplotlib.pyplot as plt

def load_series(path: str, column: str):
    df = pd.read_csv(path)
    if column not in df.columns:
        raise SystemExit(f"Column '{column}' not found in {path}. Available columns: {list(df.columns)}")
    vals = df[column].dropna().to_numpy().astype(float)
    if vals.size == 0:
        raise SystemExit("No data in column after dropping NA.")
    return vals

def neg_loglike_gauss(params, x):
    mu, log_sigma = params
    sigma = np.exp(log_sigma)
    # Gaussian negative log-likelihood
    n = x.size
    return 0.5 * n * np.log(2 * np.pi * sigma * sigma) + 0.5 * np.sum((x - mu) ** 2) / (sigma * sigma)

def mle_gauss(x, initial=None):
    if initial is None:
        mu0 = float(np.mean(x))
        sigma0 = float(np.std(x, ddof=0))
        initial = np.array([mu0, np.log(max(sigma0, 1e-6))])
    res = optimize.minimize(neg_loglike_gauss, initial, args=(x,), method="L-BFGS-B")
    if not res.success:
        raise RuntimeError("MLE optimization failed: " + res.message)
    mu_hat, log_sigma_hat = res.x
    sigma_hat = float(np.exp(log_sigma_hat))
    # approximate Hessian-based covariance (inverse fisher)
    eps = 1e-5
    # numerical approx of fisher information via finite differences (diagonal approx)
    # For practicality return simple estimates:
    se_mu = sigma_hat / np.sqrt(x.size)
    se_sigma = sigma_hat / np.sqrt(2 * x.size)
    return {"mu": float(mu_hat), "sigma": float(sigma_hat), "se_mu": float(se_mu), "se_sigma": float(se_sigma), "opt_result": res}

def bootstrap_ci(x, statistic_fn, n_boot=2000, seed=42, ci=95):
    rng = np.random.default_rng(seed)
    n = x.size
    stats_boot = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(x, size=n, replace=True)
        stats_boot[i] = statistic_fn(sample)
    lower = np.percentile(stats_boot, (100 - ci) / 2)
    upper = np.percentile(stats_boot, 100 - (100 - ci) / 2)
    return {"boot_values": stats_boot, "ci": (float(lower), float(upper))}

def toy_mc_pvalue(x, null_mu: float, n_toys: int = 1000, seed: int = 42):
    rng = np.random.default_rng(seed)
    # Observed test statistic: difference between sample mean and null, scaled by sample std / sqrt(n)
    n = x.size
    obs_mean = float(np.mean(x))
    obs_std = float(np.std(x, ddof=1))
    if obs_std == 0:
        raise RuntimeError("Observed standard deviation is zero; toy-MC not meaningful.")
    obs_z = (obs_mean - null_mu) / (obs_std / np.sqrt(n))
    # Generate toys under H0: Gaussian with mu=null_mu and sigma=obs_std (use observed sigma)
    toy_z = np.empty(n_toys)
    for i in range(n_toys):
        toy = rng.normal(loc=null_mu, scale=obs_std, size=n)
        toy_z[i] = (np.mean(toy) - null_mu) / (np.std(toy, ddof=1) / np.sqrt(n))
    # two-sided p-value
    pvalue = np.mean(np.abs(toy_z) >= np.abs(obs_z))
    return {"obs_z": float(obs_z), "toy_z": toy_z, "pvalue": float(pvalue)}

def plot_hist(values, vline=None, xlabel="value", title=None, outpath=None, bins=60):
    plt.figure(figsize=(7,4))
    plt.hist(values, bins=bins, alpha=0.8)
    if vline is not None:
        plt.axvline(vline, color="k", linewidth=2)
    plt.xlabel(xlabel)
    plt.ylabel("counts")
    if title:
        plt.title(title)
    plt.tight_layout()
    if outpath:
        plt.savefig(outpath)
        plt.close()
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Statistical tools: MLE, bootstrap CI, toy-MC p-value for a numeric column.")
    parser.add_argument("--input", "-i", required=True, help="CSV input (e.g. results/angles_summary.csv)")
    parser.add_argument("--column", "-c", default="mean_angle_deg", help="Numeric column to analyze")
    parser.add_argument("--output", "-o", default="results/stats_results.json", help="JSON output report")
    parser.add_argument("--n-toys", type=int, default=2000, help="Number of toy-MC samples")
    parser.add_argument("--bootstrap-n", type=int, default=2000, help="Number of bootstrap resamples")
    parser.add_argument("--null-mu", type=float, default=0.0, help="Null hypothesis mean for toy-MC test")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--no-plots", action="store_true", help="Skip saving PNG plots")
    args = parser.parse_args()

    outdir = Path(args.output).parent
    outdir.mkdir(parents=True, exist_ok=True)

    print("Loading data:", args.input, "column:", args.column)
    x = load_series(args.input, args.column)
    n = x.size
    print("N =", n)

    t0 = time.time()
    print("Running MLE (Gaussian)...")
    mle = mle_gauss(x)
    mle_time = time.time() - t0

    print("Running bootstrap for mean and sigma...")
    boot_mean = bootstrap_ci(x, lambda s: float(np.mean(s)), n_boot=args.bootstrap_n, seed=args.seed, ci=95)
    boot_sigma = bootstrap_ci(x, lambda s: float(np.std(s, ddof=1)), n_boot=args.bootstrap_n, seed=args.seed+1, ci=95)

    print("Running toy-MC under null mu =", args.null_mu)
    toy = toy_mc_pvalue(x, null_mu=args.null_mu, n_toys=args.n_toys, seed=args.seed+2)

    # plotting
    if not args.no_plots:
        plot_hist(boot_mean["boot_values"], vline=mle["mu"],
                  xlabel="bootstrap mean", title="Bootstrap distribution of mean",
                  outpath=str(outdir / "bootstrap_mean_hist.png"))
        plot_hist(boot_sigma["boot_values"], vline=mle["sigma"],
                  xlabel="bootstrap sigma", title="Bootstrap distribution of sigma",
                  outpath=str(outdir / "bootstrap_sigma_hist.png"))
        plot_hist(toy["toy_z"], vline=toy["obs_z"], xlabel="toy z-statistic",
                  title=f"Toy-MC z-statistics (H0 mu={args.null_mu})", outpath=str(outdir / "toy_z_hist.png"))

    # Build report
    report = {
        "input": str(args.input),
        "column": args.column,
        "n": int(n),
        "mle": {"mu": mle["mu"], "sigma": mle["sigma"], "se_mu": mle["se_mu"], "se_sigma": mle["se_sigma"], "mle_time_s": mle_time},
        "bootstrap": {
            "n_boot": int(args.bootstrap_n),
            "mean_ci_95": boot_mean["ci"],
            "sigma_ci_95": boot_sigma["ci"],
        },
        "toy_mc": {
            "null_mu": float(args.null_mu),
            "n_toys": int(args.n_toys),
            "obs_z": float(toy["obs_z"]),
            "pvalue": float(toy["pvalue"]),
        },
        "seed": int(args.seed),
        "provenance": {
            "script": "src/stats.py"
        }
    }

    # Save report JSON
    with open(args.output, "w") as fh:
        json.dump(report, fh, indent=2)

    # Optionally save bootstrap/toy arrays as npy for later inspection (small files)
    np.save(outdir / "bootstrap_mean_values.npy", boot_mean["boot_values"])
    np.save(outdir / "bootstrap_sigma_values.npy", boot_sigma["boot_values"])
    np.save(outdir / "toy_z_values.npy", toy["toy_z"])

    print("Done. Results saved to", args.output)
    print("Elapsed (s):", time.time() - t0)

if __name__ == "__main__":
    main()

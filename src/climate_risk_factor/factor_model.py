from __future__ import annotations

import math

import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm
except ImportError:  # pragma: no cover - exercised in lightweight environments
    sm = None


def _annualized_return(monthly_returns: pd.Series) -> float:
    monthly_returns = monthly_returns.dropna()
    if monthly_returns.empty:
        return np.nan
    compounded = (1 + monthly_returns).prod()
    years = len(monthly_returns) / 12
    return compounded ** (1 / years) - 1 if years else np.nan


def _max_drawdown(monthly_returns: pd.Series) -> float:
    wealth = (1 + monthly_returns.fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def _normal_p_value(t_stat: float) -> float:
    if not np.isfinite(t_stat):
        return np.nan
    return float(math.erfc(abs(t_stat) / math.sqrt(2)))


def _ols_numpy(y: pd.Series, x: pd.DataFrame) -> pd.DataFrame:
    names = ["const", *x.columns]
    x_mat = np.column_stack([np.ones(len(x)), x.to_numpy(dtype=float)])
    y_vec = y.to_numpy(dtype=float)
    beta = np.linalg.pinv(x_mat.T @ x_mat) @ x_mat.T @ y_vec
    residuals = y_vec - x_mat @ beta
    dof = max(len(y_vec) - x_mat.shape[1], 1)
    sigma2 = float((residuals @ residuals) / dof)
    cov = sigma2 * np.linalg.pinv(x_mat.T @ x_mat)
    se = np.sqrt(np.diag(cov))
    t_stats = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se != 0)
    total = ((y_vec - y_vec.mean()) ** 2).sum()
    r_squared = 1 - ((residuals**2).sum() / total) if total else np.nan
    return pd.DataFrame(
        [
            {
                "term": name,
                "coefficient": beta[i],
                "t_stat": t_stats[i],
                "p_value": _normal_p_value(t_stats[i]),
                "r_squared": r_squared,
                "n_obs": len(y_vec),
            }
            for i, name in enumerate(names)
        ]
    )


def construct_factor_returns(
    returns: pd.DataFrame,
    signal_table: pd.DataFrame,
    value_weighted: bool = False,
) -> pd.DataFrame:
    required_returns = {"date", "ticker", "ret"}
    required_signals = {"ticker", "filing_year", "climate_portfolio"}
    missing = required_returns - set(returns.columns)
    if missing:
        raise ValueError(f"returns missing columns: {sorted(missing)}")
    missing = required_signals - set(signal_table.columns)
    if missing:
        raise ValueError(f"signal_table missing columns: {sorted(missing)}")

    ret = returns.copy()
    sig = signal_table.copy()
    ret["date"] = pd.to_datetime(ret["date"])
    ret["signal_year"] = ret["date"].dt.year - 1
    sig = sig.rename(columns={"filing_year": "signal_year"})

    merged = ret.merge(
        sig[["ticker", "signal_year", "climate_portfolio", "overall_climate_risk_score"]],
        on=["ticker", "signal_year"],
        how="inner",
    )

    if value_weighted and "market_cap" in merged.columns:
        grouped = (
            merged.groupby(["date", "climate_portfolio"])
            .apply(lambda g: np.average(g["ret"], weights=g["market_cap"]))
            .rename("portfolio_return")
            .reset_index()
        )
    else:
        grouped = (
            merged.groupby(["date", "climate_portfolio"])["ret"]
            .mean()
            .rename("portfolio_return")
            .reset_index()
        )

    wide = grouped.pivot(index="date", columns="climate_portfolio", values="portfolio_return")
    for col in ["high", "low"]:
        if col not in wide:
            wide[col] = np.nan
    wide["climate_risk_factor"] = wide["high"] - wide["low"]
    wide = wide.reset_index()
    return wide.sort_values("date")


def summarize_returns(factor_returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    numeric_cols = [c for c in factor_returns.columns if c != "date"]
    for col in numeric_cols:
        series = factor_returns[col].dropna()
        if series.empty:
            continue
        ann_ret = _annualized_return(series)
        ann_vol = series.std(ddof=1) * math.sqrt(12)
        sharpe = ann_ret / ann_vol if ann_vol else np.nan
        rows.append(
            {
                "portfolio": col,
                "months": len(series),
                "mean_monthly_return": series.mean(),
                "annualized_return": ann_ret,
                "annualized_volatility": ann_vol,
                "sharpe": sharpe,
                "max_drawdown": _max_drawdown(series),
            }
        )
    return pd.DataFrame(rows)


def run_factor_regression(
    factor_returns: pd.DataFrame,
    benchmark_factors: pd.DataFrame,
    dependent_col: str = "climate_risk_factor",
) -> pd.DataFrame:
    data = factor_returns.merge(benchmark_factors, on="date", how="inner").dropna()
    candidates = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
    factor_cols = [col for col in candidates if col in data.columns]
    if "rf" in data.columns:
        y = data[dependent_col] - data["rf"]
    else:
        y = data[dependent_col]
    if sm is None:
        return _ols_numpy(y, data[factor_cols])

    x = sm.add_constant(data[factor_cols])
    model = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": 3})

    rows = []
    for name in model.params.index:
        rows.append(
            {
                "term": name,
                "coefficient": model.params[name],
                "t_stat": model.tvalues[name],
                "p_value": model.pvalues[name],
                "r_squared": model.rsquared,
                "n_obs": int(model.nobs),
            }
        )
    return pd.DataFrame(rows)


def run_predictive_regression(
    returns: pd.DataFrame,
    signal_table: pd.DataFrame,
    controls: list[str] | None = None,
) -> pd.DataFrame:
    controls = controls or ["log_market_cap", "momentum_12_1"]
    ret = returns.copy()
    sig = signal_table.copy()
    ret["date"] = pd.to_datetime(ret["date"])
    ret["signal_year"] = ret["date"].dt.year - 1
    sig = sig.rename(columns={"filing_year": "signal_year"})

    data = ret.merge(sig, on=["ticker", "signal_year"], how="inner")
    cols = ["overall_climate_risk_score"] + [c for c in controls if c in data.columns]
    data = data.dropna(subset=["ret", *cols])
    if data.empty:
        raise ValueError("No rows available for predictive regression.")

    if sm is None:
        return _ols_numpy(data["ret"], data[cols])

    x = sm.add_constant(data[cols])
    model = sm.OLS(data["ret"], x).fit(cov_type="cluster", cov_kwds={"groups": data["date"]})
    rows = []
    for name in model.params.index:
        rows.append(
            {
                "term": name,
                "coefficient": model.params[name],
                "t_stat": model.tvalues[name],
                "p_value": model.pvalues[name],
                "r_squared": model.rsquared,
                "n_obs": int(model.nobs),
            }
        )
    return pd.DataFrame(rows)

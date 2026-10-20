"""Which factor matters most? Does model size matter?

Fits a logistic regression on the *valid* triples (the ones where the model got
the agree and context-only versions right):

    trigger_win ~ direction + strength + distance + model        (model-as-category)
    trigger_win ~ direction + strength + distance + log(params)  (size as a number)

Standard errors are clustered by base_id, because the same scenario is run
through every model and those rows are not independent.

"Biggest effect" is answered two ways:
  * odds ratios (with 95% CI) for each factor level vs. its reference level
  * a joint Wald test per factor (p-value for "this factor does nothing")

Caveats that belong in the write-up:
  * 5 scenarios per cell is a pilot; expect wide intervals.
  * If a model (or cell) has trigger_win = 1.0 for everything, the logit cannot be
    estimated reliably (perfect separation). The script detects that, says so, and
    falls back to an L1-regularised fit: coefficients only, no p-values.

Usage:  python -m src.stats_analysis [--mock]
"""
import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from src.models.model_configs import MODELS


def load_valid(path):
    w = pd.read_csv(path)
    w = w[w.valid].copy()
    w["trigger_win"] = w.trigger_win.astype(int)
    w["log_params"] = np.log([MODELS.get(m, {}).get("params_m", np.nan) for m in w.model])
    return w


def fit(formula, data):
    """Returns (result, description, exact). exact=False means no valid p-values/CIs."""
    import warnings
    mod = smf.logit(formula, data=data)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = mod.fit(disp=0, maxiter=200, cov_type="cluster", cov_kwds={"groups": data["base_id"]})
        converged = res.mle_retvals.get("converged", True)
        # A huge coefficient means (quasi-)perfect separation: some level always/never wins.
        if (not converged) or (not np.all(np.isfinite(res.bse))) or (np.abs(res.params) > 10).any():
            bad = [n for n, v in res.params.items() if abs(v) > 10]
            raise ValueError(f"perfect/quasi-separation or non-convergence (extreme terms: {bad})")
        return res, "logit, cluster-robust SE", True
    except Exception as e:
        print(f"  ! standard logit unreliable: {e}")
        print("  ! falling back to L1-regularised fit: coefficients only, NO p-values or CIs")
        res = mod.fit_regularized(method="l1", alpha=0.5, disp=0)
        return res, "L1-regularised fallback", False


def odds_table(res, exact):
    if exact:
        ci = res.conf_int()
        t = pd.DataFrame({"odds_ratio": np.exp(res.params), "ci95_lo": np.exp(ci[0]),
                          "ci95_hi": np.exp(ci[1]), "p_value": res.pvalues})
    else:
        t = pd.DataFrame({"odds_ratio": np.exp(res.params)})
    return t.drop(index="Intercept", errors="ignore")


def joint_wald(res, data, factors):
    """p-value for each factor as a whole (all its levels = 0)."""
    names = list(res.params.index)
    rows = []
    for f in factors:
        idx = [i for i, n in enumerate(names) if n.startswith(f"C({f})")]
        if not idx:
            continue
        R = np.zeros((len(idx), len(names)))
        for r, i in enumerate(idx):
            R[r, i] = 1
        wt = res.wald_test(R, scalar=True)
        rows.append({"factor": f, "wald_chi2": float(wt.statistic), "df": len(idx), "p_value": float(wt.pvalue)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--triples", default=None)
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    tag = "_mock" if a.mock else ""
    w = load_valid(a.triples or f"results/tables/triples{tag}.csv")
    print(f"{len(w)} valid triples across {w.model.nunique()} models, {w.base_id.nunique()} scenarios")
    pd.set_option("display.float_format", lambda v: f"{v:.3f}")
    pd.set_option("display.width", 160)

    # --- model A: factors + model as category ---
    fA = ("trigger_win ~ C(direction) + C(strength, Treatment('strong')) + "
          "C(distance, Treatment('near')) + C(model)")
    fA = fA.replace("C(strength, Treatment('strong'))", "C(strength)").replace("C(distance, Treatment('near'))", "C(distance)")
    resA, kindA, exact = fit(fA, w)
    print(f"\n=== Model A: factors + model identity [{kindA}] ===")
    tA = odds_table(resA, exact)
    print(tA)
    tA.to_csv(f"{a.out_dir}/regression_odds_ratios{tag}.csv")
    if exact:
        jw = joint_wald(resA, w, ["direction", "strength", "distance", "model"])
        print("\nJoint Wald test per factor (small p = the factor matters):")
        print(jw.to_string(index=False))
        jw.to_csv(f"{a.out_dir}/regression_factor_tests{tag}.csv", index=False)
        print("\nNote: odds ratio > 1 means the trigger word wins MORE than the reference level.")

    # --- model B: size as a number ---
    wB = w.dropna(subset=["log_params"])
    if wB.log_params.nunique() > 1:
        resB, kindB, exactB = fit("trigger_win ~ C(direction) + C(strength) + C(distance) + log_params", wB)
        print(f"\n=== Model B: does size matter? [{kindB}] ===")
        if exactB:
            b, p = resB.params["log_params"], resB.pvalues["log_params"]
            ci = resB.conf_int().loc["log_params"]
            print(f"log(params) coefficient = {b:.3f}  (odds ratio per doubling = {np.exp(b*np.log(2)):.2f}, "
                  f"95% CI {np.exp(ci[0]*np.log(2)):.2f}-{np.exp(ci[1]*np.log(2)):.2f}, p = {p:.3f})")
            print("Odds ratio per doubling < 1 means bigger models are fooled less often.")
        else:
            print(f"log(params) coefficient = {resB.params['log_params']:.3f} (no p-value in fallback)")
    else:
        print("\n(size analysis skipped: need at least two models with known parameter counts)")


if __name__ == "__main__":
    main()

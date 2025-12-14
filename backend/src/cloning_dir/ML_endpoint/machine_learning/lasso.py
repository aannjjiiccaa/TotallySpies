import numpy as np
import matplotlib.pyplot as plt


def generate_exponent_tuples(p: int, degree: int):
    """
    All exponent tuples (e1,...,ep) with sum(ei) <= degree.
    Includes the all-zeros tuple (bias term).
    """
    exps = []

    def rec(i, remaining, current):
        if i == p:
            exps.append(tuple(current))
            return
        # ei can be 0..remaining
        for ei in range(remaining + 1):
            current.append(ei)
            rec(i + 1, remaining - ei, current)
            current.pop()

    # We want sum <= degree, so generate for each total d=0..degree
    for d in range(degree + 1):
        rec(0, d, [])
    return exps  # list of tuples

def poly_design_matrix(X_raw: np.ndarray, degree: int = 3):
    """
    X_raw: (n, p) predictors
    Returns:
      Phi: (n, m) polynomial feature matrix including bias column first
      exps: list of exponent tuples corresponding to each column
    """
    n, p = X_raw.shape
    exps = generate_exponent_tuples(p, degree)
    m = len(exps)
    Phi = np.ones((n, m), dtype=float)

    # Build each monomial column
    for k, e in enumerate(exps):
        # monomial = prod_j x_j ** e_j
        col = np.ones(n, dtype=float)
        for j in range(p):
            if e[j] != 0:
                col *= X_raw[:, j] ** e[j]
        Phi[:, k] = col

    return Phi, exps

def exp_to_string(e, var_names=None):
    if var_names is None:
        var_names = [f"x{j+1}" for j in range(len(e))]
    terms = []
    for v, pow_ in zip(var_names, e):
        if pow_ == 0:
            continue
        if pow_ == 1:
            terms.append(v)
        else:
            terms.append(f"{v}^{pow_}")
    return "1" if not terms else "*".join(terms)


def standardize_train_val(X_train, X_val, eps=1e-12):
    mu = X_train.mean(axis=0)
    sigma = X_train.std(axis=0)
    sigma = np.where(sigma < eps, 1.0, sigma)  # avoid divide by zero
    X_train_s = (X_train - mu) / sigma
    X_val_s = (X_val - mu) / sigma
    return X_train_s, X_val_s, mu, sigma


def soft_threshold(z, gamma):
    if z > gamma:
        return z - gamma
    if z < -gamma:
        return z + gamma
    return 0.0


def lasso_coordinate_descent(X, y, lam, max_iter=5000, tol=1e-6):
    """
    Solve: (1/2n)||y - (b + Xw)||^2 + lam * ||w||_1
    X: (n, d) standardized features (NO bias column)
    y: (n,)
    Returns b, w
    """
    n, d = X.shape
    w = np.zeros(d, dtype=float)
    b = y.mean()  # good init for intercept

    # residual r = y - (b + Xw)
    r = y - (b + X @ w)

    # precompute column norms (1/n)*sum x_ij^2
    col_norm = (X * X).sum(axis=0) / n

    for it in range(max_iter):
        w_old = w.copy()
        b_old = b

        # update intercept (not penalized)
        # minimize (1/2n)|| (y - Xw) - b ||^2 -> b = mean(y - Xw)
        b = np.mean(y - X @ w)
        r = y - (b + X @ w)

        # update each coordinate
        for j in range(d):
            # add back contribution of j
            r += X[:, j] * w[j]

            # rho = (1/n) * x_j^T r
            rho = (X[:, j] @ r) / n

            # lasso update with soft threshold
            w[j] = soft_threshold(rho, lam) / (col_norm[j] + 1e-12)

            # remove updated contribution
            r -= X[:, j] * w[j]

        # convergence check
        max_change = max(np.max(np.abs(w - w_old)), abs(b - b_old))
        if max_change < tol:
            break

    return b, w


def rmse(y_true, y_pred):
    err = y_true - y_pred
    return np.sqrt(np.mean(err * err))


def kfold_indices(n, k=5, seed=0):
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    folds = np.array_split(idx, k)
    return folds

def cross_validate_lasso(X_raw, y, degree=3, lambdas=None, k=5, seed=0):
    Phi, exps = poly_design_matrix(X_raw, degree=degree)

    # Separate bias column from the rest:
    # bias is the column corresponding to exponent tuple all zeros, which will appear multiple times
    # In our generator, d=0 term is first => bias is column 0.
    bias_col = Phi[:, [0]]
    feats = Phi[:, 1:]  # no bias column
    exps_no_bias = exps[1:]

    n = X_raw.shape[0]
    folds = kfold_indices(n, k=k, seed=seed)

    if lambdas is None:
        lambdas = np.logspace(-4, 1, 40)  # adjust as needed

    mean_rmses = []
    std_rmses = []

    for lam in lambdas:
        fold_rmses = []
        for i in range(k):
            val_idx = folds[i]
            train_idx = np.hstack([folds[j] for j in range(k) if j != i])

            Xtr = feats[train_idx]
            Xva = feats[val_idx]
            ytr = y[train_idx]
            yva = y[val_idx]

            # standardize based on train fold only
            Xtr_s, Xva_s, mu, sigma = standardize_train_val(Xtr, Xva)

            b, w = lasso_coordinate_descent(Xtr_s, ytr, lam=lam)

            yhat = b + Xva_s @ w
            fold_rmses.append(rmse(yva, yhat))

        mean_rmses.append(np.mean(fold_rmses))
        std_rmses.append(np.std(fold_rmses))

    mean_rmses = np.array(mean_rmses)
    std_rmses = np.array(std_rmses)
    best_i = int(np.argmin(mean_rmses))
    best_lam = float(lambdas[best_i])

    return {
        "lambdas": np.array(lambdas),
        "mean_rmse": mean_rmses,
        "std_rmse": std_rmses,
        "best_lambda": best_lam,
        "Phi_exps_no_bias": exps_no_bias,
    }


def main():
    # Load CSV: first 4 cols predictors, last col target (per assignment)
    data = np.loadtxt("data_hw1_2025.csv", delimiter=",")
    X_raw = data[:, :4]
    y = data[:, 4]

    # Choose lambdas and CV
    lambdas = np.logspace(-4, 1, 50)
    cv = cross_validate_lasso(X_raw, y, degree=3, lambdas=lambdas, k=5, seed=42)

    best_lam = cv["best_lambda"]
    print("Best lambda:", best_lam)

    # Plot CV curve
    plt.figure()
    plt.semilogx(cv["lambdas"], cv["mean_rmse"])
    plt.fill_between(cv["lambdas"],
                     cv["mean_rmse"] - cv["std_rmse"],
                     cv["mean_rmse"] + cv["std_rmse"],
                     alpha=0.2)
    plt.xlabel("lambda")
    plt.ylabel("CV RMSE")
    plt.title("LASSO (degree-3 polynomial) - CV RMSE vs lambda")
    plt.grid(True, which="both", ls="--", alpha=0.4)
    plt.tight_layout()
    plt.show()

    # Retrain on full data using best lambda
    Phi, exps = poly_design_matrix(X_raw, degree=3)
    feats = Phi[:, 1:]  # exclude bias
    feats_s, _, mu, sigma = standardize_train_val(feats, feats)  # standardize with full-data stats
    b, w = lasso_coordinate_descent(feats_s, y, lam=best_lam)

    # Estimated RMSE using CV minimum
    best_rmse = float(np.min(cv["mean_rmse"]))
    print("Estimated RMSE (CV mean):", best_rmse)

    # Print hypothesis (only non-zero terms)
    exps_no_bias = exps[1:]
    var_names = ["x1", "x2", "x3", "x4"]

    print("\nLearned hypothesis (standardized-feature space):")
    print(f"y_hat = {b:.6f} + sum_j w_j * phi_j(x)")

    nz = np.where(np.abs(w) > 1e-8)[0]
    print(f"\nNon-zero terms: {len(nz)} / {len(w)}")
    for j in nz:
        term = exp_to_string(exps_no_bias[j], var_names)
        print(f"  {w[j]: .6f} * {term}")

    # NOTE: If you need the hypothesis in original (unstandardized) polynomial features,
    # you can algebraically "unscale" coefficients, but for the homework it's usually
    # acceptable to report with the preprocessing described.

if __name__ == "__main__":
    main()

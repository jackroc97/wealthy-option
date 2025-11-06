import pandas as pd
import itertools
import yaml

# --- Load parameter space from YAML ---
with open("./backtests/doe.yaml", "r") as f:
    param_space = yaml.safe_load(f)["param_space"]

# --- Generate DOE for each strategy ---
dfs = []
all_columns = set()

for strategy, params in param_space.items():
    keys, values = zip(*params.items())
    combos = [dict(zip(keys, v)) for v in itertools.product(*values)]
    df = pd.DataFrame(combos)
    dfs.append(df)
    all_columns.update(df.columns)

# --- Normalize columns across all strategies ---
all_columns = sorted(all_columns)
for i in range(len(dfs)):
    for col in all_columns:
        if col not in dfs[i].columns:
            dfs[i][col] = None
    dfs[i] = dfs[i][all_columns]  # reorder columns

# --- Combine all into a single DOE table ---
doe_df = pd.concat(dfs, ignore_index=True)

# --- Add unique ID for tracking ---
doe_df.insert(0, "design_id", range(1, len(doe_df) + 1))

# --- Export to CSV ---
doe_df.to_csv("doe_designs.csv", index=False)

print(f"DOE generated with {len(doe_df)} total designs.")
print("Columns:", list(doe_df.columns))
print(doe_df.head(10))

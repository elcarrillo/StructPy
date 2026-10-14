import pandas as pd
from structpy.validate import validate_data

# Example DataFrame
data = {
    "A": [1, 2, None, 4],
    "B": [100, 200, 300, 400],
    "C": [5, 5, 5, 1000]  # Outlier in column C
}
df = pd.DataFrame(data)

# Run validation
validate_data(df)

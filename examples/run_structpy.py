from structpy.core_features import create_project_dirs, generate_filename, backup_project
from structpy.validate import validate_data
import pandas as pd

# 1. Create directories
create_project_dirs("./example_project")

# 2. Generate a filename
filename = generate_filename(prefix="example", ext="csv")
print(f"Generated filename: {filename}")

# 3. Validate a dataset
data = {
    "A": [1, 2, None],
    "B": [4, None, 6],
    "C": [100, 200, 300]
}
df = pd.DataFrame(data)
validate_data(df)

# 4. Backup the project
backup_project("./example_project", archive_name="example_project_backup")

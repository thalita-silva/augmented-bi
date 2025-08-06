import pandas as pd
import io

class DataCleanerTools:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_all_tools(self) -> list:
        """Helper method to return a list of all tools in the class."""
        return [
            self.standardize_column_names,
            self.handle_missing_values,
            self.remove_duplicates,
            self.normalize_numeric_formats,
            self.standardize_date_formats,
            self.fix_encoding_and_characters,
            self.propose_and_apply_category_standardization,
        ]

    def get_final_dataframe(self) -> pd.DataFrame:
        """Returns the modified DataFrame."""
        return self.df

    def standardize_column_names(self) -> str:
        """Standardizes all column names to snake_case."""
        self.df.columns = self.df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
        return "Column names standardized to snake_case."

    def handle_missing_values(self, strategy: str = 'fill_zero') -> str:
        """
        Handles missing values based on a specified strategy.
        Strategy options: 'fill_zero', 'leave_as_is'.
        """
        if strategy == 'fill_zero':
            for col in self.df.columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(0, inplace=True)
            return "Missing numeric values filled with 0."
        elif strategy == 'leave_as_is':
            return "Missing values were left as they are."
        else:
            return "Invalid strategy for handling missing values."

    def remove_duplicates(self) -> str:
        """Removes all duplicate rows from the DataFrame."""
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed_rows = initial_rows - len(self.df)
        return f"Removed {removed_rows} duplicate row(s)."
    
    def normalize_numeric_formats(self) -> str:
        """Normalizes numeric formats (e.g., replaces commas with periods)."""
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].astype(str).str.replace(',', '.', regex=True)
            try:
                self.df[col] = pd.to_numeric(self.df[col])
            except ValueError:
                pass
        return "Numeric formats normalized."

    def standardize_date_formats(self) -> str:
        """Standardizes all date columns to 'yyyy-mm-dd'."""
        for col in self.df.columns:
            if 'date' in col.lower() or 'timestamp' in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col])
                    return f"Date formats standardized for column '{col}'."
                except (ValueError, TypeError):
                    pass
        return "Date formats standardized."

    def fix_encoding_and_characters(self) -> str:
        """Fixes encoding and removes special characters from string columns."""
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].astype(str).str.encode('ascii', 'ignore').str.decode('utf-8')
        return "Encoding issues and special characters handled."
    
    def propose_and_apply_category_standardization(self, column: str, mapping: dict) -> str:
        """
        Applies a dictionary mapping to standardize inconsistent categorical values.
        Example mapping: {'Heinken': 'Heineken', 'HNK': 'Heineken'}.
        """
        if column in self.df.columns:
            self.df[column] = self.df[column].replace(mapping)
            return f"Categorical values in column '{column}' standardized using the provided mapping."
        return f"Column '{column}' not found. Skipping standardization."

import pandas as pd
import numpy as np
import chardet

class DataAuditorTools:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_all_tools(self) -> list:
        """Helper method to return a list of all tools in the class."""
        return [
            self.get_dataframe_info,
            self.find_missing_values,
            self.detect_duplicates,
            self.check_data_types,
            self.check_date_formats,
            self.analyze_numeric_scale_and_format,
            self.detect_encoding_and_special_chars,
            self.identify_outliers_numbers,
            self.identify_date_outliers,
            self.analyze_categorical_frequency,
        ]

    def get_dataframe_info(self) -> str:
        """
        Calculates and returns basic info about the DataFrame.
        This includes number of rows, columns, data types, and non-null counts.
        """
        info_buffer = io.StringIO()
        self.df.info(buf=info_buffer, verbose=True)
        return info_buffer.getvalue()

    def find_missing_values(self) -> str:
        """
        Identifies columns with missing values and returns a summary.
        Includes column name, number of missing values, and percentage.
        """
        missing_data = self.df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if missing_data.empty:
            return "No missing values found in any column."
        
        report = "Missing Values Report:\n"
        for column, count in missing_data.items():
            percentage = (count / len(self.df)) * 100
            report += f"- Column '{column}': {count} missing values ({percentage:.2f}%)\n"
        return report

    def detect_duplicates(self) -> str:
        """
        Checks for and reports the total number of duplicate rows in the DataFrame.
        """
        num_duplicates = self.df.duplicated().sum()
        if num_duplicates == 0:
            return "No duplicate rows found."
        return f"Found {num_duplicates} duplicate row(s)."
    
    def check_data_types(self) -> str:
        """
        Verifies if data types are consistent and suggests corrections.
        This tool identifies columns with mixed data types or incorrect types (e.g., numbers stored as strings).
        """
        report = "Data Type Check Report:\n"
        has_issue = False
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                try:
                    # Check if object column can be converted to numeric
                    pd.to_numeric(self.df[col])
                    report += f"- Column '{col}' contains numeric values and could be converted to a numeric type.\n"
                    has_issue = True
                except (ValueError, TypeError):
                    pass
        
        if not has_issue:
            return "All data types appear consistent. No issues found."
        return report

    def check_date_formats(self) -> str:
        """
        Inspects all datetime-like columns to identify inconsistent date formats.
        """
        report = "Date Format Check Report:\n"
        has_issue = False
        for col in self.df.columns:
            # Check if column looks like a date
            if 'date' in col.lower() or 'timestamp' in col.lower():
                try:
                    pd.to_datetime(self.df[col])
                except (ValueError, TypeError):
                    report += f"- Column '{col}' has inconsistent date formats and cannot be reliably parsed.\n"
                    has_issue = True
        if not has_issue:
            return "All date columns appear consistent. No issues found."
        return report

    def analyze_numeric_scale_and_format(self) -> str:
        """
        Analyzes numeric columns for scaling and formatting issues (e.g., comma decimals).
        """
        report = "Numeric Format & Scale Check Report:\n"
        has_issue = False
        for col in self.df.select_dtypes(include=['object']).columns:
            # Check for comma decimals
            if self.df[col].astype(str).str.contains(',').any():
                report += f"- Column '{col}' uses commas as decimal separators. Suggest replacing with periods.\n"
                has_issue = True
        
        # This is a heuristic and can be improved
        for col in self.df.select_dtypes(include=np.number).columns:
            if self.df[col].max() > 1000000 and self.df[col].min() > 1000:
                report += f"- Column '{col}' may be in a different scale (e.g., thousands or millions). Requires review.\n"
                has_issue = True
        
        if not has_issue:
            return "Numeric formats and scales appear consistent. No issues found."
        return report
        
    def detect_encoding_and_special_chars(self) -> str:
        """
        Detects encoding and presence of special characters in a text column.
        """
        report = "Encoding & Special Characters Report:\n"
        has_issue = False
        for col in self.df.select_dtypes(include=['object']).columns:
            text_data = ' '.join(self.df[col].dropna().astype(str))
            
            # Detect encoding
            if text_data:
                result = chardet.detect(text_data.encode())
                if result['encoding'] not in ['utf-8', 'ascii'] or result['confidence'] < 0.9:
                    report += f"- Column '{col}' might have encoding issues. Detected as {result['encoding']} with confidence {result['confidence']:.2f}.\n"
                    has_issue = True
            
            # Detect special characters
            if self.df[col].astype(str).str.contains(r'[^\x00-\x7F]+', regex=True).any():
                report += f"- Column '{col}' contains non-ASCII characters that may need to be handled.\n"
                has_issue = True

        if not has_issue:
            return "No encoding or special character issues found."
        return report

    def identify_outliers_numbers(self) -> str:
        """
        Detects potential outliers in a numeric column using the IQR method.
        """
        report = "Numeric Outlier Report:\n"
        has_issue = False
        for col in self.df.select_dtypes(include=np.number).columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            num_outliers = len(outliers)
            
            if num_outliers > 0:
                report += f"- Column '{col}' has {num_outliers} potential outliers (values outside ({lower_bound:.2f}, {upper_bound:.2f})).\n"
                has_issue = True
        
        if not has_issue:
            return "No significant numeric outliers detected."
        return report

    def identify_date_outliers(self) -> str:
        """
        Analyzes datetime columns to identify dates that are excessively old or in the future.
        """
        report = "Date Outlier Report:\n"
        has_issue = False
        for col in self.df.columns:
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                min_date = self.df[col].min()
                max_date = self.df[col].max()
                
                if min_date < pd.to_datetime('1900-01-01'):
                    report += f"- Column '{col}' has a very old date: {min_date.strftime('%Y-%m-%d')}.\n"
                    has_issue = True
                if max_date > pd.to_datetime('2050-01-01'):
                    report += f"- Column '{col}' has a very future date: {max_date.strftime('%Y-%m-%d')}.\n"
                    has_issue = True
        
        if not has_issue:
            return "No significant date outliers detected."
        return report

    def analyze_categorical_frequency(self) -> str:
        """
        Analyzes categorical columns for predominant or very low frequency values.
        """
        report = "Categorical Frequency Report:\n"
        has_issue = False
        for col in self.df.select_dtypes(include=['object']).columns:
            value_counts = self.df[col].value_counts(normalize=True)
            if value_counts.iloc[0] > 0.9:
                report += f"- Column '{col}' has a predominant value: '{value_counts.index[0]}' (over 90%).\n"
                has_issue = True
            if value_counts.iloc[-1] < 0.01 and len(value_counts) > 20:
                report += f"- Column '{col}' has many low-frequency values. May require standardization.\n"
                has_issue = True
        
        if not has_issue:
            return "Categorical frequencies appear normal. No issues found."
        return report

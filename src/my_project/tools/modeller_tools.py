import pandas as pd

class DataModellerTools:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_all_tools(self) -> list:
        """Helper method to return a list of all tools in the class."""
        return [
            self.analyze_dataset_for_modeling,
            self.propose_table_name,
            self.apply_table_rename,
            self.identify_primary_keys,
            self.propose_bi_structure,
        ]

    def analyze_dataset_for_modeling(self) -> str:
        """Analyzes the DataFrame to identify its core entities and potential relationships."""
        report = "Dataset Analysis for Modeling:\n"
        report += f"Total rows: {len(self.df)}\n"
        report += "Potential keys based on uniqueness:\n"
        for col in self.df.columns:
            if self.df[col].nunique() == len(self.df):
                report += f"- Column '{col}' is a potential primary key (all values are unique).\n"
        return report

    def propose_table_name(self) -> str:
        """Proposes a business-friendly name for the table based on its content."""
        from collections import Counter
        from wordcloud import WordCloud

        # This is a simplified heuristic to get common words from string columns
        all_words = []
        for col in self.df.select_dtypes(include=['object']).columns:
            all_words.extend(' '.join(self.df[col].astype(str)).lower().split())
        
        most_common = Counter(all_words).most_common(5)
        
        if most_common:
            base_name = most_common[0][0].capitalize()
            return f"{base_name}_Data"
        
        return "Data_Table"
    
    def apply_table_rename(self, new_name: str) -> str:
        """Renames the table/DataFrame. This is a placeholder for the user's final file name."""
        # This function doesn't modify the DataFrame itself, but prepares the app for the download with a new file name.
        return f"Table name approved and set to '{new_name}'."

    def identify_primary_keys(self) -> str:
        """Identifies columns that could serve as primary keys."""
        report = "Primary Key Identification:\n"
        potential_keys = [col for col in self.df.columns if self.df[col].nunique() == len(self.df)]
        if potential_keys:
            report += "The following columns are potential primary keys:\n"
            for key in potential_keys:
                report += f"- {key}\n"
        else:
            report += "No obvious primary keys found. A composite key might be needed."
        return report

    def propose_bi_structure(self) -> str:
        """Synthesizes all modeling suggestions into a final report."""
        report = "BI Structure Proposal:\n"
        report += f"Suggested Table Name: {self.propose_table_name()}\n"
        report += self.identify_primary_keys()
        return report

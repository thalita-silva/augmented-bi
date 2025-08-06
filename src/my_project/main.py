# main.py

#!/usr/bin/env python
import sys
import warnings
import os
import pandas as pd
from dotenv import load_dotenv

# Import the main Crew class from your project's package
from crew import AugmentedBICrew


# Load environment variables from .env file
load_dotenv()

# Filter out specific warnings if necessary (e.g., from external libraries)
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run_proactive_analysis(df: pd.DataFrame) -> str:
    """
    Runs the proactive analysis phase of the Augmented BI Crew.
    This phase involves the Data Auditor and the Chat Consultant's initial greeting/plan proposal.
    It returns the AI's initial report/message to the user.
    """
    # Create inputs dictionary, passing the DataFrame
    inputs = {'dataframe': df}
    
    # Instantiate the AugmentedBICrew class
    augmented_bi_crew_instance = AugmentedBICrew(inputs)
    
    # Get the proactive crew and kickoff the process
    proactive_crew = augmented_bi_crew_instance.proactive_crew()
    
    # The kickoff method will run the defined tasks and return the final output of the last task
    result = proactive_crew.kickoff()
    
    return result

def run_cleaning_and_modelling(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """
    Runs the cleaning, modeling, and final reporting phase of the Augmented BI Crew.
    This phase is triggered after the user approves the initial plan.
    It returns the final report from the Chat Consultant and the cleaned DataFrame.
    """
    # Create inputs dictionary, passing the DataFrame
    inputs = {'dataframe': df}
    
    # Instantiate the AugmentedBICrew class
    augmented_bi_crew_instance = AugmentedBICrew(inputs)
    
    # Get the post-approval crew and kickoff the process
    post_approval_crew = augmented_bi_crew_instance.post_approval_crew()
    
    # The kickoff method will run the defined tasks and return the final output of the last task
    final_report = post_approval_crew.kickoff()
    
    # Retrieve the final cleaned DataFrame from the crew's tools
    df_cleaned = augmented_bi_crew_instance.get_final_dataframe()
    
    return final_report, df_cleaned

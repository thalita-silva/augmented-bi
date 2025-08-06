# src/my_project/crew.py

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List
import yaml
import os
import pandas as pd
# Using relative imports for modules within the same 'my_project' package
from .tools.auditor_tools import DataAuditorTools
from .tools.cleaner_tools import DataCleanerTools
from .tools.modeller_tools import DataModellerTools

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") 

@CrewBase
class AugmentedBICrew():
    """Augmented BI Data Cleaning and Modeling Crew"""

    def __init__(self, inputs: dict):
        self.inputs = inputs
        self.df = inputs.get('dataframe', pd.DataFrame())
        # Load YAML files using a path relative to the current file's location
        self.agents_config = self.load_yaml('config/agents.yaml')
        self.tasks_config = self.load_yaml('config/tasks.yaml')

        # Instantiate tools with the DataFrame once
        self.auditor_tools = DataAuditorTools(df=self.df)
        self.cleaner_tools = DataCleanerTools(df=self.df)
        self.modeller_tools = DataModellerTools(df=self.df)

    def load_yaml(self, file_path: str):
        # The path is now relative to 'src/my_project/' where crew.py resides
        # For example, 'config/agents.yaml' correctly points to 'src/my_project/config/agents.yaml'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, file_path)
        with open(full_path, 'r') as file:
            return yaml.safe_load(file)
            
    def get_final_dataframe(self) -> pd.DataFrame:
        """Helper method to retrieve the final cleaned DataFrame from the tools."""
        return self.cleaner_tools.get_final_dataframe()

  # --- Agent Definitions ---
  @agent
  def chat_consultant(self) -> Agent:
      return Agent(
          config=self.agents_config['chat_consultant'],
          verbose=True,
          tools=[]
      )

  @agent
  def data_auditor(self) -> Agent:
      return Agent(
          config=self.agents_config['data_auditor'],
          verbose=True,
          tools=self.auditor_tools.get_all_tools()
      )

  @agent
  def data_cleaner(self) -> Agent:
      return Agent(
          config=self.agents_config['data_cleaner'],
          verbose=True,
          tools=self.cleaner_tools.get_all_tools()
      )
  
  @agent
  def data_modeller(self) -> Agent:
      return Agent(
          config=self.agents_config['data_modeller'],
          verbose=True,
          tools=self.modeller_tools.get_all_tools()
      )

  # --- Task Definitions (Correctly Chained) ---

  # Data Auditor diagnostic tasks
  @task
  def t_analyze_dataframe_info(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_dataframe_info'], 
                  agent=self.data_auditor())

  @task
  def t_find_missing_values(self) -> Task:
      return Task(config=self.tasks_config['t_find_missing_values'], 
                  agent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])

  @task
  def t_detect_duplicates(self) -> Task:
      return Task(config=self.tasks_config['t_detect_duplicates'], 
                  agent=self.data_auditor(),
                    context=[self.t_analyze_dataframe_info()])
  
  @task
  def t_check_data_types_and_inconsistencies(self) -> Task:
      return Task(config=self.tasks_config['t_check_data_types_and_inconsistencies'], 
                  agent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])
  
  @task
  def t_check_date_formats(self) -> Task:
      return Task(config=self.tasks_config['t_check_date_formats'], 
                  agent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])
  
  @task
  def t_analyze_numeric_scale_and_format(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_numeric_scale_and_format'], 
                  agent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])
  
  @task
  def t_detect_encoding_and_special_chars(self) -> Task:
      return Task(config=self.tasks_config['t_detect_encoding_and_special_chars'],
                  gent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])
  
  @task
  def t_identify_outliers_numbers(self) -> Task:
      return Task(config=self.tasks_config['t_identify_outliers_numbers'], 
                  agent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])
  
  @task
  def t_identify_date_outliers(self) -> Task:
      return Task(config=self.tasks_config['t_identify_date_outliers'], 
                  agent=self.data_auditor(), 
                  context=[self.t_check_date_formats()])
  
  @task
  def t_analyze_categorical_frequency(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_categorical_frequency'], 
                  agent=self.data_auditor(), 
                  context=[self.t_analyze_dataframe_info()])

  # The central task that synthesizes the audit findings
  @task
  def t_propose_initial_cleaning_plan(self) -> Task:
      return Task(config=self.tasks_config['t_propose_initial_cleaning_plan'], 
                  agent=self.data_auditor(),
                  context=[
                      self.t_find_missing_values(), 
                      self.t_detect_duplicates(),
                      self.t_check_data_types_and_inconsistencies(), 
                      self.t_check_date_formats(),
                      self.t_analyze_numeric_scale_and_format(), 
                      self.t_detect_encoding_and_special_chars(),
                      self.t_identify_outliers_numbers(), 
                      self.t_identify_date_outliers(),
                      self.t_analyze_categorical_frequency()
                  ])
  
  # Chat Consultant start task (proactive)
  @task
  def t_initial_greeting_and_confirmation(self) -> Task:
      return Task(config=self.tasks_config['t_initial_greeting_and_confirmation'], 
                  agent=self.chat_consultant(), 
                  context=[self.t_propose_initial_cleaning_plan()])

  # Data Cleaner Tasks
  @task
  def t_standardize_column_names(self) -> Task:
      return Task(config=self.tasks_config['t_standardize_column_names'], 
                  agent=self.data_cleaner(),
                  context=[self.t_propose_initial_cleaning_plan()])
  
  @task
  def t_handle_missing_values(self) -> Task:
      return Task(config=self.tasks_config['t_handle_missing_values'], 
                  agent=self.data_cleaner(), 
                  context=[self.t_standardize_column_names()])

  @task
  def t_remove_duplicates(self) -> Task:
      return Task(config=self.tasks_config['t_remove_duplicates'], 
                  agent=self.data_cleaner(), 
                  context=[self.t_handle_missing_values()])

  @task
  def t_normalize_numeric_formats(self) -> Task:
      return Task(config=self.tasks_config['t_normalize_numeric_formats'],
                  agent=self.data_cleaner(), 
                  context=[self.t_remove_duplicates()])

  @task
  def t_standardize_date_formats(self) -> Task:
      return Task(config=self.tasks_config['t_standardize_date_formats'], 
                  agent=self.data_cleaner(), 
                  context=[self.t_normalize_numeric_formats()])
  
  @task
  def t_fix_encoding_and_characters(self) -> Task:
      return Task(config=self.tasks_config['t_fix_encoding_and_characters'], 
                  agent=self.data_cleaner(), 
                  context=[self.t_standardize_date_formats()])
  
  @task
  def t_propose_and_apply_category_standardization(self) -> Task:
      return Task(config=self.tasks_config['t_propose_and_apply_category_standardization'], 
                  agent=self.data_cleaner(), 
                  context=[self.t_fix_encoding_and_characters()])

  # Data Modeller Tasks (chained)
  @task
  def t_analyze_dataset_for_modeling(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_dataset_for_modeling'], 
                  agent=self.data_modeller(), 
                  context=[self.t_propose_and_apply_category_standardization()])
  
  @task
  def t_propose_table_name(self) -> Task:
      return Task(config=self.tasks_config['t_propose_table_name'], 
                  agent=self.data_modeller(), 
                  context=[self.t_analyze_dataset_for_modeling()])
  
  @task
  def t_apply_table_rename(self) -> Task:
      return Task(config=self.tasks_config['t_apply_table_rename'], 
                  agent=self.data_modeller(), 
                  context=[self.t_propose_table_name()])
  
  @task
  def t_identify_primary_keys(self) -> Task:
      return Task(config=self.tasks_config['t_identify_primary_keys'], 
                  agent=self.data_modeller(), 
                  context=[self.t_apply_table_rename()])
  
  @task
  def t_propose_bi_structure(self) -> Task:
      return Task(config=self.tasks_config['t_propose_bi_structure'], 
                  agent=self.data_modeller(), 
                  context=[self.t_identify_primary_keys()])
  
  # Chat Consultant final report
  @task
  def t_present_final_report(self) -> Task:
      return Task(config=self.tasks_config['t_present_final_report'],
                  agent=self.chat_consultant(), 
                  context=[self.t_propose_bi_structure()])

  # --- Crew Definitions for each phase ---

  def proactive_crew(self) -> Crew:
      return Crew(
          agents=[self.chat_consultant(), self.data_auditor()],
          tasks=[
              self.t_analyze_dataframe_info(), self.t_find_missing_values(), self.t_detect_duplicates(),
              self.t_check_data_types_and_inconsistencies(), self.t_check_date_formats(),
              self.t_analyze_numeric_scale_and_format(), self.t_detect_encoding_and_special_chars(),
              self.t_identify_outliers_numbers(), self.t_identify_date_outliers(),
              self.t_analyze_categorical_frequency(), self.t_propose_initial_cleaning_plan(),
              self.t_initial_greeting_and_confirmation()
          ],
          process=Process.sequential,
          verbose=True
      )

  def post_approval_crew(self) -> Crew:
      return Crew(
          agents=[self.data_cleaner(), self.data_modeller(), self.chat_consultant()],
          tasks=[
              self.t_standardize_column_names(), self.t_handle_missing_values(), self.t_remove_duplicates(),
              self.t_normalize_numeric_formats(), self.t_standardize_date_formats(),
              self.t_fix_encoding_and_characters(), self.t_propose_and_apply_category_standardization(),
              self.t_analyze_dataset_for_modeling(), self.t_propose_table_name(), self.t_apply_table_rename(),
              self.t_identify_primary_keys(), self.t_propose_bi_structure(),
              self.t_present_final_report()
          ],
          process=Process.sequential,
          verbose=True
      )
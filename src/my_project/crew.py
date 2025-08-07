from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List
import yaml

@CrewBase
class AugmentedBI():

  agents_config = 'config/agents.yaml'
  tasks_config = 'config/tasks.yaml'
  
  def __init__(self, inputs):
      self.inputs = inputs

  @agent
  def chat_consultant(self) -> Agent:
    return Agent(
      config=self.agents_config['chat_consultant'], 
      verbose=True
    )

  @agent
  def data_auditor(self) -> Agent:
    return Agent(
      config=self.agents_config['data_auditor'], 
      verbose=True
    )

  @agent
  def data_cleaner(self) -> Agent:
    return Agent(
      config=self.agents_config['data_cleaner'], 
      verbose=True
    )

  @agent
  def data_modeller(self) -> Agent:
    return Agent(
      config=self.agents_config['data_modeller'], 
      verbose=True
    )

  # --Task Definitions ---
  
  # Chat Consultant Start Task
  @task
  def t_initial_greeting_and_confirmation(self) -> Task:
      return Task(config=self.tasks_config['t_initial_greeting_and_confirmation'], 
                  agent=self.chat_consultant(),
                  inputs=self.inputs)

  # Data Auditor Tasks - Base analysis first
  @task
  def t_analyze_dataframe_info(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_dataframe_info'], 
                  agent=self.data_auditor(),
                  context=[self.t_initial_greeting_and_confirmation()])

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
                  agent=self.data_auditor(),
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
                  context=[self.t_analyze_dataframe_info()])
 
  @task
  def t_analyze_categorical_frequency(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_categorical_frequency'], 
                  agent=self.data_auditor(),
                  context=[self.t_analyze_dataframe_info()])

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
  
  # Data Cleaner Tasks
  @task
  def t_handle_missing_values(self) -> Task:
      return Task(config=self.tasks_config['t_handle_missing_values'],
                  agent=self.data_cleaner(),
                  context=[self.t_find_missing_values()])

  @task
  def t_remove_duplicates(self) -> Task:
        return Task(config=self.tasks_config['t_remove_duplicates'],
                    agent=self.data_cleaner(),
                    context=[self.t_detect_duplicates()])

  @task
  def t_standardize_date_formats(self) -> Task:
        return Task(config=self.tasks_config['t_standardize_date_formats'], 
                    agent=self.data_cleaner(),
                    context=[self.t_check_date_formats()])
  
  @task
  def t_normalize_numeric_formats(self) -> Task:
      return Task(config=self.tasks_config['t_normalize_numeric_formats'], 
                  agent=self.data_cleaner(),
                  context=[self.t_analyze_numeric_scale_and_format()])
  
  @task
  def t_fix_encoding_and_characters(self) -> Task:
      return Task(config=self.tasks_config['t_fix_encoding_and_characters'], 
                  agent=self.data_cleaner(),
                  context=[self.t_detect_encoding_and_special_chars()])
  
  @task
  def t_propose_and_apply_category_standardization(self) -> Task:
      return Task(config=self.tasks_config['t_propose_and_apply_category_standardization'], 
                  agent=self.data_cleaner(),
                  context=[self.t_analyze_categorical_frequency()])
  
  @task
  def t_standardize_column_names(self) -> Task:
      return Task(config=self.tasks_config['t_standardize_column_names'], 
                  agent=self.data_cleaner(),
                  context=[self.t_propose_and_apply_category_standardization()])
  
  # Data Modeller Tasks
  @task
  def t_analyze_dataset_for_modeling(self) -> Task:
      return Task(config=self.tasks_config['t_analyze_dataset_for_modeling'], 
                  agent=self.data_modeller(),
                  context=[self.t_standardize_column_names()])
  
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
  
  # Chat Consultant final task
  @task
  def t_present_final_report(self) -> Task:
    return Task(config=self.tasks_config['t_present_final_report'], 
                agent=self.chat_consultant(), 
                context=[ 
        self.t_find_missing_values(),
        self.t_handle_missing_values(),
        self.t_detect_duplicates(),
        self.t_remove_duplicates(),
        self.t_check_data_types_and_inconsistencies(),
        self.t_analyze_numeric_scale_and_format(),
        self.t_normalize_numeric_formats(),
        self.t_check_date_formats(),
        self.t_standardize_date_formats(),
        self.t_detect_encoding_and_special_chars(),
        self.t_fix_encoding_and_characters(),
        self.t_identify_outliers_numbers(),
        self.t_identify_date_outliers(),
        self.t_analyze_categorical_frequency(),
        self.t_propose_and_apply_category_standardization(),
        self.t_standardize_column_names(),
        self.t_analyze_dataset_for_modeling(),
        self.t_propose_table_name(),
        self.t_apply_table_rename(),
        self.t_identify_primary_keys(),
        self.t_propose_bi_structure()
    ])

  @crew
  def crew(self) -> Crew:
    return Crew(
      agents=[
                self.chat_consultant(),
                self.data_auditor(),
                self.data_cleaner(),
                self.data_modeller()
            ],
      tasks=[
        self.t_initial_greeting_and_confirmation(),
        self.t_analyze_dataframe_info(),
        self.t_find_missing_values(),
        self.t_handle_missing_values(),
        self.t_detect_duplicates(),
        self.t_remove_duplicates(),
        self.t_check_data_types_and_inconsistencies(),
        self.t_analyze_numeric_scale_and_format(),
        self.t_normalize_numeric_formats(),
        self.t_check_date_formats(),
        self.t_standardize_date_formats(),
        self.t_detect_encoding_and_special_chars(),
        self.t_fix_encoding_and_characters(),
        self.t_identify_outliers_numbers(),
        self.t_identify_date_outliers(),
        self.t_analyze_categorical_frequency(),
        self.t_propose_and_apply_category_standardization(),
        self.t_standardize_column_names(),
        self.t_analyze_dataset_for_modeling(),
        self.t_propose_table_name(),
        self.t_apply_table_rename(),
        self.t_identify_primary_keys(),
        self.t_propose_bi_structure(),
        self.t_present_final_report()
      ],
      process=Process.sequential,
      verbose=True,
    )
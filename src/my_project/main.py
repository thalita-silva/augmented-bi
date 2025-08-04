# main.py

#!/usr/bin/env python
import sys
import warnings
import os
from crew import AugmentedBI
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run_contest_agent(question: str):
    # question = input("Enter your question: ")
    inputs = {
        'question': question
    }
    res = AugmentedBI(inputs).crew().kickoff(inputs=inputs) #class name from crew file
    return res
# run()
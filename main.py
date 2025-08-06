# main.py

#!/usr/bin/env python
import sys
import warnings
import os
from crew import AugmentedBI
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run_agents(question: str):
    # question = input("Enter your question: ")
    inputs = {
        'question': question
    }
    res = AugmentedBI(inputs).crew().kickoff(inputs=inputs) #class name from crew file
    return res
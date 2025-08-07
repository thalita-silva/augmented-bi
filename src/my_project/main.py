# main.py

#!/usr/bin/env python
import sys
import warnings
import os
from crew import AugmentedBI
from dotenv import load_dotenv
import pandas as pd  # Certifique-se de importar o pandas

load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run_agents(df: pd.DataFrame, question: str = "What can you tell me about this dataset?") -> dict:
    """
    Recebe um DataFrame e uma pergunta, converte o DataFrame para lista de dicionários
    e inicia o processo dos agentes.
    """
    data_records = df.to_dict(orient="records")  # Deserializa o DataFrame

    inputs = {
        'question': question,
        'data': data_records  # chave "data" com os dados deserializados
    }
    # print(data_records)
    
    res = AugmentedBI(inputs).crew().kickoff(inputs=inputs)
    return res

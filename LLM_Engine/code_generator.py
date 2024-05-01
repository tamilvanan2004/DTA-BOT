# file.py
from langchain import hub
from langchain.agents import AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain.agents import create_openai_functions_agent
from .llm import TUNED_LLM
import os
import pandas as pd

def generate_code(results, chat):
    print("Type of results:", type(results))
    print("Results:", results)
    try:
        df = pd.DataFrame(results)
    except Exception as e:
        print("Error occurred while creating DataFrame:", e)
        raise
    instructions = """You are an agent designed to write and execute python code to answer questions .
    You have access to a python REPL, which you can use to execute python code.
    If you get an error, debug your code and try again.
    Only use the output of your code to answer the question. 
    You might know the answer without running any code, but you should still run the code to get the answer.
    If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
    """
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    os.environ['GOOGLE_API_KEY'] = 'AIzaSyD4azN9sFJ_JzQXIwxTGFFhu5aKSYI4Mug'
    prompt = base_prompt.partial(instructions=instructions)
    tools = [PythonREPLTool()]
    agent = create_openai_functions_agent(TUNED_LLM(temperature=0, model='gemini-pro', convert_system_message_to_human=True), tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    x = agent_executor.invoke({"input": f'''
                           Write a python code to Visualize the DataFrame according to the Question and Dataframe was stored in variable 'df' use plotly.express as px for visualization.
                           QUESTION:
                           "{chat} Visualize the data without performing any operations to make changes; simply create a visualization based on the dataframe and give the title for the visualization. Give the name of the title inside the plot function"
                            Refer the column names {df.columns.to_list()} and use the accurate column name.
                            Note: Don't give any explanation just give the and don't create and use variables except 'df' and  'fig'
                           '''})
    return x['output']

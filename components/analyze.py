# analyze.py
import re
import pandas as pd
import streamlit as st
from components import home
import google.generativeai as genai
from LLM_Engine.code_generator import generate_code 
import plotly.express as px
genai.configure(
    api_key='AIzaSyD4azN9sFJ_JzQXIwxTGFFhu5aKSYI4Mug'
)

def analyze():
    st.title("📈 Analyze Page")

    host, user, password, database = home.db_data()
    connection = home.connect_to_database(host, user, password, database)
    if connection:
        table_names = home.get_table_names(connection)

        selected_table = st.sidebar.selectbox("Select Table", table_names)
        st.subheader(f" {selected_table}")

        # Display data for the selected table
        table_data = home.get_table_data(connection, selected_table)
        col_data = table_data.columns.tolist()
        head = table_data.head()

        st.dataframe(table_data)
        model = genai.GenerativeModel(model_name='gemini-pro')
        chat = st.sidebar.text_area('Make your prompt here', placeholder='Hello 👋 this DTA-BOT please make your queries here')

        if 'plot' in chat.lower():
            prompt = f"""
            Write a MYSQL query for this question: '{chat}'.
            Note: Refer to the table names: {selected_table}, columns: {col_data}, and head of the dataset: {head}. 
            Make sure to provide an accurate query.
            """
            if st.sidebar.button('GENERATE'):
                while True:
                    try:
                        response = model.generate_content(prompt)
                        sql_query = response.text
                        match = re.search(r'SELECT.*?;', sql_query, re.DOTALL)
                        if match:
                            trimmed_query = match.group(0)
                            if connection.is_connected():
                                cursor = connection.cursor()
                                compressed_query = re.sub(r'\s+', ' ', trimmed_query.strip())
                                results = pd.read_sql_query(compressed_query, connection)
                                df = results
                                st.warning(f'USER : {chat}')
                                res = generate_code(results, chat)
                                result = res
                                trimmed_code = result[len("```python"):-len("```")]
                                print(trimmed_code)
                                code = trimmed_code
                                target_line = "fig ="
                                filtered_code = '\n'.join(line for line in code.split('\n') if target_line in line)
                                modified_line = filtered_code.replace("fig = ", "")
                                code_string = modified_line.replace("'", '"')
                                fig=eval(code_string)
                                st.plotly_chart(fig, use_container_width=True)
                                break  # exit the loop after successful generation and plotting
                    except Exception as e:
                        print(f"Error occurred: {e}")
                        st.warning("An error occurred. Retrying...")


                    else:
                        if connection.is_connected():
                            cursor = connection.cursor()
                            compressed_query = re.sub(r'\s+', ' ', sql_query.strip())
                            cursor.execute(f"{compressed_query}")
                            results = cursor.fetchall()
                            print(f'USER : {chat}')
                            print(f'DTABOT :\n{results}')
                            st.warning(f'USER : {chat}')
                            st.write(f'{results}')
                            temp = f'''
                                Create a meaningful sentence for this MySQL output {results} in 1 to 2 lines. 
                                Note: Refer the question {chat} and the MySQL query {compressed_query}.
                            '''
                            Ans_expl = model.generate_content(temp)
                            st.success(Ans_expl.text)
        else:
            def generate_content_with_retry(prompt, model, connection, selected_table, col_data, head, chat):
                for _ in range(5):  # Try 5 times
                    try:
                        response = model.generate_content(prompt)
                        sql_query = response.text
                        match = re.search(r'SELECT.*?;', sql_query, re.DOTALL)
                        if match:
                            trimmed_query = match.group(0)
                            print(trimmed_query)
                            if connection.is_connected():
                                cursor = connection.cursor()
                                compressed_query = re.sub(r'\s+', ' ', trimmed_query.strip())
                                results = pd.read_sql_query(compressed_query, connection)
                                print(f'USER : {chat}')
                                print(f'DTABOT :\n{results}')
                                st.warning(f'USER : {chat}')
                                df = pd.DataFrame(results)
                                st.dataframe(df)
                                temp = f'''
                                Create a meaningful sentence for this MySQL output {df} in 1 to 2 lines.
                                Note: Refer the question {chat}  and the MySQL query {compressed_query}.
                                '''
                                Ans_expl = model.generate_content(temp)
                                print(f'USER : {chat}')
                                print(f'DTA-BOT :{Ans_expl.text}')
                                st.success(Ans_expl.text)
                                return  # Exit the function if successful
                        else:
                            if connection.is_connected():
                                cursor = connection.cursor()
                                compressed_query = re.sub(r'\s+', ' ', sql_query.strip())
                                results = pd.read_sql_query(compressed_query, connection)
                                print(f'USER : {chat}')
                                print(f'DTABOT :\n{results}')
                                st.warning(f'USER : {chat}')
                                st.write(f'{results}')
                                return  # Exit the function if successful
                    except Exception as e:
                        st.error("Some Error occurs Retrying!")


            prompt = f"""
            Write a MYSQL query this Question and Kindly make an accurate query
            '{chat}' 
            Note: Don't give any explanation just give the query, Refer this Table NAMES of this database {selected_table}, COLUMNS {col_data} in the {selected_table} Head of the DATASET {head} and Please make the accurate query for the {chat}.
            """

            if st.sidebar.button('GENERATE'):
                generate_content_with_retry(prompt, model, connection, selected_table, col_data, head, chat)
                
            
                        

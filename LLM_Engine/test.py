# analyze.py
import ast
import plotly.graph_objects as go
import streamlit as st
from components import home
from components.visualization import *
import pandas as pd
import google.generativeai as genai
import re
import pandas as pd
import plotly.express as px
genai.configure(
    api_key='AIzaSyD4azN9sFJ_JzQXIwxTGFFhu5aKSYI4Mug')
model = genai.GenerativeModel(
    model_name='gemini-pro')
def analyze():
    st.sidebar.title("Analyze Page")

    host, user, password, database = home.db_data()
    connection = home.connect_to_database(host,user,password,database)
    if connection:
        table_names = home.get_table_names(connection)
        
        selected_table = st.sidebar.selectbox("Select Table", table_names)
        st.subheader(f" {selected_table}")
        
        # Display data for the selected table
        table_data = home.get_table_data(connection, selected_table)
        col_data=table_data.columns.tolist()
        head=table_data.head()
        col1=st.columns(2)
        
        with col1:
            st.dataframe(table_data)
            model = genai.GenerativeModel(
                model_name='gemini-pro')
            chat=st.sidebar.text_area('Make your prompt here',placeholder='Hello 👋 this DTA-BOT please make your queries here')
            if 'plot' in chat or 'Plot' in chat or 'PLOT' in chat:
                prompt = f"""
                Write a MYSQL query this Question 
                '{chat}' and Kindly make an accurte query
                
                Note:Don't give any explaination just give the query, Refer this Table NAMES of this database {selected_table} , COLUMNS {col_data}in the {selected_table} Head of the DATASET {head} and Please make the accurate query for the {chat}.
                """
                if st.sidebar.button('GENERATE'):
                    response = model.generate_content(prompt)
                    data=st.write(response.text)
                    sql_query=response.text
                    match= re.search(r'SELECT.*?;', sql_query, re.DOTALL)
                    if match:
                        trimmed_query = match.group(0)
                        print(trimmed_query)
                        if connection.is_connected():
                            cursor=connection.cursor()
                            compressed_query = re.sub(r'\s+', ' ', trimmed_query.strip())
                            
                            results = pd.read_sql_query(compressed_query,connection)
                            print(f'USER : {chat}')
                            print(f'DTABOT :\n{results}')
                            st.warning(f'USER : {chat}')
                            
                            df=pd.DataFrame(results)
                            
                            print(df)
                            
                            print(chat)
                            print(col_data)
                            m_df_columns=model.generate_content(f''' 
                                                                Give the accurate {len(df.columns.tolist())} column name for this Dataframe
                                                                {df}
                                                                By refering the original column names {col_data} and refer mysql query '{compressed_query}'
                                                                Note: Don't make extra contents just make  the column name in the square bracket and please use 1 line don't use multiple lines''')
                            
                            print(m_df_columns.text)
                            m_df_columns= ast.literal_eval(m_df_columns.text)
                            df.columns= m_df_columns
                            st.dataframe(df)
                            print(df)
                            res=model.generate_content(f'''
                           Write a python code to Visualize the DataFrame according to the Question and Dataframe was stored in variable 'df' use plotly.express as px for visualization.
                           QUESTION:
                           "{chat} Visualize the data without performing any operations to make changes; simply create a visualization based on the dataframe and give accurate title."
                            Refer the column names {df.columns.to_list()} and use the accurate column name.
                            Note: Don't give any explaination just give the and don't create and use variables except 'df' and  'fig'
                           ''')
                            
                            result=res.text
                            trimmed_code = result[len("```python"):-len("```")]
                            print(trimmed_code)
                            code= trimmed_code
                            target_line = "fig ="
                            filtered_code = '\n'.join(line for line in code.split('\n') if target_line in line)
                            modified_line = filtered_code.replace("fig = ","")
                            code_string = modified_line.replace("'", '"')
                             
                            fig = eval(code_string)
                            
                            st.plotly_chart(fig,use_container_width=True)
                            
                        else:
                            if connection.is_connected():
                                cursor=connection.cursor()
                                compressed_query = re.sub(r'\s+', ' ', sql_query.strip())
                                cursor.execute(f"{compressed_query}")
                                results = cursor.fetchall()
                                print(f'USER : {chat}')
                                print(f'DTABOT :\n{results}')
                                st.warning(f'USER : {chat}')
                                st.write(f'{results}')
                                temp=f'''
                                Create a meaning full sentence for this mysql output {results} in 1 to 2 lines. 
                                Note: Refer the question {chat} and the mysql query {compressed_query}.
                                '''
                                Ans_expl=model.generate_content(temp)
                                st.success(Ans_expl.text)
            else:
                prompt = f"""
                Write a MYSQL query this Question and Kindly make an accurte query
                '{chat}' 
                Note:Don't give any explaination just give the query, Refer this Table NAMES of this database {selected_table} , COLUMNS {col_data}in the {selected_table} Head of the DATASET {head} and Please make the accurate query for the {chat}.
                """
                if st.sidebar.button('GENERATE'):
                    response = model.generate_content(prompt)
                    
                    sql_query=response.text
                    match= re.search(r'SELECT.*?;', sql_query, re.DOTALL)
                    if match:
                        trimmed_query = match.group(0)
                        print(trimmed_query)
                        if connection.is_connected():
                            cursor=connection.cursor()
                            compressed_query = re.sub(r'\s+', ' ', trimmed_query.strip())
                            
                            results = pd.read_sql_query(compressed_query,connection)
                            print(f'USER : {chat}')
                            print(f'DTABOT :\n{results}')
                            st.warning(f'USER : {chat}')
                            
                            df=pd.DataFrame(results)
                            st.dataframe(df)
                            temp=f'''
                            Create a meaning full sentence for this mysql output {df} in 1 to 2 lines.
                            Note: Refer the question {chat}  and the mysql query {compressed_query}.
                            '''
                            Ans_expl=model.generate_content(temp)
                            print(f'USER : {chat}')
                            print(f'DTA-BOT :{Ans_expl.text}')
                            st.success(Ans_expl.text)
                        else:
                            if connection.is_connected():
                                cursor=connection.cursor()
                                compressed_query = re.sub(r'\s+', ' ', sql_query.strip())
                                
                                results = results = pd.read_sql_query(compressed_query,connection)
                                print(f'USER : {chat}')
                                print(f'DTABOT :\n{results}')
                                st.warning(f'USER : {chat}')
                                st.write(f'{results}')
                                temp=f'''
                                Create a meaning full sentence for this mysql output {results} in 1 to 2 lines. 
                                Note: Refer the question {chat} and the mysql query {compressed_query}.
                                '''
                                Ans_expl=model.generate_content(temp)
                                st.success(Ans_expl.text)
            
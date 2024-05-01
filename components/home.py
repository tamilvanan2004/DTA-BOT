# home.py

import streamlit as st
import pandas as pd
import mysql.connector
import pandas as pd

import streamlit as st





def connect_to_database(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        return connection
    except mysql.connector.Error as err:
        st.warning(f"Please connect with your Database")
        return None

def get_table_names(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    return [table[0] for table in tables]

def get_table_data(connection, table_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, connection)
    
    return df



def db_data():
    with st.sidebar.expander("Database Configuration"):
        user = st.text_input("Enter the Username")
        password = st.text_input("Enter the Password", type="password")
        database = st.text_input("Enter the Database")
        host = st.text_input("Enter the Host")
        
        
        
    
    return host,user,password,database

def db_data_dic():
    host = 'localhost'
    user = 'root'
    password = ''
    database = 'shopsy'
    
    return {'host': host, 'user': user, 'password': password, 'database': database}

def home(host,user,password,database):
    
 
    connection = connect_to_database(host, user, password, database)
    if connection:
        with st.spinner('connecting'):
            st.success("Connected to the database!")
            st.header(f"Table from '{database}' DataBase")
            table_names = get_table_names(connection)
            selected_table = st.sidebar.selectbox("Select Table", table_names)
            st.header(f" '{selected_table}' Dataset")
            table_data = get_table_data(connection, selected_table)
            df=st.dataframe(table_data)
        
             
            
            
def main():
    host, user, password, database = db_data()
    home(host, user, password, database)
  

    
if __name__ == "__main__":
    main()
                   
                    
                    
                    

                    
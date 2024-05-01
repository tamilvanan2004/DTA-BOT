
import streamlit as st
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from components.home import db_data

def create_connection(host, password, user, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conn
    except Exception as e:
        st.write(e)
        return None

def close_connection(conn):
    if conn:
        conn.close()

def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

def upload_data():
    st.markdown("# Upload Data")
    host, user, password, database = db_data()
    table_name = st.text_input('Table Name to Insert')

    conn = create_connection(host, password, user, database)
    
    if conn is not None:
        uploaded_file = st.file_uploader('Choose a file')

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)

                # Check if the table already exists in the database
                if not table_exists(conn, table_name):
                    # If the table doesn't exist, create it
                    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
                    df.to_sql(name=table_name, con=engine, index=False, if_exists='replace')
                    st.write('Table created successfully.')
                    st.dataframe(df)
                else:
                    # If the table already exists, append data to it
                    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
                    df.to_sql(name=table_name, con=engine, index=False, if_exists='append')
                    st.write('Data appended to the existing table.')
                    st.write('These are the first 5 rows:')
                    st.dataframe(df)

            except Exception as e:
                st.write(e)

        # Close the connection after use
        close_connection(conn)

if __name__ =='__main__':
    upload_data()

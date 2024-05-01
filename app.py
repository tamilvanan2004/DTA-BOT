import streamlit as st
import mysql.connector
import pandas as pd
from components import home,analyze,info
from streamlit_option_menu import option_menu



def main():
    st.sidebar.title("DTA-BOT")
    
   
    

    with st.sidebar:
    
        
        selected = option_menu(None, ["Home", "Analysis"],
                               
                                default_index=0, orientation="horizontal")

    if selected == 'Home':
        home.main()
    elif selected == 'Analysis':
        analyze.analyze() 
    
        
        
    



    
if __name__ == "__main__":
    main()

import streamlit as st
from config_controller import list_test_name, tests_names
from server_automation.tests import *

st.title('Dashboard tests run')
option = st.selectbox(
    'Which test u want to run ?', tuple(list_test_name)
    )
st.text_input("Enter parameters if u need ", "CONF_FILE=")

st.write('Test to run:', option)

button = st.button("Run Test ")

if button:
    show_log = True
    try:
        exec(tests_names[option])
    except Exception as e:
        show_log = False
        st.warning("Exception", icon="⚠️")
        st.code(str(e), language="python")
    if show_log:
        st.success('This is a success message!', icon="✅")
        st.code("OK", language="python")


st.write('You selected:', option)


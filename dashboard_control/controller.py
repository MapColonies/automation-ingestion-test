from dashboard_control.config_controller import list_test_name, func_to_execute
import streamlit as st


st.title('Welcom to test app')
option = st.selectbox(
    'Which test u want to run ?', tuple(list_test_name)
    )
st.text_input("Enter parameters if u need ", "CONF_FILE=")

button = st.button("my button")
if button:
    st.success('This is a success message!', icon="✅")
    st.warning(option, icon="⚠️")
    func_to_execute(option)

st.write('You selected:', option)


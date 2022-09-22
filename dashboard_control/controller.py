import glob
import os
from multiprocessing import Process
import streamlit as st
import importlib
import time

MAIN_PATH = 'server_automation'
CONF_FP = f"{MAIN_PATH}/configuration/configuration.json"
LOGS = "logs.log"

files = glob.glob(f'server_automation/tests/*py')
st.title('Dashboard tests run')
path = st.selectbox(
    'Which test u want to run ?', tuple(files)
)
options = 'Default', 'Custom'
config_file = st.radio('Config File:', options=options)

fp = CONF_FP if config_file == options[0] else st.text_input("Enter parameters if u need ")

st.write('Test to run:', path)

if os.path.exists(LOGS):
    os.remove(LOGS)

if st.button("Run Test "):
    process = Process(target=os.system, args=(f"CONF_FILE={fp} py.test {path} >{LOGS}",))
    process.start()
    with st.expander('Logs', expanded=True):
        placeholder = st.empty()
        counter = 0
        with st.empty():
            while process.is_alive():
                time.sleep(1.5)
                if os.path.exists(LOGS):
                    with open(LOGS, 'r') as l:
                        st.code(l.read(), language="python")
              #  if st.button("Stop test", key=counter):
               #     process.kill()
                # Clear all those elements:
             #   counter += 1
        placeholder.empty()

    # st.write(os.system(f"CONF_FILE={fp} py.test {path} >{LOGS}"))

# if button:
#     show_log = True
#     try:
#         imp = "server_automation.tests.test_"+str(option)
#         print(imp)
#         importlib.import_module(imp)
#         st.write(option)
#         st.write(tests_names[option])
#         exec(tests_names[option])
#     except Exception as e:
#         show_log = False
#         st.warning("Exception", icon="⚠️")
#         st.code(str(e), language="python")
#     if show_log:
#         st.success('This is a success message!', icon="✅")
#         st.code("OK", language="python")

# st.write('You selected:', option)

import openai
import streamlit as st
import time
import os
import zipfile
import yaml
 
from utils import create_assistant_from_config_file, upload_to_openai, export_assistant
from exportChat import export_chat

st.set_page_config(
    page_title="MVP",
    page_icon="🤖",
    layout="wide",
    #menu_items={
        #'Get Help': 'mailto:servizi@intelligenzaartificialeitalia.net',
        #'Report a bug': "https://github.com/IntelligenzaArtificiale/Build-Share-Sell-OpenAI-Assistants-API/issues",
        #'About': "# This is a simple web app to build, share and sell OpenAI Assistants API\n\n"
    #}
)

st.title("MVP🤖")

if os.environ["OPENAI_API_KEY"]:
    client = openai.OpenAI()
    id_assistente = "asst_6DrmaKhqvVgDRsfhttLTM0sZ"

if id_assistente:
    try: 
        inference(id_assistente)
    except Exception as e:
        st.error("🛑 There was a problem with OpenAI Servers")
        st.error(e)
        if st.button("🔄 Restart"):
            st.rerun()

#html_chat = '<center><h6>🤗 Support the project with a donation for the development of new features 🤗</h6>'
#html_chat += '<br><a href="https://rebrand.ly/SupportAUTOGPTfree"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal donate button" /></a><center><br>'
#st.markdown(html_chat, unsafe_allow_html=True)
#st.write('Made with ❤️ by [Alessandro CIciarelli](https://intelligenzaartificialeitalia.net)')

def inference(id_assistente):
    if "msg_bot" not in st.session_state:
        st.session_state.msg_bot = []
        st.session_state.msg_bot.append("Hi🤗, I'm your assistant. How can I help you?")
        st.session_state.msg = []
        
        try :
            #create a thread
            thread = openai.beta.threads.create()
            my_thread_id = thread.id
        
            st.session_state.thread_id = my_thread_id
        except:
            st.error("🛑 There was a problem with OpenAI Servers")
            time.sleep(5)
            st.rerun()
            
        

    def get_response(domanda):
        #create a message
        if "thread_id" in st.session_state:
            try:
                message = openai.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=domanda
                )
            
                #run
                run = openai.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=id_assistente,
                )
            
                return run.id
            except:
                st.error("🛑 There was a problem with OpenAI Servers")

        time.sleep(5)
        st.rerun()

    def check_status(run_id):
        try: 
            run = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run_id,
            )
            return run.status
        except:
            st.error("🛑 There was a problem with OpenAI Servers")
            time.sleep(5)
            st.rerun()


    input = st.chat_input(placeholder="🖊 Write a message...")

    if input:
        st.session_state.msg.append(input)
        with st.spinner("🤖 Thinking..."):
            run_id = get_response(input)
            status = check_status(run_id)
            
            while status != "completed":
                status = check_status(run_id)
                time.sleep(3)
            
            response = openai.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            if response.data:
                print(response.data[0].content[0].text.value)
                st.session_state.msg_bot.append(response.data[0].content[0].text.value) 
            else:
                st.session_state.msg_bot.append("😫 Sorry, I didn't understand. Can you rephrase?")

    if "msg_bot" in st.session_state:
        bot_messages_count = len(st.session_state.msg_bot)
        for i in range(len(st.session_state.msg_bot)):
            with st.chat_message("ai"):
                st.write(st.session_state.msg_bot[i])
                
                
            if "msg" in st.session_state:
                if i < len(st.session_state.msg):
                    if st.session_state.msg[i]:
                        with st.chat_message("user"):
                            st.write(st.session_state.msg[i])

    if "msg_bot" in st.session_state:
        if len(st.session_state.msg) > 0 :
            export_chat()

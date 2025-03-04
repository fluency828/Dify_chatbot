import requests
import streamlit as st 
import json
import time

dify_api_key = "your api key"

url = "your url"

st.title("Dify Streamlit App")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Enter you question")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        headers = {
            'Authorization': f'Bearer {dify_api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "inputs": {},
            "query": prompt,
            "response_mode": "streaming",
            "conversation_id": st.session_state.conversation_id,
            "user": "abc-123",
            "files": []
        }

        try:
            message_placeholder = st.empty()
            full_response = ""
            i = 0

            
            with requests.post(url, headers=headers, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    i+=1
                    if i==1:
                        full_response += "<summary> Thinking... </summary>"
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.01)
                        continue
                    
                    if line:
                        line_text = line.decode('utf-8')
                        # print(line_text)
                        try:
                            if line_text.startswith('data: '):
                                json_str = line_text[6:]  # 移除'data: '前缀
                                
                                json_response = json.loads(json_str)
                                event_type = json_response.get('event')
                                
                                # 处理message事件
                                if event_type == 'message':
                                    answer = json_response.get('answer', '')

                                    buffer = ""  # 重置buffer以显示新内容
                                    
                                    if answer:
                                        full_response += answer
                                        message_placeholder.markdown(full_response + "▌")
                                        # print(new_text)
                                        time.sleep(0.01)
                                
                                # 保存会话ID
                                if 'conversation_id' in json_response:
                                    st.session_state.conversation_id = json_response['conversation_id']
                                
                        except json.JSONDecodeError:
                            st.warning("收到无效的JSON数据，已跳过")
                            continue

            # 显示最终结果（不带光标）
            if full_response:  # 只有在有实际回答时才更新
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })

        except requests.exceptions.RequestException as e:
            st.error(f"发生错误: {str(e)}")
            full_response = "获取响应时发生错误。"

import streamlit as st
import json
import _snowflake
from snowflake.snowpark.context import get_active_session
import os

session = get_active_session()

API_ENDPOINT = "/api/v2/cortex/agent:run"
API_TIMEOUT = 50000  # in milliseconds


# Define multiple YAML files
semantic_model_file = [
    "@CORTEX_AGENT_DB.CORTEX_AGENT_SCHEMA.agent_data/farm_ca.yaml",
    "@CORTEX_AGENT_DB.CORTEX_AGENT_SCHEMA.agent_data/business_ca.yaml"
]


# Custom CSS styling
st.markdown("""
<style>
/* Unified Color Palette */
:root {
    --background-color: #FFFFFF;
    --text-color: #222222;
    --title-color: #1A1A1A;
    --button-color: #1a56db;
    --button-text: #FFFFFF;
    --border-color: #CBD5E0;
    --accent-color: #2C5282;
}

/* General App Styling */
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

/* Title Styling */
h1, .stTitle {
    color: var(--title-color) !important;
    font-size: 36px !important;
    font-weight: 600 !important;
    padding: 1.5rem 0;
}

/* Input Fields */
textarea {
    background-color: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 4px !important;
    padding: 16px !important;
    font-size: 16px !important;
    color: var(--text-color) !important;
}

textarea:focus {
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 1px var(--accent-color) !important;
}

textarea::placeholder {
    color: #666666 !important;
}

/* Success & Error Messages */
.stException {
    background-color: #FEE2E2 !important;
    border: 1px solid #EF4444 !important;
    padding: 16px !important;
    border-radius: 4px !important;
    margin: 16px 0 !important;
    color: #991B1B !important;
}

div[data-testid="stAlert"], div[data-testid="stException"] {
    background-color: #f8d7da !important;
    color: #721c24 !important;
    border: 1px solid #f5c6cb !important;
    padding: 12px !important;
    border-radius: 6px !important;
    font-weight: bold !important;
}

div[data-testid="stAlertContentError"] {
    color: #721c24 !important;
}

.stFormSubmitButton {
    background-color: white !important;
    padding: 10px;
    border-radius: 8px;
}

button[data-testid="stBaseButton-secondaryFormSubmit"] {
    background-color: #007bff !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 5px !important;
    padding: 8px 16px !important;
    border: none !important;
}

/* Sidebar Buttons */
.stSidebar button {
    background-color: #1a56db !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
}

/* Tooltips */
.tooltip {
    visibility: hidden;
    opacity: 0;
    background-color: white;
    color: var(--text-color);
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
    line-height: 1.5;
    width: max-content;
    max-width: 300px;
    position: absolute;
    z-index: 1000;
    bottom: calc(100% + 5px);
    left: 50%;
    transform: translateX(-50%);
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.citation:hover + .tooltip {
    visibility: visible;
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* Hide Streamlit Branding */
#MainMenu, header, footer {
    visibility: hidden;
}

[data-testid="stDownloadButton"] button {
    background-color: #2196F3 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    border-radius: 0.375rem !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)



def run_snowflake_query(query):
    try:
        df = session.sql(query.replace(';',''))
        return df

    except Exception as e:
        st.error(f"Error executing SQL: {str(e)}")
        return None, None

def snowflake_api_call(query: str, limit: int = 10):
    results = []
    
    for model_file in semantic_model_file:  # Iterate over each YAML file
        payload = {
            "model": "llama3.1-70b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ],
            "tools": [
                {
                    "tool_spec": {
                        "type": "cortex_analyst_text_to_sql",
                        "name": "analyst1"
                    }
                }
            ],
            "tool_resources": {
                "analyst1": {"semantic_model_file": model_file}  # Send one file at a time
            }
        }

        try:
            resp = _snowflake.send_snow_api_request(
                "POST",
                API_ENDPOINT,
                {},
                {},
                payload,
                None,
                API_TIMEOUT,
            )
            
            try:
                response_content = json.loads(resp["content"])
                results.append(response_content)  # Collect all responses
            except json.JSONDecodeError:
                st.error("❌ Failed to parse API response. The server may have returned an invalid JSON format.")
                if resp["status"] != 200:
                    st.error(f"Error:{resp}")
                return None

        except Exception as e:
            st.error(f"Error making request: {str(e)}")
            return None

    return results  # Return all collected responses



def process_sse_response(responses):
    """Process SSE response from multiple YAML files"""
    text = ""
    sql = ""

    if not responses:  # If the response list is empty, return
        return text, sql

    try:
        # Loop through multiple responses (since we query each YAML file separately)
        for response in responses:
            st.write("Raw response:", response)  # Debugging output

            # Check if response is a string and try parsing it as JSON
            if isinstance(response, str):
                response = json.loads(response)

            # Iterate through response events
            for event in response:
                if isinstance(event, dict) and 'event' in event and event['event'] == "message.delta":
                    data = event.get('data', {})
                    delta = data.get('delta', {})

                    for content_item in delta.get('content', []):
                        content_type = content_item.get('type')

                        if content_type == "tool_results":
                            tool_results = content_item.get('tool_results', {})
                            if 'content' in tool_results:
                                for result in tool_results['content']:
                                    if result.get('type') == 'json':
                                        json_result = result.get('json', {})

                                        # Extract SQL query if present
                                        if 'sql' in json_result and json_result['sql']:
                                            sql += "\n" + json_result['sql']

                                        # Extract text response
                                        if 'text' in json_result and json_result['text']:
                                            text += "\n" + json_result['text']

    except json.JSONDecodeError as e:
        st.error(f"Error processing events: {str(e)}")
    except Exception as e:
        st.error(f"Error processing events: {str(e)}")

    return text.strip(), sql.strip()




def main():
    st.title("Intelligent Agent Assistant")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'].replace("•", "\n\n-"))

    if query := st.chat_input("Would you like to learn?"):
        # Add user message to chat
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})

        # Get response from API
        with st.spinner("Processing your request..."):
            response = snowflake_api_call(query, 1)
            text, sql = process_sse_response(response)

            # Add assistant response to chat
            if text:
                st.session_state.messages.append({"role": "assistant", "content": text})
                with st.chat_message("assistant"):
                    st.markdown(text.replace("•", "\n\n-"))

            # Display SQL if present
            if sql:
                st.markdown("### Generated SQL")
                st.code(sql, language="sql")
                sales_results = run_snowflake_query(sql)
                if sales_results:
                    st.write("### Property Report")
                    st.dataframe(sales_results)

if __name__ == "__main__":
    main()

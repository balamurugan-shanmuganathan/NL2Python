import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import os
import pandas as pd
from PIL import Image
from user_codes.user_defined_functions import run_code_with_retries, execute_code, delete_image_if_exists, check_image_if_exists

# Load LLM
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)


# Convert user query into Python code
def query_to_code(query, df_columns):
    try:
        template = """
        You are an assistant that converts natural language queries into Python code along with its libraries
        and stored in variable name is called context_result using pandas.

        If user wants to create chat/graph make sure use seaborn library with dark themes to create your snippets.
        The chart should be saved as image in the name of context_result.png format

        If you are facing a difficulties to generate code then say, please reframe your query. (only return clean Python no quotes or text)
        Dataframe variable name: df
        Dataframe columns: {df_columns}
        Query: {query}

        Return a JSON object with two keys:
        - 'query': the original query
        - 'code': Python code to filter the population as a string

        Example: 
            {{
            "query": "Can you please group by survived people",
            "code": "import pandas as pd \ncontext_result = df[df['Survived'] == 1]"
            }}

        Example 2:
            {{
                "query": "distribution plot for Sepal_Width",
                "code": "import seaborn as sns\nimport matplotlib.pyplot as plt\nsns.set_theme(style='darkgrid')\nax = sns.histplot(df['Sepal_Width'])\nplt.title("Box Plot of Sepal Width")\nax.set(xlabel='Sepal Width', ylabel='Value')\nplt.savefig('context_result.png')"
            }}

        don't include ``` and python anywhere in your response
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm.bind(stop=["PythonResult:"]) | JsonOutputParser()
        response = chain.invoke({"df_columns": df_columns, "query": query})

        if not response or "code" not in response:
            return {"error": f"Invalid response: {response}"}
        return response
    except Exception as e:
        return {"error": f"Error in query generation: {e}"}
    
def chatbot_ui(data):
    if prompt := st.chat_input("Enter your query to filter the population"):
        with st.chat_message("user"):
            st.markdown(f"**You asked:** {prompt}")

        with st.chat_message("assistant"):
            # Retry logic on query-to-code generation
            query_to_code_response = run_code_with_retries(
                lambda: query_to_code(prompt, data.columns)
            )
            if "error" in query_to_code_response:
                st.markdown(f"🚨 **Error:** {query_to_code_response['error']}")
            else:
                img_path = 'context_result.png'
                delete_image_if_exists(img_path)  # Delete existing image.
                code = query_to_code_response.get("code", "")
                if code:
                    st.markdown("***Generated Python Code:***")
                    st.code(code, language="python")  # Show the generated code
                    execution_result = execute_code(code, data) # Pass data and execute the code 
            
                    is_img = check_image_if_exists(img_path)
                    # Check if the result is a DataFrame/series or error
                    if isinstance(execution_result, (pd.DataFrame, pd.Series)):
                        st.markdown("***Execution Result:***")
                        execution_result = pd.DataFrame(execution_result)
                        st.dataframe(execution_result)  # Display dataframe
                    elif is_img:
                        img = Image.open(img_path)
                        st.markdown("***Execution Result:***")
                        st.image(img, caption="PIL Image Display", use_container_width =True)
                    else:
                        st.markdown(f"***Execution Result:*** {execution_result}")
                else:
                    st.markdown("⚠️ **Unable to generate code. Please refine your query.**")

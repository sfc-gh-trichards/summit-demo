import streamlit as st
import numpy as np
from snowflake.snowpark.context import get_active_session
import pandas as pd
st.set_page_config(layout="wide")

def is_local() -> bool:
    """
    Check if app is running locally

    Returns:
        bool: True if running locally, else (if in SiS) False.
    """
    return st.experimental_user.email in {"test@localhost.com", "test@example.com"}

st.title(f"Streamlit in Snowflake Key Metrics")
st.sidebar.image("./snowflake_logo.png")

if is_local():
    conn = st.connection('snowflake')
    session = conn.session()
else:
    session = get_active_session()


df = pd.DataFrame({
    'date': pd.date_range(start='1/1/2020', periods=100),
    'customers': np.random.randint(100, 1000, 100)
    })

#make the customers cumulative
df['customers'] = df['customers'].cumsum()
col1, col2 = st.columns(2)
with col1:
    st.subheader("Number of customers")
    taba, tabb = st.tabs(["Chart", "Data"])
    taba.line_chart(df.set_index('date'))
    tabb.write(df)

df['views'] = np.random.randint(100, 1000, 100)
df['views'] = df['views'] * np.log(df.index) * np.random.uniform(1, 1.6, 100)
df['views'][0] = 0

with col2:
    st.subheader("views spent per day")
    tabc, tabd = st.tabs(["Chart", "Data"])
    tabc.line_chart(df.set_index('date')['views'])
    tabd.write(df)

#beyond this point will be live coded

#views per company
df['views_per_company'] = df['views'] / df['customers']

st.subheader("views per customer")
st.line_chart(df.set_index('date')['views_per_company'])


from snowflake.cortex import Complete
prompt = """
Please summarize the following feedback comments
    in markdown from our streamlit in snowflake users, just give the top 3 good things and 3 improvement areas about the product: '
"""
df_feedback = session.sql('select * from streamlit.public.feedback_table').to_pandas()
#add feedback to prompt
prompt += "\n\n".join(df_feedback['FEEDBACK'])
st.subheader("User Feedback")
response = Complete(
    model='mistral-large',
    prompt=prompt,
    session=session
)
st.write(response)
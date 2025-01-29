import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from preprocessing import extract_args
from prediction import predict_on_csv

st.set_page_config(
    page_title="AI Predictions",  # Title of the page
    page_icon="🤖",  # AI-related emoji (you can change this to any emoji or use a custom image)
    layout="centered"  # Set the layout to wide
)

# Streamlit UI
st.title("Secure Brain: SusNet")
st.image("front/images/dataset-cover.jpg", use_column_width=True)
# Dataset Information
st.header("About the BETH Dataset")
st.write(
    "This dataset corresponds to the paper 'BETH Dataset: Real Cybersecurity Data for Anomaly Detection Research' "
    "by Kate Highnam, Kai Arulkumaran, Zachary Hanif, and Nicholas R. Jennings. Published in ICML 2021 and CAMLIS 2021."
)

st.subheader("Context")
st.write(
    "When deploying machine learning models in real-world cybersecurity, detecting anomalies and shifts in data distribution "
    "is crucial. The BETH dataset is designed for benchmarking uncertainty and robustness in ML models, containing modern "
    "host activity and attack data."
)

st.subheader("About Our Model")
st.markdown("""
Our model is designed to classify data into two categories: **safe** and **suspicious**. The model has achieved high performance on both the validation and test sets, demonstrating its ability to generalize well to unseen data.
""")

# Creating a DataFrame to display the performance metrics in a table format
data = {
    "Metric": ["Accuracy", "Precision", "Recall", "F1-Score"],
    "safe":["98.85%","99%","100%","99%"],
    "suspicious":["98.85%","98%","94%","96%"]
}

# Convert the dictionary to a pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame in the Streamlit app
st.table(df)


with st.sidebar:
    st.header("Upload Test CSV File")
    test_file = st.file_uploader("Upload a CSV file for testing", type=["csv"])
    
    if test_file is not None:
        test_df = pd.read_csv(test_file)
        #st.write("Test Data Preview:")
        #st.dataframe(test_df.head())
        test_data =  extract_args.extract(test_df)

if test_file is None:
    st.info('You can load a test csv from the sidebar in order to make predictions', icon="ℹ️")


if test_file is not None:
    st.dataframe(test_data)
    model_path = 'models/xgboost_model.json'
    if st.button("Predict"):
            input_data = test_data.select_dtypes(include=['int', 'float'])
            preds = predict_on_csv.predict_from_dataframe(model_path=model_path, input_data=input_data , orig_data=test_df)
            
            def color_prediction(val):
                color = 'lightgreen' if val == 'safe' else 'red' if val == 'sus' else ''
                return f'background-color: {color}'
        
            styled_preds = preds.style.applymap(color_prediction, subset=['prediction'])
            
            st.dataframe(styled_preds)
            
            # Bar plot for 'safe' and 'sus' in the prediction column
            prediction_counts = preds['prediction'].value_counts()
            st.subheader("Sus vs Safe")
            # Display a bar chart for 'safe' and 'sus' in the prediction column
            st.bar_chart(prediction_counts,color=['#2934ff'])
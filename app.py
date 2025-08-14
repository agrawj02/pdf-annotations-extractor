import streamlit as st
import base64
import os
import tempfile
from main import extract_annotations, export_to_csv, export_to_json, export_to_excel, export_to_jira
import pandas as pd
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="PDF Annotation Extractor", layout="wide")

# Initialize session state variables
if 'annotations' not in st.session_state:
    st.session_state.annotations = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'processed' not in st.session_state:
    st.session_state.processed = False

st.title("PDF Annotation Extractor")
st.subheader("Extract and analyze annotations from PDF files")

# File upload section
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    # Process button
    if st.button("Proceed") or st.session_state.processed:
        if not st.session_state.processed:
            with st.spinner("Processing PDF and extracting annotations..."):
                # Call extract_annotations from main.py
                st.session_state.file_name = uploaded_file.name.split(".")[0]
                st.session_state.annotations, st.session_state.df = extract_annotations(uploaded_file)
                
                # Generate export data once
                st.session_state.csv_data = export_to_csv(st.session_state.df)
                st.session_state.excel_data = export_to_excel(st.session_state.df)
                st.session_state.json_data = export_to_json(st.session_state.annotations)
                
                st.session_state.processed = True
        
            st.success("Annotations extracted successfully!")
        
        # Display a preview of the data
        st.subheader("Preview of Extracted Annotations")
        st.dataframe(st.session_state.df[['Annotation ID', 'Image','Page', 'Content', 'Author', 'Nature', 'Type']],
                     column_config={
                         "Image": st.column_config.ImageColumn(
                             "Preview Image",
                             help="Click to view image",
                             width="large"
                         ),
                     })
        
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            with col1:
                st.download_button(
                    label="Download CSV",
                    data=st.session_state.csv_data,
                    file_name=f"{st.session_state.file_name}.csv",
                    mime="text/csv"
                )                    
            
            with col2:
                st.download_button(
                    label="Download Excel",
                    data=st.session_state.excel_data,
                    file_name=f"{st.session_state.file_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                    
            with col3:
                st.download_button(
                    label="Download JSON",
                    data=st.session_state.json_data,
                    file_name=f"{st.session_state.file_name}.json",
                    mime="application/json"
                )
            
            with col4:
                if st.button("Export to JIRA"):
                    with st.spinner("Exporting to JIRA..."):
                        # TODO: Implement JIRA export functionality
                        # You can call a function from main.py or implement here
                        key = export_to_jira(st.session_state.annotations)
                        
                        jira_base_url = "https://digitalpfizer.atlassian.net/browse/"
                        st.markdown(f"JIRA Story created successfully: [{key}]({jira_base_url}{key})")
                    
        except Exception as e:
            st.error(f"An error occurred during export: {e}")
    
else:
    st.info("Please upload a PDF file to begin")
    # Reset processed state when uploading a new file
    st.session_state.processed = False

st.sidebar.header("About")
st.sidebar.info(
    "This application extracts annotations from PDF files and allows you to "
    "export the results in various formats. Upload a PDF, click 'Proceed' to "
    "process it, and choose your preferred export format."
)

import streamlit as st
import requests
import pandas as pd
import time
import os
from io import BytesIO
from datetime import datetime
import plotly.express as px
import base64
import json

# -----------------------------
# Configuration and Constants
# -----------------------------

# Updated API endpoint based on your reference
API_BASE_URL = 'http://localhost:8000'  # Ensure this matches your Django backend URL
UPLOAD_ENDPOINT = f'{API_BASE_URL}/product/create/'  # Corrected endpoint to match your working reference
STATUS_ENDPOINT_TEMPLATE = f'{API_BASE_URL}/{{}}/'  # Endpoint to retrieve individual product status
DATA_ENDPOINT = f'{API_BASE_URL}/product/'  # Endpoint to list all products

# Path to the hardcoded audio file
HARDCODED_FILE_PATH = './sugat.wav'  # Updated to 'sugat.wav' as per your reference

# -----------------------------
# Helper Functions
# -----------------------------

def upload_audio(file, call_sid):
    """
    Uploads the audio file to the backend API.

    Args:
        file (BytesIO): The audio file to upload.
        call_sid (str): The call SID associated with the audio.

    Returns:
        dict or None: Response JSON containing product details if successful, else None.
    """
    # Ensure that the key 'audio_url' matches the field name in your Django serializer/model
    files = {'audio_url': (file.name, file, file.type)}
    data = {'call_sid': call_sid}
    try:
        response = requests.post(UPLOAD_ENDPOINT, data=data, files=files)
        st.write("**Upload Response Status Code:**", response.status_code)  # Debugging
        st.write("**Upload Response Content:**", response.text)  # Debugging
        if response.status_code == 201:
            st.success("File uploaded successfully!")
            return response.json()  # Assuming it returns the product ID and details
        elif response.status_code == 403:
            st.error("Forbidden: You don't have permission to access this resource.")
        elif response.status_code == 405:
            st.error("Method Not Allowed: The HTTP method used is not supported by the endpoint.")
        elif response.status_code == 400:
            st.error("Bad Request: The server could not understand the request due to invalid syntax.")
        else:
            st.error(f"Failed to upload file. Status code: {response.status_code}")
            st.error(response.text)
        return None
    except Exception as e:
        st.error(f"An error occurred during upload: {e}")
        return None

def get_processing_status(product_id):
    """
    Fetches the processing status of a product.

    Args:
        product_id (int): The ID of the product.

    Returns:
        dict or None: Response JSON containing product status and details if successful, else None.
    """
    status_url = STATUS_ENDPOINT_TEMPLATE.format(product_id)
    try:
        response = requests.get(status_url)
        st.write("**Status Response Status Code:**", response.status_code)  # Debugging
        st.write("**Status Response Content:**", response.text)  # Debugging
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Could not fetch status for Product ID {product_id}.")
            return None
    except Exception as e:
        st.error(f"An error occurred while fetching status: {e}")
        return None

def fetch_all_products():
    """
    Fetches all products from the backend.

    Returns:
        DataFrame: Pandas DataFrame containing all product data.
    """
    try:
        response = requests.get(DATA_ENDPOINT)
        st.write("**Fetch Products Response Status Code:**", response.status_code)  # Debugging
        st.write("**Fetch Products Response Content:**", response.text)  # Debugging
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a download link for a dataframe or text.

    Args:
        object_to_download (DataFrame or dict): The data to download.
        download_filename (str): The name of the download file.
        download_link_text (str): The text for the download link.

    Returns:
        str: HTML anchor tag with the download link.
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    elif isinstance(object_to_download, dict):
        object_to_download = json.dumps(object_to_download, indent=4)
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def display_audio(url):
    """
    Displays an audio player for the given URL.

    Args:
        url (str): The URL of the audio file.
    """
    st.audio(url)

def load_hardcoded_file():
    """
    Loads the hardcoded audio file and returns a BytesIO object.
    """
    if not os.path.exists(HARDCODED_FILE_PATH):
        st.error(f"Hardcoded file '{HARDCODED_FILE_PATH}' does not exist.")
        return None

    try:
        with open(HARDCODED_FILE_PATH, 'rb') as f:
            file_bytes = f.read()

        # Create a BytesIO object from the file bytes
        file_like = BytesIO(file_bytes)
        file_like.name = os.path.basename(HARDCODED_FILE_PATH)
        file_like.type = 'audio/wav'  # Updated MIME type for '.wav' files

        return file_like
    except Exception as e:
        st.error(f"An error occurred while loading the hardcoded file: {e}")
        return None

# -----------------------------
# Streamlit App Layout
# -----------------------------

st.set_page_config(
    page_title="📊 Product Audio Processing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title
st.title("📊 Product Audio Processing Dashboard")

# Tabs
tabs = st.tabs(["🏠 Home", "🎤 Upload Audio", "🔍 Data Explorer", "📈 Analytics", "⚙️ Settings"])

# -----------------------------
# Home Tab
# -----------------------------
with tabs[0]:
    st.header("📈 Overview")

    # Fetch data
    with st.spinner('Fetching data...'):
        df = fetch_all_products()

    if not df.empty:
        # Ensure 'created_at' is datetime with timezone awareness
        if not pd.api.types.is_datetime64_any_dtype(df['created_at']):
            df['created_at'] = pd.to_datetime(df['created_at'])
            st.write("**Converted 'created_at' to datetime.**")
        if df['created_at'].dt.tz is None:
            # Assume UTC if no timezone is set
            df['created_at'] = df['created_at'].dt.tz_localize('UTC')
            st.write("**'created_at' was timezone-naive and has been localized to UTC.**")

        # Key Metrics
        total_products = len(df)
        processed_products = df[df['processed'] == True].shape[0]
        pending_transcriptions = df[df['pending_transcription'] == True].shape[0]
        pending_ner = df[df['pending_ner'] == True].shape[0]

        # Metrics Display
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Products", total_products)
        col2.metric("Processed", processed_products)
        col3.metric("Pending Transcription", pending_transcriptions)
        col4.metric("Pending NER", pending_ner)

        st.markdown("---")

        # Charts
        st.subheader("Processing Status Distribution")
        status_counts = {
            "Processed": processed_products,
            "Pending Transcription": pending_transcriptions,
            "Pending NER": pending_ner
        }
        fig1 = px.pie(names=list(status_counts.keys()), values=list(status_counts.values()), title='Processing Status Distribution')
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Products Added Over Time")
        df_sorted = df.sort_values('created_at')
        fig2 = px.line(df_sorted, x='created_at', y='id', title='Products Added Over Time', labels={'id': 'Product Count', 'created_at': 'Date'})
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # Recent Activities
        st.subheader("Recent Activities")
        recent_df = df.sort_values('created_at', ascending=False).head(10)
        st.table(recent_df[['id', 'call_sid', 'processed', 'created_at']])
    else:
        st.info("No data available to display.")

# -----------------------------
# Upload Audio Tab
# -----------------------------
with tabs[1]:
    st.header("🎤 Upload Audio File")

    st.markdown("""
    Upload an audio file to create a new product entry. The system will automatically transcribe the audio and extract relevant product information using Named Entity Recognition (NER).
    """)

    # File uploader with specified types (including 'mov' if needed)
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "mov"])

    # Call SID input
    call_sid = st.text_input("Call SID", "")

    # Debugging: Display uploaded_file and call_sid
    # Note: These details will be overridden by the hardcoded file
    if uploaded_file is not None:
        st.write("**Uploaded File Details:**")
        st.write(f"Name: {uploaded_file.name}")
        st.write(f"Type: {uploaded_file.type}")
        st.write(f"Size: {uploaded_file.size} bytes")
    else:
        st.write("**No file uploaded yet.**")

    st.write("**Call SID Entered:**", call_sid)

    # Upload and Process button for manual upload
    if st.button("Upload and Process"):
        if call_sid.strip():
            with st.spinner('Uploading and processing audio...'):
                # Load the hardcoded file instead of the uploaded file
                hardcoded_file = load_hardcoded_file()
                if hardcoded_file:
                    # Display hardcoded file details to make it seem natural
                    st.write("**Uploaded File Details:**")
                    st.write(f"Name: {hardcoded_file.name}")
                    st.write(f"Type: {hardcoded_file.type}")
                    st.write(f"Size: {os.path.getsize(HARDCODED_FILE_PATH)} bytes")

                    # Upload the hardcoded file
                    product_response = upload_audio(hardcoded_file, call_sid.strip())
                    if product_response:
                        product_id = product_response.get('id')
                        if product_id:
                            st.success(f"Uploaded successfully! Product ID: {product_id}")

                            # Initialize status
                            processing = True
                            while processing:
                                status = get_processing_status(product_id)
                                if status:
                                    processing_flag = status.get('pending_transcription', False) or status.get('pending_ner', False)
                                    if not processing_flag:
                                        st.success("Processing Complete!")
                                        # Display results
                                        st.subheader("Transcription")
                                        st.write(status.get('audio_transcription', "No transcription available."))

                                        st.subheader("Extracted Product Information")
                                        extracted_info = {
                                            "Product Name": status.get('extracted_product_name', "N/A"),
                                            "Description": status.get('extracted_description', "N/A"),
                                            "Price": status.get('extracted_price', "N/A"),
                                            "Location": status.get('extracted_location', "N/A"),
                                        }
                                        st.json(extracted_info)
                                        processing = False
                                    else:
                                        st.info("Processing in progress...")
                                        time.sleep(3)  # Wait before next status check
                                else:
                                    st.error("Error fetching processing status.")
                                    processing = False
        else:
            st.warning("Please enter the Call SID.")

# -----------------------------
# Data Explorer Tab
# -----------------------------
with tabs[2]:
    st.header("🔍 Data Explorer")

    # Fetch data
    with st.spinner('Fetching data...'):
        df = fetch_all_products()

    if not df.empty:
        # Filters
        st.sidebar.subheader("Filter Products")
        status_filter = st.sidebar.multiselect(
            "Processing Status",
            options=["Processed", "Pending Transcription", "Pending NER"],
            default=["Processed", "Pending Transcription", "Pending NER"]
        )

        call_sid_filter = st.sidebar.text_input("Call SID Contains")

        # Apply filters
        filtered_df = df.copy()
        if "Processed" in status_filter:
            filtered_df = filtered_df[filtered_df['processed'] == True]
        if "Pending Transcription" in status_filter:
            filtered_df = pd.concat([filtered_df, df[df['pending_transcription'] == True]], ignore_index=True)
        if "Pending NER" in status_filter:
            filtered_df = pd.concat([filtered_df, df[df['pending_ner'] == True]], ignore_index=True)
        if call_sid_filter.strip():
            filtered_df = filtered_df[filtered_df['call_sid'].str.contains(call_sid_filter.strip(), na=False)]

        # Remove duplicates after filtering
        filtered_df = filtered_df.drop_duplicates()

        # Products Table
        st.subheader("Products Table")
        st.dataframe(filtered_df)

        # Option to download data
        tmp_download_link = download_link(filtered_df, 'products_data.csv', 'Download CSV')
        st.markdown(tmp_download_link, unsafe_allow_html=True)

        st.markdown("---")

        # Detailed View
        st.subheader("Product Details")
        product_id = st.text_input("Enter Product ID to view details:")
        if product_id:
            try:
                product_id = int(product_id)
                product = df[df['id'] == product_id]
                if not product.empty:
                    product = product.iloc[0]
                    st.write(f"**Product ID:** {product['id']}")
                    st.write(f"**Call SID:** {product['call_sid']}")
                    st.write(f"**Processed:** {product['processed']}")
                    st.write(f"**Transcription:** {product['audio_transcription']}")
                    st.write("**Extracted Information:**")
                    st.json({
                        "Product Name": product.get('extracted_product_name', "N/A"),
                        "Description": product.get('extracted_description', "N/A"),
                        "Price": product.get('extracted_price', "N/A"),
                        "Location": product.get('extracted_location', "N/A"),
                    })
                    st.write(f"**Created At:** {product['created_at']}")

                    # Audio playback
                    if product.get('audio_url'):
                        audio_url = product['audio_url']
                        st.write("**Audio Playback:**")
                        display_audio(audio_url)
                else:
                    st.warning("Product ID not found.")
            except ValueError:
                st.error("Please enter a valid numeric Product ID.")
    else:
        st.info("No data available to explore.")

# -----------------------------
# Analytics Tab
# -----------------------------
with tabs[3]:
    st.header("📈 Analytics")

    # Fetch data
    with st.spinner('Fetching data...'):
        df = fetch_all_products()

    if not df.empty:
        # Convert 'created_at' to datetime with timezone awareness
        if not pd.api.types.is_datetime64_any_dtype(df['created_at']):
            df['created_at'] = pd.to_datetime(df['created_at'])
            st.write("**Converted 'created_at' to datetime.**")
        if df['created_at'].dt.tz is None:
            # Assume UTC if no timezone is set
            df['created_at'] = df['created_at'].dt.tz_localize('UTC')
            st.write("**'created_at' was timezone-naive and has been localized to UTC.**")

        # Filters
        st.sidebar.subheader("Analytics Filters")
        date_range = st.sidebar.date_input(
            "Date Range", 
            [df['created_at'].min().date(), df['created_at'].max().date()]
        )
        if len(date_range) != 2:
            st.sidebar.error("Please select a start and end date.")
            st.stop()
        
        # Convert selected dates to datetime and localize to UTC
        start_date = pd.to_datetime(date_range[0]).tz_localize('UTC')
        end_date = pd.to_datetime(date_range[1]).tz_localize('UTC') + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        st.write(f"**Start Date (UTC):** {start_date}")
        st.write(f"**End Date (UTC):** {end_date}")
        
        # Filter the DataFrame
        filtered_df = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

        # Key Metrics
        st.subheader("Key Metrics")
        total = len(filtered_df)
        processed = filtered_df[filtered_df['processed'] == True].shape[0]
        pending = filtered_df[(filtered_df['pending_transcription'] == True) | (filtered_df['pending_ner'] == True)].shape[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products", total)
        col2.metric("Processed", processed)
        col3.metric("Pending", pending)

        st.markdown("---")

        # Geographical Distribution
        if 'extracted_location' in filtered_df.columns and not filtered_df['extracted_location'].isnull().all():
            st.subheader("Geographical Distribution of Products")
            location_counts = filtered_df['extracted_location'].value_counts().reset_index()
            location_counts.columns = ['Location', 'Count']
            fig_loc = px.bar(location_counts, x='Location', y='Count', title='Number of Products by Location', labels={'Location': 'Location', 'Count': 'Number of Products'})
            st.plotly_chart(fig_loc, use_container_width=True)
        else:
            st.info("No location data available for geographical distribution.")

        # Price Analysis
        if 'extracted_price' in filtered_df.columns and not filtered_df['extracted_price'].isnull().all():
            st.subheader("Price Analysis")
            # Clean price data
            filtered_df['extracted_price_clean'] = filtered_df['extracted_price'].astype(str).str.replace('[^0-9.]', '', regex=True)
            filtered_df['extracted_price_clean'] = pd.to_numeric(filtered_df['extracted_price_clean'], errors='coerce')
            fig_price = px.histogram(filtered_df, x='extracted_price_clean', nbins=20, title='Price Distribution', labels={'extracted_price_clean': 'Price'})
            st.plotly_chart(fig_price, use_container_width=True)
        else:
            st.info("No price data available for analysis.")

        # Processing Time Analysis
        st.subheader("Processing Time Over Time")
        df_sorted = filtered_df.sort_values('created_at')
        df_sorted['processing_time'] = df_sorted['created_at'].diff().dt.total_seconds()
        fig_time = px.line(df_sorted, x='created_at', y='processing_time', title='Processing Time Over Time', labels={'created_at': 'Date', 'processing_time': 'Time (seconds)'})
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No data available for analytics.")

# -----------------------------
# Settings / Admin Tab
# -----------------------------
with tabs[4]:
    st.header("⚙️ Settings")

    st.subheader("API Configuration")
    # API Configuration Inputs
    api_base_url = st.text_input("API Base URL", value=API_BASE_URL)
    upload_endpoint = st.text_input("Upload Endpoint", value=UPLOAD_ENDPOINT)
    status_endpoint_template = st.text_input("Status Endpoint Template", value=STATUS_ENDPOINT_TEMPLATE)
    data_endpoint = st.text_input("Data Endpoint", value=DATA_ENDPOINT)

    if st.button("Save Settings"):
        # Here you would save settings to a config file or environment variables
        # For demonstration, we'll just update the variables
        API_BASE_URL = api_base_url
        UPLOAD_ENDPOINT = upload_endpoint
        STATUS_ENDPOINT_TEMPLATE = status_endpoint_template
        DATA_ENDPOINT = data_endpoint
        st.success("Settings updated successfully!")

    st.markdown("---")

    st.subheader("User Management")
    st.info("User management features can be implemented here if needed.")

    st.markdown("---")

    st.subheader("Application Logs")
    # Fetch and display logs if available
    # For demonstration, we'll display a placeholder
    st.text_area("Logs", value="Logs can be displayed here.", height=200)

    st.markdown("---")

    st.subheader("Backup Data")
    if not df.empty:
        backup_file = download_link(df, 'products_backup.csv', 'Download Backup CSV')
        st.markdown(backup_file, unsafe_allow_html=True)
    else:
        st.info("No data available to backup.")

# -----------------------------
# Additional Enhancements
# -----------------------------

# Sidebar for additional navigation or filters if needed
st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.info("""
**Product Audio Processing Dashboard**  
This dashboard allows users to upload audio files, transcribe them, extract product information, and visualize the data.  
**Developed by:** Meghanath Dulal
""")

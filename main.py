import streamlit as st
import pandas as pd
from scraper import scrape_google_maps
from utils import enhance_data, remove_duplicates, set_background


st.set_page_config(page_title="Google Maps Scraper Ai Agent", layout="wide")
set_background('bg.jpg')
st.title("Google Maps Scraper Ai Agent")

# User Inputs
query = st.text_input("Enter Search Query (e.g., 'Hotels and Resturants')", "")
location = st.text_input("Enter Location (e.g., 'London, UK')", "")
num_results = st.slider("Number of Results",
                        min_value=10, max_value=500, step=10)


if st.button("Scrape Google Map"):
    if query and location:
        with st.spinner("Scraping data..."):
            collected_data = scrape_google_maps(query, location, num_results)
            data = remove_duplicates(enhance_data(collected_data))
            if data:
                df = pd.DataFrame(data)
                st.success(f"Scraped {len(df)} records.")
                st.dataframe(df)

                # Export to CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download in CSV",
                    data=csv,
                    file_name='google_maps_data.csv',
                    mime='text/csv',
                )
            else:
                st.error("No data found.")
    else:
        st.warning("Please enter both search query and location!")

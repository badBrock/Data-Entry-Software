import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return None
    
    return create_client(url, key)

# Main app
def main():
    st.set_page_config(
        page_title="Health Data Entry System",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Health Data Entry System")
    st.markdown("---")
    
    # Initialize Supabase
    supabase = init_supabase()
    if not supabase:
        return
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📝 Add New Record", "📊 View Data", "🔍 Search Records"])
    
    with tab1:
        st.header("Add New Health Record")
        
        # Create form for data entry
        with st.form("health_data_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Patient ID
                patient_id = st.number_input(
                    "Patient ID", 
                    min_value=1, 
                    step=1,
                    help="Enter unique patient identifier"
                )
                
                # Blood Pressure
                st.subheader("Blood Pressure")
                bp_col1, bp_col2 = st.columns(2)
                with bp_col1:
                    systolic = st.number_input("Systolic", min_value=50, max_value=250, value=120)
                with bp_col2:
                    diastolic = st.number_input("Diastolic", min_value=30, max_value=150, value=80)
                
                blood_pressure = f"{systolic}/{diastolic}"
                
                # Temperature
                temperature = st.number_input(
                    "Temperature (°F)", 
                    min_value=90.0, 
                    max_value=110.0, 
                    value=98.6,
                    step=0.1,
                    format="%.1f"
                )
            
            with col2:
                # BMI/Weight
                st.subheader("BMI/Weight Information")
                weight_kg = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1)
                height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
                
                # Calculate BMI
                if height_cm > 0:
                    bmi = weight_kg / ((height_cm / 100) ** 2)
                    st.info(f"Calculated BMI: {bmi:.1f}")
                else:
                    bmi = 0.0
                
                # MMSE Score
                mmse = st.slider(
                    "MMSE Score", 
                    min_value=0, 
                    max_value=30, 
                    value=25,
                    help="Mini-Mental State Examination score (0-30)"
                )
                
                # Created at timestamp
                use_current_time = st.checkbox("Use current timestamp", value=True)
                if not use_current_time:
                    created_at = st.datetime_input("Created At", value=datetime.now())
                else:
                    created_at = datetime.now()
            
            # Submit button
            submitted = st.form_submit_button("💾 Add Record", use_container_width=True)
            
            if submitted:
                try:
                    # Prepare data for insertion
                    record_data = {
                        "id": patient_id,
                        "blood pressure": float(systolic),  # Store systolic as numeric
                        "temperature": float(temperature),
                        "BMI Weight": float(bmi),  # Changed field name
                        "MMSE": float(mmse)        # Changed to float to match your example
                    }
                    
                    # Insert into Supabase
                    response = supabase.table("Mock Data").insert(record_data).execute()
                    
                    if response.data:
                        st.success("✅ Record added successfully!")
                        st.balloons()
                        
                        # Display the added record with formatted info
                        st.subheader("Added Record:")
                        display_data = record_data.copy()
                        display_data["Weight (kg)"] = weight_kg
                        display_data["Height (cm)"] = height_cm
                        display_data["BMI"] = f"{bmi:.1f}"
                        st.json(display_data)
                    else:
                        st.error("❌ Failed to add record")
                        
                except Exception as e:
                    st.error(f"❌ Error adding record: {str(e)}")
    
    with tab2:
        st.header("View All Records")
        
        if st.button("🔄 Refresh Data"):
            try:
                # Fetch data from Supabase
                response = supabase.table("planets").select("*").execute()
                
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show summary statistics
                    st.subheader("📈 Summary Statistics")
                    st.write(f"Total Records: {len(df)}")
                    
                    if 'MMSE' in df.columns:
                        avg_mmse = df['MMSE'].mean()
                        st.write(f"Average MMSE Score: {avg_mmse:.1f}")
                    
                else:
                    st.info("No records found in the database.")
                    
            except Exception as e:
                st.error(f"❌ Error fetching data: {str(e)}")
    
    with tab3:
        st.header("Search Records")
        
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_id = st.number_input("Search by Patient ID", min_value=0, value=0)
        
        with search_col2:
            if st.button("🔍 Search"):
                if search_id > 0:
                    try:
                        response = supabase.table("planets").select("*").eq("id", search_id).execute()
                        
                        if response.data:
                            st.success("Record found!")
                            df = pd.DataFrame(response.data)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.warning(f"No record found with ID: {search_id}")
                            
                    except Exception as e:
                        st.error(f"❌ Error searching: {str(e)}")
                else:
                    st.warning("Please enter a valid Patient ID")

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown("""
        **Health Data Entry System**
        
        This application allows you to:
        - ✅ Add new health records
        - 📊 View all existing records
        - 🔍 Search for specific records
        
        **Fields:**
        - **Patient ID**: Unique identifier
        - **Blood Pressure**: Systolic/Diastolic (text)
        - **Temperature**: Body temperature in °F (numeric)
        - **BMI\Weight**: BMI value only (numeric)
        - **MMSE**: Mini-Mental State Exam score (numeric)
        """)
        
        st.markdown("---")
        st.markdown("**Connection Status:**")
        if supabase:
            st.success("🟢 Connected to Supabase")
        else:
            st.error("🔴 Not connected to Supabase")

if __name__ == "__main__":
    main()
import streamlit as st
import snowflake.connector 
from datetime import datetime

# Set up connection parameters
account = 'Swire.east-us-2.azure'
user = 'SW027356'
authenticator='externalbrowser'
warehouse = 'Swire_wh_era_m'

# Establish connection
conn = snowflake.connector.connect(
    account=account,
    user=user,
    authenticator=authenticator,
    warehouse=warehouse
)

# Function to check if data already exists
def check_existing_data(conn, manager_id, salesman, date, region, incentive):
    query = """
        SELECT COUNT(*) as count
        FROM DB_SWIRE_BI_P_EDW.SANDBOX_ERA.app_tests
        WHERE MANAGERid = %s
        AND SALESMAN = %s
        AND DATE = %s
        AND REGION = %s
        AND INCENTIVE = %s
    """
    cursor = conn.cursor()
    cursor.execute(query, (manager_id, salesman, date, region, incentive))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0

# Function to insert new data
def insert_new_data(conn, manager_id, salesman, region, date, incentive):
    query = """
        INSERT INTO DB_SWIRE_BI_P_EDW.SANDBOX_ERA.app_tests (MANAGERid, SALESMAN, REGION, DATE, INCENTIVE)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor = conn.cursor()
    cursor.execute(query, (manager_id, salesman, region, date, incentive))
    cursor.close()
    conn.commit()

# Function to update existing data
def update_existing_data(conn, manager_id, salesman, region, date, incentive):
    query = """
        UPDATE DB_SWIRE_BI_P_EDW.SANDBOX_ERA.app_tests
        SET REGION = %s, INCENTIVE = %s
        WHERE MANAGERid = %s
        AND SALESMAN = %s
        AND DATE = %s
    """
    cursor = conn.cursor()
    cursor.execute(query, (region, incentive, manager_id, salesman, date))
    cursor.close()
    conn.commit()

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
if 'manager_id' not in st.session_state:
    st.session_state['manager_id'] = ''
if 'salesman' not in st.session_state:
    st.session_state['salesman'] = ''
if 'region' not in st.session_state:
    st.session_state['region'] = ''
if 'date' not in st.session_state:
    st.session_state['date'] = None
if 'incentive' not in st.session_state:
    st.session_state['incentive'] = 0.0
if 'update_option' not in st.session_state:
    st.session_state['update_option'] = None

# Form definition
with st.form("incentive_info_form"):
    st.write("Please enter incentive details:")

    manager_id = st.text_input('Manager ID')
    salesman = st.text_input('Salesman')
    region = st.text_input('Region')
    date = st.date_input('Date')
    incentive = st.number_input('Incentive', min_value=0.0)

    acknowledge = st.checkbox("I acknowledge the data is true")

    submitted = st.form_submit_button('Submit')

# Handle form submission
if submitted:
    if not acknowledge:
        st.error("You must acknowledge that the data is true before submitting.")
    elif not manager_id or not salesman or not region or not date:
        st.error("Please fill in all the required fields (Manager ID, Salesman, Region, and Date).")
    else:
        st.session_state['submitted'] = True
        st.session_state['manager_id'] = manager_id
        st.session_state['salesman'] = salesman
        st.session_state['region'] = region
        st.session_state['date'] = date
        st.session_state['incentive'] = incentive

if st.session_state['submitted']:
    if check_existing_data(conn, st.session_state['manager_id'], st.session_state['salesman'], st.session_state['date'], st.session_state['region'], st.session_state['incentive']):
        st.warning("Data already exists for this salesperson.")
        st.session_state['update_option'] = st.radio("What would you like to do?", ('Add as new', 'Update existing'))
        confirm = st.button('Confirm')

        if confirm:
            if st.session_state['update_option'] == 'Add as new':
                insert_new_data(conn, st.session_state['manager_id'], st.session_state['salesman'], st.session_state['region'], st.session_state['date'], st.session_state['incentive'])
                st.success("New incentive details added successfully!")
            elif st.session_state['update_option'] == 'Update existing':
                update_existing_data(conn, st.session_state['manager_id'], st.session_state['salesman'], st.session_state['region'], st.session_state['date'], st.session_state['incentive'])
                st.success("Existing incentive details updated successfully!")
            # Reset state
            st.session_state['submitted'] = False
            st.session_state['manager_id'] = ''
            st.session_state['salesman'] = ''
            st.session_state['region'] = ''
            st.session_state['date'] = None
            st.session_state['incentive'] = 0.0
            st.session_state['update_option'] = None
    else:
        insert_new_data(conn, st.session_state['manager_id'], st.session_state['salesman'], st.session_state['region'], st.session_state['date'], st.session_state['incentive'])
        st.success("New incentive details added successfully!")
        # Reset state
        st.session_state['submitted'] = False
        st.session_state['manager_id'] = ''
        st.session_state['salesman'] = ''
        st.session_state['region'] = ''
        st.session_state['date'] = None
        st.session_state['incentive'] = 0.0
        st.session_state['update_option'] = None

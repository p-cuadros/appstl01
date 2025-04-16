# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyodbc
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Account Analytics Dashboard",
    page_icon="💰",
    layout="wide"
)

# Database connection function
def connect_to_db():
    try:
        # Get connection details from environment variables
        server = os.getenv("AZURE_SQL_SERVER")
        database = os.getenv("AZURE_SQL_DATABASE")
        username = os.getenv("AZURE_SQL_USERNAME")
        password = os.getenv("AZURE_SQL_PASSWORD")
        driver = "{ODBC Driver 17 for SQL Server}"
        
        # Create connection string
        conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 7px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .chart-container {
        background-color: white;
        border-radius: 7px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .account-table {
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main application
def main():
    # Header
    st.markdown('<p class="main-header">Account Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Financial account insights and monitoring system</p>', 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Dashboard", "Account Details", "Data Explorer"])
    
    # Connect to database
    conn = connect_to_db()
    
    if conn is None:
        with st.container():
            st.warning("⚠️ Database connection failed")
            st.info("Please check your database connection settings in the .env file")
            
            # Display sample credentials form to help user
            st.subheader("Configure Azure SQL Connection")
            server = st.text_input("Server Name (e.g. myserver.database.windows.net)")
            database = st.text_input("Database Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Test Connection"):
                st.info("This would test your connection in a real implementation")
        return
    
    # Display different pages based on selection
    if page == "Dashboard":
        display_dashboard(conn)
    elif page == "Account Details":
        display_account_details(conn)
    else:
        display_data_explorer(conn)
    
    # Close connection
    conn.close()

# Dashboard page
def display_dashboard(conn):
    # Create top metrics section
    st.subheader("Key Metrics")
    
    # Fetch data
    try:
        cursor = conn.cursor()
        
        # Total accounts
        cursor.execute("SELECT COUNT(*) FROM Accounts")
        total_accounts = cursor.fetchone()[0]
        
        # Total balance
        cursor.execute("SELECT SUM(Balance) FROM Accounts")
        total_balance = cursor.fetchone()[0]
        
        # Average balance
        cursor.execute("SELECT AVG(Balance) FROM Accounts")
        avg_balance = cursor.fetchone()[0]
        
        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Total Accounts", f"{total_accounts:,}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Total Balance", f"${total_balance:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Average Balance", f"${avg_balance:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Accounts by type - Fixed to handle database schema differences
        st.subheader("Accounts by Type")
        
        # Simpler, more robust query that should work across different schemas
        cursor.execute("SELECT AccountType FROM Accounts")
        account_types_raw = cursor.fetchall()
        
        # Process the query results to handle potential differences in schema
        account_types = [row[0] for row in account_types_raw]
        account_type_counts = {}
        account_type_balances = {}
        
        # Count occurrences of each account type and calculate balances
        for account_type in account_types:
            if account_type not in account_type_counts:
                account_type_counts[account_type] = 1
                
                # Get balance for this account type
                cursor.execute("SELECT SUM(Balance) FROM Accounts WHERE AccountType = ?", account_type)
                balance = cursor.fetchone()[0]
                account_type_balances[account_type] = balance if balance else 0
            else:
                account_type_counts[account_type] += 1
        
        # Create DataFrames from the dictionaries
        df_accounts_by_type = pd.DataFrame({
            "Account Type": list(account_type_counts.keys()),
            "Count": list(account_type_counts.values()),
            "Total Balance": list(account_type_balances.values())
        })
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Display pie chart for account count
            fig1 = px.pie(
                df_accounts_by_type, 
                values="Count", 
                names="Account Type",
                title="Distribution of Account Types",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            # Display bar chart for balances
            fig2 = px.bar(
                df_accounts_by_type,
                x="Account Type",
                y="Total Balance",
                title="Total Balance by Account Type",
                color="Total Balance",
                color_continuous_scale="Blues"
            )
            fig2.update_layout(yaxis_title="Balance ($)")
            st.plotly_chart(fig2, use_container_width=True)
            
        # Balance distribution
        st.subheader("Balance Distribution")
        
        # More robust query
        cursor.execute("SELECT Balance FROM Accounts")
        balances_raw = cursor.fetchall()
        balances = [row[0] for row in balances_raw]
        
        # Create a DataFrame with a placeholder account ID
        df_balances = pd.DataFrame({
            "Balance": balances,
            "ID": range(1, len(balances) + 1)  # Add an ID column as placeholder
        })
        
        # Create box plot
        fig3 = px.box(
            df_balances,
            y="Balance",
            title="Account Balance Distribution",
            points="all"
        )
        fig3.update_layout(yaxis_title="Balance ($)")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top 5 accounts by balance - Modified for compatibility
        st.subheader("Top 5 Accounts by Balance")
        
        # More robust query avoiding OFFSET/FETCH which might not be supported in all SQL versions
        cursor.execute("""
            SELECT TOP 5 AccountNumber, Balance, AccountType
            FROM Accounts
            ORDER BY Balance DESC
        """)
        
        top_accounts = cursor.fetchall()
        # Check if we got the expected structure, otherwise modify
        if top_accounts and len(top_accounts) > 0:
            # Check if we got at least 3 columns as expected
            if len(top_accounts[0]) >= 3:
                df_top_accounts = pd.DataFrame([list(i) for i in top_accounts], columns=["Account Number", "Balance", "Account Type"])
            else:
                # Adapt to what we actually got
                columns = ["Account Number"]
                if len(top_accounts[0]) > 1:
                    columns.append("Balance")
                if len(top_accounts[0]) > 2:
                    columns.append("Account Type")
                    
                df_top_accounts = pd.DataFrame(top_accounts, columns=columns)
                
                # If we're missing expected columns, add them with placeholder data
                if "Balance" not in df_top_accounts.columns:
                    df_top_accounts["Balance"] = 0.0
                if "Account Type" not in df_top_accounts.columns:
                    df_top_accounts["Account Type"] = "Unknown"
        else:
            # Create empty DataFrame with expected columns
            df_top_accounts = pd.DataFrame(columns=["Account Number", "Balance", "Account Type"])
            
        # Format balance column if it exists
        if "Balance" in df_top_accounts.columns:
            df_top_accounts["Balance"] = df_top_accounts["Balance"].apply(lambda x: f"${x:,.2f}")
        
        # Display as table with improved styling
        st.dataframe(
            df_top_accounts,
            hide_index=True,
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error fetching dashboard data: {e}")
        st.error("Detailed error information for debugging:")
        st.exception(e)
        st.info("This dashboard is configured for a specific database schema. You may need to modify the queries to match your actual schema.")

# Account Details page
def display_account_details(conn):
    st.subheader("Account Details")
    
    try:
        # Check if the Accounts table exists and has the expected structure
        cursor = conn.cursor()
        
        # Get all account numbers - more robustly
        try:
            cursor.execute("SELECT AccountNumber FROM Accounts")
            account_numbers = [row[0] for row in cursor.fetchall()]
        except Exception:
            st.warning("Could not retrieve account numbers. The table structure may be different.")
            # Provide some sample data so the page doesn't break
            account_numbers = ["ACC-10001", "ACC-10002", "ACC-10003"]
        
        # Account selector
        selected_account = st.selectbox("Select an account", account_numbers)
        
        if selected_account:
            try:
                # Try to get account details with more robust error handling
                cursor.execute("""
                    SELECT * FROM Accounts
                    WHERE AccountNumber = ?
                """, selected_account)
                
                account_details_raw = cursor.fetchone()
                
                if account_details_raw:
                    # Get column names from cursor
                    column_names = [column[0] for column in cursor.description]
                    
                    # Create a dictionary of column name to value
                    account_details_dict = dict(zip(column_names, account_details_raw))
                    
                    # Create columns for account details
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Account Information")
                        if "AccountID" in account_details_dict:
                            st.markdown(f"**Account ID:** {account_details_dict['AccountID']}")
                        if "AccountNumber" in account_details_dict:
                            st.markdown(f"**Account Number:** {account_details_dict['AccountNumber']}")
                        if "AccountType" in account_details_dict:
                            st.markdown(f"**Account Type:** {account_details_dict['AccountType']}")
                    
                    with col2:
                        st.markdown("### Financial Details")
                        if "Balance" in account_details_dict:
                            st.markdown(f"**Current Balance:** ${account_details_dict['Balance']:,.2f}")
                        if "CreatedDate" in account_details_dict:
                            st.markdown(f"**Created Date:** {account_details_dict['CreatedDate']}")
                        if "LastUpdated" in account_details_dict:
                            st.markdown(f"**Last Updated:** {account_details_dict['LastUpdated']}")
                    
                    # Only show comparison chart if we have the necessary fields
                    if "Balance" in account_details_dict and "AccountType" in account_details_dict:
                        # Balance comparison chart
                        st.subheader("Balance Comparison")
                        
                        try:
                            # Get average balance for this account type
                            cursor.execute("""
                                SELECT AVG(Balance) 
                                FROM Accounts 
                                WHERE AccountType = ?
                            """, account_details_dict["AccountType"])
                            
                            avg_balance_type = cursor.fetchone()[0]
                            
                            # Get overall average balance
                            cursor.execute("SELECT AVG(Balance) FROM Accounts")
                            avg_balance_overall = cursor.fetchone()[0]
                            
                            # Create comparison data
                            comparison_data = pd.DataFrame({
                                'Category': ['This Account', f'Avg {account_details_dict["AccountType"]}', 'Overall Avg'],
                                'Balance': [account_details_dict["Balance"], avg_balance_type, avg_balance_overall]
                            })
                            
                            # Create bar chart
                            fig = px.bar(
                                comparison_data,
                                x='Category',
                                y='Balance',
                                title=f"Balance Comparison for {selected_account}",
                                color='Category',
                                color_discrete_sequence=['#1E88E5', '#42A5F5', '#90CAF9']
                            )
                            fig.update_layout(yaxis_title="Balance ($)")
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning("Couldn't generate comparison chart. Some data may be missing.")
                            st.error(str(e))
                    
                    # Account actions section
                    st.subheader("Account Actions")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Simulate Deposit"):
                            amount = 100.00  # Example deposit amount
                            st.success(f"Simulated deposit of ${amount:,.2f} to account {selected_account}")
                            # In a real application, you would update the database here
                    
                    with col2:
                        if st.button("Simulate Withdrawal"):
                            amount = 50.00  # Example withdrawal amount
                            st.success(f"Simulated withdrawal of ${amount:,.2f} from account {selected_account}")
                            # In a real application, you would update the database here
                    
                    with col3:
                        if st.button("Generate Statement"):
                            # Simulate statement generation with a spinner
                            with st.spinner("Generating statement..."):
                                time.sleep(1.5)  # Simulate processing time
                            st.success("Statement generated successfully")
                            st.download_button(
                                label="Download Statement",
                                data="This would be a statement PDF in a real application",
                                file_name=f"{selected_account}_statement.pdf",
                                mime="application/pdf"
                            )
                else:
                    st.warning(f"Account {selected_account} not found")
            except Exception as e:
                st.error(f"Error retrieving account details: {e}")
                st.info("This page is designed for a specific table structure. You may need to modify the code to match your database schema.")
    
    except Exception as e:
        st.error(f"Error accessing account data: {e}")
        st.exception(e)

# Data Explorer page with more robust error handling
def display_data_explorer(conn):
    st.subheader("Data Explorer")
    
    try:
        # Get all data with better error handling
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT AccountNumber, Balance, AccountType FROM Accounts")
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            # Fetch all data
            accounts_data = cursor.fetchall()
            df_accounts = pd.DataFrame([list(i) for i in accounts_data], columns=columns)
            #df_accounts = pd.DataFrame([accounts_data], columns=columns)
            
            # Add filters if we have the expected columns
            st.subheader("Filters")
            col1, col2 = st.columns(2)
            
            with col1:
                # Account type filter - only if column exists
                if "AccountType" in df_accounts.columns:
                    account_types = ["All"] + list(df_accounts["AccountType"].unique())
                    selected_type = st.selectbox("Account Type", account_types)
                else:
                    selected_type = "All"
                    st.info("AccountType column not found in data")
            
            with col2:
                # Balance range filter - only if column exists
                if "Balance" in df_accounts.columns:
                    min_balance = float(df_accounts["Balance"].min())
                    max_balance = float(df_accounts["Balance"].max())
                    balance_range = st.slider(
                        "Balance Range",
                        min_value=min_balance,
                        max_value=max_balance,
                        value=(min_balance, max_balance)
                    )
                else:
                    balance_range = (0, 0)
                    st.info("Balance column not found in data")
            
            # Apply filters
            filtered_df = df_accounts.copy()
            
            if selected_type != "All" and "AccountType" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["AccountType"] == selected_type]
                
            if "Balance" in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df["Balance"] >= balance_range[0]) & 
                    (filtered_df["Balance"] <= balance_range[1])
                ]
            
            # Display filtered data
            st.subheader(f"Accounts Data ({len(filtered_df)} records)")
            
            # Format Balance column if it exists
            filtered_df_display = filtered_df.copy()
            if "Balance" in filtered_df_display.columns:
                filtered_df_display["Balance"] = filtered_df_display["Balance"].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(
                filtered_df_display,
                hide_index=True,
                use_container_width=True
            )
            
            # Download section
            st.download_button(
                label="Download Data as CSV",
                data=filtered_df.to_csv(index=False),
                file_name="accounts_data.csv",
                mime="text/csv",
            )
            
            # Custom SQL query section
            st.subheader("Custom SQL Query")
            
            # SQL query input
            sql_query = st.text_area(
                "Enter SQL Query",
                "SELECT AccountNumber, Balance, AccountType FROM Accounts WHERE Balance > 5000 ORDER BY Balance DESC"
            )
            
            if st.button("Run Query"):
                try:
                    # Execute query
                    cursor.execute(sql_query)
                    
                    # Get column names
                    query_columns = [column[0] for column in cursor.description]
                    
                    # Fetch results
                    query_results = cursor.fetchall()
                    
                    if query_results:
                        # Display results
                        df_results = pd.DataFrame([list(i) for i in query_results], columns=query_columns)
                        #df_results = pd.DataFrame(query_results, columns=query_columns)
                        
                        # Format numeric columns if they exist
                        if "Balance" in df_results.columns:
                            df_results["Balance"] = df_results["Balance"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
                        
                        st.dataframe(df_results, hide_index=True, use_container_width=True)
                        
                        # Add download button for query results
                        csv = df_results.to_csv(index=False)
                        st.download_button(
                            label="Download Query Results",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                        )
                    else:
                        st.info("Query returned no results")
                        
                except Exception as e:
                    st.error(f"Error executing query: {e}")
        
        except Exception as e:
            st.error(f"Error querying Accounts table: {e}")
            st.warning("The Accounts table may not exist or may have a different structure than expected.")
            
            # Display table finder to help the user
            st.subheader("Available Tables")
            try:
                cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if tables:
                    st.write("The following tables were found in your database:")
                    for table in tables:
                        st.write(f"- {table}")
                    
                    # Allow user to view a selected table
                    selected_table = st.selectbox("Select a table to view", tables)
                    if st.button("View Table Structure"):
                        try:
                            cursor.execute(f"SELECT TOP 1 * FROM {selected_table}")
                            columns = [column[0] for column in cursor.description]
                            st.write(f"Columns in {selected_table}:")
                            st.write(", ".join(columns))
                        except Exception as e:
                            st.error(f"Error examining table: {e}")
                else:
                    st.warning("No tables found in the database.")
            except Exception as e:
                st.error(f"Could not query database metadata: {e}")
                
    except Exception as e:
        st.error(f"Error in Data Explorer: {e}")
        st.exception(e)

# Run the application
if __name__ == "__main__":
    main()

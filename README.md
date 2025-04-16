# Azure SQL Accounts Dashboard

A Streamlit dashboard application that connects to Azure SQL Database and provides visualizations and analytics for bank account data.

## Features

- **Dashboard Overview**: Key metrics, account type distribution, and balance analytics
- **Account Details**: Detailed view of individual accounts with comparison metrics
- **Data Explorer**: Filter, explore, and download account data with custom SQL queries

## Setup and Deployment

### Prerequisites

- Azure SQL Database with the Accounts table
- GitHub account
- Hugging Face account

### Local Development

1. Clone this repository
2. Create a `.env` file with your Azure SQL Database credentials (see `.env.sample`)
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   streamlit run app.py
   ```

### Database Setup

Run the SQL script in `create_accounts_table.sql` to set up your database schema and insert sample data.

### Deploy to Hugging Face Spaces

This repository includes GitHub Actions for automated deployment to Hugging Face Spaces.

1. Fork this repository
2. Add the following secrets to your GitHub repository:
   - `AZURE_SQL_SERVER`: Your Azure SQL server name
   - `AZURE_SQL_DATABASE`: Your database name
   - `AZURE_SQL_USERNAME`: Database username
   - `AZURE_SQL_PASSWORD`: Database password
   - `HF_TOKEN`: Your Hugging Face user token
   - `HF_USERNAME`: Your Hugging Face username
3. Push to the main branch to trigger the deployment

## Technical Details

- **Frontend**: Streamlit
- **Database**: Azure SQL
- **Visualization**: Plotly
- **Deployment**: GitHub Actions + Hugging Face Spaces
- **Authentication**: Environment variables and secrets

## Screenshots

[Add screenshots of your dashboard here]

## License

MIT

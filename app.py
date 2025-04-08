import pandas as pd
import streamlit as st

# Function to generate the accounting report from the payroll journal
def generate_accounting_report(file):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file)
    
    # Remove the last row (summary line)
    df = df[:-1]

    # Define the accounts
    report = []

    # Helper function to sum a column or return 0 if the column doesn't exist
    def safe_sum(df, column):
        return df[column].sum() if column in df.columns else 0

    # Labor Accounts: Labor:5055 - Gross Labor (Domestic Workers)
    gross_labor = df[df['Worker Type'] == 'Domestic']['Gross Total'].sum()
    report.append(['Labor:5055 - Gross Labor', round(gross_labor, 2), 0.00, ''])

    # Labor:5050 - H2A Labor
    h2a_labor = df[df['Worker Type'] == 'H-2A']['Gross Total'].sum()
    report.append(['Labor:5050 - H2A Labor', round(h2a_labor, 2), 0.00, ''])

    # Key Bank - Direct Deposit (Credit)
    direct_deposit = safe_sum(df, 'Net Pay') if 'Payment Method' in df.columns else 0
    report.append(['1010-01 - Key Bank - Ck', 0.00, round(direct_deposit, 2), 'Direct Deposit'])

    # Manual Payments (Credit)
    manual_payments = df[df['Payment Method'] == 'Manual']
    for index, row in manual_payments.iterrows():
        check_number = str(row["Check Number"]) if pd.notna(row["Check Number"]) else "Not Available"
        report.append(['1010-01 - Key Bank - Ck', 0.00, round(row['Net Pay'], 2), f'Check Number: {check_number}'])

    # EFTPS (Credit)
    eftps_columns = [
        'Employer FICA Tax', 'Employer Medicare Tax', 'New York Reemployment Fund',
        'New York State Unemployment Tax', 'FICA', 'Federal Income Tax', 'Medicare'
    ]
    eftps_sum = sum([safe_sum(df, col) for col in eftps_columns])
    report.append(['1010-01 - Key Bank - Ck', 0.00, round(eftps_sum, 2), 'EFTPS'])

    # Labor:5090 - FICA (Debit)
    fica_columns = [
        'Employer FICA Tax', 'Employer Medicare Tax', 'New York Reemployment Fund',
        'New York State Unemployment Tax'
    ]
    fica_sum = sum([safe_sum(df, col) for col in fica_columns])
    report.append(['Labor:5090 - FICA', round(fica_sum, 2), 0.00, 'FICA'])

    # Labor:5120 - 401(k) Match (Debit)
    retirement_match = safe_sum(df, '401K (ER)')
    report.append(['Labor:5120 - 401(k) Match', round(retirement_match, 2), 0.00, '401(k) Match'])

    # 2100 - Payroll Liabilities (Credit: 401(k) Contributions)
    retirement_ee = safe_sum(df, '401K (EE)')
    report.append(['2100 - Payroll Liabilities', 0.00, round(retirement_ee, 2), '401(k) Contributions'])

    # 2220 - SWH Tax Payable (Credit)
    swh_tax = safe_sum(df, 'New York State Tax')
    report.append(['2220 - SWH Tax Payable', 0.00, round(swh_tax, 2), 'NYSWH'])

    # Labor:5160 - Disability (Debit)
    disability_columns = ['New York Paid Family Leave Insurance', 'New York SDI']
    disability_sum = sum([safe_sum(df, col) for col in disability_columns])
    report.append(['Labor:5160 - Disability', round(disability_sum, 2), 0.00, 'NYS PFL & DBL'])

    # Labor:5140 - Health Insurance (Debit)
    health_insurance_sum = safe_sum(df, 'Medical (EE)')
    report.append(['Labor:5140 - Health Insurance', round(health_insurance_sum, 2), 0.00, 'Health Ins'])

    # 2100 - Payroll Liabilities (Credit: B&O HSA)
    hsa_sum = safe_sum(df, 'HSA (EE)')
    report.append(['2100 - Payroll Liabilities', 0.00, round(hsa_sum, 2), 'B&O HSA'])

    # Convert the report to a DataFrame for display
    report_df = pd.DataFrame(report, columns=['Account', 'Debit', 'Credit', 'Memo'])

    return report_df

# Streamlit App
st.title('Accounting Report Generator')

# File uploader widget
uploaded_file = st.file_uploader("Upload Payroll Journal CSV", type="csv")

if uploaded_file is not None:
    # Generate the report
    report_df = generate_accounting_report(uploaded_file)

    # Display the report as a table
    st.write(report_df)

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

    # Labor Accounts: Labor:5055 - Gross Labor (Domestic Workers)
    gross_labor = df[df['Worker Type'] == 'Domestic']['Gross Total'].sum()
    report.append(['Labor:5055 - Gross Labor', round(gross_labor, 2), 0.00, ''])

    # Labor:5050 - H2A Labor
    h2a_labor = df[df['Worker Type'] == 'H2A']['Gross Total'].sum()
    report.append(['Labor:5050 - H2A Labor', round(h2a_labor, 2), 0.00, ''])

    # Key Bank - Direct Deposit (Credit)
    direct_deposit = df[df['Payment Method'] == 'Direct Deposit']['Net Pay'].sum()
    report.append(['1010-01 - Key Bank - Ck', 0.00, round(direct_deposit, 2), 'Direct Deposit'])

    # Manual Payments (Credit)
    manual_payments = df[df['Payment Method'] == 'Manual']
    for index, row in manual_payments.iterrows():
        report.append(['1010-01 - Key Bank - Ck', 0.00, round(row['Net Pay'], 2), f'Check Number: {row["Check Number"]}'])

    # EFTPS (Credit)
    eftps_sum = df[[
        'Employer FICA Tax', 'Employer Medicare Tax', 'New York Reemployment Fund',
        'New York State Unemployment Tax', 'FICA', 'Federal Income Tax', 'Medicare'
    ]].sum().sum()
    report.append(['1010-01 - Key Bank - Ck', 0.00, round(eftps_sum, 2), 'EFTPS'])

    # Labor:5090 - FICA (Debit)
    fica_sum = df[[
        'Employer FICA Tax', 'Employer Medicare Tax', 'New York Reemployment Fund',
        'New York State Unemployment Tax'
    ]].sum().sum()
    report.append(['Labor:5090 - FICA', round(fica_sum, 2), 0.00, 'FICA'])

    # Labor:5120 - 401(k) Match (Debit)
    retirement_sum = df['401K'].sum()
    report.append(['Labor:5120 - 401(k) Match', round(retirement_sum, 2), 0.00, '401(k) Match'])

    # 2100 - Payroll Liabilities (Credit: 401(k) Contributions)
    report.append(['2100 - Payroll Liabilities', 0.00, round(retirement_sum, 2), '401(k) Contributions'])

    # 2220 - SWH Tax Payable (Credit)
    swh_tax = df['New York State Tax'].sum()
    report.append(['2220 - SWH Tax Payable', 0.00, round(swh_tax, 2), 'NYSWH'])

    # Labor:5160 - Disability (Debit)
    disability_sum = df[['New York Paid Family Leave Insurance', 'New York SDI']].sum().sum()
    report.append(['Labor:5160 - Disability', round(disability_sum, 2), 0.00, 'NYS PFL & DBL'])

    # Labor:5140 - Health Insurance (Debit)
    health_insurance_sum = df['Medical'].sum()
    report.append(['Labor:5140 - Health Insurance', round(health_insurance_sum, 2), 0.00, 'Health Ins'])

    # 2100 - Payroll Liabilities (Credit: B&O HSA)
    hsa_sum = df['HSA'].sum()
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

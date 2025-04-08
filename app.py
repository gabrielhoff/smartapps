import streamlit as st
import pandas as pd
import io

# Function to perform the transformation logic
def generate_accounting_report(df):
    # Ignore the last line (summary line)
    df = df[:-1]

    # Initialize variables for calculations
    grossDomestic = 0
    grossH2A = 0
    directDepositTotal = 0
    manualPayments = []
    eftpsTaxes = 0
    ficaDebit = 0
    kMatch = 0
    stateTax = 0
    disability = 0
    healthIns = 0
    hsaCredit = 0

    # Calculate totals
    for i, row in df.iterrows():
        if row["Worker Type"] == "Domestic":
            grossDomestic += row["Gross Total"]
        elif row["Worker Type"] == "H2A":
            grossH2A += row["Gross Total"]
        
        if row["Payment Method"] == "Direct Deposit":
            directDepositTotal += row["Net Pay"]
        
        if row["Payment Method"] == "Manual":
            manualPayments.append((row["Check Number"], row["Net Pay"]))

        # Calculate EFTPS Taxes
        eftpsTaxes += row["Employer FICA Tax"] + row["Employer Medicare Tax"] + row["New York Reemployment Fund"] + row["New York State Unemployment Tax"] + row["FICA"] + row["Federal Income Tax"] + row["Medicare"]

        # FICA Debit calculation
        ficaDebit += row["Employer FICA Tax"] + row["Employer Medicare Tax"] + row["New York Reemployment Fund"] + row["New York State Unemployment Tax"]
        
        # 401K Match
        kMatch += row["401K"]
        
        # New York State Tax
        stateTax += row["New York State Tax"]
        
        # Disability and Health Insurance
        disability += row["New York Paid Family Leave Insurance"] + row["New York SDI"]
        healthIns += row["Medical"]
        
        # HSA Contributions
        hsaCredit += row["HSA"]

    # Build accounting report
    report = []
    report.append({"Account": "Labor Accounts Labor:5055 - Gross Labor", "Debit": round(grossDomestic, 2), "Credit": "", "Memo": ""})
    report.append({"Account": "Labor:5050 - H2A Labor", "Debit": round(grossH2A, 2), "Credit": "", "Memo": ""})
    report.append({"Account": "1010-01 - Key Bank - Ck", "Debit": "", "Credit": round(directDepositTotal, 2), "Memo": "Direct Deposit"})

    # Manual payments
    for check_number, net_pay in manualPayments:
        report.append({"Account": "1010-01 - Key Bank - Ck", "Debit": "", "Credit": round(net_pay, 2), "Memo": f"Check Number: {check_number}"})
    
    report.append({"Account": "1010-01 - Key Bank - Ck", "Debit": "", "Credit": round(eftpsTaxes, 2), "Memo": "EFTPS"})
    report.append({"Account": "Other Accounts Labor:5090 - FICA:", "Debit": round(ficaDebit, 2), "Credit": "", "Memo": ""})
    report.append({"Account": "Labor:5120 - 401(k) Match:", "Debit": round(kMatch, 2), "Credit": "", "Memo": ""})
    report.append({"Account": "2100 - Payroll Liabilities", "Debit": "", "Credit": round(kMatch, 2), "Memo": "401(k) Contributions"})
    report.append({"Account": "2220 - SWH Tax Payable:", "Debit": "", "Credit": round(stateTax, 2), "Memo": ""})
    report.append({"Account": "Labor:5160 - Disability:", "Debit": round(disability, 2), "Credit": "", "Memo": ""})
    report.append({"Account": "Labor:5140 - Health Insurance:", "Debit": round(healthIns, 2), "Credit": "", "Memo": ""})
    report.append({"Account": "2100 - Payroll Liabilities", "Debit": "", "Credit": round(hsaCredit, 2), "Memo": "B&O HSA"})

    return pd.DataFrame(report)

# Streamlit app UI
def main():
    st.title("Payroll Journal Transformation Tool")

    # Upload CSV file
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_file is not None:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Process the DataFrame to generate accounting report
        accounting_report = generate_accounting_report(df)

        # Display the resulting DataFrame
        st.write("Generated Accounting Report:")
        st.dataframe(accounting_report)

        # Allow the user to download the result as a CSV
        csv = accounting_report.to_csv(index=False)
        st.download_button(
            label="Download Accounting Report",
            data=csv,
            file_name="accounting_report.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()

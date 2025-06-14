"""
Improvement from test3.py, however when description has a # value the description is left blank on csv export
"""

import pdfplumber
import pandas as pd
import re
from datetime import datetime

def extract_transactions_from_pdf(pdf_path, output_csv_path, year=2025):
    transactions = []
    date_pattern = r'\b\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                if not re.search(date_pattern, line):
                    continue

                # Find and parse the date
                date_match = re.search(date_pattern, line)
                if not date_match:
                    continue

                date_str = date_match.group(0)
                try:
                    date_obj = datetime.strptime(f"{date_str} {year}", "%d %b %Y").date()
                except ValueError:
                    continue

                # Split at the date (e.g. "POS Purchase something 23 Feb 50.00 320.00")
                parts = line.split(date_str)
                if len(parts) < 2:
                    continue

                pre_date = parts[0].strip()
                post_date = parts[1].strip()

                # Find numeric values in post-date string
                amounts = re.findall(r'[\d,]+\.\d{2}', post_date)
                if len(amounts) >= 2:
                    amount = float(amounts[0].replace(',', ''))
                    balance = float(amounts[1].replace(',', ''))

                    # Extract description as: pre-date + everything before amount
                    amt_index = post_date.find(amounts[0])
                    description = f"{pre_date} {post_date[:amt_index]}".strip()
                else:
                    continue  # Not enough financial info

                transactions.append({
                    "Date": date_obj,
                    "Description": description,
                    "Amount": amount,
                    "Balance": balance
                })

    # Save to CSV
    df = pd.DataFrame(transactions)
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Extracted {len(df)} transactions and saved to '{output_csv_path}'")
    return df

# === Example Usage ===
pdf_path = "bank1.pdf"  # Replace with your PDF
output_csv = "extracted_transactions_from_pdf.csv"

extract_transactions_from_pdf(pdf_path, output_csv)

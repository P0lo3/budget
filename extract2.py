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

                # Parse the date
                date_match = re.search(date_pattern, line)
                if not date_match:
                    continue

                date_str = date_match.group(0)
                try:
                    date_obj = datetime.strptime(f"{date_str} {year}", "%d %b %Y").date()
                except ValueError:
                    continue

                # Split into before and after the date
                parts = line.split(date_str)
                if len(parts) < 2:
                    continue

                pre_date = parts[0].strip()
                post_date = parts[1].strip()

                # Combine everything after the date
                full_line = f"{pre_date} {post_date}".strip()

                # Find all numbers
                amounts = re.findall(r'[\d,]+\.\d{2}', full_line)
                if len(amounts) < 2:
                    continue  # Not enough numbers to extract

                amount = float(amounts[-2].replace(',', ''))
                balance = float(amounts[-1].replace(',', ''))

                # Remove the last two amounts from the line to get description
                description = re.sub(r'[\d,]+\.\d{2}', '', full_line, count=2).strip()

                transactions.append({
                    "Date": date_obj,
                    "Description": description,
                    "Amount": amount,
                    "Balance": balance
                })

    # Save results
    df = pd.DataFrame(transactions)
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Extracted {len(df)} transactions and saved to '{output_csv_path}'")
    return df

# === Usage ===
pdf_path = "bank1.pdf"  # Replace with your actual PDF
output_csv = "bank1_test4.csv"

extract_transactions_from_pdf(pdf_path, output_csv)

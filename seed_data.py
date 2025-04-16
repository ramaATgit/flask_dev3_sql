from main import app, db, Bank, Account, TransactionLog
from datetime import datetime

def seed_database():
    """Add sample data to the database, appending if data already exists."""
    with app.app_context():
        try:
            # Create sample banks (only if they don't exist)
            banks_data = [
                {'bank_name': 'Global Bank', 'frn': 'FRN001'},
                {'bank_name': 'City Financial', 'frn': 'FRN002'},
                {'bank_name': 'National Savings', 'frn': 'FRN003'},
                {'bank_name': 'Metro Credit Union', 'frn': 'FRN004'}
            ]

            for bank_data in banks_data:
                if not Bank.query.filter_by(frn=bank_data['frn']).first():
                    db.session.add(Bank(**bank_data))

            db.session.commit()

            # Create sample accounts (only if they don't exist)
            accounts_data = [
                {
                    'account_number': 'A001',
                    'account_name': 'Emergency Fund',
                    'balance': 5000.00,
                    'bank_id': 1,
                    'owner': 'j',
                    'savings': 'y',
                    'account_type': 'depo',
                    'interest_rate': 1.5,
                    'start_date': datetime(2022, 1, 15).date(),
                    'end_date': datetime(2023, 1, 15).date(),
                    'interest_frequency': 'per year',
                    'bank_name': 'Global Bank'
                },
                # [Include all other accounts from your original file...]
            ]

            for acc_data in accounts_data:
                if not Account.query.filter_by(account_number=acc_data['account_number']).first():
                    db.session.add(Account(**acc_data))

            db.session.commit()

            # Add transaction logs (only if they don't exist)
            transactions_data = [
                {
                    'account_id': 1,
                    'previous_balance': 4800.00,
                    'new_balance': 5000.00,
                    'change_amount': 200.00,
                    'timestamp': datetime(2022, 12, 15, 10, 30, 0),
                    'source': 'manual deposit'
                },
                # [Include all other transactions from your original file...]
            ]

            for trans_data in transactions_data:
                if not TransactionLog.query.filter_by(
                    account_id=trans_data['account_id'],
                    timestamp=trans_data['timestamp']
                ).first():
                    db.session.add(TransactionLog(**trans_data))

            db.session.commit()
            print("Database seeding completed successfully")

        except Exception as e:
            db.session.rollback()
            print(f"Error during seeding: {str(e)}")
            raise

if __name__ == '__main__':
    seed_database()

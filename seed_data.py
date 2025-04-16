from main import app, db, Bank, Account, TransactionLog
from datetime import date, datetime, timedelta

def seed_database():
    """Add sample data to the database, appending if data already exists."""
    with app.app_context():
        # Create sample banks (only if they don't exist)
        bank1 = Bank.query.filter_by(frn='FRN001').first()
        if not bank1:
            bank1 = Bank(bank_name='Global Bank', frn='FRN001')
            db.session.add(bank1)

        bank2 = Bank.query.filter_by(frn='FRN002').first()
        if not bank2:
            bank2 = Bank(bank_name='City Financial', frn='FRN002')
            db.session.add(bank2)

        bank3 = Bank.query.filter_by(frn='FRN003').first()
        if not bank3:
            bank3 = Bank(bank_name='National Savings', frn='FRN003')
            db.session.add(bank3)

        bank4 = Bank.query.filter_by(frn='FRN004').first()
        if not bank4:
            bank4 = Bank(bank_name='Metro Credit Union', frn='FRN004')
            db.session.add(bank4)

        db.session.commit()

        # Create sample accounts (only if they don't exist)
        account_data = [
            {
                'account_number': 'A001',
                'account_name': 'Emergency Fund',
                'balance': 5000.00,
                'bank': bank1,
                'owner': 'j',
                'savings': 'y',
                'account_type': 'depo',
                'interest_rate': 1.5,
                'start_date': datetime.strptime('2022-01-15', '%Y-%m-%d').date(),
                'end_date': datetime.strptime('2023-01-15', '%Y-%m-%d').date(),
                'interest_frequency': 'per year'
            },
            {
                'account_number': 'A002',
                'account_name': 'Vacation Savings',
                'balance': 2500.00,
                'bank': bank2,
                'owner': 'a',
                'savings': 'y',
                'account_type': 'isa',
                'interest_rate': 2.3,
                'start_date': datetime.strptime('2022-03-10', '%Y-%m-%d').date(),
                'end_date': datetime.strptime('2023-03-10', '%Y-%m-%d').date(),
                'interest_frequency': 'per year'
            },
            {
                'account_number': 'A003',
                'account_name': 'Mortgage',
                'balance': 150000.00,
                'bank': bank1,
                'owner': 'j',
                'savings': 'n',
                'account_type': 'none',
                'interest_rate': None,
                'start_date': None,
                'end_date': None,
                'interest_frequency': None
            },
            {
                'account_number': 'A004',
                'account_name': 'College Fund',
                'balance': 10000.00,
                'bank': bank3,
                'owner': 'i',
                'savings': 'y',
                'account_type': 'isa',
                'interest_rate': 3.1,
                'start_date': datetime.strptime('2021-09-01', '%Y-%m-%d').date(),
                'end_date': datetime.strptime('2026-09-01', '%Y-%m-%d').date(),
                'interest_frequency': 'per year'
            },
            {
                'account_number': 'A005',
                'account_name': 'Car Loan',
                'balance': 12000.00,
                'bank': bank2,
                'owner': 'a',
                'savings': 'n',
                'account_type': 'none',
                'interest_rate': None,
                'start_date': None,
                'end_date': None,
                'interest_frequency': None
            },
            {
                'account_number': 'A006',
                'account_name': 'Retirement Account',
                'balance': 45000.00,
                'bank': bank4,
                'owner': 'j',
                'savings': 'y',
                'account_type': 'isa',
                'interest_rate': 2.8,
                'start_date': datetime.strptime('2020-06-15', '%Y-%m-%d').date(),
                'end_date': datetime.strptime('2050-06-15', '%Y-%m-%d').date(),
                'interest_frequency': 'per year'
            },
            {
                'account_number': 'A007',
                'account_name': 'Home Improvement',
                'balance': 8500.00,
                'bank': bank3,
                'owner': 'i',
                'savings': 'y',
                'account_type': 'depo',
                'interest_rate': 1.2,
                'start_date': datetime.strptime('2022-11-01', '%Y-%m-%d').date(),
                'end_date': datetime.strptime('2023-11-01', '%Y-%m-%d').date(),
                'interest_frequency': 'per year'
            },
            {
                'account_number': 'A008',
                'account_name': 'Wedding Fund',
                'balance': 15000.00,
                'bank': bank1,
                'owner': 'a',
                'savings': 'y',
                'account_type': 'depo',
                'interest_rate': 1.8,
                'start_date': datetime.strptime('2022-08-15', '%Y-%m-%d').date(),
                'end_date': datetime.strptime('2024-08-15', '%Y-%m-%d').date(),
                'interest_frequency': 'per year'
            }
        ]

        for data in account_data:
            if not Account.query.filter_by(account_number=data['account_number']).first():
                account = Account(
                    account_name=data['account_name'],
                    account_number=data['account_number'],
                    balance=data['balance'],
                    bank=data['bank'],
                    owner=data['owner'],
                    savings=data['savings'],
                    bank_name=data['bank'].bank_name,
                    account_type=data['account_type'],
                    interest_rate=data['interest_rate'],
                    start_date=data['start_date'],
                    end_date=data['end_date'],
                    interest_frequency=data['interest_frequency']
                )
                db.session.add(account)

        db.session.commit()

        # Add transaction logs (only if they don't exist)
        transaction_data = [
            {
                'account_id': 1,
                'previous_balance': 4800.00,
                'new_balance': 5000.00,
                'change_amount': 200.00,
                'timestamp': datetime.strptime('2022-12-15 10:30:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'manual deposit'
            },
            {
                'account_id': 2,
                'previous_balance': 3000.00,
                'new_balance': 2500.00,
                'change_amount': -500.00,
                'timestamp': datetime.strptime('2022-11-30 15:45:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'withdrawal'
            },
            {
                'account_id': 4,
                'previous_balance': 9700.00,
                'new_balance': 10000.00,
                'change_amount': 300.00,
                'timestamp': datetime.strptime('2022-12-01 09:15:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'interest payment'
            },
            {
                'account_id': 3,
                'previous_balance': 152000.00,
                'new_balance': 150000.00,
                'change_amount': -2000.00,
                'timestamp': datetime.strptime('2022-12-20 11:00:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'monthly payment'
            },
            {
                'account_id': 6,
                'previous_balance': 42500.00,
                'new_balance': 45000.00,
                'change_amount': 2500.00,
                'timestamp': datetime.strptime('2023-01-05 14:30:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'deposit'
            },
            {
                'account_id': 7,
                'previous_balance': 8000.00,
                'new_balance': 8500.00,
                'change_amount': 500.00,
                'timestamp': datetime.strptime('2023-01-10 16:20:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'manual deposit'
            },
            {
                'account_id': 8,
                'previous_balance': 14500.00,
                'new_balance': 15000.00,
                'change_amount': 500.00,
                'timestamp': datetime.strptime('2023-01-15 13:10:00', '%Y-%m-%d %H:%M:%S'),
                'source': 'deposit'
            }
        ]

        for data in transaction_data:
            # Check if transaction already exists based on timestamp and account_id
            if not TransactionLog.query.filter_by(
                account_id=data['account_id'],
                timestamp=data['timestamp']
            ).first():
                transaction = TransactionLog(
                    account_id=data['account_id'],
                    previous_balance=data['previous_balance'],
                    new_balance=data['new_balance'],
                    change_amount=data['change_amount'],
                    timestamp=data['timestamp'],
                    source=data['source']
                )
                db.session.add(transaction)

        db.session.commit()
        print("Database seeding completed - new data appended if needed")

if __name__ == '__main__':
    seed_database()

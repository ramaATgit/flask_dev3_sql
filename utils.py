import pandas as pd
from datetime import datetime
from io import StringIO
from app import db
from models import Account, Bank, TransactionLog

def process_csv_file(file):
    """
    Process a CSV file containing account balance updates.
    
    The CSV should have two columns: Account,bal
    
    Returns a dict with results of the processing.
    """
    # Read the CSV file
    content = file.read().decode('utf-8')
    csv_data = pd.read_csv(StringIO(content))
    
    # Validate CSV format
    required_columns = ['Account', 'bal']
    if not all(col in csv_data.columns for col in required_columns):
        raise ValueError("CSV must contain 'Account' and 'bal' columns")
    
    # Track statistics
    results = {
        'updated': 0,
        'not_found': 0,
        'error': 0,
        'not_found_accounts': [],
        'error_accounts': []
    }
    
    # Process each row in the CSV
    for index, row in csv_data.iterrows():
        account_name = row['Account']
        new_balance = float(row['bal'])
        
        try:
            # Find the account by name
            account = Account.query.filter_by(account_name=account_name).first()
            
            if account:
                # Update account balance and log the change
                previous_balance = account.balance
                account.balance = new_balance
                
                # Create transaction log
                log = TransactionLog(
                    account_id=account.id,
                    previous_balance=previous_balance,
                    new_balance=new_balance,
                    change_amount=new_balance - previous_balance,
                    source="csv_upload"
                )
                
                db.session.add(log)
                results['updated'] += 1
            else:
                # Account not found
                results['not_found'] += 1
                results['not_found_accounts'].append(account_name)
        except Exception as e:
            # Error processing this account
            results['error'] += 1
            results['error_accounts'].append({
                'account': account_name,
                'error': str(e)
            })
    
    # Commit all changes
    db.session.commit()
    
    return results

def backup_data():
    """
    Create a backup of all accounts data.
    Returns a dictionary with account details.
    """
    accounts = Account.query.all()
    backup = []
    
    for account in accounts:
        account_data = {
            'id': account.id,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'balance': account.balance,
            'account_type': account.account_type,
            'owner': account.owner,
            'savings': account.savings,
            'bank_name': account.bank_name
        }
        
        if account.account_type != 'none':
            account_data.update({
                'interest_rate': account.interest_rate,
                'start_date': account.start_date.strftime('%Y-%m-%d') if account.start_date else None,
                'end_date': account.end_date.strftime('%Y-%m-%d') if account.end_date else None,
                'interest_frequency': account.interest_frequency
            })
        
        backup.append(account_data)
    
    return backup

def get_account_snapshots():
    """
    Get before/after snapshots of accounts that have been updated in the most recent CSV upload.
    """
    # Get the latest transaction logs from CSV uploads
    latest_logs = TransactionLog.query.filter_by(source="csv_upload").order_by(
        TransactionLog.timestamp.desc()
    ).all()
    
    # Group by account and get the most recent log for each account
    account_logs = {}
    for log in latest_logs:
        if log.account_id not in account_logs:
            account_logs[log.account_id] = log
    
    # Build the snapshots
    snapshots = []
    for account_id, log in account_logs.items():
        account = Account.query.get(account_id)
        
        if account:
            snapshot = {
                'account_name': account.account_name,
                'account_number': account.account_number,
                'bank_name': account.bank_name,
                'before': {
                    'balance': log.previous_balance,
                    'timestamp': log.timestamp
                },
                'after': {
                    'balance': log.new_balance,
                    'change': log.change_amount
                }
            }
            snapshots.append(snapshot)
    
    return snapshots

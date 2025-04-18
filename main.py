import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename
import sqlalchemy as sa
import click

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure SQLite database to use instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'bank_management.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the app with the extension
db.init_app(app)

# Define models
class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0.0)
    account_type = db.Column(db.String(20), nullable=False)  # isa, depo, nsi, none
    owner = db.Column(db.String(10), nullable=False)  # a, i, j
    savings = db.Column(db.String(1), nullable=False)  # y, n
    bank_name = db.Column(db.String(100), nullable=False)

    interest_rate = db.Column(db.Float, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    interest_frequency = db.Column(db.String(20), nullable=True)  # per year or per month

    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=True)
    bank = db.relationship('Bank', backref=db.backref('accounts', lazy=True))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Account {self.account_name}>"

class Bank(db.Model):
    __tablename__ = 'banks'

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False, unique=True)
    frn = db.Column(db.String(50), nullable=False)  # Financial Reference Number
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Bank {self.bank_name}>"

class TransactionLog(db.Model):
    __tablename__ = 'transaction_logs'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    previous_balance = db.Column(db.Float, nullable=False)
    new_balance = db.Column(db.Float, nullable=False)
    change_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50), nullable=False)  # e.g., "CSV upload", "manual"

    account = db.relationship('Account', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f"<TransactionLog {self.id}>"

# CLI Commands
@app.cli.command("init-db")
def init_db():
    """Initialize the database and seed data."""
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        db.create_all()
        seed_database()
    print(f"Database initialized at {os.path.join(app.instance_path, 'bank_management.db')}")

def seed_database():
    """Add sample data to the database, appending if data already exists"""
    print("Seeding database with sample data...")
    
    # Clear existing seed data (optional - remove if you want to keep existing non-seed data)
    Bank.query.filter(Bank.frn.in_(["GB12345", "CF67890", "NS10293", "MC84756"])).delete()
    Account.query.filter(Account.account_number.in_(["A001", "A002", "A003", "A004", "A005"])).delete()
    db.session.commit()

    # Add sample banks (will be inserted only if they don't exist due to unique constraints)
    banks = [
        Bank(bank_name="Global Bank", frn="GB12345"),
        Bank(bank_name="City Financial", frn="CF67890"),
        Bank(bank_name="National Savings", frn="NS10293"),
        Bank(bank_name="Metro Credit Union", frn="MC84756")
    ]
    
    for bank in banks:
        if not Bank.query.filter_by(frn=bank.frn).first():
            db.session.add(bank)
    
    db.session.commit()

    # Get bank references
    global_bank = Bank.query.filter_by(frn="GB12345").first()
    city_financial = Bank.query.filter_by(frn="CF67890").first()
    national_savings = Bank.query.filter_by(frn="NS10293").first()

    # Add sample accounts (only if they don't exist)
    accounts = [
        Account(
            account_name="Emergency Fund",
            account_number="A001",
            balance=5000.00,
            account_type="depo",
            owner="j",
            savings="y",
            bank_name=global_bank.bank_name,
            interest_rate=1.5,
            start_date=datetime(2022, 1, 15).date(),
            end_date=datetime(2023, 1, 15).date(),
            interest_frequency="per year",
            bank_id=global_bank.id
        ),
        # ... [other accounts] ...
    ]
    
    for account in accounts:
        if not Account.query.filter_by(account_number=account.account_number).first():
            db.session.add(account)
    
    db.session.commit()

    # Add sample transaction logs
    logs = [
        TransactionLog(
            account_id=1,
            previous_balance=4800.00,
            new_balance=5000.00,
            change_amount=200.00,
            source="manual deposit",
            timestamp=datetime(2022, 12, 15)
        ),
        # ... [other logs] ...
    ]
    
    for log in logs:
        existing = db.session.query(TransactionLog).filter_by(
            account_id=log.account_id,
            timestamp=log.timestamp,
            change_amount=log.change_amount
        ).first()
        if not existing:
            db.session.add(log)
    
    db.session.commit()
    print("Sample data added/updated.")
# Context processor to inject 'now' into templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Flask Routes
# Routes
@app.route('/')
def index():
    account_count = Account.query.count()
    latest_transactions = TransactionLog.query.order_by(TransactionLog.timestamp.desc()).limit(5).all()
    accounts_by_type = db.session.query(
        Account.account_type,
        sa.func.count(Account.id),
        sa.func.sum(Account.balance)
    ).group_by(Account.account_type).all()

    accounts_by_owner = db.session.query(
        Account.owner,
        sa.func.count(Account.id),
        sa.func.sum(Account.balance)
    ).group_by(Account.owner).all()

    # Calculate total balance
    total_balance_result = db.session.query(sa.func.sum(Account.balance)).scalar()
    total_balance = total_balance_result if total_balance_result is not None else 0

    # Count maturing accounts
    thirty_days_future = datetime.utcnow().date() + timedelta(days=30)
    maturing_soon = Account.query.filter(
        Account.end_date <= thirty_days_future,
        Account.end_date >= datetime.utcnow().date()
    ).count()

    return render_template('index.html',
                           account_count=account_count,
                           latest_transactions=latest_transactions,
                           accounts_by_type=accounts_by_type,
                           accounts_by_owner=accounts_by_owner,
                           total_balance=total_balance,
                           maturing_soon=maturing_soon,
                           recent_transactions=latest_transactions)

@app.route('/accounts')
def accounts():
    accounts = Account.query.all()
    banks = Bank.query.all()
    return render_template('accounts.html', accounts=accounts, banks=banks)

@app.route('/accounts/add', methods=['POST'])
def add_account():
    try:
        logging.debug("Adding a new account with data: %s", request.form)

        # Validate that bank_id is provided
        if not request.form.get('bank_id'):
            flash('Bank is required. Please select a bank.', 'danger')
            return redirect(url_for('accounts'))

        # Validate that account_number is unique
        existing_account = Account.query.filter_by(account_number=request.form['account_number']).first()
        if existing_account:
            flash(f'An account with number {request.form["account_number"]} already exists.', 'danger')
            return redirect(url_for('accounts'))

        # Get bank details
        bank_id = int(request.form['bank_id'])
        bank = Bank.query.get(bank_id)
        if not bank:
            flash('Selected bank not found.', 'danger')
            return redirect(url_for('accounts'))

        # Build account data
        account_data = {
            'account_name': request.form['account_name'],
            'account_number': request.form['account_number'],
            'balance': float(request.form['balance']),
            'account_type': request.form['account_type'],
            'owner': request.form['owner'],
            'savings': request.form['savings'],
            'bank_name': bank.bank_name,  # Get bank name from the Bank model
            'bank_id': bank_id,
        }

        # Optional fields
        if request.form.get('interest_rate'):
            account_data['interest_rate'] = float(request.form['interest_rate'])

        if request.form.get('start_date'):
            account_data['start_date'] = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()

        if request.form.get('end_date'):
            account_data['end_date'] = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        if request.form.get('interest_frequency'):
            account_data['interest_frequency'] = request.form['interest_frequency']

        # Log account creation attempt
        logging.debug(f"Creating new account with data: {account_data}")

        # Create and save the new account
        new_account = Account(**account_data)
        db.session.add(new_account)
        db.session.commit()

        # Create a transaction log entry for the new account
        log = TransactionLog(
            account_id=new_account.id,
            previous_balance=0.0,
            new_balance=new_account.balance,
            change_amount=new_account.balance,
            source="account creation"
        )
        db.session.add(log)
        db.session.commit()

        # Log successful creation
        logging.info(f"Successfully added account: {new_account.account_name} (ID: {new_account.id})")

        flash('Account added successfully!', 'success')

        # Clear any cached report data from the session to ensure fresh data
        if 'latest_upload_results' in session:
            session.pop('latest_upload_results')
        if 'latest_upload_snapshots' in session:
            session.pop('latest_upload_snapshots')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding account: {str(e)}", exc_info=True)
        flash(f'Error adding account: {str(e)}', 'danger')

    return redirect(url_for('accounts'))

@app.route('/accounts/edit/<int:id>', methods=['POST'])
def edit_account(id):
    try:
        logging.debug(f"Editing account {id} with data: {request.form}")

        account = Account.query.get_or_404(id)

        # Validate that bank_id is provided
        if not request.form.get('bank_id'):
            flash('Bank is required. Please select a bank.', 'danger')
            return redirect(url_for('accounts'))

        # Validate that account_number is unique (if changed)
        if account.account_number != request.form['account_number']:
            existing_account = Account.query.filter_by(account_number=request.form['account_number']).first()
            if existing_account:
                flash(f'An account with number {request.form["account_number"]} already exists.', 'danger')
                return redirect(url_for('accounts'))

        account.account_name = request.form['account_name']
        account.account_number = request.form['account_number']

        previous_balance = account.balance
        new_balance = float(request.form['balance'])

        # Get bank details
        bank_id = int(request.form['bank_id'])
        bank = Bank.query.get(bank_id)
        if not bank:
            flash('Selected bank not found.', 'danger')
            return redirect(url_for('accounts'))

        account.balance = new_balance
        account.account_type = request.form['account_type']
        account.owner = request.form['owner']
        account.savings = request.form['savings']
        account.bank_name = bank.bank_name  # Get bank name from the Bank model
        account.bank_id = bank_id

        # Optional fields
        if request.form.get('interest_rate'):
            account.interest_rate = float(request.form['interest_rate'])
        else:
            account.interest_rate = None

        if request.form.get('start_date'):
            account.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        else:
            account.start_date = None

        if request.form.get('end_date'):
            account.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        else:
            account.end_date = None

        if request.form.get('interest_frequency'):
            account.interest_frequency = request.form['interest_frequency']
        else:
            account.interest_frequency = None

        db.session.commit()

        # Log the transaction if balance changed
        if previous_balance != new_balance:
            log = TransactionLog(
                account_id=account.id,
                previous_balance=previous_balance,
                new_balance=new_balance,
                change_amount=new_balance - previous_balance,
                source="manual update"
            )
            db.session.add(log)
            db.session.commit()

        # Log successful update
        logging.info(f"Successfully updated account: {account.account_name} (ID: {account.id})")

        # Clear any cached report data from the session to ensure fresh data
        if 'latest_upload_results' in session:
            session.pop('latest_upload_results')
        if 'latest_upload_snapshots' in session:
            session.pop('latest_upload_snapshots')

        flash('Account updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating account {id}: {str(e)}", exc_info=True)
        flash(f'Error updating account: {str(e)}', 'danger')

    return redirect(url_for('accounts'))

@app.route('/accounts/delete/<int:id>')
def delete_account(id):
    try:
        account = Account.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()

        # Clear any cached report data from the session to ensure fresh data
        if 'latest_upload_results' in session:
            session.pop('latest_upload_results')
        if 'latest_upload_snapshots' in session:
            session.pop('latest_upload_snapshots')

        flash('Account deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting account {id}: {str(e)}")
        flash(f'Error deleting account: {str(e)}', 'danger')

    return redirect(url_for('accounts'))

@app.route('/banks')
def banks():
    banks = Bank.query.all()
    return render_template('banks.html', banks=banks)

@app.route('/banks/add', methods=['POST'])
def add_bank():
    try:
        bank_name = request.form['bank_name']
        frn = request.form['frn']

        new_bank = Bank(bank_name=bank_name, frn=frn)
        db.session.add(new_bank)
        db.session.commit()

        # Clear any cached report data from the session to ensure fresh data
        if 'latest_upload_results' in session:
            session.pop('latest_upload_results')
        if 'latest_upload_snapshots' in session:
            session.pop('latest_upload_snapshots')

        flash('Bank added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding bank: {str(e)}")
        flash(f'Error adding bank: {str(e)}', 'danger')

    return redirect(url_for('banks'))

@app.route('/banks/edit/<int:id>', methods=['POST'])
def edit_bank(id):
    try:
        bank = Bank.query.get_or_404(id)

        bank.bank_name = request.form['bank_name']
        bank.frn = request.form['frn']

        db.session.commit()

        # Clear any cached report data from the session to ensure fresh data
        if 'latest_upload_results' in session:
            session.pop('latest_upload_results')
        if 'latest_upload_snapshots' in session:
            session.pop('latest_upload_snapshots')

        flash('Bank updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating bank {id}: {str(e)}")
        flash(f'Error updating bank: {str(e)}', 'danger')

    return redirect(url_for('banks'))

@app.route('/banks/delete/<int:id>')
def delete_bank(id):
    try:
        bank = Bank.query.get_or_404(id)

        # Check if any accounts are associated with this bank
        if Account.query.filter_by(bank_id=id).first():
            flash('Cannot delete bank with associated accounts!', 'danger')
            return redirect(url_for('banks'))

        db.session.delete(bank)
        db.session.commit()

        # Clear any cached report data from the session to ensure fresh data
        if 'latest_upload_results' in session:
            session.pop('latest_upload_results')
        if 'latest_upload_snapshots' in session:
            session.pop('latest_upload_snapshots')

        flash('Bank deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting bank {id}: {str(e)}")
        flash(f'Error deleting bank: {str(e)}', 'danger')

    return redirect(url_for('banks'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Debug: Log the form data and files
        logging.debug(f"Form data: {request.form}")
        logging.debug(f"Files: {request.files}")

        if 'file' not in request.files:
            logging.error("No file part in the request")
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']
        logging.debug(f"File received: {file.filename}")

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file:
            try:
                # Process CSV file
                logging.debug("Reading CSV file")
                df = pd.read_csv(file)
                logging.debug(f"CSV data: {df.head()}")

                # Validate columns
                required_columns = ['Account', 'bal']
                if not all(col in df.columns for col in required_columns):
                    flash('CSV file must contain Account and bal columns', 'danger')
                    return redirect(request.url)

                # Track before/after states
                results = {
                    'updated': 0,
                    'error': 0,
                    'not_found': 0,
                    'not_found_accounts': [],
                    'error_accounts': [],
                    'snapshots': []
                }

                # Process each row
                for _, row in df.iterrows():
                    account_number = str(row['Account']).strip()
                    try:
                        new_balance = float(row['bal'])
                        account = Account.query.filter_by(account_number=account_number).first()

                        if account:
                            # Create snapshot
                            snapshot = {
                                'account_number': account_number,
                                'account_name': account.account_name,
                                'bank_name': account.bank_name,
                                'previous_balance': account.balance,
                                'new_balance': new_balance,
                                'change': new_balance - account.balance
                            }
                            results['snapshots'].append(snapshot)

                            # Log the transaction
                            log = TransactionLog(
                                account_id=account.id,
                                previous_balance=account.balance,
                                new_balance=new_balance,
                                change_amount=new_balance - account.balance,
                                source="CSV upload"
                            )
                            db.session.add(log)

                            # Update the account balance
                            account.balance = new_balance
                            account.updated_at = datetime.utcnow()

                            results['updated'] += 1
                            logging.debug(f"Updated account {account_number}: balance {account.balance} -> {new_balance}")
                        else:
                            results['not_found'] += 1
                            results['not_found_accounts'].append(account_number)
                            logging.debug(f"Account not found: {account_number}")
                    except Exception as e:
                        error_info = {'account': account_number, 'error': str(e)}
                        results['error_accounts'].append(error_info)
                        results['error'] += 1
                        logging.error(f"Error processing account {account_number}: {str(e)}")

                db.session.commit()

                flash(f"Updated {results['updated']} accounts. {results['not_found']} not found. {results['error']} errors.", 'info')

                # Store results in session for report view
                session['latest_upload_results'] = {
                    'updated': results['updated'],
                    'not_found': results['not_found'],
                    'error': results['error'],
                    'not_found_accounts': results['not_found_accounts'],
                    'error_accounts': results['error_accounts']
                }

                # Store snapshots in session for report view
                session_snapshots = [
                    {
                        'account_number': s['account_number'],
                        'account_name': s['account_name'],
                        'bank_name': s['bank_name'],
                        'before': {
                            'balance': s['previous_balance']
                        },
                        'after': {
                            'balance': s['new_balance'],
                            'change': s['change']
                        }
                    }
                    for s in results['snapshots']
                ]

                session['latest_upload_snapshots'] = session_snapshots

                return redirect(url_for('reports'))

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')
                logging.error(f"Upload error: {str(e)}")
                return redirect(request.url)

    return render_template('upload.html')

@app.route('/reports')
def reports():
    logging.debug("Generating reports with timestamp query param: " + str(request.args.get('_', 'none')))

    try:
        # Force a clean slate for database queries - make sure we don't have stale data
        db.session.close()
        db.session.expire_all()

        # Create a completely fresh engine connection for this request
        with app.app_context():
            logging.debug("Explicitly refreshing database session")

            # Get accounts maturing soon (within 30 days)
            thirty_days_future = datetime.utcnow().date() + timedelta(days=30)

            # Use direct SQL for reliable results
            maturing_sql = sa.text('''
            SELECT * FROM accounts
            WHERE end_date <= :future_date
            AND end_date >= :today
            ORDER BY end_date
            ''')

            maturing_result = db.session.execute(
                maturing_sql,
                {'future_date': thirty_days_future, 'today': datetime.utcnow().date()}
            )

            # Convert to list of dictionaries
            maturing_accounts = []
            for row in maturing_result:
                # Convert SQLAlchemy row to dict
                account_dict = dict(row._mapping)
                # Create an object that mimics the ORM object
                account = type('Account', (), account_dict)
                maturing_accounts.append(account)

            # Get account balances by FRN using direct SQL
            frn_balances_sql = sa.text('''
            SELECT b.frn, SUM(a.balance) as total_balance
            FROM banks b
            JOIN accounts a ON a.bank_id = b.id
            GROUP BY b.frn
            ''')

            frn_balances_result = db.session.execute(frn_balances_sql)
            frn_balances = [(row[0], row[1]) for row in frn_balances_result]
            logging.debug(f"FRN Balances (direct SQL): {frn_balances}")

            # Get account balances by owner
            owner_balances_sql = sa.text('''
            SELECT owner, SUM(balance) as total_balance
            FROM accounts
            GROUP BY owner
            ''')

            owner_balances_result = db.session.execute(owner_balances_sql)
            owner_balances = [(row[0], row[1]) for row in owner_balances_result]
            logging.debug(f"Owner Balances (direct SQL): {owner_balances}")

            # Get accounts by FRN and owner for the grouped report
            # Using direct SQL for most reliable results
            grouped_sql = sa.text('''
            SELECT b.frn, a.owner,
                   COUNT(a.id) as account_count,
                   SUM(a.balance) as total_balance
            FROM banks b
            JOIN accounts a ON a.bank_id = b.id
            GROUP BY b.frn, a.owner
            ORDER BY b.frn, a.owner
            ''')

            # Execute with the current session connection
            grouped_result = db.session.execute(grouped_sql)

            # Process the results
            accounts_by_frn_owner = []
            for row in grouped_result:
                accounts_by_frn_owner.append({
                    'frn': row[0],
                    'owner': row[1],
                    'account_count': row[2],
                    'total_balance': row[3]
                })

            logging.debug(f"Accounts by FRN and Owner (direct SQL): {accounts_by_frn_owner}")

            # Get latest snapshots from session or create empty list
            latest_upload = session.get('latest_upload_results', {})
            account_snapshots = session.get('latest_upload_snapshots', [])

            # Create a Flask response with cache control headers
            response = make_response(render_template('reports.html',
                                  maturing_accounts=maturing_accounts,
                                  frn_balances=frn_balances,
                                  owner_balances=owner_balances,
                                  accounts_by_frn_owner=accounts_by_frn_owner,
                                  csv_results=latest_upload,
                                  account_snapshots=account_snapshots))

            # Set cache control headers to prevent browser caching
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response

    except Exception as e:
        # Log the full error with traceback for debugging
        logging.error(f"Error generating reports: {str(e)}", exc_info=True)
        # Return a friendly error page
        return render_template('error.html', error=str(e)), 500

@app.route('/api/frn-owner-data')
def frn_owner_data():
    """API endpoint specifically for getting the accounts grouped by FRN and owner."""
    timestamp = request.args.get('_', 'none')
    logging.debug(f"Generating FRN-Owner data with timestamp: {timestamp}")

    try:
        # Create a completely new session to bypass any caching
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Get a brand new connection from the database URL
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"],
                             pool_pre_ping=True,
                             echo=True)
        Session = sessionmaker(bind=engine)
        fresh_session = Session()

        # Direct SQL query with the fresh session
        query = sa.text('''
        SELECT
            b.frn,
            a.owner,
            COUNT(a.id) as account_count,
            SUM(a.balance) as total_balance
        FROM banks b
        JOIN accounts a ON a.bank_id = b.id
        GROUP BY b.frn, a.owner
        ORDER BY b.frn, a.owner
        ''')

        result = fresh_session.execute(query)

        # Process the results
        accounts_by_frn_owner = []
        for row in result:
            accounts_by_frn_owner.append({
                'frn': row[0],
                'owner': row[1],
                'account_count': row[2],
                'total_balance': row[3]
            })

        # Close the fresh session
        fresh_session.close()

        logging.debug(f"API FRN-Owner data: {accounts_by_frn_owner}")

        # Return with aggressive no-cache headers
        response = jsonify({'accounts_by_frn_owner': accounts_by_frn_owner})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Timestamp'] = str(timestamp)  # Echo timestamp to confirm fresh response
        return response

    except Exception as e:
        logging.error(f"Error generating FRN-Owner data: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'accounts_by_frn_owner': []
        }), 500

@app.route('/api/chart-data')
def chart_data():
    logging.debug("Generating chart data")

    try:
        # Force a clean slate for database queries
        db.session.close()  # Close the session
        db.session.expire_all()  # Expire all objects

        # Account type distribution - using direct SQL for reliability
        query1 = sa.text('''
        SELECT account_type, COUNT(id) as count
        FROM accounts
        GROUP BY account_type
        ''')
        result1 = db.session.execute(query1)

        labels = []
        values = []
        for row in result1:
            labels.append(row[0])
            values.append(row[1])

        account_type_data = {
            'labels': labels,
            'values': values
        }
        logging.debug(f"Account types (fresh SQL): {account_type_data}")

        # Owner distribution
        query2 = sa.text('''
        SELECT owner, COUNT(id) as count
        FROM accounts
        GROUP BY owner
        ''')
        result2 = db.session.execute(query2)

        labels = []
        values = []
        for row in result2:
            labels.append(row[0])
            values.append(row[1])

        owner_data = {
            'labels': labels,
            'values': values
        }
        logging.debug(f"Owners (fresh SQL): {owner_data}")

        # FRN distribution
        query3 = sa.text('''
        SELECT b.frn, COUNT(a.id) as count
        FROM banks b
        JOIN accounts a ON a.bank_id = b.id
        GROUP BY b.frn
        ''')
        result3 = db.session.execute(query3)

        labels = []
        values = []
        for row in result3:
            labels.append(row[0] if row[0] else 'Unknown')
            values.append(row[1])

        frn_data = {
            'labels': labels,
            'values': values
        }
        logging.debug(f"FRNs (fresh SQL): {frn_data}")

        # Set cache control headers
        response = jsonify({
            'account_types': account_type_data,
            'owners': owner_data,
            'frns': frn_data
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    except Exception as e:
        # Log the full error with traceback for debugging
        logging.error(f"Error generating chart data: {str(e)}", exc_info=True)
        # Return error as JSON
        return jsonify({
            'error': str(e),
            'account_types': {'labels': [], 'values': []},
            'owners': {'labels': [], 'values': []},
            'frns': {'labels': [], 'values': []}
        }), 500

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

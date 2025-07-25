# Install necessary libraries if running in an environment like Google Colab
# If you are running this locally and have these installed, you can comment these lines out.
import subprocess
import sys

def install_packages():
    required_packages = ['streamlit', 'pandas', 'altair']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            # Use --break-system-packages for environments like Colab if needed
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])
            print(f"{package} installed successfully.")

# Call the installation function at the very beginning
install_packages()

import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import hashlib # For password hashing
import altair as alt # For charts

# --- App Config ---
st.set_page_config(page_title="MyKhata Modern", layout="wide")

# --- Custom CSS for Mobile Optimization and Styling ---
st.markdown("""
    <style>
    /* Hide Streamlit branding and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* General body styling for mobile */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #f0f2f6;
        margin: 0;
        padding: 0;
    }

    /* Streamlit specific elements adjustments */
    .stApp {
        padding-bottom: 80px; /* Space for bottom nav */
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Custom Card Styling */
    .stCard {
        background-color: #e3f2fd; /* Light blue */
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 15px;
        border: none;
    }
    .stCard > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .stCard h3 {
        color: #1976D2; /* Darker blue for headings */
        margin-bottom: 5px;
    }
    .stCard p {
        font-size: 1.5em;
        font-weight: bold;
        color: #424242;
    }

    /* Dashboard Main Balance Card - New Styling for Gradient and Layout */
    .main-balance-card {
        background: linear-gradient(135deg, #6a82fb, #fc5c7d); /* Gradient as in image */
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        padding: 25px;
        margin-bottom: 25px;
        color: white;
        text-align: center;
    }
    .main-balance-card h4 {
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 5px;
        font-weight: normal;
    }
    .main-balance-card .balance-amount {
        font-size: 2.8em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .main-balance-card .income-expense-row {
        display: flex;
        justify-content: space-around;
        width: 100%;
        margin-top: 15px;
    }
    .main-balance-card .income-expense-item {
        display: flex;
        align-items: center;
        font-size: 1.1em;
        font-weight: 600;
    }
    .main-balance-card .income-expense-item .icon {
        font-size: 1.5em;
        margin-right: 8px;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .main-balance-card .income-expense-item .income-icon {
        background-color: rgba(76, 175, 80, 0.3); /* Green with transparency */
        color: #4CAF50;
    }
    .main-balance-card .income-expense-item .expense-icon {
        background-color: rgba(244, 67, 54, 0.3); /* Red with transparency */
        color: #F44336;
    }
    .main-balance-card .income-expense-item .amount {
        color: white;
    }


    /* Transaction List Item Styling */
    .transaction-item {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        padding: 15px 20px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .transaction-item .icon-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #e3f2fd; /* Light blue background for icon */
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        margin-right: 15px;
    }
    .transaction-item .details {
        flex-grow: 1;
    }
    .transaction-item .category-name {
        font-weight: bold;
        font-size: 1.1em;
        color: #333;
    }
    .transaction-item .note-date {
        font-size: 0.85em;
        color: #777;
    }
    .transaction-item .amount-display {
        font-weight: bold;
        font-size: 1.2em;
        margin-left: 10px;
        text-align: right;
    }
    .transaction-item .amount-income {
        color: #4CAF50; /* Green */
    }
    .transaction-item .amount-expense {
        color: #F44336; /* Red */
    }
    .transaction-item .amount-loan {
        color: #FFC107; /* Amber */
    }
    .transaction-item .amount-emi {
        color: #2196F3; /* Blue */
    }

    /* Top bar for dashboard (non-functional, visual only) */
    .top-bar-placeholder {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        font-size: 0.9em;
        color: #555;
    }
    .top-bar-placeholder .time {
        font-weight: bold;
    }
    .top-bar-placeholder .status-icons span {
        margin-left: 8px;
    }

    /* Header for sections like "Transaction" with filter icon */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .section-header h3 {
        margin: 0;
        color: #333;
    }
    /* Removed filter-icon styling as it's removed from HTML */


    /* Bottom Navigation Bar Styling */
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: #e3f2fd; /* Light blue */
        padding: 8px 0;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }
    .nav-button-container {
        display: flex;
        justify-content: space-around;
        width: 100%;
    }
    .nav-button-wrapper {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .nav-button-wrapper button {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        color: #555 !important;
        font-size: 0.8em !important;
        font-weight: 600 !important;
        transition: color 0.3s ease !important;
        height: auto !important;
        width: auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        cursor: pointer !important;
    }
    .nav-button-wrapper button:hover {
        color: #2196F3 !important;
    }
    .nav-button-wrapper button > div { /* Target the inner div containing icon and text */
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .nav-button-wrapper button .icon {
        font-size: 24px !important;
        margin-bottom: 3px !important;
    }
    .nav-button-wrapper button.active-nav-item {
        color: #2196F3 !important; /* Active state color */
    }

    .plus-btn-wrapper {
        flex: 0 0 auto; /* Don't grow or shrink */
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: -30px; /* Pull up to float */
        z-index: 1001; /* Ensure it's above other nav items */
    }
    .plus-btn-wrapper button {
        font-size: 32px !important; /* Larger plus icon */
        color: white !important;
        background: #2196F3 !important; /* Bright blue for add button */
        border-radius: 50% !important;
        width: 60px !important; /* Larger circle */
        height: 60px !important;
        line-height: 60px !important;
        text-align: center !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
        transition: background 0.3s ease !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    .plus-btn-wrapper button:hover {
        background: #1976D2 !important;
    }


    /* Hide hamburger menu (sidebar toggle) */
    .css-1lcbmhc {
        visibility: hidden;
    }

    /* Adjust Streamlit columns for mobile responsiveness */
    div[data-testid="stVerticalBlock"] > div {
        gap: 1rem; /* Adjust vertical spacing */
    }
    div[data-testid="stHorizontalBlock"] > div {
        gap: 1rem; /* Adjust horizontal spacing */
    }

    /* Chart specific styling */
    .stPlotlyChart {
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 10px;
        background-color: white;
    }

    /* Form input styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stDateInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }
    .stButton>button {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }

    /* Message box styling */
    .st-emotion-cache-1c7y2kd { /* This class might change, but targets success/error messages */
        border-radius: 8px;
    }

    /* Profile Page image upload */
    .stFileUploader {
        border: 2px dashed #2196F3;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #e3f2fd;
    }
    </style>
""", unsafe_allow_html=True)


# --- Session State Setup ---
for key in ["logged_in", "username", "user_role", "parent_username", "show_signup", "account_created", "active_page", "current_user_data", "transaction_df", "category_df"]:
    if key not in st.session_state:
        if key == "logged_in": st.session_state[key] = False
        elif key == "show_signup": st.session_state[key] = False
        elif key == "account_created": st.session_state[key] = False
        elif key == "active_page": st.session_state[key] = "Home"
        elif key == "user_role": st.session_state[key] = "Main" # Default role
        else: st.session_state[key] = None

# --- File Paths ---
DATA_FILE = "mykhata_data.csv"
USERS_FILE = "users_public_details.csv"
CATEGORY_FILE = "category_memory.csv"

# --- Utility Functions ---

def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Loads user data from CSV or creates an empty DataFrame."""
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        # Added 'ParentUsername' column for sub-users
        df = pd.DataFrame(columns=["Username", "PasswordHash", "Name", "Mobile", "Email", "Role", "ParentUsername"])
        df.to_csv(USERS_FILE, index=False)
        return df

def save_users(df):
    """Saves user data to CSV."""
    df.to_csv(USERS_FILE, index=False)

def load_transactions(effective_username):
    """Loads transaction data for a specific effective_username or creates an empty DataFrame."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Ensure 'Username' column exists and filter by effective_username
        if 'Username' not in df.columns:
            df['Username'] = '' # Add it if missing
        return df[df['Username'] == effective_username].copy()
    else:
        df = pd.DataFrame(columns=["Username", "Date", "Type", "Category", "Amount", "Note"])
        df.to_csv(DATA_FILE, index=False)
        return df[df['Username'] == effective_username].copy()

def save_transaction(effective_username, date, trans_type, category, amount, note):
    """Saves a single transaction to the main data file."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Username", "Date", "Type", "Category", "Amount", "Note"])
        df.to_csv(DATA_FILE, index=False)

    df = pd.read_csv(DATA_FILE)
    new_transaction = pd.DataFrame([{
        "Username": effective_username,
        "Date": date.strftime('%Y-%m-%d'),
        "Type": trans_type,
        "Category": category,
        "Amount": amount,
        "Note": note
    }])
    df = pd.concat([df, new_transaction], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.session_state.transaction_df = load_transactions(effective_username) # Refresh session state data

def load_categories(username):
    """Loads custom categories for a user or creates an empty DataFrame."""
    if os.path.exists(CATEGORY_FILE):
        df = pd.read_csv(CATEGORY_FILE)
        # Filter categories specific to the user or global (if any)
        return df[df['Username'] == username].copy()
    else:
        df = pd.DataFrame(columns=["Username", "CategoryType", "CategoryName"])
        df.to_csv(CATEGORY_FILE, index=False)
        return df[df['Username'] == username].copy()

def save_category(username, category_type, category_name):
    """Saves a custom category for a user."""
    if not os.path.exists(CATEGORY_FILE):
        df = pd.DataFrame(columns=["Username", "CategoryType", "CategoryName"])
        df.to_csv(CATEGORY_FILE, index=False)

    df = pd.read_csv(CATEGORY_FILE) # Read from CATEGORY_FILE to check existing categories
    if not ((df['Username'] == username) & (df['CategoryName'] == category_name)).any():
        new_category = pd.DataFrame([{
            "Username": username,
            "CategoryType": category_type,
            "CategoryName": category_name
        }])
        df = pd.concat([df, new_category], ignore_index=True)
        df.to_csv(CATEGORY_FILE, index=False)
        st.session_state.category_df = load_categories(username) # Refresh session state data

# --- Authentication Pages ---

def login_page():
    st.markdown("<h2 style='text-align: center; color: #1976D2;'>🎉 Welcome to MyKhata – Manage your money smartly.</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            create_account_button = st.form_submit_button("Create a new account")

    if login_button:
        users = load_users()
        hashed_password = hash_password(password)
        match = users[(users["Username"] == username) & (users["PasswordHash"] == hashed_password)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = match.iloc[0]["Role"]
            st.session_state.parent_username = match.iloc[0]["ParentUsername"] if pd.notna(match.iloc[0]["ParentUsername"]) else None
            
            # Determine the effective username for data storage
            st.session_state.effective_username = st.session_state.parent_username if st.session_state.user_role == "Sub" else st.session_state.username
            
            st.session_state.transaction_df = load_transactions(st.session_state.effective_username)
            st.session_state.category_df = load_categories(st.session_state.username) # Categories are per actual user
            st.success("✅ Login Successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

    if create_account_button:
        st.session_state.show_signup = True
        st.experimental_rerun()

def signup_page():
    st.markdown("<h2 style='text-align: center; color: #1976D2;'>📝 Create New Account</h2>", unsafe_allow_html=True)

    with st.form("signup_form"):
        name = st.text_input("Your Name")
        username = st.text_input("Username (Starts with uppercase, alphanumeric)")
        password = st.text_input("Password (Starts with uppercase, alphanumeric, includes a symbol)", type="password")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email Address")
        
        col1, col2 = st.columns(2)
        with col1:
            create_account_button = st.form_submit_button("Create Account")
        with col2:
            back_to_login_button = st.form_submit_button("Back to Login")

    if create_account_button:
        # Username validation
        if not re.match(r"^[A-Z][A-Za-z0-9]+$", username):
            st.error("Username must start with an uppercase letter and contain only alphanumeric characters.")
            return
        # Password validation
        if not re.match(r"^[A-Z](?=.*[!@#$%^&*()_+={}\[\]:;<>,.?/~`-])[A-Za-z0-9!@#$%^&*()_+={}\[\]:;<>,.?/~`-]*$", password):
            st.error("Password must start with an uppercase letter and include at least one special character.")
            return

        users = load_users()
        if username in users["Username"].values:
            st.error("Username already exists. Please choose a different one.")
        else:
            hashed_password = hash_password(password)
            new_user = pd.DataFrame([[username, hashed_password, name, mobile, email, "Main", None]],
                                    columns=["Username", "PasswordHash", "Name", "Mobile", "Email", "Role", "ParentUsername"])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("Account created successfully! Please log in.")
            st.session_state.show_signup = False
            st.session_state.account_created = True # Indicate successful creation for login page
            st.experimental_rerun()
    
    if back_to_login_button:
        st.session_state.show_signup = False
        st.experimental_rerun()

# --- Navigation Bar ---
def bottom_navbar():
    # Use st.columns for horizontal layout of buttons
    st.markdown('<div class="bottom-bar">', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1, 1, 1]) # 5 columns for 5 buttons

    nav_items = [
        ("Home", "🏠"),
        ("Wallet", "📈"),
        ("Add", "+"), # Plus button is special
        ("Report", "📊"),
        ("Profile", "👤")
    ]

    for i, (page, icon) in enumerate(nav_items):
        with cols[i]:
            if page == "Add":
                # Special styling for the Add button
                if st.button(icon, key=f"nav_btn_{page}", help=page):
                    st.session_state.active_page = page
                    st.experimental_rerun()
                # Applying CSS for the plus button
                st.markdown(f"""
                    <style>
                        div[data-testid="stColumn"]:nth-child({i+1}) button[data-testid="stButton"] {{
                            font-size: 32px !important;
                            color: white !important;
                            background: #2196F3 !important;
                            border-radius: 50% !important;
                            width: 60px !important;
                            height: 60px !important;
                            line-height: 60px !important;
                            text-align: center !important;
                            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
                            transition: background 0.3s ease !important;
                            display: flex !important;
                            justify-content: center !important;
                            align-items: center !important;
                            margin-top: -30px !important; /* Pull up to float */
                        }}
                        div[data-testid="stColumn"]:nth-child({i+1}) button[data-testid="stButton"]:hover {{
                            background: #1976D2 !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)
            else:
                # Regular navigation buttons
                # The text and icon are passed together in the button label
                # The active state is handled by setting the color dynamically in the CSS
                if st.button(f"<span class='icon'>{icon}</span> {page}", key=f"nav_btn_{page}", help=page, unsafe_allow_html=True):
                    st.session_state.active_page = page
                    st.experimental_rerun()
                
                # Apply CSS for the regular nav items
                st.markdown(f"""
                    <style>
                        div[data-testid="stColumn"]:nth-child({i+1}) button {{
                            background: none !important;
                            border: none !important;
                            padding: 0 !important;
                            margin: 0 !important;
                            box-shadow: none !important;
                            color: {'#2196F3' if st.session_state.active_page == page else '#555'} !important; /* Dynamic color based on active_page */
                            font-size: 0.8em !important;
                            font-weight: 600 !important;
                            transition: color 0.3s ease !important;
                            height: auto !important;
                            width: auto !important;
                            display: flex !important;
                            flex-direction: column !important;
                            align-items: center !important;
                            cursor: pointer !important;
                        }}
                        div[data-testid="stColumn"]:nth-child({i+1}) button:hover {{
                            color: #2196F3 !important;
                        }}
                        div[data-testid="stColumn"]:nth-child({i+1}) button > div {{ /* Target the inner div containing icon and text */
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                        }}
                        div[data-testid="stColumn"]:nth-child({i+1}) button .icon {{
                            font-size: 24px !important;
                            margin-bottom: 3px !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# --- Pages ---

def dashboard():
    # Top bar placeholder (non-functional, for visual resemblance)
    st.markdown("""
    <div class="top-bar-placeholder">
        <span class="time">09:00</span>
        <div class="status-icons">
            <span>📶</span><span>🔋</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div style="display: flex; align-items: center;">
            <img src="https://placehold.co/60x60/e0e0e0/ffffff?text=👨‍💻" style="border-radius: 50%; margin-right: 15px;">
            <h2 style='color: #333; margin: 0;'>Hello, {st.session_state.username}!</h2>
        </div>
        <div style="font-size: 28px; cursor: pointer; color: #555;">🔔</div>
    </div>
    """, unsafe_allow_html=True)


    effective_username = st.session_state.effective_username
    user_transactions = st.session_state.transaction_df
    
    if user_transactions.empty:
        total_balance = 0
        total_income = 0
        total_expense = 0
    else:
        # Ensure 'Amount' column is numeric
        user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce').fillna(0)

        total_income = user_transactions[user_transactions['Type'] == 'Income']['Amount'].sum()
        total_expense = user_transactions[user_transactions['Type'] == 'Expense']['Amount'].sum()
        total_loans_taken = user_transactions[user_transactions['Type'] == 'Loan']['Amount'].sum()
        total_emi_paid = user_transactions[user_transactions['Type'] == 'EMI']['Amount'].sum()
        
        total_balance = total_income - total_expense - total_emi_paid + total_loans_taken
    
    # Main Balance Card
    st.markdown(f"""
    <div class="main-balance-card">
        <h4>Total Balance</h4>
        <div class="balance-amount">₹ {total_balance:,.2f}</div>
        <div class="income-expense-row">
            <div class="income-expense-item">
                <span class="icon income-icon">⬇️</span>
                <div>
                    <div style="font-size: 0.9em; color: rgba(255, 255, 255, 0.8);">Income</div>
                    <div class="amount">₹ {total_income:,.2f}</div>
                </div>
            </div>
            <div class="income-expense-item">
                <span class="icon expense-icon">⬆️</span>
                <div>
                    <div style="font-size: 0.9em; color: rgba(255, 255, 255, 0.8);">Expense</div>
                    <div class="amount">₹ {total_expense:,.2f}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header">
        <h3>Transaction</h3>
    </div>
    """, unsafe_allow_html=True) # Removed filter icon as it was not functional

    if not user_transactions.empty:
        # Sort by date descending for latest transactions first
        display_transactions = user_transactions.sort_values(by='Date', ascending=False)

        # Basic icon mapping for categories (can be expanded)
        category_icons = {
            "Food": "🍔", "Transport": "🚗", "Rent": "🏠", "Utilities": "💡",
            "Shopping": "🛍️", "Entertainment": "🎬", "Health": "🏥", "Education": "📚",
            "Salary": "💰", "Freelance": "💼", "Investment": "📈", "Gift": "🎁",
            "Personal Loan": "💳", "Home Loan": "🏡", "Car Loan": "🚗", "Student Loan": "🎓",
            "Loan Repayment": "💸", "Credit Card Bill": "💳",
            "Other Income": "➕", "Other Expense": "➖", "Other Loan": "🤝", "Other EMI": "🔄"
        }

        for index, row in display_transactions.iterrows():
            icon = category_icons.get(row['Category'], "📝") # Default icon
            amount_class = ""
            if row['Type'] == 'Income':
                amount_class = "amount-income"
            elif row['Type'] == 'Expense':
                amount_class = "amount-expense"
            elif row['Type'] == 'Loan':
                amount_class = "amount-loan"
            elif row['Type'] == 'EMI':
                amount_class = "amount-emi"

            st.markdown(f"""
            <div class="transaction-item">
                <div class="icon-circle">{icon}</div>
                <div class="details">
                    <div class="category-name">{row['Category']}</div>
                    <div class="note-date">{pd.to_datetime(row['Date']).strftime('%d %b')} - {row['Note']}</div>
                </div>
                <div class="amount-display {amount_class}">
                    ₹ {row['Amount']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No transactions to display.")


def add_transaction():
    st.markdown("<h2 style='color: #1976D2;'>➕ Add Transaction</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    current_username = st.session_state.username # For category management

    # Load categories for the current user
    user_categories_df = st.session_state.category_df
    
    # Default categories
    default_income_categories = ["Salary", "Freelance", "Investment", "Gift", "Other Income"]
    default_expense_categories = ["Food", "Transport", "Rent", "Utilities", "Shopping", "Entertainment", "Health", "Education", "Other Expense"]
    default_loan_categories = ["Personal Loan", "Home Loan", "Car Loan", "Student Loan", "Other Loan"]
    default_emi_categories = ["Loan Repayment", "Credit Card Bill", "Other EMI"]

    # Combine default and user-defined categories
    all_income_categories = sorted(list(set(default_income_categories + user_categories_df[user_categories_df['CategoryType'] == 'Income']['CategoryName'].tolist())))
    all_expense_categories = sorted(list(set(default_expense_categories + user_categories_df[user_categories_df['CategoryType'] == 'Expense']['CategoryName'].tolist())))
    all_loan_categories = sorted(list(set(default_loan_categories + user_categories_df[user_categories_df['CategoryType'] == 'Loan']['CategoryName'].tolist())))
    all_emi_categories = sorted(list(set(default_emi_categories + user_categories_df[user_categories_df['CategoryType'] == 'EMI']['CategoryName'].tolist())))

    with st.form("transaction_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now().date())
        trans_type = st.selectbox("Type", ["Expense", "Income", "Loan", "EMI"], key="trans_type")

        category_options = []
        if trans_type == "Income":
            category_options = all_income_categories
        elif trans_type == "Expense":
            category_options = all_expense_categories
        elif trans_type == "Loan":
            category_options = all_loan_categories
        elif trans_type == "EMI":
            category_options = all_emi_categories
        
        # Add a "Add New Category" option
        category_options.append("➕ Add New Category...")
        
        category = st.selectbox("Category", category_options, key="category_select")

        new_category_name = ""
        if category == "➕ Add New Category...":
            new_category_name = st.text_input("Enter New Category Name", key="new_category_input")
            if new_category_name:
                # Save new category to memory
                save_category(current_username, trans_type, new_category_name)
                category = new_category_name # Use the new category for the current transaction
                st.success(f"Category '{new_category_name}' added!")
                # Re-run to update category dropdown with new option
                st.experimental_rerun()
            else:
                st.warning("Please enter a name for the new category.")
                st.stop() # Stop execution if new category is selected but not named

        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        note = st.text_area("Note (Optional)", max_chars=200)

        submitted = st.form_submit_button("Save Transaction")

        if submitted:
            if not category or category == "➕ Add New Category...":
                st.error("Please select or add a category.")
            elif amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                save_transaction(effective_username, date, trans_type, category, amount, note)
                st.success("✅ Transaction saved successfully!")
                # No explicit rerun here, form clear_on_submit handles it

def wallet():
    st.markdown("<h2 style='color: #1976D2;'>💼 Wallet Overview</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    user_transactions = st.session_state.transaction_df

    if user_transactions.empty:
        st.info("No transactions recorded yet to display wallet overview.")
        total_balance = 0
        total_income = 0
        total_expense = 0
        net_loans = 0
    else:
        user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce').fillna(0)

        total_income = user_transactions[user_transactions['Type'] == 'Income']['Amount'].sum()
        total_expense = user_transactions[user_transactions['Type'] == 'Expense']['Amount'].sum()
        total_loans_taken = user_transactions[user_transactions['Type'] == 'Loan']['Amount'].sum()
        total_emi_paid = user_transactions[user_transactions['Type'] == 'EMI']['Amount'].sum()
        
        total_balance = total_income - total_expense - total_emi_paid + total_loans_taken
        net_loans = total_loans_taken - total_emi_paid

    # Display summary cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stCard">
            <h3>Current Balance</h3>
            <p>₹ {total_balance:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Income</h3>
            <p>₹ {total_income:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Expense</h3>
            <p>₹ {total_expense:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stCard">
            <h3>Net Loans</h3>
            <p>₹ {net_loans:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Expense Breakdown by Category")

    if not user_transactions.empty and not user_transactions[user_transactions['Type'] == 'Expense'].empty:
        expense_by_category = user_transactions[user_transactions['Type'] == 'Expense'].groupby('Category')['Amount'].sum().reset_index()
        
        chart = alt.Chart(expense_by_category).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Amount", type="quantitative"),
            color=alt.Color(field="Category", type="nominal", title="Category"),
            order=alt.Order("Amount", sort="descending"),
            tooltip=["Category", alt.Tooltip("Amount", format=",.2f")]
        ).properties(
            title="Expense Distribution"
        ).interactive()
        
        text = alt.Chart(expense_by_category).mark_text(radius=140).encode(
            theta=alt.Theta(field="Amount", type="quantitative"),
            text=alt.Text("Amount", format=",.2f"),
            order=alt.Order("Amount", sort="descending"),
            color=alt.value("black") # Set the color of the labels to black
        )
        
        st.altair_chart(chart + text, use_container_width=True)
    else:
        st.info("No expense transactions to display a breakdown.")


def report():
    st.markdown("<h2 style='color: #1976D2;'>📊 Reports</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    user_transactions = st.session_state.transaction_df

    if user_transactions.empty:
        st.info("No transactions to generate reports.")
        return

    user_transactions['Date'] = pd.to_datetime(user_transactions['Date'])
    user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce').fillna(0)

    report_type = st.selectbox("Select Report Type:", ["Income vs. Expense", "Category Spending", "Loan/EMI Trends"], key="report_type_select")
    time_filter = st.selectbox("Filter by:", ["Daily", "Monthly", "Yearly"], key="report_time_filter")

    # Determine grouping period
    if time_filter == "Daily":
        period_format = '%Y-%m-%d'
        period_title = 'Date'
        group_by_period = user_transactions['Date'].dt.date
    elif time_filter == "Monthly":
        period_format = '%Y-%m'
        period_title = 'Month'
        group_by_period = user_transactions['Date'].dt.to_period('M')
    else: # Yearly
        period_format = '%Y'
        period_title = 'Year'
        group_by_period = user_transactions['Date'].dt.to_period('Y')

    if report_type == "Income vs. Expense":
        st.subheader("Income vs. Expense Over Time")
        income_data = user_transactions[user_transactions['Type'] == 'Income'].groupby(group_by_period)['Amount'].sum().reset_index()
        expense_data = user_transactions[user_transactions['Type'] == 'Expense'].groupby(group_by_period)['Amount'].sum().reset_index()

        income_data['Type'] = 'Income'
        expense_data['Type'] = 'Expense'

        # Rename the period column for Altair
        income_data.rename(columns={income_data.columns[0]: 'Period'}, inplace=True)
        expense_data.rename(columns={expense_data.columns[0]: 'Period'}, inplace=True)

        combined_data = pd.concat([income_data, expense_data])
        
        if not combined_data.empty:
            # Convert Period to timestamp for Altair
            combined_data['Period'] = combined_data['Period'].astype(str).apply(lambda x: datetime.strptime(x, period_format))

            chart = alt.Chart(combined_data).mark_line(point=True).encode(
                x=alt.X('Period', axis=alt.Axis(format=period_format, title=period_title)),
                y=alt.Y('Amount', title='Amount (₹)'),
                color=alt.Color('Type', legend=alt.Legend(title="Transaction Type")),
                tooltip=[alt.Tooltip('Period', format=period_format), 'Type', alt.Tooltip('Amount', format=",.2f")]
            ).properties(
                title=f'Income vs. Expense ({time_filter})'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No income or expense data for this period.")

    elif report_type == "Category Spending":
        st.subheader("Spending by Category Over Time")
        expense_data = user_transactions[user_transactions['Type'] == 'Expense'].copy()
        
        if not expense_data.empty:
            expense_data['Period'] = group_by_period.astype(str) # Convert to string for grouping
            
            # Group by Period and Category
            grouped_expense = expense_data.groupby(['Period', 'Category'])['Amount'].sum().reset_index()
            
            # Convert Period back to datetime for Altair
            grouped_expense['Period'] = grouped_expense['Period'].apply(lambda x: datetime.strptime(x, period_format))

            chart = alt.Chart(grouped_expense).mark_bar().encode(
                x=alt.X('Period', axis=alt.Axis(format=period_format, title=period_title)),
                y=alt.Y('Amount', title='Total Spending (₹)'),
                color=alt.Color('Category', title="Category"),
                tooltip=[alt.Tooltip('Period', format=period_format), 'Category', alt.Tooltip('Amount', format=",.2f")]
            ).properties(
                title=f'Spending by Category ({time_filter})'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No expense data to display category spending.")

    elif report_type == "Loan/EMI Trends":
        st.subheader("Loan and EMI Trends Over Time")
        loan_data = user_transactions[user_transactions['Type'] == 'Loan'].groupby(group_by_period)['Amount'].sum().reset_index()
        emi_data = user_transactions[user_transactions['Type'] == 'EMI'].groupby(group_by_period)['Amount'].sum().reset_index()

        loan_data['Type'] = 'Loan Taken'
        emi_data['Type'] = 'EMI Paid'

        loan_data.rename(columns={loan_data.columns[0]: 'Period'}, inplace=True)
        emi_data.rename(columns={emi_data.columns[0]: 'Period'}, inplace=True)

        combined_data = pd.concat([loan_data, emi_data])

        if not combined_data.empty:
            combined_data['Period'] = combined_data['Period'].astype(str).apply(lambda x: datetime.strptime(x, period_format))

            chart = alt.Chart(combined_data).mark_line(point=True).encode(
                x=alt.X('Period', axis=alt.Axis(format=period_format, title=period_title)),
                y=alt.Y('Amount', title='Amount (₹)'),
                color=alt.Color('Type', legend=alt.Legend(title="Transaction Type")),
                tooltip=[alt.Tooltip('Period', format=period_format), 'Type', alt.Tooltip('Amount', format=",.2f")]
            ).properties(
                title=f'Loan and EMI Trends ({time_filter})'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No loan or EMI data for this period.")


def profile():
    st.markdown("<h2 style='color: #1976D2;'>👤 Profile Settings</h2>", unsafe_allow_html=True)

    users_df = load_users()
    current_user_row = users_df[users_df['Username'] == st.session_state.username].iloc[0]

    st.subheader("Your Profile Information")
    col_img, col_details = st.columns([1, 2])
    with col_img:
        # Placeholder for profile photo upload
        st.image("https://placehold.co/150x150/e0e0e0/ffffff?text=Profile", width=150, caption="Profile Photo")
        # st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"], key="profile_photo_uploader")
        st.markdown("<small><i>(Photo upload is for display only; persistence requires backend storage)</i></small>", unsafe_allow_html=True)
    
    with col_details:
        st.write(f"**Name:** {current_user_row['Name']}")
        st.write(f"**Username:** {current_user_row['Username']}")
        st.write(f"**Mobile:** {current_user_row['Mobile']}")
        st.write(f"**Email:** {current_user_row['Email']}")
        st.write(f"**Role:** {current_user_row['Role']}")
        if current_user_row['Role'] == "Sub" and pd.notna(current_user_row['ParentUsername']):
            st.write(f"**Linked to Main Account:** {current_user_row['ParentUsername']}")

    st.markdown("---")

    if st.session_state.user_role == "Main":
        st.subheader("Add New Sub-User")
        st.info("You are a 'Main' user. You can invite sub-users to access your account.")
        with st.form("add_sub_user_form", clear_on_submit=True):
            sub_user_name = st.text_input("Sub-User's Name")
            sub_user_username = st.text_input("Sub-User's Username (Starts with uppercase, alphanumeric)")
            sub_user_password = st.text_input("Sub-User's Password (Starts with uppercase, alphanumeric, includes a symbol)", type="password")
            sub_user_mobile = st.text_input("Sub-User's Mobile Number")
            sub_user_email = st.text_input("Sub-User's Email Address")

            add_sub_user_button = st.form_submit_button("Create Sub-User Account")

            if add_sub_user_button:
                # Sub-user username validation
                if not re.match(r"^[A-Z][A-Za-z0-9]+$", sub_user_username):
                    st.error("Sub-User Username must start with an uppercase letter and contain only alphanumeric characters.")
                    return
                # Sub-user password validation
                if not re.match(r"^[A-Z](?=.*[!@#$%^&*()_+={}\[\]:;<>,.?/~`-])[A-Za-z0-9!@#$%^&*()_+={}\[\]:;<>,.?/~`-]*$", sub_user_password):
                    st.error("Sub-User Password must start with an uppercase letter and include at least one special character.")
                    return

                if sub_user_username in users_df["Username"].values:
                    st.error("Sub-User Username already exists. Please choose a different one.")
                else:
                    hashed_sub_password = hash_password(sub_user_password)
                    new_sub_user = pd.DataFrame([[sub_user_username, hashed_sub_password, sub_user_name, sub_user_mobile, sub_user_email, "Sub", st.session_state.username]],
                                                columns=["Username", "PasswordHash", "Name", "Mobile", "Email", "Role", "ParentUsername"])
                    users_df = pd.concat([users_df, new_sub_user], ignore_index=True)
                    save_users(users_df)
                    st.success(f"Sub-user '{sub_user_username}' created successfully and linked to your account!")
                    st.experimental_rerun()
    else:
        st.info(f"You are a 'Sub' user linked to '{st.session_state.parent_username}' account. Only the main user can add new sub-users.")

    st.markdown("---")
    st.subheader("Payment Reminders (Upcoming)")
    st.info("This section will display upcoming loan or EMI due dates.")
    st.markdown("<small><i>(Feature placeholder)</i></small>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.session_state.parent_username = None
        st.session_state.effective_username = ""
        st.session_state.transaction_df = pd.DataFrame() # Clear dataframes
        st.session_state.category_df = pd.DataFrame()
        st.success("You have been logged out.")
        st.experimental_rerun()

# --- Main App Logic ---
def main_app():
    # Get navigation parameter from URL query string
    nav = st.query_params.get("nav", "Home") # Default to Home if not present
    st.session_state.active_page = nav

    # Ensure data is loaded when app starts or after login
    if st.session_state.logged_in and (st.session_state.transaction_df is None or st.session_state.category_df is None or st.session_state.transaction_df.empty):
        st.session_state.effective_username = st.session_state.parent_username if st.session_state.user_role == "Sub" else st.session_state.username
        st.session_state.transaction_df = load_transactions(st.session_state.effective_username)
        st.session_state.category_df = load_categories(st.session_state.username)


    if st.session_state.active_page == "Home":
        dashboard()
    elif st.session_state.active_page == "Add":
        add_transaction()
    elif st.session_state.active_page == "Wallet":
        wallet()
    elif st.session_state.active_page == "Report":
        report()
    elif st.session_state.active_page == "Profile":
        profile()
    
    bottom_navbar()

# --- Launch App ---
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    main_app()

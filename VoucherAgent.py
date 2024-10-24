import streamlit as st
import pandas as pd
from llama_index.core.agent import ReActAgent
import ast  
import random
import pandas as pd
import ast  
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

open_ai_api_key = st.secrets["OPEN_AI"]

llm = OpenAI(api_key=open_ai_api_key,model="gpt-4o",temperature=0.2)

def add_user(name, user_id, mail, token_list=None):
    try:
        users = pd.read_csv('dummydata/users.csv')
    except FileNotFoundError:
        users = pd.DataFrame(columns=['Name', 'ID', 'mail', 'token_list'])
    
    if token_list is None:
        token_list = []
    
    token_list_str = str(token_list)
    
    new_user = pd.DataFrame({
        'Name': [name], 
        'ID': [user_id], 
        'mail': [mail], 
        'token_list': [token_list_str]
    })
    
    users = pd.concat([users, new_user], ignore_index=True)
    
    users.to_csv('dummydata/users.csv', index=False)

def add_voucher(name, conditions, status, amount, buyamount):
    try:
        vouchers = pd.read_csv('dummydata/vouchers.csv')
    except FileNotFoundError:
        vouchers = pd.DataFrame(columns=['Name', 'Conditions', 'Status', 'Amount', ' BuyAmount'])
    
    if conditions is None:
        conditions = []
    
    conditions_str = str(conditions)
    
    new_voucher = pd.DataFrame({
        'Name': [name], 
        'Conditions': [conditions_str], 
        'Status': [status], 
        'Amount': [amount],
        'BuyAmount': [buyamount]
    })
    
    vouchers = pd.concat([vouchers, new_voucher], ignore_index=True)
    
    vouchers.to_csv('dummydata/vouchers.csv', index=False)

def add_token(voucher_type):
    try:
        tokens = pd.read_csv('dummydata/tokens.csv')
    except FileNotFoundError:
        tokens = pd.DataFrame(columns=['ID', 'VoucherType'])
    flag=0
    while(flag==0):
        token_id  = random.randint(1, 1000)
        issame=0
        for tid in range(len(tokens['ID'])):
            if int(tokens['ID'][tid]) == token_id:
                print("Token ID already taken")
                issame=1
        if issame == 0:
            flag = 1
    new_token = pd.DataFrame({'ID': [token_id], 'VoucherType': [voucher_type]})
    tokens = pd.concat([tokens,new_token],ignore_index=True)
    tokens.to_csv('dummydata/tokens.csv', index=False)

def append_tokens_to_user(user_id, new_tokens):
    try:
        users = pd.read_csv('dummydata/users.csv')
        
        user_idx = users[users['ID'] == user_id].index
        
        if not user_idx.empty:
            current_tokens = ast.literal_eval(users.at[user_idx[0], 'token_list'])
            
            current_tokens.extend(new_tokens)
            
            users.at[user_idx[0], 'token_list'] = str(current_tokens)
            
            users.to_csv('dummydata/users.csv', index=False)
            print(f'Tokens added to user {user_id}')
        else:
            print(f'User with ID {user_id} not found.')
    
    except FileNotFoundError:
        print('Users CSV not found.')

def list_users():
    try:
        users = pd.read_csv('dummydata/users.csv')
        return users
    except FileNotFoundError:
        print('Users CSV not found.')
        return pd.DataFrame()

def delete_user(user_id):
    try:
        users = pd.read_csv('dummydata/users.csv')
        
        user_idx = users[users['ID'] == user_id].index
        
        if not user_idx.empty:
            users = users.drop(user_idx)
            
            users.to_csv('dummydata/users.csv', index=False)
            print(f'User {user_id} deleted.')
        else:
            print(f'User with ID {user_id} not found.')
    
    except FileNotFoundError:
        print('Users CSV not found.')

def get_user_by_id(user_id):
    """Gets the details of a user given the user ID."""
    try:
        users = pd.read_csv('dummydata/users.csv')
        user = users[users['ID'] == user_id]
        if not user.empty:
            return user.iloc[0].to_dict()
        else:
            print(f'User with ID {user_id} not found.')
            return None
    except FileNotFoundError:
        print('Users CSV not found.')
        return None

def get_feature_of_user(user_id, feature):
    try:
        users = pd.read_csv('dummydata/users.csv')
        
        if feature not in users.columns:
            print(f'Feature "{feature}" does not exist.')
            return None
        
        user = users[users['ID'] == user_id]
        
        if not user.empty:
            return user[feature].values[0]
        else:
            print(f'User with ID {user_id} not found.')
            return None
    except FileNotFoundError:
        print('Users CSV not found.')
        return None

def get_token_vouchertype(token_id):
    """Returns the voucher ID of the token given the token ID."""
    tokens_df = pd.read_csv('dummydata/tokens.csv')
    token = tokens_df.loc[tokens_df['TokenID'] == token_id]
    if not token.empty:
        vouchertype = token['VoucherType'].values[0]
        return vouchertype
    return f"No VoucherType for this token."

def check_user_token(email, token_id):
    """Given the email id of a user and a token ID, checks whether the user owns the particular token."""
    users_df = pd.read_csv('dummydata/users.csv')
    user = users_df.loc[users_df['Mail'] == email]
    
    if not user.empty:
        token_list = eval(user['token_list'].values[0])  
        if token_id in token_list:
            return f"User owns the token {token_id}."
        else:
            return f"User does not own the token {token_id}."
    return "User not found."

def check_voucher_expiry(voucher_id):
    """Given the VoucherID, checks whether voucher is expired or not."""
    vouchers_df = pd.read_csv('dummydata/vouchers.csv')
    voucher = vouchers_df.loc[vouchers_df['VoucherID'] == voucher_id]
    
    if not voucher.empty:
        status = voucher['Status'].values[0]
        if status == "Expired":
            return f"Voucher {voucher_id} is expired."
        elif status == "Redeemed":
            return f"Voucher {voucher_id} is redeemed and cannot be used again."
        else:
            return f"Voucher {voucher_id} is valid and can be used."
    return "Voucher not found."

def get_voucher_conditions(voucher_id):
    """Returns the conditions for using the voucher. Requires VoucherID as a parameter."""
    vouchers_df = pd.read_csv('dummydata/vouchers.csv')
    voucher = vouchers_df.loc[vouchers_df['VoucherID'] == voucher_id]
    if not voucher.empty:
        conditions = voucher['Conditions'].values[0]
        return conditions
    return f"No conditions for using the voucher {voucher_id}"

def verify_user(email):
    """Verifies the identify of the user by checking the email provided by the user. If user exists it returns all the details of the user."""
    users_df = pd.read_csv('dummydata/users.csv')
    user = users_df.loc[users_df['Mail'] == email]
    
    if not user.empty:
        user_info = {
            'Name': user['Name'].values[0],
            'ID': user['ID'].values[0],
            'Mail':email,
            'Token List': user['token_list'].values[0]
        }
        return f"User verified: {user_info}"
    else:
        return "Email not found. Please check your email."
    
def recover_lost_token(email):
    """Given the user email, retreives all the tokens of a user."""
    users_df = pd.read_csv('dummydata/users.csv')
    user = users_df.loc[users_df['Mail'] == email]
    
    if not user.empty:
        token_list = eval(user['token_list'].values[0])  
        return f"Your tokens are: {token_list}"
    else:
        return "User not found or invalid email."
    
def ask_user_email():
    """Asks the user for their email if we are not aware of that."""
    with st.chat_message("assistant"):
        st.markdown("Please enter your mail.")    

AskEmailTool = FunctionTool.from_defaults(fn=ask_user_email)
GetTokenTool = FunctionTool.from_defaults(fn=recover_lost_token)
VerificationTool = FunctionTool.from_defaults(fn=verify_user)
VoucherTool = FunctionTool.from_defaults(fn=get_voucher_conditions)
ExpiryTool = FunctionTool.from_defaults(fn=check_voucher_expiry)
Ownership = FunctionTool.from_defaults(fn=check_user_token)

prompt_for_react_agent = f"""You are an intelligent voucher assistant. You have access to the following tools:
Your goal is to assist the user with queries related to vouchers, tokens, and purchases by calling the correct tools and formulating a user-friendly response.

### How to respond:
1. If the user query relates to a specific voucher, token, or purchase, analyze the query and decide which tool(s) to use.
2. Use the user's email if the user is asking about personal tokens or vouchers. Ask for their email using **AskEmailTool**. Once they have entred the email remember it until they want to change or enter a different value for email.
3. If the user asks about the conditions or applicability of a voucher, use **VoucherTool** to retrieve the conditions.
4. If the user asks about the expiry of a voucher, use **ExpiryTool** to check if the voucher is expired.
5. If the user has lost a token, use **GetTokenTool** after verification.
6. Respond clearly and explain the results of the tool's actions to the user.

### Now, please process the following query: "{{query}}".

"""
agent = ReActAgent.from_tools(tools=[AskEmailTool,ExpiryTool,VoucherTool,GetTokenTool,VerificationTool,Ownership],llm=llm,verbose=True)

if query := st.chat_input("Ask about market-sentiments?"):
    st.chat_message("user").markdown(query)
    
    response = agent.chat(prompt_for_react_agent.format(query=query))
    with st.chat_message("assistant"):
        st.markdown(response)
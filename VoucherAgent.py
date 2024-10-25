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

def get_token_vouchertype(token_id_list:list[int]):
    """When a list of token IDs is provided, returns a list of corresponding voucher IDs, it does not add a voucher ID for a token ID if the token does not eist in our database."""
    tokens_df = pd.read_csv('dummydata/tokens.csv')
    voucher_id_list = []
    for token_id in token_id_list:
        token = tokens_df.loc[tokens_df['TokenID'] == token_id]
        if not token.empty:
            vouchertype = token['VoucherID'].values[0]
            voucher_id_list.append({token_id:vouchertype})
    return voucher_id_list

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

def get_all_vouchers():
    """Returns the details of all the vouchers in the dataset."""
    vouchers_df = pd.read_csv('dummydata/vouchers.csv')
    return vouchers_df

def get_particular_voucher(voucher_id_list: list[int]):
    """Given the list of voucher IDs(integer), returns all the details for each voucher. It appends the list with the voucher details only if that voucher id exists in our database."""
    vouchers_df = pd.read_csv('dummydata/vouchers.csv')
    voucher_list = []
    for voucher_id in voucher_id_list:
        voucher = vouchers_df.loc[vouchers_df['VoucherID'] == voucher_id]
        if not voucher.empty:
            voucher_list.append(voucher)
    return voucher_list

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
VoucherConditionTool = FunctionTool.from_defaults(fn=get_voucher_conditions)
ExpiryTool = FunctionTool.from_defaults(fn=check_voucher_expiry)
Ownership = FunctionTool.from_defaults(fn=check_user_token)
VoucherFromTokenTool = FunctionTool.from_defaults(fn=get_token_vouchertype)
GetAllVoucherTool = FunctionTool.from_defaults(fn=get_all_vouchers)
GetOneVoucherTool = FunctionTool.from_defaults(fn=get_particular_voucher)

prompt_for_react_agent = f"""You are an intelligent voucher customer support assistant.
Your goal is to assist the user with queries related to vouchers, tokens, and purchases by calling the correct tools and formulating a user-friendly response.
Each user can own a certain set of vouchers which can be used for purchase. The user will have a set of tokens they can use. All the tokens have a token id. Each token id is mapped to a voucher. Each voucher has various details of usage. 
Using your tools, you can extract data of the users, tokens, and vouchers.
Please formulate a proper answer. If you are missing an argument, you can reply by asking the user about it if needed.
If the user wants to ask something related to the set of tokens/vouchers they own, you can ask their email and get the user details from your tool.
If the user asks a general query about the type of tokens and vouchers available you can directly access other tools and get the required data.
TIP: If you have an operation that is very iterative, you can pass on inputs together as a list in some of the functions if they allow it.
Now, please process the following query: "{{query}}".

"""
agent = ReActAgent.from_tools(tools=[GetOneVoucherTool,GetAllVoucherTool,VoucherFromTokenTool,GetTokenTool,VerificationTool],llm=llm,verbose=True)

if query := st.chat_input("Ask about market-sentiments?"):
    st.chat_message("user").markdown(query)
    
    response = agent.chat(prompt_for_react_agent.format(query=query))
    with st.chat_message("assistant"):
        st.markdown(response)

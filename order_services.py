from torch._subclasses.fake_impls import data_dep
from order_template import ORDER_TEMPLATE
import json
import os
import time
from datetime import datetime
from memory_store import load_memory,save_memory
from order_parser import parse_order_text, validate_order_data,REQUIRED_FIELDS, llm_extract_order

ORDERS_FILE = 'orders.json'


def save_order(order_data):
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f)

    with open(ORDERS_FILE, 'r') as f:
        orders = json.load(f)
    order_id = f'ORD{len(orders) + 1:04d}'

    order_data['order_id'] = order_id
    order_data['timestamp'] = str(datetime.utcnow())
    order_data['status'] = 'confirmed'

    orders.append(order_data)

    with open(ORDERS_FILE,'w') as f:
        json.dump(orders,f, indent=2)

    return order_id

def start_order(user_id):
    session = load_memory(user_id)

    session['order']['state'] = 'awaiting_template'
    session['order']['data'] = {}
    session['order']['last_update'] = time.time()

    save_memory(user_id,session)
    return ORDER_TEMPLATE

def handle_order_submission(text,user_id):

    session = load_memory(user_id)
    session['order']['last_update'] = time.time()
    state = session['order']['state']
    order_data = session['order']['data']

    user_input = text.strip().lower()

    if user_input in ['cancel', 'abort', 'stop']:
        session['order'] = {'state':'idle', 'data':{}}
        save_memory(user_id,session)
        return 'Your order has been cancelled'
    
    if state == 'awaiting_template':

        parsed = parse_order_text(text)
        if not parsed:
            parsed = llm_extract_order(text, user_id)

        order_data = merge_order_data(order_data,parsed)
        session['order']['data'] = order_data

        missing = get_missing_fields(order_data)

        if missing:
            save_memory(user_id, session)
            missing_fields = '\n'.join([f'{field}:' for field in missing])

            if 'summary' in user_input:
                summary = build_order_Summery(order_data)
                return f'''
            Some fields are missing.
            
            Please fill the following :
            {missing_fields}

            Current details:
            {summary}'''

            return f'''
            Some fields are missing.
            
            Please fill the following :
            {missing_fields}'''

        session['order']['state'] = 'awaiting_confirmation'
        save_memory(user_id, session)

        summary = build_order_Summery(order_data)

        return f"Please confirm your order:\n\n{summary}\n\nReply YES to confirm or type any correction."

    elif state == 'awaiting_confirmation':
        
        if  user_input in ['yes','y']:
            is_valid, issues = validate_order_data(order_data)
            if not is_valid:
                # Do not place the order; surface validation problems instead.
                problem_lines = []
                for issue in issues:
                    if issue == 'PINCODE must be numeric':
                        problem_lines.append(issue)
                    else:
                        problem_lines.append(f"Missing field: {issue}")
                problems_text = "\n".join(problem_lines)
                return f"There are some issues with your order:\n\n{problems_text}\n\nPlease update these details before confirming with YES."

            order_id = save_order(order_data)

            session['order'] = {
                'state': 'idle',
                'data':{},
                'last_update': None
                }
            save_memory(user_id, session)

            return f"Your order has been placed successfully! Order ID: {order_id}"

        if 'summary' in user_input:
            summary = build_order_Summery(order_data)
            return f"Here is your order summary:\n\n{summary}\n\nReply YES to confirm or send corrections in the same format."

        parsed = parse_order_text(text)
        if not parsed:
            parsed = llm_extract_order(text, user_id)

        if parsed:
            order_data = merge_order_data(order_data, parsed)
            session['order']['data'] = order_data
            save_memory(user_id,session)

            summary = build_order_Summery(order_data)
            return f"Updated order detials:\n\n{summary}\n\nReply Yes to confirm. "
        return 'Please reply YES to confirm or provide corrections.'
    return 'No active order. Please type "order" to start.'
   

def check_order_status(query,user_id):
    return 'reached order status'

def merge_order_data(existing,new_data):
    if not new_data:
        return existing

    for key, value in new_data.items():
        if value and value.strip():
            existing[key] = value.strip()

    return existing

def get_missing_fields(data):
    missing = []
    for fields in REQUIRED_FIELDS:
        key = fields.lower().replace(' ','_')
        if key not in data or not data[key].strip():
            missing.append(fields)
    return missing

def build_order_Summery(data):
    lines = []
    for key,value in data.items():
        lines.append(f"{key.replace('_',' ').title()}: {value}")
    return '\n'.join(lines)


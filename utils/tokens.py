import streamlit as st

# Pricing from build.txt
# Input tokens: $0.30 per 1M tokens
# Output tokens: $2.50 per 1M tokens
COST_PER_1M_INPUT = 0.30
COST_PER_1M_OUTPUT = 2.50

def calculate_cost(input_tokens, output_tokens):
    """
    Calculates the cost based on token counts.
    """
    input_cost = (input_tokens / 1_000_000) * COST_PER_1M_INPUT
    output_cost = (output_tokens / 1_000_000) * COST_PER_1M_OUTPUT
    return input_cost + output_cost

def track_usage(input_tokens, output_tokens):
    """
    Updates the session state with new token usage and accumulated cost.
    """
    if 'usage' not in st.session_state:
        st.session_state.usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_cost': 0.0
        }
    
    cost = calculate_cost(input_tokens, output_tokens)
    
    st.session_state.usage['input_tokens'] += input_tokens
    st.session_state.usage['output_tokens'] += output_tokens
    st.session_state.usage['total_cost'] += cost
    
    return cost

def get_current_usage():
    """
    Returns the current usage stats from session state.
    """
    return st.session_state.get('usage', {
        'input_tokens': 0,
        'output_tokens': 0,
        'total_cost': 0.0
    })

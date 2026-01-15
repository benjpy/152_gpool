import time
import functools
import streamlit as st

def time_execution(func):
    """
    Decorator to measure and store execution time of functions.
    Results are stored in streamlit session state for visibility if needed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        if 'execution_times' not in st.session_state:
            st.session_state.execution_times = {}
        
        st.session_state.execution_times[func.__name__] = duration
        print(f"DEBUG: {func.__name__} took {duration:.4f} seconds")
        return result
    return wrapper

import pandas as pd

class SessionState:
    """Mock class for Streamlit session state"""
    def __init__(self):
        self.portfolio = pd.DataFrame()
        self.cash = 10000.0
        self.needs_cash = False

class StreamlitMock:
    """Base mock class for Streamlit components"""
    def __init__(self):
        self.calls = []
        self.session_state = SessionState()
    
    def _record_call(self, method, *args, **kwargs):
        """Record method calls for testing"""
        self.calls.append((method, args, kwargs))
        return self
    
    # Basic Streamlit methods
    def metric(self, label, value, delta=None):
        self._record_call('metric', label, value, delta)
    
    def info(self, text):
        self._record_call('info', text)
    
    def dataframe(self, df):
        self._record_call('dataframe', df)
    
    def subheader(self, text):
        self._record_call('subheader', text)
    
    def markdown(self, text):
        self._record_call('markdown', text)
    
    def form(self, key, **kwargs):
        self._record_call('form', key, **kwargs)
        return self
    
    def expander(self, label, expanded=False):
        self._record_call('expander', label, expanded)
        return self
    
    def columns(self, num_cols):
        cols = [StreamlitMock() for _ in range(num_cols)]
        self._record_call('columns', num_cols)
        return cols
    
    # Context manager support
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None
    
    # Testing helpers
    def get_calls(self, method_name=None):
        """Get all calls or filtered by method name"""
        if method_name:
            return [c for c in self.calls if c[0] == method_name]
        return self.calls
    
    def assert_called(self, method_name):
        """Assert a method was called"""
        return any(c[0] == method_name for c in self.calls)
    
    def assert_called_with(self, method_name, *args, **kwargs):
        """Assert a method was called with specific arguments"""
        for call in self.calls:
            if (call[0] == method_name and 
                call[1] == args and 
                call[2] == kwargs):
                return True
        return False
    
    def assert_info_called_with(self, text):
        """Assert info was called with specific text"""
        return ('info', (text,), {}) in self.calls
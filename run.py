"""
Entrypoint script to execute VoyageAI Streamlit app or build indexes.
"""

import sys
import os

if __name__ == "__main__":
    # Launch Streamlit
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=127.0.0.1"]
    sys.exit(stcli.main())

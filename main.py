# main.py
from monitoring_system import create_monitoring_system
import warnings

def main():
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Create and run the monitoring system
    app = create_monitoring_system()
    app.run()

if __name__ == "__main__":
    main()

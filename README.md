# Market-Intelligence

A financial analysis platform designed for market intelligence and data-driven insights.

## Project Structure

```text
.
├── app/                  # Core application logic
│   ├── analytics/        # Django backend apps
│   └── api/              # API implementation
├── Config/               # Django configuration
├── Data/                 # Data storage
├── streamlit_app/        # Streamlit frontend
├── manage.py             # Django entry point
├── pipeline.py           # Data pipeline script
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── Makefile              # Automation commands
└── pyproject.toml        # Tooling configuration
```

## Getting Started

### Prerequisites
- Python 3.10+
- `pip` package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Market-Intelligence
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configurations if needed
   ```

## Running the Application

### 1. Start the Backend API (Django)
The backend server must be running for the frontend to fetch data.

```bash
# Using Makefile
make api

# OR using manual command
python Returns manage.py runserver 8000
```
The API will be available at `http://localhost:8000/api/v1/`.

### 2. Run the Data Pipeline (Optional)
To fetch and process the latest financial data:

```bash
# Using Makefile
make pipeline

# OR using manual command
python pipeline.py
```

### 3. Start the Frontend (Streamlit)
Launch the user interface in a separate terminal:

```bash
# Using Makefile
make run

# OR using manual command
streamlit run streamlit_app/app.py
```
The dashboard will open in your browser at `http://localhost:8501`.

## Navigation
- **Market Pulse**: Overview of tracked assets and overall market trends.
- **Asset Analysis**: Detailed charts and metrics for individual assets. Use the "Dashboard" button to return to the pulse view.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
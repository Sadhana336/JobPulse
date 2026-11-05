

⚡ JobPulse – India Tech Hiring Intelligence Platform
JobPulse is a data analytics dashboard designed to explore India's technology job market. It helps users understand hiring trends, identify in-demand technical skills, explore salary information, and discover job opportunities through interactive visualizations.

Built using Python, Streamlit, Pandas, Plotly, and SQLite, JobPulse transforms job-posting data into meaningful career insights.

🚀 Key Features
📊 Hiring Market Overview
Total job posting analysis
Company and job role statistics
Employment type distribution
Interactive charts and visualizations
🧠 Technical Skill Analysis
Extracts technical skills from job descriptions
Identifies frequently demanded skills
Displays skill demand through interactive charts
💰 Salary Intelligence
Explores available salary information
Displays minimum and maximum salary ranges
Compares salary information by currency and pay period
🌍 Roles and Location Analysis
Identifies popular job roles
Explores locations mentioned in job postings
Analyzes experience levels
Displays job publication trends
🎯 Skill Gap Explorer
Allows users to select their existing skills
Compares selected skills with identified job-market demand
Highlights skills that users may want to learn
🔎 Job Explorer
Search and filter job postings
Explore company and role information
View available application links
Download filtered job records as CSV
🛠️ Technology Stack
Technology	Purpose
Python	Core programming
Streamlit	Interactive dashboard
Pandas	Data processing
NumPy	Numerical operations
Plotly	Interactive visualizations
SQLAlchemy	Database connectivity
SQLite	Local data storage
Scikit-learn	Installed for potential future analytics extensions
Requests	API communication
Himalayas Jobs API	Job-posting data source
📁 Project Structure
JobPulse/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── jobpulse.db
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── analysis.py
│   └── database.py
│
└── assets/
⚙️ Installation and Setup
1. Clone the repository
git clone YOUR_GITHUB_REPOSITORY_URL
cd JobPulse
2. Create a virtual environment
python -m venv .venv
3. Activate the environment
Windows:

.venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Run the application
streamlit run app.py
The dashboard will open in your browser at:

http://localhost:8501

📡 Data Source
JobPulse retrieves job-posting information through the Himalayas Jobs API.

Users can also upload compatible CSV files to explore their own job datasets.

Data note: The dashboard analyzes the information returned by the API or uploaded by the user. Results depend on the available job descriptions, salary fields, locations, and publication dates. Skill extraction is based on keyword matching, not a trained prediction model.

📈 Project Objective
The objective of JobPulse is to make job-market information easier to understand through data analytics and interactive visualizations.

It demonstrates practical skills in:

Data collection through APIs
Data cleaning and preprocessing
Exploratory data analysis
Data visualization
Database integration
Interactive dashboard development
Insight generation
🔮 Future Enhancements
Advanced job-market forecasting
Machine learning-based job trend analysis
Personalized career recommendations
More job data sources
Cloud database integration
Automated job-market reports
👩‍💻 Developed By
Sadhana P D

B.E. Computer Science and Engineering

Dr. N.G.P. Institute of Technology

📌 Project
JobPulse – India Tech Hiring Intelligence Platform

Built with Python and Streamlit.





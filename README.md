# Tamkeen – Disability Services Assistant

**Tamkeen** is a Python-based application designed to help persons with disabilities in Egypt understand available government services and prepare the required documents before applying.

The project aims to make information easier to access through a simple, user-friendly interface.

## Problem

Many persons with disabilities face difficulties understanding available services, identifying required documents, and following application procedures.

Tamkeen aims to reduce this confusion by organizing service information and guiding users through the preparation process.

## Key Features

- **Service Selection:** Explore services based on the user's needs.
- **Document Checklist:** View required documents and track their availability.
- **Data Validation:** Validate entered information and National ID format.
- **Progress Tracking:** Monitor document preparation progress.
- **Report Generation:** Generate a summary report of selected services and document status.
- **Bilingual Interface:** Support for Arabic and English.

## Technologies Used

- Python
- Streamlit
- JSON
- Git & GitHub

## Project Structure

```text
Tamkeen/
├── app.py
├── ui.py
├── services.py
├── checklist.py
├── validators.py
├── report_generator.py
├── data/
│   ├── services.json
│   └── reports/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/DarkByteSec/Tamkeen.git
```

2. Navigate to the project directory:

```bash
cd Tamkeen
```

3. Create and activate a virtual environment:

```bash
python -m venv venv
```

Linux / macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the application:

```bash
streamlit run app.py
```

## Important Note

Tamkeen is an independent assistance tool. It is not an official government platform and does not submit applications to government authorities.

Users should always verify service requirements and procedures through the relevant official authorities.

## Project Status

This project is currently under development.

## Author

**Yousef Amr Mahmoud**

GitHub: [@DarkByteSec](https://github.com/DarkByteSec)

# EV-Solar-Feasibility-Calculator
A Python Dash web app for modeling the financial feasibility and CO₂ impact of solar-powered EV charging stations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A Python Dash web application for modeling the financial feasibility and CO₂ impact of solar-powered EV charging stations. This tool helps clean energy consultants, infrastructure developers, and researchers quickly assess the viability of a project based on a wide range of configurable parameters.

The application features an intuitive user interface, dynamic charts, and a one-click professional PDF report generator for sharing the results.

### Key Features

*   **Interactive Web Dashboard:** A clean, user-friendly interface built with Dash and Bootstrap.
*   **Comprehensive Financial Modeling:** Calculates key metrics like Net Present Value (NPV), Internal Rate of Return (IRR), and Simple Payback Period.
*   **Environmental Impact Analysis:** Estimates and visualizes the CO₂ emissions saved compared to a grid-only baseline.
*   **Dynamic Visualizations:** Interactive Plotly charts for cash flow analysis and environmental impact.
*   **Professional PDF Reporting:** Generates a neatly formatted, multi-page PDF summary of all inputs, KPIs, charts, and data tables with a single click.
*   **Manual Simulation Control:** Calculations are triggered intentionally by a "Run Simulation" button for a better user experience.

### Dashboard Screenshot


<img width="1900" height="845" alt="2" src="https://github.com/user-attachments/assets/5ea78605-ec80-447b-b65e-0d856be5e994" />


### Technology Stack

*   **Backend & Web Framework:** Python, Dash
*   **UI Components:** Dash Bootstrap Components
*   **Calculations:** Pandas, NumPy, NumPy-Financial
*   **Charting:** Plotly Express & Graph Objects
*   **PDF Generation:** WeasyPrint

### Setup and Installation

Follow these steps to get the application running on your local machine.

**1. Clone the repository:**
```bash
git clone https://https://github.com/vaijayanth-sheri/EV-Solar-Feasibility-Calculator.git
cd EV-Solar-Feasibility-Calculator
```

**2. Create and activate a virtual environment:**
*   **On macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
*   **On Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

**3. Install the required packages:**
```bash
pip install -r requirements.txt
```

**Important Note on `WeasyPrint`:**
This library is powerful but may require a one-time setup of system dependencies (like GTK3) on your first use. If you encounter an error related to `pango`, `cairo`, or `dll not found` when generating a PDF, please follow the official installation instructions for your operating system on the [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

### How to Run the Application

With your virtual environment activated, run the following command from the project's root directory:

```bash
python app.py
```

Open your web browser and navigate to **`http://127.0.0.1:8050`**.

### Project Structure

This project uses a simple, single-file structure for clarity and ease of management.

```
/
├── app.py              # The entire Dash application (layout, logic, callbacks)
├── requirements.txt    # List of Python dependencies
├── README.md           
└── .gitignore          
```

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

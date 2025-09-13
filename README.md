# Kindi-BE3: OSINT B2B SaaS Platform Backend

This repository contains the backend services for the Kindi OSINT platform. It is built with Django and Django REST Framework.

## Project Structure

The project is divided into several Django apps, each responsible for a specific data collection or integration task:

-   `ip_rotator`: Manages a pool of AWS API Gateways to use as proxies.
-   `people_search`: Integrates with the ReachStream API for contact data.
-   `threat_intel`: Integrates with the ThreatMiner API for IOC data.
-   `phishing_intel`: Integrates with the PhishTank API for phishing URL checks.
-   `malware_intel`: Integrates with the URLhaus API for malware data.
-   `vulnerability_intel`: Integrates with NVD and Vulners for vulnerability data.
-   `serpapi_integration`: Integrates with SerpAPI for various Google search capabilities.

## Quick Start

### 1. Setup Environment

This project uses `python-dotenv` to manage environment variables. Create a `.env` file in the project root by copying the example:

```bash
cp .env.example .env
```

Then, fill in the required API keys in the `.env` file. You will need to register for keys from:
-   AWS (for the `ip_rotator`)
-   ReachStream
-   PhishTank
-   URLhaus
-   NVD
-   Vulners
-   SerpAPI

### 2. Install Dependencies

It is recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Run Migrations

Apply the database migrations to set up the schema:

```bash
python manage.py migrate
```

### 4. Create a Superuser

To access the Django admin, you will need a superuser account:

```bash
python manage.py createsuperuser
```

### 5. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/v1/`.
The Django admin will be available at `http://127.0.0.1:8000/admin/`.

### 6. Running Checks

To run all linters and tests, use the `make ci` command:

```bash
make ci
```

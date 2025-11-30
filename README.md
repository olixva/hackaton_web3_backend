# Hackaton Web3 Backend

A FastAPI-based backend for a web3 hackaton project, integrating BSV blockchain payments, user management, meter readings, and dynamic energy consumption charts.

## Problem

**From the Company's Perspective**:
- Traditional payment systems are prone to fraud.
- Traditional payment systems lack liquidity for instant settlements.

**From the User's Perspective**:
- Lack of clear visibility into energy spending due to complex mathematical formulas and calculations.
- No total control over consumption costs, as users don't understand the underlying math.

## Solution

**From the Company's Perspective**:
- Runs automatic payment flows like a smart meter, triggering micropayments on hourly consumption.
- Integrates cryptocurrency payments for fraud prevention through early detection of non-payments via hourly micropayments.
- Integrates cryptocurrency payments for instant liquidity maintained by continuous microtransactions per hour.

**From the User's Perspective**:
- Provides clear control over energy spending in monetary terms.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/olixva/hackaton_web3_backend.git
   cd hackaton-web3-backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file):
   ```
   MONGODB_URL=mongodb://localhost:27017/hackaton
   WOC_API_KEY=your_whats_on_chain_api_key
   DESTINATION_BSV_ADDRESS=your_bsv_address
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

- Access the API documentation at `http://localhost:8000/docs` (Swagger UI).
- Use scripts in `scripts/` to populate data or simulate readings.

### Scripts

- `populate_meter_readings.py`: Generate historical meter data.
- `simulate_meter.py`: Run continuous meter simulation posting to API.

## API Endpoints

- `GET /user/{user_id}`: Get user details with balance.
- `POST /user`: Create a new user.
- `PATCH /user/{user_id}`: Update user settings.
- `POST /meter`: Create a meter reading (triggers payment).
- `GET /meter/chart`: Get consumption chart.
- `GET /meter/chart/users`: Paywalled aggregated chart for all users.
- `POST /alarm`: Create an alarm.
- `GET /alarm/user/{user_id}`: Get user alarms.
- `DELETE /alarm/{alarm_id}`: Delete an alarm.

## Technologies

- **FastAPI**: Async web framework.
- **Beanie**: ODM for MongoDB.
- **BSV SDK**: Bitcoin SV blockchain interactions.
- **httpx**: Async HTTP client.
- **Pydantic**: Data validation.
- **WhatsOnChain API**: BSV blockchain data.
- **CoinGecko API**: Cryptocurrency prices.
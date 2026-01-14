# Installation

This guide covers installing Praxis for **Browser Mode**, which allows you to run Praxis entirely within your web browser for local use, demonstrations, or UI development.

## Browser Mode (Recommended for Local Use)

Browser mode allows you to run Praxis entirely within your web browser. It uses Pyodide to run the Python logic and WebSerial/WebUSB to talk to your hardware. No backend installation is required beyond hosting the frontend.

### To run locally

1. Ensure you have Node.js 20+ installed.
2. Clone the repo and install frontend dependencies:

   ```bash
   git clone https://github.com/maraxen/pylabpraxis.git
   cd pylabpraxis/praxis/web-client
   npm install
   ```

3. Start the dev server in browser configuration:

   ```bash
   npm run start:browser
   ```

4. Open <http://localhost:4200>. You are now running in **Browser Mode**.

## Browser Mode (No Backend Required)

For quick demonstrations without setting up the backend:

```bash
cd praxis/web-client
npm run start:browser
```

This runs the frontend with mock data - perfect for demos or UI development.

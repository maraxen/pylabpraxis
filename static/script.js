console.log('Script loaded'); // Basic check at the beginning

// Attach event listener to the form
document.addEventListener('DOMContentLoaded', function () {
  // Call updateUI on page load to handle redirect if already logged in or to show login form
  updateUI();

  // Get the form element by its ID
  const loginForm = document.getElementById('login-form');

  // Check if the form element exists before adding the event listener
  if (loginForm) {
    // Attach event listener to the form for submit event
    loginForm.addEventListener('submit', function (event) {
      event.preventDefault(); // Prevent default form submission
      login(); // Call the login function
    });
  } else {
    console.error('Login form not found!');
  }

  // Fetch and list available protocols and running protocols
  fetchProtocols();
  fetchRunningProtocols();
  fetchDeckFiles();
});

// Function to show/hide elements based on login status
function updateUI() {
  const loggedIn = isLoggedIn();
  console.log("Updating UI, loggedIn:", loggedIn);
  document.getElementById('auth-section').style.display = loggedIn ? 'none' : 'block';
  document.getElementById('dashboard-content').style.display = loggedIn ? 'block' : 'none';

  if (loggedIn) {
    // Fetch data that is only accessible to logged-in users
    fetchProtocols();
    fetchRunningProtocols();
    fetchDeckFiles();
    document.getElementById('login-status').textContent = 'Logged in as ' + localStorage.getItem('username');
  } else {
    document.getElementById('login-status').textContent = 'Not logged in';
  }
}

// Function to handle key presses in the password field
function handleKeyPress(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // Prevent form submission
    login(); // Call the login function
  }
}

// Call updateUI on page load
window.onload = () => {
  console.log("Window onload, checking login status"); // Log when window.onload is executed
  updateUI();
};

// Make the login function async
async function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('/api/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        'username': username,
        'password': password
      })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('username', username); // Store the username

    // Update UI after successful login
    updateUI();

  } catch (error) {
    console.error('Error during login:', error);
    document.getElementById('login-status').textContent = 'Login failed';
  }
}

// Function to check if the user is logged in
function isLoggedIn() {
  return localStorage.getItem('access_token') !== null;
}

// Function to show/hide elements based on login status
function updateUI() {
  const loggedIn = isLoggedIn();
  document.getElementById('auth-section').style.display = loggedIn ? 'none' : 'block';
  document.getElementById('dashboard-content').style.display = loggedIn ? 'block' : 'none';

  if (loggedIn) {
    // Fetch data that is only accessible to logged-in users
    fetchProtocols();
    fetchRunningProtocols();
    document.getElementById('login-status').textContent = 'Logged in as ' + localStorage.getItem('username');
  } else {
    document.getElementById('login-status').textContent = 'Not logged in';
  }
}

async function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('username');
  updateUI();
}
// Function to fetch the list of available protocols
async function fetchProtocols() {
  const token = localStorage.getItem("access_token");
  console.log('Fetching protocols with token:', token ? 'present' : 'missing');

  try {
    const response = await fetch("/api/protocols/", {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log('Protocols response status:', response.status);

    if (!response.ok) {
      throw new Error(`Failed to fetch protocols: ${response.status}`);
    }

    const protocols = await response.json();
    console.log('Received protocols:', protocols);

    const protocolsList = document.getElementById("protocol-list");
    protocolsList.innerHTML = "";
    protocols.forEach((protocol) => {
      const li = document.createElement("li");
      li.textContent = protocol;
      protocolsList.appendChild(li);
    });
  } catch (error) {
    console.error("Error fetching protocols:", error);
  }
}

// Function to fetch and display running protocols
async function fetchRunningProtocols() {
  const token = localStorage.getItem("access_token");
  try {
    const response = await fetch("/api/protocols/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error("Failed to fetch running protocols");
    }
    const protocols = await response.json();
    const runningList = document.getElementById("running-protocols-list");
    runningList.innerHTML = "";
    protocols.forEach((protocol) => {
      const li = document.createElement("li");
      li.textContent = `${protocol} (Status: ${protocol.status})`;
      runningList.appendChild(li);
    });
  } catch (error) {
    console.error("Error:", error);
  }
}

// Function to start a protocol
async function startProtocol() {
  const protocolName = document.getElementById("protocol-name").value;
  const configFile = document.getElementById("config-file").files[0];
  const deckFile = document.getElementById("deck-file").files[0];
  const liquidHandler = document.getElementById("liquid-handler-name").value;
  const manualCheck = document.getElementById("manual-check").checked;
  const token = localStorage.getItem("access_token");

  const configFormData = new FormData();
  configFormData.append("file", configFile);

  const deckFormData = new FormData();
  deckFormData.append("file", deckFile);

  try {
    // First, upload the config file
    const configFileResponse = await fetch("/api/protocols/upload_config_file", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: configFormData,
    });
    if (!configFileResponse.ok)
      throw new Error("Failed to upload config file");
    const configFilePath = await configFileResponse.json();

    // Then, upload the deck file
    const deckFileResponse = await fetch("/api/protocols/upload_deck_file", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: deckFormData,
    });
    if (!deckFileResponse.ok)
      throw new Error("Failed to upload deck file");
    const deckFilePath = await deckFileResponse.json();

    // Finally, start the protocol
    const protocolResponse = await fetch("/api/protocols/start", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        protocol_name: protocolName,
        config_file: configFilePath,
        deck_file: deckFilePath,
        liquid_handler_name: liquidHandler,
        manual_check_list: manualCheck ? ["Manual check required"] : [],
      }),
    });

    if (!protocolResponse.ok)
      throw new Error("Failed to start protocol");
    const protocolStatus = await protocolResponse.json();
    alert(
      `Protocol started: ${protocolStatus.name} - Status: ${protocolStatus.status}`
    );

    // Refresh the list of running protocols
    fetchRunningProtocols();
  } catch (error) {
    console.error("Error:", error);
    alert(error.message);
  }
}

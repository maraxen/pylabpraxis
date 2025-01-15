// Function to handle user login
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
    localStorage.setItem('access_token', data.access_token); // Store the token
    document.getElementById('login-status').textContent = 'Logged in as ' + username;
    // Optionally, refresh the list of protocols or other data
    // fetchProtocols();
    // fetchRunningProtocols();
  } catch (error) {
    console.error('Error during login:', error);
    document.getElementById('login-status').textContent = 'Login failed';
  }
}

// Function to fetch the list of available protocols
async function fetchProtocols() {
  try {
    const response = await fetch('/api/protocols/');
    if (!response.ok) {
      throw new Error('Failed to fetch protocols');
    }
    const protocols = await response.json();
    const protocolsList = document.getElementById('protocol-list');
    protocolsList.innerHTML = '';
    protocols.forEach(protocol => {
      const li = document.createElement('li');
      li.textContent = protocol;
      protocolsList.appendChild(li);
    });
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to fetch and display running protocols
async function fetchRunningProtocols() {
  try {
    const response = await fetch('/api/protocols/');
    if (!response.ok) {
      throw new Error('Failed to fetch running protocols');
    }
    const protocols = await response.json();
    const runningList = document.getElementById('running-protocols-list');
    runningList.innerHTML = '';
    protocols.forEach(protocol => {
      const li = document.createElement('li');
      li.textContent = `${protocol} (Status: ${protocol.status})`;
      runningList.appendChild(li);
    });
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to start a protocol
async function startProtocol() {
  const protocolName = document.getElementById('protocol-name').value;
  const configFile = document.getElementById('config-file').files[0];
  const deckFile = document.getElementById('deck-file').files[0];
  const liquidHandler = document.getElementById('liquid-handler-name').value;
  const manualCheck = document.getElementById('manual-check').checked;

  const configFormData = new FormData();
  configFormData.append('file', configFile);

  const deckFormData = new FormData();
  deckFormData.append('file', deckFile);

  try {
    // First, upload the config file
    const configFileResponse = await fetch('/api/protocols/upload_config_file', {
      method: 'POST',
      body: configFormData
    });
    if (!configFileResponse.ok) throw new Error('Failed to upload config file');
    const configFilePath = await configFileResponse.json();

    // Then, upload the deck file
    const deckFileResponse = await fetch('/api/protocols/upload_deck_file', {
      method: 'POST',
      body: deckFormData
    });
    if (!deckFileResponse.ok) throw new Error('Failed to upload deck file');
    const deckFilePath = await deckFileResponse.json();

    // Finally, start the protocol
    const protocolResponse = await fetch('/api/protocols/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        protocol_name: protocolName,
        config_file: configFilePath,
        deck_file: deckFilePath,
        liquid_handler_name: liquidHandler,
        manual_check_list: manualCheck ? ['Manual check required'] : []
      })
    });

    if (!protocolResponse.ok) throw new Error('Failed to start protocol');
    const protocolStatus = await protocolResponse.json();
    alert(`Protocol started: ${protocolStatus.name} - Status: ${protocolStatus.status}`);

    // Refresh the list of running protocols
    fetchRunningProtocols();
  } catch (error) {
    console.error('Error:', error);
    alert(error.message);
  }
}

// Function to schedule a plate reader task
async function schedulePlateReaderTask() {
  const experimentName = document.getElementById('experiment-name').value;
  const plateName = document.getElementById('plate-name').value;
  const measurementType = document.getElementById('measurement-type').value;
  const wells = document.getElementById('wells').value;
  const estimatedDuration = document.getElementById('estimated-duration').value;

  try {
    const response = await fetch('/api/protocols/plate_reader_task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        experiment_name: experimentName,
        plate_name: plateName,
        measurement_type: measurementType,
        wells: wells.split(',').map(well => well.trim()),
        estimated_duration: estimatedDuration
      })
    });

    if (!response.ok) throw new Error('Failed to schedule plate reader task');
    const result = await response.json();
    alert(result.message);
  } catch (error) {
    console.error('Error:', error);
    alert(error.message);
  }
}

// Initial fetch on page load
fetchProtocols();
fetchRunningProtocols();
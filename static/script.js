document.addEventListener('DOMContentLoaded', function () {
  updateUI();
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      event.preventDefault();
      login();
    });
  } else {
    console.error('Login form not found!');
  }

  // Initialize theme
  const savedTheme = localStorage.getItem('theme') || 'system';
  changeTheme(savedTheme);

  // Add hash change listener
  window.addEventListener('hashchange', handleHashChange);

  // Initialize section from URL hash if present
  const initialHash = window.location.hash.slice(1);
  if (initialHash && isLoggedIn()) {
    showSection(initialHash);
  }
});

function isLoggedIn() {
  return localStorage.getItem('access_token') !== null;
}

function updateUI() {
  const loggedIn = isLoggedIn();
  const authSection = document.getElementById('auth-section');
  const content = document.getElementById('content');
  const sidebar = document.getElementById('sidebar');
  const initialLoader = document.getElementById('initial-loader');

  // Remove loading state
  document.getElementById('app').classList.remove('loading');
  initialLoader.style.display = 'none';

  if (loggedIn) {
    authSection.style.display = 'none';
    content.style.display = 'flex';
    sidebar.style.display = 'block';
    document.getElementById('logged-in-user').textContent =
      'Logged in as ' + localStorage.getItem('username');

    // Check for hash in URL, otherwise default to home
    const hash = window.location.hash.slice(1);
    showSection(hash || 'home');
  } else {
    authSection.style.display = 'flex';
    content.style.display = 'none';
    sidebar.style.display = 'none';
    document.getElementById('login-status').textContent = 'Not logged in';
  }
}

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
    localStorage.setItem('username', username);
    localStorage.setItem('is_admin', data.is_admin || false); // Store admin status

    updateUI();
  } catch (error) {
    console.error('Error during login:', error);
    document.getElementById('login-status').textContent = 'Login failed';
  }
}

async function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('username');
  localStorage.removeItem('is_admin');
  // Reset UI state
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('content').classList.remove('sidebar-open');
  document.getElementById('main-content').innerHTML = '';
  document.getElementById('logged-in-user').textContent = '';
  window.location.hash = ''; // Clear the hash when logging out
  updateUI();
}

function showSection(sectionId) {
  // Update URL hash without triggering the hashchange event
  window.removeEventListener('hashchange', handleHashChange);
  window.location.hash = sectionId;
  window.addEventListener('hashchange', handleHashChange);

  // Update active state in sidebar
  const navItems = document.querySelectorAll('#sidebar-nav li');
  navItems.forEach(item => {
    item.classList.remove('active');
    if (item.dataset.section === sectionId) {
      item.classList.add('active');
    }
  });

  // Fetch and display content based on sectionId
  switch (sectionId) {
    case 'home':
      showHome();
      break;
    case 'start-protocol':
      showStartProtocolForm();
      break;
    case 'manage-protocols':
      fetchProtocols();
      fetchRunningProtocols();
      break;
    case 'data-viewer':
      showDataViewer();
      break;
    case 'lab-inventory':
      showLabInventory();
      break;
    case 'settings':
      showSettings();
      break;
    // Add cases for other sections as needed
  }
}

// Add hash change handler
function handleHashChange() {
  const hash = window.location.hash.slice(1); // Remove the # symbol
  if (hash && isLoggedIn()) {
    showSection(hash);
  }
}

function showHome() {
  const content = `
      <div class="home-actions" style="display: flex; gap: 20px; margin-bottom: 30px;">
        <button type="button" class="action-button" style="background-color: var(--blue);"
                onclick="showSection('start-protocol')">
          <i class="fas fa-play"></i>
          Start Protocol
        </button>
        <button type="button" class="action-button" style="background-color: var(--gray);">
          <i class="fas fa-book"></i>
          Documentation
        </button>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0;">Running Protocols</h2>
        <button type="button" class="action-button green" onclick="fetchRunningProtocols()">
          <i class="fas fa-sync-alt"></i>
          Refresh
        </button>
      </div>

      <ul id="running-protocols-list"></ul>
  `;
  document.getElementById('main-content').innerHTML = content;
  fetchRunningProtocols();
}

function showStartProtocolForm() {
  const protocols = JSON.parse(localStorage.getItem('available_protocols') || '[]');

  const content = `
    <h2>Start Protocol</h2>
    <form id="start-protocol-form" onsubmit="event.preventDefault(); startProtocol();">
      <div>
        <label for="protocol-select">Select Protocol:</label>
        <select id="protocol-select" name="protocol-select" required onchange="updateProtocolForm(this.value)">
          <option value="">Choose a protocol...</option>
          ${protocols.map(p => `
            <option value="${p.name}">${p.name}</option>
          `).join('')}
        </select>
        <button type="button" onclick="refreshAvailableProtocols()" class="small-button">
          <i class="fas fa-sync"></i>
        </button>
      </div>
      <div id="protocol-specific-form">
        <!-- Protocol-specific form will be loaded here -->
      </div>
    </form>
  `;

  document.getElementById('main-content').innerHTML = content;
}

function showDataViewer() {
  document.getElementById('main-content').innerHTML = '<p>Data Viewer content will be here.</p>';
}

function showLabInventory() {
  document.getElementById('main-content').innerHTML = '<p>Lab Inventory content will be here.</p>';
}

async function showSettings() {
  console.log('Showing settings page');
  const isAdmin = localStorage.getItem('is_admin') === 'true';
  const currentTheme = localStorage.getItem('theme') || 'system';

  try {
    // Fetch settings and directories
    const token = localStorage.getItem('access_token');
    const [settingsResponse, directoriesResponse] = await Promise.all([
      fetch('/api/protocols/settings', {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      fetch('/api/protocols/protocol_directories', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    ]);

    let settings = {
      default_protocol_dir: '',
      user_settings: {}
    };

    if (settingsResponse.ok) {
      settings = await settingsResponse.json();
    }

    let directories = [];
    if (directoriesResponse.ok) {
      directories = await directoriesResponse.json();
    }

    const content = `
      <div class="settings-container">
        <input type="text" class="settings-search" placeholder="Search settings..." onkeyup="filterSettings(this.value)">

        <div class="settings-section" data-section="protocols">
          <div class="settings-header" onclick="toggleSettingsSection(this)">
            <span><i class="fas fa-flask"></i> Protocols</span>
            <i class="fas fa-chevron-down"></i>
          </div>
          <div class="settings-content">
            <h3>Protocol Directories</h3>
            <div class="directory-list">
              ${directories.map(dir => `
                <div class="directory-item">
                  <span class="directory-path" title="${dir}">${dir}</span>
                  ${dir === settings.default_protocol_dir ?
        '<span class="directory-badge">Default</span>' :
        `<button class="directory-button remove" onclick="removeProtocolDirectory('${dir}')" title="Remove directory">
                       <i class="fas fa-minus"></i>
                     </button>`
      }
                </div>
              `).join('')}
            </div>
            <div class="directory-controls">
              <button class="directory-button" onclick="addProtocolDirectory()" title="Add directory">
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="settings-section" data-section="appearance">
          <div class="settings-header" onclick="toggleSettingsSection(this)">
            <span><i class="fas fa-palette"></i> Appearance</span>
            <i class="fas fa-chevron-down"></i>
          </div>
          <div class="settings-content">
            <h3>Color Theme</h3>
            <select class="theme-selector" onchange="changeTheme(this.value)" value="${currentTheme}">
              <option value="system" ${currentTheme === 'system' ? 'selected' : ''}>Use System Settings</option>
              <option value="light" ${currentTheme === 'light' ? 'selected' : ''}>Light Mode</option>
              <option value="dark" ${currentTheme === 'dark' ? 'selected' : ''}>Dark Mode</option>
              <option value="high-contrast-light" ${currentTheme === 'high-contrast-light' ? 'selected' : ''}>High Contrast Light</option>
              <option value="high-contrast-dark" ${currentTheme === 'high-contrast-dark' ? 'selected' : ''}>High Contrast Dark</option>
            </select>
          </div>
        </div>

        <div class="settings-section admin ${isAdmin ? 'enabled' : ''}" data-section="admin">
          <div class="settings-header" onclick="toggleSettingsSection(this)">
            <span><i class="fas fa-shield-alt"></i> Admin Settings</span>
            <i class="fas fa-chevron-down"></i>
          </div>
          <div class="settings-content">
            <p>${isAdmin ? 'Admin settings will go here' : 'Requires admin privileges'}</p>
          </div>
        </div>
      </div>
    `;

    console.log('Updating main content with settings');
    document.getElementById('main-content').innerHTML = content;

    // Expand sections
    console.log('Expanding default sections');
    document.querySelector('.settings-section[data-section="protocols"] .settings-content').classList.add('expanded');
    document.querySelector('.settings-section[data-section="protocols"] .settings-header').classList.add('expanded');
    document.querySelector('.settings-section[data-section="appearance"] .settings-content').classList.add('expanded');
    document.querySelector('.settings-section[data-section="appearance"] .settings-header').classList.add('expanded');

  } catch (error) {
    console.error('Error loading settings:', error);
    document.getElementById('main-content').innerHTML = `<div class="error">Failed to load settings: ${error.message}</div>`;
  }
}

function toggleSettingsSection(header) {
  const section = header.closest('.settings-section');
  if (section.classList.contains('admin') && !section.classList.contains('enabled')) {
    return; // Don't toggle if it's a disabled admin section
  }

  header.classList.toggle('expanded');
  header.nextElementSibling.classList.toggle('expanded');
}

function filterSettings(query) {
  query = query.toLowerCase();
  const sections = document.querySelectorAll('.settings-section');

  sections.forEach(section => {
    const text = section.textContent.toLowerCase();
    const match = text.includes(query);
    section.style.display = match ? 'block' : 'none';
  });
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('content');

  if (sidebar.classList.contains('open')) {
    sidebar.classList.remove('open');
    content.classList.remove('sidebar-open');
  } else {
    sidebar.classList.add('open');
    content.classList.add('sidebar-open');
  }
}

async function fetchProtocols() {
  const token = localStorage.getItem("access_token");
  try {
    const response = await fetch("/api/protocols/", {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch protocols: ${response.status}`);
    }

    const protocols = await response.json();
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

async function fetchDeckFiles() {
  try {
    const response = await fetch('/api/protocols/deck_layouts');
    if (!response.ok) {
      throw new Error('Failed to fetch deck files');
    }
    const deckFiles = await response.json();
    const deckFileSelect = document.getElementById('deck-file');
    deckFileSelect.innerHTML = ''; // Clear existing options

    deckFiles.forEach(file => {
      const option = document.createElement('option');
      option.value = file;
      option.text = file;
      deckFileSelect.appendChild(option);
    });
  } catch (error) {
    console.error('Error:', error);
  }
}

async function startProtocol() {
  const protocolName = document.getElementById('protocol-name').value;
  const configFile = document.getElementById('config-file').files[0];
  const deckFileName = document.getElementById('deck-file').value; // Get the selected file name
  const liquidHandler = document.getElementById('liquid-handler-name').value;
  const manualCheck = document.getElementById('manual-check').checked;
  const token = localStorage.getItem('access_token');

  const configFormData = new FormData();
  configFormData.append('file', configFile);

  try {
    // First, upload the config file
    const configFileResponse = await fetch('/api/protocols/upload_config_file', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: configFormData
    });
    if (!configFileResponse.ok) throw new Error('Failed to upload config file');
    const configFilePath = await configFileResponse.json();

    // Construct the full path for the deck file
    const deckFilePath = './protocol/deck_layouts/' + deckFileName;

    // Start the protocol with the selected deck file
    const protocolResponse = await fetch('/api/protocols/start', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        protocol_name: protocolName,
        config_file: configFilePath,
        deck_file: deckFilePath, // Send the full path
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

// Add theme management functions
function changeTheme(theme) {
  if (theme === 'system') {
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
    }
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      if (localStorage.getItem('theme') === 'system') {
        document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
      }
    });
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
  localStorage.setItem('theme', theme);
}

// Protocol directory management
async function addProtocolDirectory() {
  const input = document.createElement('input');
  input.type = 'file';
  input.webkitdirectory = true;
  input.directory = true;

  input.addEventListener('change', async (e) => {
    const directory = e.target.files[0].path.split('/').slice(0, -1).join('/');
    const token = localStorage.getItem('access_token');

    try {
      // Send directory to backend for discovery
      const response = await fetch('/api/protocols/discover', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ directories: [directory] })
      });

      if (!response.ok) {
        throw new Error('Failed to add directory');
      }

      // Refresh available protocols
      await refreshAvailableProtocols();
      // Refresh settings view
      await showSettings();
    } catch (error) {
      console.error('Error adding directory:', error);
      alert('Failed to add directory: ' + error.message);
    }
  });

  input.click();
}

async function removeProtocolDirectory(directory) {
  const token = localStorage.getItem('access_token');
  try {
    const response = await fetch(`/api/protocols/directories/${encodeURIComponent(directory)}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to remove directory');
    }

    // Refresh settings view
    await showSettings();
    // Refresh available protocols
    await refreshAvailableProtocols();
  } catch (error) {
    console.error('Error removing directory:', error);
    alert('Failed to remove directory: ' + error.message);
  }
}

// Protocol discovery and management
async function refreshAvailableProtocols() {
  const token = localStorage.getItem('access_token');

  try {
    // Get protocol directories from server
    const dirResponse = await fetch('/api/protocols/protocol_directories', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!dirResponse.ok) throw new Error('Failed to get protocol directories');
    const directories = await dirResponse.json();

    // Discover protocols in these directories
    const response = await fetch('/api/protocols/discover', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ directories })
    });

    if (!response.ok) throw new Error('Failed to discover protocols');
    const protocols = await response.json();
    localStorage.setItem('available_protocols', JSON.stringify(protocols));
    return protocols;
  } catch (error) {
    console.error('Error discovering protocols:', error);
    return [];
  }
}

// Call updateUI on page load
window.onload = () => {
  updateUI();
};
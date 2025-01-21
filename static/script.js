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
    localStorage.setItem('is_admin', data.is_admin || false);

    // Load all initial data
    await Promise.all([
      refreshAvailableProtocols(),
      loadInitialData()
    ]);

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

// Protocol form handling functions
function getInputTypeForParameter(param) {
  switch (param.type) {
    case 'bool':
      return 'checkbox';
    case 'int':
    case 'float':
      return 'number';
    case 'list':
      return 'text'; // Will be handled as comma-separated values
    default:
      return 'text';
  }
}

function renderParameterInput(param) {
  const inputType = getInputTypeForParameter(param);
  const id = `param-${param.name}`;
  const name = `param-${param.name}`;

  if (inputType === 'checkbox') {
    return `
      <input type="checkbox"
             id="${id}"
             name="${name}"
             ${param.default ? 'checked' : ''}
             ${param.required ? 'required' : ''}>
    `;
  }

  if (inputType === 'number') {
    const constraints = param.constraints || {};
    return `
      <input type="number"
             id="${id}"
             name="${name}"
             value="${param.default !== undefined ? param.default : ''}"
             ${constraints.min_value !== undefined ? `min="${constraints.min_value}"` : ''}
             ${constraints.max_value !== undefined ? `max="${constraints.max_value}"` : ''}
             ${param.required ? 'required' : ''}>
    `;
  }

  return `
    <input type="text"
           id="${id}"
           name="${name}"
           value="${param.default !== undefined ? param.default : ''}"
           ${param.required ? 'required' : ''}>
  `;
}

function updateProtocolForm(protocolName) {
  console.log("Updating protocol form for:", protocolName);
  const protocols = JSON.parse(localStorage.getItem('available_protocols') || '[]');
  const assets = JSON.parse(localStorage.getItem('available_assets') || '[]');
  const users = JSON.parse(localStorage.getItem('available_users') || '[]');
  const deckFiles = JSON.parse(localStorage.getItem('available_deck_files') || '[]');

  console.log('Available protocols:', protocols);
  console.log('Available assets:', assets);
  console.log('Available users:', users);
  console.log('Available deck files:', deckFiles);

  const protocol = protocols.find(p => p.name === protocolName);

  if (!protocol) {
    console.error("Protocol not found:", protocolName);
    return;
  }

  console.log("Protocol data:", protocol);

  // Create the form content
  const formContent = `
    <div class="form-section">
      <h3>Protocol Configuration</h3>
      <div class="form-group">
        <label for="protocol-name">Name:</label>
        <input type="text" id="protocol-name" name="name" required value="${protocol.name || ''}"
               onchange="validateProtocolName(this.value)">
        <div id="name-validation-message" class="validation-message"></div>
      </div>
      <div class="form-group">
        <label for="protocol-details">Details:</label>
        <textarea id="protocol-details" name="details">${protocol.config_fields?.details || ''}</textarea>
      </div>
      <div class="form-group">
        <label for="protocol-description">Description:</label>
        <textarea id="protocol-description" name="description">${protocol.config_fields?.description || ''}</textarea>
      </div>
      <div class="form-group">
        <label for="protocol-machines">Machines:</label>
        <div class="select-with-refresh">
          <select id="protocol-machines" name="machines" multiple>
            ${assets.filter(a => a.type === 'machine').map(m => `
              <option value="${m.id}">${m.name}</option>
            `).join('')}
          </select>
          <button type="button" onclick="refreshAssets()" class="refresh-button" title="Refresh machines">
            <i class="fas fa-sync"></i>
          </button>
        </div>
      </div>
      <div class="form-group">
        <label for="protocol-liquid-handlers">Liquid Handlers:</label>
        <div class="select-with-refresh">
          <select id="protocol-liquid-handlers" name="liquid_handler_ids" multiple>
            ${assets.filter(a => a.type === 'liquid_handler').map(h => `
              <option value="${h.id}">${h.name}</option>
            `).join('')}
          </select>
          <button type="button" onclick="refreshAssets()" class="refresh-button" title="Refresh liquid handlers">
            <i class="fas fa-sync"></i>
          </button>
        </div>
      </div>
      <div class="form-group">
        <label for="protocol-users">Users:</label>
        <div class="select-with-refresh">
          <select id="protocol-users" name="users" multiple>
            ${users.map(u => `
              <option value="${u.username}">${u.display_name || u.username}</option>
            `).join('')}
          </select>
          <button type="button" onclick="refreshUsers()" class="refresh-button" title="Refresh users">
            <i class="fas fa-sync"></i>
          </button>
        </div>
      </div>
      <div class="form-group">
        <label for="protocol-directory">Directory:</label>
        <div class="directory-select">
          <input type="text" id="protocol-directory" name="directory"
                 value="${protocol.config_fields?.directory || ''}" readonly>
          <button type="button" onclick="selectDirectory()" class="directory-button">
            <i class="fas fa-folder-open"></i> Browse
          </button>
        </div>
      </div>
      <div class="form-group">
        <label for="protocol-deck">Deck File:</label>
        <div class="select-with-refresh">
          <select id="protocol-deck" name="deck" required>
            <option value="">Select a deck file...</option>
            ${deckFiles.map(f => `<option value="${f}">${f}</option>`).join('')}
          </select>
          <button type="button" onclick="refreshDeckFiles()" class="refresh-button" title="Refresh deck files">
            <i class="fas fa-sync"></i>
          </button>
        </div>
      </div>
    </div>
    <div id="protocol-parameters" class="form-section">
      <!-- Parameters will be dynamically added here -->
    </div>
    <div class="form-actions">
      <button type="submit" class="action-button">Start Protocol</button>
    </div>
  `;

  const formContainer = document.getElementById('protocol-specific-form');
  formContainer.innerHTML = formContent;

  // Initialize SlimSelect for all select elements
  const selectElements = {
    'protocol-machines': {
      placeholder: 'Select machines...',
      searchText: 'No machines found'
    },
    'protocol-liquid-handlers': {
      placeholder: 'Select liquid handlers...',
      searchText: 'No liquid handlers found'
    },
    'protocol-users': {
      placeholder: 'Select users...',
      searchText: 'No users found'
    },
    'protocol-deck': {
      placeholder: 'Select a deck file...',
      searchText: 'No deck files found'
    }
  };

  // Initialize each select with SlimSelect
  Object.entries(selectElements).forEach(([id, settings]) => {
    const element = document.getElementById(id);
    if (element) {
      console.log(`Initializing SlimSelect for ${id}`);
      new SlimSelect({
        select: element,
        settings: {
          ...settings,
          allowDeselect: true
        }
      });
    } else {
      console.error(`Element not found: ${id}`);
    }
  });

  // Set any previously selected values
  if (protocol.config_fields?.machines) {
    const machinesSelect = document.getElementById('protocol-machines');
    if (machinesSelect && machinesSelect.slim) {
      machinesSelect.slim.setSelected(protocol.config_fields.machines);
    }
  }
  if (protocol.config_fields?.liquid_handler_ids) {
    const lhSelect = document.getElementById('protocol-liquid-handlers');
    if (lhSelect && lhSelect.slim) {
      lhSelect.slim.setSelected(protocol.config_fields.liquid_handler_ids);
    }
  }
  if (protocol.config_fields?.users) {
    const usersSelect = document.getElementById('protocol-users');
    if (usersSelect && usersSelect.slim) {
      usersSelect.slim.setSelected(protocol.config_fields.users);
    }
  }
  if (protocol.config_fields?.deck) {
    const deckSelect = document.getElementById('protocol-deck');
    if (deckSelect && deckSelect.slim) {
      deckSelect.slim.setSelected(protocol.config_fields.deck);
    }
  }

  // Add parameters if they exist
  if (protocol.parameters && protocol.parameters.length > 0) {
    console.log("Rendering parameters:", protocol.parameters);

    const parametersDiv = document.createElement('div');
    parametersDiv.className = 'protocol-parameters';
    parametersDiv.innerHTML = '<h3>Protocol Parameters</h3>';

    protocol.parameters.forEach((param) => {
      const paramGroup = document.createElement('div');
      paramGroup.className = 'parameter-group';

      const label = document.createElement('label');
      label.className = 'parameter-label';
      label.textContent = param.name;

      const description = document.createElement('div');
      description.className = 'parameter-description';
      description.textContent = param.description || '';

      paramGroup.appendChild(label);
      paramGroup.appendChild(description);

      const input = createParameterInput(param.name, param);
      input.className = 'parameter-input';
      paramGroup.appendChild(input);

      parametersDiv.appendChild(paramGroup);
    });

    const parametersContainer = document.getElementById('protocol-parameters');
    if (parametersContainer) {
      parametersContainer.innerHTML = '';
      parametersContainer.appendChild(parametersDiv);
    }
  }
}

function createParameterInput(name, param) {
  let input;

  switch (param.type) {
    case 'bool':
      input = document.createElement('input');
      input.type = 'checkbox';
      input.name = name;
      input.checked = param.default || false;
      break;

    case 'number':
    case 'float':
    case 'int':
      input = document.createElement('input');
      input.type = 'number';
      input.name = name;
      input.value = param.default || '';
      if (param.constraints) {
        if (param.constraints.min_value !== undefined) {
          input.min = param.constraints.min_value;
        }
        if (param.constraints.max_value !== undefined) {
          input.max = param.constraints.max_value;
        }
        if (param.type === 'int') {
          input.step = 1;
        }
      }
      break;

    case 'list':
      input = document.createElement('select');
      input.name = name;
      input.multiple = true;
      if (param.default) {
        param.default.forEach(value => {
          const option = document.createElement('option');
          option.value = value;
          option.textContent = value;
          option.selected = true;
          input.appendChild(option);
        });
      }
      break;

    default:
      input = document.createElement('input');
      input.type = 'text';
      input.name = name;
      input.value = param.default || '';
  }

  return input;
}

function showStartProtocolForm() {
  const protocols = JSON.parse(localStorage.getItem('available_protocols') || '[]');
  console.log('Available protocols:', protocols);

  const content = `
    <h2>Start Protocol</h2>
    <form id="start-protocol-form">
      <div class="form-group">
        <label for="protocol-select">Select Protocol:</label>
        <select id="protocol-select" name="protocol-select" required class="searchable-select">
          <option value="">Choose a protocol...</option>
          ${protocols.map(p => `
            <option value="${p.name}" title="${p.file}">${p.name} (${p.file})</option>
          `).join('')}
        </select>
      </div>
      <div id="protocol-specific-form">
        <!-- Protocol-specific form will be loaded here -->
      </div>
    </form>
  `;

  document.getElementById('main-content').innerHTML = content;

  // Initialize searchable select for protocol selection
  new SlimSelect({
    select: '#protocol-select',
    settings: {
      allowDeselect: true,
      searchPlaceholder: 'Type to search protocols...',
      searchText: 'No protocols found'
    },
    events: {
      afterChange: (newVal) => {
        if (newVal && newVal[0] && newVal[0].value) {
          updateProtocolForm(newVal[0].value);
        }
      }
    }
  });
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
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/protocols/deck_layouts', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch deck files: ${response.status}`);
    }

    const deckFiles = await response.json();
    const deckSelect = document.getElementById('protocol-deck');
    if (!deckSelect) {
      console.error('Deck select element not found');
      return;
    }

    // Clear existing options
    deckSelect.innerHTML = '<option value="">Select a deck file...</option>';

    // Add new options
    if (Array.isArray(deckFiles)) {
      deckFiles.forEach(file => {
        const option = document.createElement('option');
        option.value = file;
        option.text = file;
        deckSelect.appendChild(option);
      });
    } else {
      console.error('Deck files response is not an array:', deckFiles);
    }
  } catch (error) {
    console.error('Error fetching deck files:', error);
  }
}

async function startProtocol() {
  const form = document.getElementById('start-protocol-form');
  const protocolName = document.getElementById('protocol-select').value;
  const protocols = JSON.parse(localStorage.getItem('available_protocols') || '[]');
  const protocol = protocols.find(p => p.name === protocolName);

  if (!protocol) {
    alert('Protocol not found');
    return;
  }

  // Gather configuration data
  const configData = {
    name: form.querySelector('#protocol-name').value,
    details: form.querySelector('#protocol-details').value,
    description: form.querySelector('#protocol-description').value,
    machines: Array.from(form.querySelector('#protocol-machines').selectedOptions).map(opt => opt.value),
    liquid_handler_ids: Array.from(form.querySelector('#protocol-liquid-handlers').selectedOptions).map(opt => opt.value),
    users: Array.from(form.querySelector('#protocol-users').selectedOptions).map(opt => opt.value),
    directory: form.querySelector('#protocol-directory').value,
    deck: form.querySelector('#protocol-deck').value,
    parameters: {}
  };

  // Gather parameter values
  if (protocol.parameters && protocol.parameters.length > 0) {
    protocol.parameters.forEach(param => {
      const input = form.querySelector(`#param-${param.name}`);
      if (input) {
        let value;
        if (input.type === 'checkbox') {
          value = input.checked;
        } else if (input.type === 'number') {
          value = param.type === 'int' ? parseInt(input.value) : parseFloat(input.value);
        } else if (param.type === 'list') {
          value = Array.from(input.selectedOptions).map(opt => opt.value);
        } else {
          value = input.value;
        }
        configData.parameters[param.name] = value;
      }
    });
  }

  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/protocols/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        protocol_name: protocolName,
        config_data: configData
      })
    });

    if (!response.ok) {
      throw new Error('Failed to start protocol');
    }

    const result = await response.json();
    alert(`Protocol ${protocolName} started successfully!`);
    window.location.hash = 'manage-protocols';
  } catch (error) {
    console.error('Error starting protocol:', error);
    alert('Failed to start protocol: ' + error.message);
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
  if (!token) {
    console.error('No access token found');
    return [];
  }

  try {
    // Try to refresh the token first
    await refreshToken();
    const newToken = localStorage.getItem('access_token');

    // Get protocol directories from server
    const dirResponse = await fetch('/api/protocols/protocol_directories', {
      headers: {
        'Authorization': `Bearer ${newToken}`
      }
    });

    if (!dirResponse.ok) {
      if (dirResponse.status === 401) {
        alert('Your session has expired. Please log in again.');
        logout();
        return [];
      }
      throw new Error('Failed to get protocol directories');
    }

    const directories = await dirResponse.json();
    console.log('Found protocol directories:', directories);

    // Discover protocols in these directories
    const response = await fetch('/api/protocols/discover', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${newToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ directories })
    });

    if (!response.ok) {
      if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        logout();
        return [];
      }
      throw new Error('Failed to discover protocols');
    }

    const protocols = await response.json();
    console.log('Discovered protocols:', protocols);

    // Store the full protocol data
    localStorage.setItem('available_protocols', JSON.stringify(protocols));
    return protocols;
  } catch (error) {
    console.error('Error discovering protocols:', error);
    if (error.message.includes('401') || error.message.includes('unauthorized')) {
      alert('Your session has expired. Please log in again.');
      logout();
    }
    return [];
  }
}

// Add this function to help with debugging
async function debugProtocolLoading() {
  console.log('Starting protocol debug...');

  // First, check what's in localStorage
  const storedProtocols = localStorage.getItem('available_protocols');
  console.log('Currently stored protocols:', JSON.parse(storedProtocols));

  // Then try to refresh protocols
  const newProtocols = await refreshAvailableProtocols();
  console.log('Newly fetched protocols:', newProtocols);

  // Update the form
  showStartProtocolForm();
}

// Call updateUI on page load
window.onload = () => {
  updateUI();
};

// Add token refresh functionality
async function refreshToken() {
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  try {
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return true;
  } catch (error) {
    console.error('Error refreshing token:', error);
    return false;
  }
}

// Add these helper functions for fetching data
async function fetchAssets() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/protocols/assets', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch assets');
    return await response.json();
  } catch (error) {
    console.error('Error fetching assets:', error);
    return [];
  }
}

async function fetchUsers() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/protocols/users', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to fetch users');
    return await response.json();
  } catch (error) {
    console.error('Error fetching users:', error);
    return [];
  }
}

// Add these functions at the top level
async function loadInitialData() {
  console.log('Loading initial data...');
  await Promise.all([
    refreshAssets(),
    refreshUsers(),
    refreshDeckFiles()
  ]);
}

async function refreshAssets() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/protocols/assets', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      if (response.status === 401) {
        // If unauthorized, try refreshing token
        if (await refreshToken()) {
          return refreshAssets(); // Retry with new token
        } else {
          alert('Your session has expired. Please log in again.');
          logout();
        }
      }
      throw new Error('Failed to fetch assets');
    }
    const assets = await response.json();
    localStorage.setItem('available_assets', JSON.stringify(assets));
    return assets;
  } catch (error) {
    console.error('Error fetching assets:', error);
    return [];
  }
}

async function refreshUsers() {
  try {
    console.log('Fetching users...');
    const token = localStorage.getItem('access_token');
    console.log('Token:', token ? 'Present' : 'Missing');

    const response = await fetch('/api/protocols/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('Response status:', response.status);
    if (!response.ok) {
      if (response.status === 401) {
        console.log('Unauthorized, attempting token refresh...');
        // If unauthorized, try refreshing token
        if (await refreshToken()) {
          console.log('Token refreshed, retrying...');
          return refreshUsers(); // Retry with new token
        } else {
          console.log('Token refresh failed');
          alert('Your session has expired. Please log in again.');
          logout();
          return [];
        }
      }

      const errorText = await response.text();
      console.error('Server error response:', errorText);
      throw new Error(`Failed to fetch users: ${response.status} ${errorText}`);
    }

    const users = await response.json();
    console.log('Fetched users:', users);
    localStorage.setItem('available_users', JSON.stringify(users));
    return users;
  } catch (error) {
    console.error('Error fetching users:', error);
    console.error('Error stack:', error.stack);
    return [];
  }
}

async function refreshDeckFiles() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/protocols/deck_layouts', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      if (response.status === 401) {
        // If unauthorized, try refreshing token
        if (await refreshToken()) {
          return refreshDeckFiles(); // Retry with new token
        } else {
          alert('Your session has expired. Please log in again.');
          logout();
        }
      }
      throw new Error('Failed to fetch deck files');
    }
    const deckFiles = await response.json();
    localStorage.setItem('available_deck_files', JSON.stringify(deckFiles));
    return deckFiles;
  } catch (error) {
    console.error('Error fetching deck files:', error);
    return [];
  }
}
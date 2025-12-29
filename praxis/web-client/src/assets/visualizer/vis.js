mode = MODE_VISUALIZER;

const statusLabel = document.getElementById("status-label");
const statusIndicator = document.getElementById("status-indicator");
function updateStatusLabel(status) {
  if (status === "loaded") {
    statusLabel.innerText = "Connected";
    statusLabel.classList.add("connected");
    statusLabel.classList.remove("disconnected");
    statusIndicator.classList.add("connected");
    statusIndicator.classList.remove("disconnected");
  } else if (status === "disconnected") {
    statusLabel.innerText = "Disconnected";
    statusLabel.classList.add("disconnected");
    statusLabel.classList.remove("connected");
    statusIndicator.classList.add("disconnected");
    statusIndicator.classList.remove("connected");
  } else {
    statusLabel.innerText = "Loading...";
    statusLabel.classList.remove("connected");
    statusLabel.classList.remove("disconnected");
    statusIndicator.classList.remove("connected");
    statusIndicator.classList.remove("disconnected");
  }
}

function setRootResource(data) {
  resource = loadResource(data.resource);

  resource.location = { x: 0, y: 0, z: 0 };
  resource.draw(resourceLayer);

  // pulse animation
  if (!window.ghostAnim) {
    window.ghostAnim = new Konva.Animation(function (frame) {
      var scale = 0.5 + 0.4 * Math.sin(frame.time / 500); // Pulse opacity

      // Find ghost groups
      var groups = resourceLayer.find(node => node.name().startsWith('ghost_'));

      groups.forEach(group => {
        // Apply style to the main shape (Rects) inside the group
        // This ensures we outline the container itself
        var shapes = group.find('Rect');
        shapes.forEach(shape => {
          shape.stroke('#dc3545'); // Bootstrap danger red
          shape.strokeWidth(2);
          shape.dash([10, 5]); // Dashed line
          shape.opacity(scale);
        });
      });
    }, resourceLayer);
    window.ghostAnim.start();
  }

  // center the root resource on the stage.
  let centerXOffset = (stage.width() - resource.size_x) / 2;
  let centerYOffset = (stage.height() - resource.size_y) / 2;
  stage.x(centerXOffset);
  stage.y(-centerYOffset);
}

function removeResource(resourceName) {
  let resource = resources[resourceName];
  resource.destroy();
}

function setState(allStates) {
  for (let resourceName in allStates) {
    let state = allStates[resourceName];
    let resource = resources[resourceName];
    resource.setState(state);
  }
}

async function processCentralEvent(event, data) {
  switch (event) {
    case "set_root_resource":
      setRootResource(data);
      break;

    case "resource_assigned":
      resource = loadResource(data.resource);
      resource.draw(resourceLayer);
      setState(data.state);
      break;

    case "resource_unassigned":
      removeResource(data.resource_name);
      break;

    case "set_state":
      let allStates = data;
      setState(allStates);

      break;

    default:
      throw new Error(`Unknown event: ${event}`);
  }
}

async function handleEvent(id, event, data) {
  if (event === "ready") {
    return; // don't parse response.
  }

  if (event === "pong") {
    return; // don't parse pongs.
  }

  console.log("[event] " + event, data);

  const ret = {
    event: event,
    id: id,
  };

  // Actually process the event.
  try {
    await processCentralEvent(event, data);
  } catch (e) {
    console.error(e);
    ret.error = e.message;
  }

  // Set the `success` field based on whether there was an error.
  if ((ret.error === undefined || ret.error === null) && (typeof webSocket !== 'undefined' && webSocket)) {
    ret.success = true;
    webSocket.send(JSON.stringify(ret));
  } else if (typeof webSocket !== 'undefined' && webSocket) {
    ret.success = false;
    webSocket.send(JSON.stringify(ret));
  } else {
    // console.log("Demo mode: Skipping WebSocket response", ret);
  }
}

// ===========================================================================
// init
// ===========================================================================

var socketLoading = false;
function openSocket() {
  if (socketLoading) {
    return;
  }

  socketLoading = true;
  updateStatusLabel("loading");
  let wsPortInput = document.querySelector(`input[id="ws_port"]`);
  let wsHost = window.location.hostname;
  let wsPort = wsPortInput.value;
  webSocket = new WebSocket(`ws://${wsHost}:${wsPort}/`);

  webSocket.onopen = function (event) {
    console.log("Connected to " + event.target.url);
    webSocket.send(`{"event": "ready"}`);
    updateStatusLabel("loaded");
    socketLoading = false;

    heartbeat();
  };

  webSocket.onerror = function () {
    updateStatusLabel("disconnected");
    socketLoading = false;
  };

  webSocket.onclose = function () {
    updateStatusLabel("disconnected");
    socketLoading = false;
  };

  // webSocket.onmessage = function (event) {
  webSocket.addEventListener("message", function (event) {
    var data = event.data;
    data = JSON.parse(data, (key, value) => {
      if (value == "Infinity") return Infinity;
      if (value == "-Infinity") return -Infinity;
      return value;
    });
    console.log(`[message] Data received from server:`, data);
    handleEvent(data.id, data.event, data.data);
  });
}

function heartbeat() {
  if (!webSocket) return;
  if (webSocket.readyState !== WebSocket.OPEN) return;
  webSocket.send(JSON.stringify({ event: "ping" }));
  setTimeout(heartbeat, 5000);
}

window.addEventListener("load", function () {
  updateStatusLabel("disconnected");

  const urlParams = new URLSearchParams(window.location.search);
  const isDemo = urlParams.get('mode') === 'demo';

  if (!isDemo) {
    openSocket();
  } else {
    updateStatusLabel("loaded"); // Set initial state for demo
    statusLabel.innerText = "Demo Mode";
  }
});

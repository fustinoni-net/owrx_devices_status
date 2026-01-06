
let panel;
let source;
let owrx_devices_status_base_url = '';

function upsertDeviceStatus(device, value) {
  let row = panel.querySelector(`[data-device="${device}"]`);
  if (!row) {
    row = document.createElement('div');
    row.dataset.device = device;
    row.id = 'ods' + device;
    row.className = "openwebrx-progressbar";
    panel.appendChild(row);
    panel.appendChild(document.createTextNode(' '));
  }

  row.innerHTML = '';
  const span = document.createElement('span');
  span.className = 'openwebrx-progressbar-text';
  span.textContent = `${device} [${value}]`;
  const bar = document.createElement('div');
  bar.className = 'openwebrx-progressbar-bar';
  bar.style.transform = (value === 'Stopped') ? 'translate(-100%) translateZ(0px)' : 'translate(0%) translateZ(0px)';
  row.appendChild(span);
  row.appendChild(bar);
}

function onmessage(event){
          if (!event.data) return;
          try {
            const payload = JSON.parse(event.data);
            Object.entries(payload).forEach(([device, value]) => upsertDeviceStatus(device, value));
          } catch (err) {
            console.error('Err parsing the event:', err, event.data);
          }
}

function onerror(err){
        console.error(`Error stream ${owrx_devices_status_base_url}/devicesEvents:`, err);
}

function start(){
        panel = document.getElementById('openwebrx-panel-status');
        source = new EventSource(`${owrx_devices_status_base_url}/devicesEvents`);

        source.onmessage = (event) => onmessage(event);
        source.onerror = (err) => onerror(err);
    }

if (typeof Plugins !== 'undefined' && Plugins !== null) {

    Plugins.owrx_devices_status_API_URL ??= '';
    Plugins.owrx_devices_status.API_URL ??= Plugins.owrx_devices_status_API_URL;

    Plugins.owrx_devices_status.no_css = true;

    // Init function of the plugin
    Plugins.owrx_devices_status.init = function () {
            Plugins.owrx_devices_status.API_URL = Plugins.owrx_devices_status.API_URL.replace(/\/$/, '');

            panel = document.getElementById('openwebrx-panel-status');
            source = new EventSource(`${owrx_devices_status_base_url}/devicesEvents`);

            source.onmessage = (event) => onmessage(event);
            source.onerror = (err) => onerror(err);

            return true;
        }

}
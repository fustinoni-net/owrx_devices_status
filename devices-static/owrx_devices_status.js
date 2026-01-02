    const panel = document.getElementById('openwebrx-panel-status');
    const source = new EventSource('/devicesEvents');

    function upsertDeviceStatus(device, value) {
      let row = panel.querySelector(`[data-device="${device}"]`);
      if (!row) {
        row = document.createElement('div');
        row.dataset.device = device;
        row.id = 'ods' + device;
        row.className = "openwebrx-progressbar";
        //row.style.margin = "8px"; // Spaziatura direttamente via JS
        panel.appendChild(row);
      }
      // Crea o aggiorna la struttura interna
      row.innerHTML = '';
      const span = document.createElement('span');
      span.className = 'openwebrx-progressbar-text';
      span.textContent = `${device}: ${value}`;
      const bar = document.createElement('div');
      bar.className = 'openwebrx-progressbar-bar';
      bar.style.transform = (value === 'Stopped') ? 'translate(-100%) translateZ(0px)' : 'translate(0%) translateZ(0px)';
      row.appendChild(span);
      row.appendChild(bar);
    }

    source.onmessage = (event) => {
      if (!event.data) return;
      try {
        const payload = JSON.parse(event.data);
        Object.entries(payload).forEach(([device, value]) => upsertDeviceStatus(device, value));
      } catch (err) {
        console.error('Errore nel parsing dell\'evento:', err, event.data);
      }
    };

    source.onerror = (err) => console.error('Errore stream /devicesEvents:', err);
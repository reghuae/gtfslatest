/* Dataiku Standard Webapp - JS tab */

function setStatus(msg, isError) {
  var el = document.getElementById('status');
  el.textContent = msg || '';
  el.className = 'status' + (isError ? ' error' : '');
}

function loadTables() {
  setStatus('Loading file list…');
  fetch(getWebAppBackendUrl('/tables'))
    .then(function (r) {
      if (!r.ok) { throw new Error('Backend returned HTTP ' + r.status); }
      return r.json();
    })
    .then(function (data) {
      var tbody = document.getElementById('file-rows');
      tbody.innerHTML = '';
      data.files.forEach(function (f) {
        var tr = document.createElement('tr');

        var tdName = document.createElement('td');
        tdName.innerHTML = '<code>' + f.filename + '</code>' +
          (f.required ? ' <span class="tag tag-req">core</span>' : '');
        tr.appendChild(tdName);

        var tdTable = document.createElement('td');
        tdTable.textContent = f.table;
        tr.appendChild(tdTable);

        var tdAccess = document.createElement('td');
        tdAccess.textContent = f.as_dataset
          ? 'project dataset'
          : 'Hive (' + data.connection + ')';
        tr.appendChild(tdAccess);

        var tdBtn = document.createElement('td');
        var btn = document.createElement('button');
        btn.className = 'btn btn-small';
        btn.textContent = 'Download';
        btn.addEventListener('click', function () {
          setStatus('Preparing ' + f.filename + ' … download starts automatically.');
          window.location.href = getWebAppBackendUrl('/download/' + f.name);
        });
        tdBtn.appendChild(btn);
        tr.appendChild(tdBtn);

        tbody.appendChild(tr);
      });
      setStatus('');
    })
    .catch(function (err) {
      setStatus('Could not load the file list: ' + err.message +
        ' — check that the backend is running and HIVE_CONNECTION is set.', true);
    });
}

document.getElementById('btn-refresh').addEventListener('click', loadTables);

document.getElementById('btn-download-all').addEventListener('click', function () {
  setStatus('Building gtfs.zip — this exports every table and can take a few ' +
            'minutes. The download starts automatically when ready.');
  window.location.href = getWebAppBackendUrl('/download_all');
});

loadTables();

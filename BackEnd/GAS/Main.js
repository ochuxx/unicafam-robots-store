const googleSheetsRef = PropertiesService.getScriptProperties().getProperty('GOOGLE_SHEETS_REF');

function doPost(e) {
  const action = e.parameter.action || e.postData.contents && JSON.parse(e.postData.contents).action;
  const data = JSON.parse(e.postData.contents);

  const routes = {
    'set_clients':  () => setClients(data),
    'edit_clients': () => editClients(data),
    'delete_clients':    () => deleteClients(data),
    'set_robots':  () => setRobots(data),
    'edit_robots': () => editRobots(data),
    'delete_robots':    () => deleteRobots(data)
  };

  const handler = routes[action];

  if (!handler) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, message: `Acción desconocida: ${action}` })
    ).setMimeType(ContentService.MimeType.JSON);
  }

  const result = handler();

  return ContentService.createTextOutput(
    JSON.stringify(result)
  ).setMimeType(ContentService.MimeType.JSON);
}
const googleSheetsRef = PropertiesService.getScriptProperties().getProperty('GOOGLE_SHEETS_REF');

function doPost(e) {
  try {
    const action = e.parameter.action || e.postData.contents && JSON.parse(e.postData.contents).action;
    const data = JSON.parse(e.postData.contents);

    const routes = {
      'set_clients': () => setClients(data),
      'edit_clients': () => editClients(data),
      'delete_clients': () => deleteClients(data),
      'set_robots':  () => setRobots(data),
      'edit_robots': () => editRobots(data),
      'delete_robots': () => deleteRobots(data),
      'set_empleados': () => setEmpleados(data),
      'edit_empleados': () => editEmpleados(data),
      'delete_empleados': () => deleteEmpleados(data),
      'set_proveedores': () => setProveedores(data),
      'edit_proveedores': () => editProveedores(data),
      'delete_proveedores': () => deleteProveedores(data),
      'set_inventarios': () => setInventarios(data),
      'edit_inventarios': () => editInventarios(data),
      'delete_inventarios': () => deleteInventarios(data),
      'set_ventas': () => setVentas(data),
      'edit_ventas': () => editVentas(data),
      'delete_ventas': () => deleteVentas(data),
      'set_detalles_ventas': () => setDetallesVentas(data),
      'edit_detalles_ventas': () => editDetallesVentas(data),
      'delete_detalles_ventas': () => deleteDetallesVentas(data),
      'set_soportes_tecnicos': () => setSoportesTecnicos(data),
      'edit_soportes_tecnicos': () => editSoportesTecnicos(data),
      'delete_soportes_tecnicos': () => deleteSoportesTecnicos(data)
    };

    const handler = routes[action];

    if (!handler) {
      return ContentService
      .createTextOutput(JSON.stringify({ success: false, message: action }))
      .setMimeType(ContentService.MimeType.JSON);
    }

    const result = handler();

    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService
    .createTextOutput(JSON.stringify({ success: false, message: error.message }))
    .setMimeType(ContentService.MimeType.JSON);
  }
}
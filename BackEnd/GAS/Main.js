const googleSheetsRef = PropertiesService.getScriptProperties().getProperty('GOOGLE_SHEETS_REF');

function doPost(e) {
  try {
    const action = e.parameter.action || e.postData.contents && JSON.parse(e.postData.contents).action;
    const data = JSON.parse(e.postData.contents);

    const routes = {
      'set_clientes': () => setClients(data),
      'edit_clientes': () => editClients(data),
      'delete_clientes': () => deleteClients(data),
      'get_clientes': () => getClients(data),
      'set_robots':  () => setRobots(data),
      'edit_robots': () => editRobots(data),
      'delete_robots': () => deleteRobots(data),
      'get_robots': () => getRobots(data),
      'set_empleados': () => setEmpleados(data),
      'edit_empleados': () => editEmpleados(data),
      'delete_empleados': () => deleteEmpleados(data),
      'get_empleados': () => getEmpleados(data),
      'set_proveedores': () => setProveedores(data),
      'edit_proveedores': () => editProveedores(data),
      'delete_proveedores': () => deleteProveedores(data),
      'get_proveedores': () => getProveedores(data),
      'set_inventarios': () => setInventarios(data),
      'edit_inventarios': () => editInventarios(data),
      'delete_inventarios': () => deleteInventarios(data),
      'get_inventarios': () => getInventarios(data),
      'set_ventas': () => setVentas(data),
      'edit_ventas': () => editVentas(data),
      'delete_ventas': () => deleteVentas(data),
      'get_ventas': () => getVentas(data),
      'set_detalles_ventas': () => setDetallesVentas(data),
      'edit_detalles_ventas': () => editDetallesVentas(data),
      'delete_detalles_ventas': () => deleteDetallesVentas(data),
      'get_detalles_ventas': () => getDetallesVentas(data),
      'set_soportes_tecnicos': () => setSoportesTecnicos(data),
      'edit_soportes_tecnicos': () => editSoportesTecnicos(data),
      'delete_soportes_tecnicos': () => deleteSoportesTecnicos(data),
      'get_soportes_tecnicos': () => getSoportesTecnicos(data)
    };

    const handler = routes[action];

    if (!handler) {
      return ContentService
      .createTextOutput(JSON.stringify({ success: false, message: action ? `Acción no reconocida: ${action}` : "No se especificó una acción" }))
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

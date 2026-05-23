// Guardar datos en sheets
function setVentas(data) {
  const fields = ['id_cliente', 'id_empleado', 'total'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Ventas');
  let newId = 1;
  
  try {
    const lastRow = sheet.getLastRow();
    
    if (lastRow >= 2) {
      const lastId = sheet.getRange(lastRow, 1).getValue();
      
      if (typeof lastId === 'number' && !isNaN(lastId)) {
        newId = lastId + 1;
      } else {
        newId = 1;
      }
    } else {
      newId = 1;
    }
  } catch (error) {
    console.error('Error al generar ID:', error);
    newId = 1;
  }
  
  // Agregar el ID al inicio de la fila
  rowToAppend.push(newId);
  
  const date = Utilities.formatDate(new Date(), 'America/Bogota', 'yyyy-MM-dd HH:mm:ss');
  rowToAppend.push(date);
  
  // Procesar cada campo
  fields.forEach(field => {
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    // Personaliza las transformaciones según el campo
    if (field === 'id_cliente') value = value ? +value : '';
    if (field === 'id_empleado') value = value ? +value : '';
    if (field === 'total') value = value ? parseFloat(value) : 0;

    rowToAppend.push(value);
  });
  
  // Agregar la fila completa a la hoja
  sheet.appendRow(rowToAppend);
  
  return {
    success: true,
    id: newId,
    message: `Registro agregado exitosamente con ID: ${newId}`
  };
}


// Editar datos en sheets
function editVentas(data) {
  const fields = ['id_cliente', 'id_empleado', 'total'];

  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Ventas');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_venta) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró la venta con ID: ${+data.id_venta}`
    };
  }

  // Procesar y actualizar cada campo (columnas 3 a 5, porque col 1 es ID y col 2 es fecha)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;

    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];

    if (field === 'id_cliente') value = value ? +value : '';
    if (field === 'id_empleado') value = value ? +value : '';
    if (field === 'total') value = value ? +value : 0;

    sheet.getRange(targetRow, index + 3).setValue(value); // +3 porque col 1 es ID, col 2 es fecha
  });

  return {
    success: true,
    id: data.id_venta,
    message: `Venta con ID ${data.id_venta} actualizada exitosamente`
  };
}


// Eliminar fila en sheets
function deleteVentas(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Ventas');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_venta) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró la venta con ID: ${data.id_venta}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_venta,
    message: `Venta con ID ${data.id_venta} eliminada exitosamente`
  };
}

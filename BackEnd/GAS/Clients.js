// Guardar datos en sheets
function setClients(data) {
  const fields = ['cedula', 'nombre', 'correo', 'telefono', 'direccion'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Clientes');
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
  
  // Procesar cada campo
  fields.forEach(field => {
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    // Personaliza las transformaciones según el campo
    if (field === 'cedula') {
      value = value ? String(value).trim() : '';
    }
    if (field === 'nombre') {
      value = value ? String(value).toUpperCase().trim() : '';
    }
    if (field === 'correo') {
      value = value ? String(value).toLowerCase().trim() : '';
    }
    if (field === 'telefono') {
      value = value ? String(value).trim() : '';
    }
    if (field === 'direccion') {
      value = value ? String(value).toUpperCase().trim() : '';
    }

    rowToAppend.push(value);
  });
  
  const date = Utilities.formatDate(new Date(), 'America/Bogota', 'yyyy-MM-dd HH:mm:ss');
  rowToAppend.push(date);
  
  // Agregar la fila completa a la hoja
  sheet.appendRow(rowToAppend);
  
  return {
    success: true,
    id: newId,
    message: `Registro agregado exitosamente con ID: ${newId}`
  };
}


// Editar datos en sheets
function editClients(data) {
  const fields = ['cedula', 'nombre', 'correo', 'telefono', 'direccion'];

  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Clientes');

  // Buscar la fila por id_cliente (columna 1)
  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_cliente) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el cliente con ID: ${+data.id_cliente}`
    };
  }

  // Procesar y actualizar cada campo (columnas 2 a 6)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;

    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];

    if (field === 'cedula')   value = value ? String(value).trim() : '';
    if (field === 'nombre')   value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'correo')   value = value ? String(value).toLowerCase().trim() : '';
    if (field === 'telefono') value = value ? String(value).trim() : '';
    if (field === 'direccion') value = value ? String(value).toUpperCase().trim() : '';

    sheet.getRange(targetRow, index + 2).setValue(value); // +2 porque col 1 es el ID
  });

  return {
    success: true,
    id: data.id_cliente,
    message: `Cliente con ID ${data.id_cliente} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteClients(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Clientes');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_cliente) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el cliente con ID: ${data.id_cliente}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_cliente,
    message: `Cliente con ID ${data.id_cliente} eliminado exitosamente`
  };
}
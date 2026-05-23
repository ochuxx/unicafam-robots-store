// Guardar datos en sheets
function setProveedores(data) {
  const fields = ['nombre_empresa', 'contacto', 'telefono', 'correo'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Proveedores');
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
    if (field === 'nombre_empresa') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'contacto') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'telefono') value = value ? String(value).trim() : '';
    if (field === 'correo') value = value ? String(value).toLowerCase().trim() : '';

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
function editProveedores(data) {
  const fields = ['nombre_empresa', 'contacto', 'telefono', 'correo'];

  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Proveedores');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_proveedor) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el proveedor con ID: ${+data.id_proveedor}`
    };
  }

  // Procesar y actualizar cada campo (columnas 2 a 5)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;

    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];

    if (field === 'nombre_empresa') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'contacto') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'telefono') value = value ? String(value).trim() : '';
    if (field === 'correo') value = value ? String(value).toLowerCase().trim() : '';

    sheet.getRange(targetRow, index + 2).setValue(value); // +2 porque col 1 es el ID
  });

  return {
    success: true,
    id: data.id_proveedor,
    message: `Proveedor con ID ${data.id_proveedor} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteProveedores(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Proveedores');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_proveedor) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el proveedor con ID: ${data.id_proveedor}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_proveedor,
    message: `Proveedor con ID ${data.id_proveedor} eliminado exitosamente`
  };
}

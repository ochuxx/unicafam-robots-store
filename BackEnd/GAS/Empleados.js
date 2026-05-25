// Guardar datos en sheets
function setEmpleados(data) {
  const fields = ['nombre', 'cargo', 'correo', 'telefono'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Empleados');
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
    if (field === 'nombre') value = value ? String(value).trim() : '';
    if (field === 'cargo') value = value ? String(value).trim() : '';
    if (field === 'correo') value = value ? String(value).toLowerCase().trim() : '';
    if (field === 'telefono') value = value ? String(value).trim() : '';
    
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
function editEmpleados(data) {
  const fields = ['nombre', 'cargo', 'correo', 'telefono'];
  
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Empleados');
  
  const lastRow = sheet.getLastRow();
  let targetRow = null;
  
  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_empleado) {
      targetRow = i;
      break;
    }
  }
  
  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el empleado con ID: ${+data.id_empleado}`
    };
  }
  
  // Procesar y actualizar cada campo (columnas 2 a 5)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;
    
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    if (field === 'nombre') value = value ? String(value).trim() : '';
    if (field === 'cargo') value = value ? String(value).trim() : '';
    if (field === 'correo') value = value ? String(value).toLowerCase().trim() : '';
    if (field === 'telefono') value = value ? String(value).trim() : '';
    
    sheet.getRange(targetRow, index + 2).setValue(value); // +2 porque col 1 es el ID
  });
  
  return {
    success: true,
    id: data.id_empleado,
    message: `Empleado con ID ${data.id_empleado} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteEmpleados(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Empleados');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_empleado) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el empleado con ID: ${data.id_empleado}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_empleado,
    message: `Empleado con ID ${data.id_empleado} eliminado exitosamente`
  };
}


// Obtener datos desde sheets
function getEmpleados(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Empleados');
  const params = normalizeGetParams(data);
  const defaultFields = ['id', 'nombre', 'cargo', 'correo', 'telefono'];

  let records = sheetToObjects(sheet).map(mapEmpleadoRecord);

  if (params.limit) {
    records = records.slice(0, params.limit);
  }

  const fields = params.fields.length ? params.fields : defaultFields;
  records = applyFieldSelection(records, fields);

  return {
    success: true,
    data: records
  };
}

function mapEmpleadoRecord(record) {
  const id = record.id || record.id_empleado || record['id_empleado'];

  return {
    id: id !== undefined && id !== null ? String(id).trim() : '',
    nombre: record.nombre || '',
    cargo: record.cargo || '',
    correo: record.correo || '',
    telefono: record.telefono || ''
  };
}

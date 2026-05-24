// Guardar datos en sheets
function setClients(data) {
  const fields = ['nit', 'nombre', 'correo', 'telefono', 'direccion'];
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
    if (field === 'nit') {
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

  const fields = ['nit', 'nombre', 'correo', 'telefono', 'direccion'];
  
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Clientes');
  
  // Buscar la fila por id_cliente (columna 1)
  const lastRow = sheet.getLastRow();
  let targetRow = null;
  
  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    const nit = sheet.getRange(i, 2).getValue();
    if (cellId == +data.id_cliente || nit == +data.nit) {
      targetRow = i;
      break;
    }
  }
  
  if (!targetRow) {
    return {
      success: false,
      message: data.id_cliente ? `No se encontró el cliente con ID: ${+data.id_cliente}` : `No se encontró el cliente con NIT: ${+data.nit}, la última fila leida de la db es ${lastRow}`
    };
  }
  
  // Procesar y actualizar cada campo (columnas 2 a 6)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;
    
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    if (field === 'nit')   value = value ? String(value).trim() : '';
    if (field === 'nombre')   value = value ? String(value).trim() : '';
    if (field === 'correo')   value = value ? String(value).toLowerCase().trim() : '';
    if (field === 'telefono') value = value ? String(value).trim() : '';
    if (field === 'direccion') value = value ? String(value).trim() : '';
    
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
    const nit = sheet.getRange(i, 2).getValue();
    if (cellId === +data.id_cliente || nit === +data.nit) {
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


// Obtener datos desde sheets
function getClients(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Clientes');
  const params = normalizeGetParams(data);
  const defaultFields = ['nit', 'nombre', 'correo', 'telefono', 'direccion', 'fecha_registro'];

  let records = sheetToObjects(sheet).map(mapClientRecord);

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

function mapClientRecord(record) {
  const nit = record.nit || record.cedula || record.NIT || record.id_cliente || record.id;
  
  // Busca la fecha en múltiples posibles nombres de columna (insensible a mayúsculas/minúsculas)
  let fecha = null;
  const possibleDateKeys = [
    'fecha_registro'
  ];
  
  for (const key of possibleDateKeys) {
    if (record.hasOwnProperty(key) && record[key] !== null && record[key] !== undefined) {
      fecha = record[key];
      break;
    }
  }

  return {
    nit: nit !== undefined && nit !== null ? String(nit).trim() : '',
    nombre: record.nombre || '',
    correo: record.correo || '',
    telefono: record.telefono || '',
    direccion: record.direccion || '',
    fecha_registro: record.fecha_registro || fecha || ''
  };
}
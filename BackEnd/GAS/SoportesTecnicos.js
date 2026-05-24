// Guardar datos en sheets
function setSoportesTecnicos(data) {
  // Validate input data
  if (!validateTextLength(data.problema, 1, 500)) {
    return {
      success: false,
      message: 'Problema es requerido y debe tener entre 1 y 500 caracteres'
    };
  }
  
  if (!validateTextLength(data.estado, 1, 50)) {
    return {
      success: false,
      message: 'Estado es requerido y debe tener entre 1 y 50 caracteres'
    };
  }
  
  if (!validateNumericId(data.id_cliente)) {
    return {
      success: false,
      message: 'ID de cliente es requerido y debe ser un número positivo'
    };
  }
  
  if (!validateNumericId(data.id_robot)) {
    return {
      success: false,
      message: 'ID de robot es requerido y debe ser un número positivo'
    };
  }
  
  const fields = ['problema', 'estado', 'id_cliente', 'id_robot'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Soportes_Tecnicos');
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
    if (field === 'problema') value = value ? String(value).trim() : '';
    if (field === 'estado') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'id_cliente') value = value ? +value : '';
    if (field === 'id_robot') value = value ? +value : '';
    
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
function editSoportesTecnicos(data) {
  // Validate ID
  if (!validateNumericId(data.id_soporte)) {
    return {
      success: false,
      message: 'ID de soporte es requerido y debe ser un número positivo'
    };
  }
  
  // Validate input data if provided
  if (data.problema !== undefined && !validateTextLength(data.problema, 1, 500)) {
    return {
      success: false,
      message: 'Problema debe tener entre 1 y 500 caracteres'
    };
  }
  
  if (data.estado !== undefined && !validateTextLength(data.estado, 1, 50)) {
    return {
      success: false,
      message: 'Estado debe tener entre 1 y 50 caracteres'
    };
  }
  
  if (data.id_cliente !== undefined && !validateNumericId(data.id_cliente)) {
    return {
      success: false,
      message: 'ID de cliente debe ser un número positivo'
    };
  }
  
  if (data.id_robot !== undefined && !validateNumericId(data.id_robot)) {
    return {
      success: false,
      message: 'ID de robot debe ser un número positivo'
    };
  }
  
  const fields = ['problema', 'estado', 'id_cliente', 'id_robot'];
  
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Soportes_Tecnicos');
  
  const lastRow = sheet.getLastRow();
  let targetRow = null;
  
  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_soporte) {
      targetRow = i;
      break;
    }
  }
  
  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el soporte con ID: ${+data.id_soporte}`
    };
  }
  
  // Procesar y actualizar cada campo (columnas 3 a 6, porque col 1 es ID y col 2 es fecha)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;
    
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    if (field === 'problema') value = value ? String(value).trim() : '';
    if (field === 'estado') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'id_cliente') value = value ? +value : '';
    if (field === 'id_robot') value = value ? +value : '';
    
    sheet.getRange(targetRow, index + 3).setValue(value); // +3 porque col 1 es ID, col 2 es fecha
  });
  
  return {
    success: true,
    id: data.id_soporte,
    message: `Soporte con ID ${data.id_soporte} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteSoportesTecnicos(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Soportes_Tecnicos');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_soporte) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el soporte con ID: ${data.id_soporte}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_soporte,
    message: `Soporte con ID ${data.id_soporte} eliminado exitosamente`
  };
}


// Obtener datos desde sheets
function getSoportesTecnicos(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Soportes_Tecnicos');
  const params = normalizeGetParams(data);
  const defaultFields = ['id', 'fecha_reporte', 'problema', 'estado', 'id_cliente', 'id_robot'];

  let records = sheetToObjects(sheet).map(mapSoporteRecord);

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

function mapSoporteRecord(record) {
  const id = record.id || record.id_soporte || record['id_soporte'];
  const fecha = record.fecha_reporte || record.fecha || record.fechaReporte || record['fecha_reporte'];

  return {
    id: id !== undefined && id !== null ? String(id).trim() : '',
    fecha_reporte: normalizeDateValue(fecha),
    problema: record.problema || '',
    estado: record.estado || '',
    id_cliente: record.id_cliente || '',
    id_robot: record.id_robot || ''
  };
}

// Guardar datos en sheets
function setRobots(data) {
  const fields = ['nombre_robot', 'descripcion', 'tipo'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Robots');
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
    if (field === 'nombre_robot') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'descripcion')  value = value ? String(value).trim() : '';
    if (field === 'tipo') value = value ? String(value).toUpperCase().trim() : '';
    
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
function editRobots(data) {
  const fields = ['nombre_robot', 'descripcion', 'tipo'];
  
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Robots');
  
  const lastRow = sheet.getLastRow();
  let targetRow = null;
  
  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_robot) {
      targetRow = i;
      break;
    }
  }
  
  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el robot con ID: ${+data.id_robot}`
    };
  }
  
  // Procesar y actualizar cada campo (columnas 2 a 4)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;
    
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    if (field === 'nombre_robot') value = value ? String(value).toUpperCase().trim() : '';
    if (field === 'descripcion')  value = value ? String(value).trim() : '';
    if (field === 'tipo') value = value ? String(value).toUpperCase().trim() : '';
    
    sheet.getRange(targetRow, index + 2).setValue(value); // +2 porque col 1 es el ID
  });
  
  return {
    success: true,
    id: data.id_robot,
    message: `Robot con ID ${data.id_robot} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteRobots(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Robots');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_robot) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el cliente con ID: ${data.id_robot}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_robot,
    message: `Cliente con ID ${data.id_robot} eliminado exitosamente`
  };
}


// Obtener datos desde sheets
function getRobots(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Robots');
  const params = normalizeGetParams(data);
  const defaultFields = ['id', 'nombre', 'descripcion', 'tipo'];

  let records = sheetToObjects(sheet).map(mapRobotRecord);

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

function mapRobotRecord(record) {
  const id = record.id || record.id_robot || record['id_robot'];

  return {
    id: id !== undefined && id !== null ? String(id).trim() : '',
    nombre: record.nombre || record.nombre_robot || '',
    descripcion: record.descripcion || '',
    tipo: record.tipo || ''
  };
}

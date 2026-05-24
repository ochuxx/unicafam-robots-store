// Guardar datos en sheets
function setInventarios(data) {
  // Validate input data
  if (data.precio !== undefined && (!validateNumericId(data.precio) || Number(data.precio) < 0)) {
    return {
      success: false,
      message: 'Precio debe ser un número positivo'
    };
  }
  
  if (data.stock !== undefined && (!validateNumericId(data.stock) || Number(data.stock) < 0)) {
    return {
      success: false,
      message: 'Stock debe ser un número positivo'
    };
  }
  
  if (data.id_robot !== undefined && !validateTextLength(data.id_robot, 1, 50)) {
    return {
      success: false,
      message: 'ID de robot es requerido y debe tener entre 1 y 50 caracteres'
    };
  }
  
  if (data.id_proveedor !== undefined && !validateTextLength(data.id_proveedor, 1, 50)) {
    return {
      success: false,
      message: 'ID de proveedor es requerido y debe tener entre 1 y 50 caracteres'
    };
  }
  
  const fields = ['precio', 'stock', 'id_robot', 'id_proveedor'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Inventarios');
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
    if (field === 'precio') value = value ? parseFloat(value) : 0;
    if (field === 'stock') value = value ? +value : 0;
    if (field === 'id_robot') value = value ? +value : '';
    if (field === 'id_proveedor') value = value ? +value : '';
    
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
function editInventarios(data) {
  // Validate ID
  if (!validateNumericId(data.id_inventario)) {
    return {
      success: false,
      message: 'ID de inventario es requerido y debe ser un número positivo'
    };
  }
  
  // Validate input data if provided
  if (data.precio !== undefined && (!validateNumericId(data.precio) || Number(data.precio) < 0)) {
    return {
      success: false,
      message: 'Precio debe ser un número positivo'
    };
  }
  
  if (data.stock !== undefined && (!validateNumericId(data.stock) || Number(data.stock) < 0)) {
    return {
      success: false,
      message: 'Stock debe ser un número positivo'
    };
  }
  
  if (data.id_robot !== undefined && !validateTextLength(data.id_robot, 1, 50)) {
    return {
      success: false,
      message: 'ID de robot debe tener entre 1 y 50 caracteres'
    };
  }
  
  if (data.id_proveedor !== undefined && !validateTextLength(data.id_proveedor, 1, 50)) {
    return {
      success: false,
      message: 'ID de proveedor debe tener entre 1 y 50 caracteres'
    };
  }
  
  const fields = ['precio', 'stock', 'id_robot', 'id_proveedor'];
  
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Inventarios');
  
  const lastRow = sheet.getLastRow();
  let targetRow = null;
  
  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_inventario) {
      targetRow = i;
      break;
    }
  }
  
  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el inventario con ID: ${+data.id_inventario}`
    };
  }
  
  // Procesar y actualizar cada campo (columnas 2 a 5)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;
    
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    if (field === 'precio') value = value ? parseFloat(value) : 0;
    if (field === 'stock') value = value ? +value : 0;
    if (field === 'id_robot') value = value ? +value : '';
    if (field === 'id_proveedor') value = value ? +value : '';
    
    sheet.getRange(targetRow, index + 2).setValue(value); // +2 porque col 1 es el ID
  });
  
  return {
    success: true,
    id: data.id_inventario,
    message: `Inventario con ID ${data.id_inventario} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteInventarios(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Inventarios');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_inventario) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el inventario con ID: ${data.id_inventario}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_inventario,
    message: `Inventario con ID ${data.id_inventario} eliminado exitosamente`
  };
}


// Obtener datos desde sheets
function getInventarios(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Inventarios');
  const params = normalizeGetParams(data);
  const defaultFields = ['id', 'precio', 'stock', 'fecha_registro', 'id_robot', 'id_proveedor'];

  let records = sheetToObjects(sheet).map(mapInventarioRecord);

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

function mapInventarioRecord(record) {
  const id = record.id || record.id_inventario || record['id_inventario'];
  const fecha = record.fecha_registro || record.fecha || record.fechaRegistro || record['fecha_registro'];

  return {
    id: id !== undefined && id !== null ? String(id).trim() : '',
    precio: record.precio !== undefined && record.precio !== null ? record.precio : '',
    stock: record.stock !== undefined && record.stock !== null ? record.stock : '',
    fecha_registro: normalizeDateValue(fecha),
    id_robot: record.id_robot || '',
    id_proveedor: record.id_proveedor || ''
  };
}

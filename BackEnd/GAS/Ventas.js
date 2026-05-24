// Guardar datos en sheets
function setVentas(data) {
  // Validate input data
  if (!validateNumericId(data.id_cliente)) {
    return {
      success: false,
      message: 'ID de cliente es requerido y debe ser un número positivo'
    };
  }
  
  if (!validateNumericId(data.id_empleado)) {
    return {
      success: false,
      message: 'ID de empleado es requerido y debe ser un número positivo'
    };
  }
  
  if (data.total !== undefined && (!validateNumericId(data.total) || Number(data.total) < 0)) {
    return {
      success: false,
      message: 'Total debe ser un número positivo'
    };
  }
  
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
  // Validate ID
  if (!validateNumericId(data.id_venta)) {
    return {
      success: false,
      message: 'ID de venta es requerido y debe ser un número positivo'
    };
  }
  
  // Validate input data if provided
  if (data.id_cliente !== undefined && !validateNumericId(data.id_cliente)) {
    return {
      success: false,
      message: 'ID de cliente debe ser un número positivo'
    };
  }
  
  if (data.id_empleado !== undefined && !validateNumericId(data.id_empleado)) {
    return {
      success: false,
      message: 'ID de empleado debe ser un número positivo'
    };
  }
  
  if (data.total !== undefined && (!validateNumericId(data.total) || Number(data.total) < 0)) {
    return {
      success: false,
      message: 'Total debe ser un número positivo'
    };
  }
  
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


// Obtener datos desde sheets
function getVentas(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Ventas');
  const params = normalizeGetParams(data);
  const defaultFields = ['id', 'fecha_venta', 'total', 'id_cliente', 'id_empleado'];

  let records = sheetToObjects(sheet).map(mapVentaRecord);

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

function mapVentaRecord(record) {
  const id = record.id || record.id_venta || record['id_venta'];
  const fecha = record.fecha_venta || record.fecha || record.fechaVenta || record['fecha_venta'];

  return {
    id: id !== undefined && id !== null ? String(id).trim() : '',
    fecha_venta: normalizeDateValue(fecha),
    total: record.total !== undefined && record.total !== null ? record.total : '',
    id_cliente: record.id_cliente || '',
    id_empleado: record.id_empleado || ''
  };
}

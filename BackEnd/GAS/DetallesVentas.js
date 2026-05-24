// Guardar datos en sheets
function setDetallesVentas(data) {
  // Validate input data
  if (data.cantidad !== undefined && (!validateNumericId(data.cantidad) || Number(data.cantidad) < 0)) {
    return {
      success: false,
      message: 'Cantidad debe ser un número positivo'
    };
  }
  
  if (data.subtotal !== undefined && (!validateNumericId(data.subtotal) || Number(data.subtotal) < 0)) {
    return {
      success: false,
      message: 'Subtotal debe ser un número positivo'
    };
  }
  
  if (!validateNumericId(data.id_venta)) {
    return {
      success: false,
      message: 'ID de venta es requerido y debe ser un número positivo'
    };
  }
  
  if (!validateNumericId(data.id_inventario)) {
    return {
      success: false,
      message: 'ID de inventario es requerido y debe ser un número positivo'
    };
  }
  
  const fields = ['cantidad', 'subtotal', 'id_venta', 'id_inventario'];
  const rowToAppend = [];
  
  // Generar ID autoincremental
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Detalles_Ventas');
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
    if (field === 'cantidad') value = value ? +value : 0;
    if (field === 'subtotal') value = value ? parseFloat(value) : 0;
    if (field === 'id_venta') value = value ? +value : '';
    if (field === 'id_inventario') value = value ? +value : '';
    
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
function editDetallesVentas(data) {
  // Validate ID
  if (!validateNumericId(data.id_detalle)) {
    return {
      success: false,
      message: 'ID de detalle es requerido y debe ser un número positivo'
    };
  }
  
  // Validate input data if provided
  if (data.cantidad !== undefined && (!validateNumericId(data.cantidad) || Number(data.cantidad) < 0)) {
    return {
      success: false,
      message: 'Cantidad debe ser un número positivo'
    };
  }
  
  if (data.subtotal !== undefined && (!validateNumericId(data.subtotal) || Number(data.subtotal) < 0)) {
    return {
      success: false,
      message: 'Subtotal debe ser un número positivo'
    };
  }
  
  if (data.id_venta !== undefined && !validateNumericId(data.id_venta)) {
    return {
      success: false,
      message: 'ID de venta debe ser un número positivo'
    };
  }
  
  if (data.id_inventario !== undefined && !validateNumericId(data.id_inventario)) {
    return {
      success: false,
      message: 'ID de inventario debe ser un número positivo'
    };
  }
  
  const fields = ['cantidad', 'subtotal', 'id_venta', 'id_inventario'];
  
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Detalles_Ventas');
  
  const lastRow = sheet.getLastRow();
  let targetRow = null;
  
  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_detalle) {
      targetRow = i;
      break;
    }
  }
  
  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el detalle con ID: ${+data.id_detalle}`
    };
  }
  
  // Procesar y actualizar cada campo (columnas 2 a 5)
  fields.forEach((field, index) => {
    if (data[field] === undefined) return;
    
    let value = typeof data[field] === 'boolean' ? +data[field] : data[field];
    
    if (field === 'cantidad') value = value ? +value : 0;
    if (field === 'subtotal') value = value ? parseFloat(value) : 0;
    if (field === 'id_venta') value = value ? +value : '';
    if (field === 'id_inventario') value = value ? +value : '';
    
    sheet.getRange(targetRow, index + 2).setValue(value); // +2 porque col 1 es el ID
  });
  
  return {
    success: true,
    id: data.id_detalle,
    message: `Detalle con ID ${data.id_detalle} actualizado exitosamente`
  };
}


// Eliminar fila en sheets
function deleteDetallesVentas(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Detalles_Ventas');

  const lastRow = sheet.getLastRow();
  let targetRow = null;

  for (let i = 2; i <= lastRow; i++) {
    const cellId = sheet.getRange(i, 1).getValue();
    if (cellId === +data.id_detalle) {
      targetRow = i;
      break;
    }
  }

  if (!targetRow) {
    return {
      success: false,
      message: `No se encontró el detalle con ID: ${data.id_detalle}`
    };
  }

  sheet.deleteRow(targetRow);

  return {
    success: true,
    id: data.id_detalle,
    message: `Detalle con ID ${data.id_detalle} eliminado exitosamente`
  };
}


// Obtener datos desde sheets
function getDetallesVentas(data) {
  const sheet = SpreadsheetApp.openById(googleSheetsRef).getSheetByName('Detalles_Ventas');
  const params = normalizeGetParams(data);
  const defaultFields = ['id', 'id_venta', 'id_inventario', 'cantidad', 'subtotal'];

  let records = sheetToObjects(sheet).map(mapDetalleVentaRecord);

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

function mapDetalleVentaRecord(record) {
  const id = record.id || record.id_detalle || record['id_detalle'];

  return {
    id: id !== undefined && id !== null ? String(id).trim() : '',
    id_venta: record.id_venta || '',
    id_inventario: record.id_inventario || '',
    cantidad: record.cantidad !== undefined && record.cantidad !== null ? record.cantidad : '',
    subtotal: record.subtotal !== undefined && record.subtotal !== null ? record.subtotal : ''
  };
}

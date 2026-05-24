function normalizeGetParams(data) {
  return {
    limit: normalizeGetLimit(data),
    fields: normalizeGetFields(data)
  };
}

function normalizeGetFields(data) {
  if (!data) return [];

  const raw = data.fields || data.campos;
  if (!raw) return [];

  if (Array.isArray(raw)) {
    return raw
      .map(item => String(item).trim())
      .filter(Boolean);
  }

  if (typeof raw === 'string') {
    return raw
      .split(',')
      .map(item => item.trim())
      .filter(Boolean);
  }

  return [];
}

function normalizeGetLimit(data) {
  if (!data) return 0;

  const raw = data.n || data.limit || data.cantidad || data.count;
  const parsed = parseInt(raw, 10);

  if (isNaN(parsed) || parsed < 1) return 0;

  return parsed;
}

function applyFieldSelection(records, fields) {
  if (!fields || fields.length === 0) return records;

  return records.map(record => pickFields(record, fields));
}

function pickFields(record, fields) {
  const picked = {};

  fields.forEach(field => {
    if (Object.prototype.hasOwnProperty.call(record, field)) {
      picked[field] = record[field];
    }
  });

  return picked;
}

function sheetToObjects(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();

  if (lastRow < 2 || lastCol < 1) return [];

  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  const rows = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();

  return rows.map(row => {
    const record = {};

    headers.forEach((header, index) => {
      const key = header ? String(header).trim() : '';
      if (!key) return;
      record[key] = row[index];
    });

    return record;
  });
}

function normalizeDateValue(value) {
  if (!value) return '';

  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value)) {
    return Utilities.formatDate(value, 'America/Bogota', 'yyyy-MM-dd');
  }

  return String(value);
}

// Validation functions
function validatePhone(value) {
  if (!value) return true; // Optional field
  // Remove all non-digit characters and check if what remains are all digits
  const cleaned = value.toString().replace(/\D/g, '');
  return /^\d+$/.test(cleaned) && cleaned.length >= 7 && cleaned.length <= 15;
}

function validateEmail(value) {
  if (!value) return true; // Optional field
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(value);
}

function validateTextLength(value, minLength = 1, maxLength = 100) {
  if (!value && minLength === 0) return true; // Optional and empty is OK
  if (!value) return false; // Required but empty
  const strValue = String(value);
  return strValue.length >= minLength && strValue.length <= maxLength;
}

function validateNumericId(value) {
  if (!value) return false; // ID is required
  const numValue = Number(value);
  return !isNaN(numValue) && numValue > 0 && Number.isInteger(numValue);
}

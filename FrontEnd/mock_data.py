# mock_data.py - 1000 registros por tabla (todos los NIT de clientes son únicos)
from datetime import datetime, timedelta
import random

# =============================================
# 1. CLIENTES (NIT único)
# =============================================
clientes_mock = []
for i in range(1, 1001):
    nit = f"900{i:06d}-{i%10}"
    clientes_mock.append({
        "nit": nit,
        "nombre": f"Cliente {i}",
        "correo": f"cliente{i}@mail.com",
        "telefono": f"300{random.randint(1000000, 9999999)}",
        "direccion": f"Calle {i} # {i%20}-{i%10}, Bogotá",
        "fecha_registro": (datetime(2024, 1, 1) + timedelta(days=i)).strftime("%Y-%m-%d")
    })

# =============================================
# 2. PROVEEDORES (NIT único)
# =============================================
proveedores_mock = []
for i in range(1, 1001):
    proveedores_mock.append({
        "nit": f"800{i:06d}-{i%10}",
        "nombre_empresa": f"Proveedor S.A.S. {i}",
        "contacto": f"Contacto {i}",
        "telefono": f"310{random.randint(1000000, 9999999)}",
        "correo": f"proveedor{i}@empresa.com"
    })

# =============================================
# 3. ROBOTS (Número de serie único)
# =============================================
robots_mock = []
tipos_robot = ["Hogar", "Industrial", "Educativo", "Médico", "Seguridad"]
for i in range(1, 1001):
    robots_mock.append({
        "id": f"SER-{i:04d}",
        "nombre": f"Robot Modelo {i}",
        "descripcion": f"Robot versión {i}.0 para {random.choice(tipos_robot)}",
        "tipo": random.choice(tipos_robot)
    })

# =============================================
# 4. EMPLEADOS (ID autoincremental)
# =============================================
empleados_mock = []
cargos = ["Vendedor", "Técnico Soporte", "Gerente", "Almacenista", "Contador"]
for i in range(1, 1001):
    empleados_mock.append({
        "id": random.randint(1000, 9999),
        "nombre": f"Empleado {i}",
        "cargo": random.choice(cargos),
        "correo": f"empleado{i}@smartbot.com",
        "telefono": f"320{random.randint(1000000, 9999999)}"
    })

# =============================================
# 5. INVENTARIO (Código de barras único)
# =============================================
inventario_mock = []
for i in range(1, 1001):
    codigo_barras = f"1234567890{i:04d}"
    inventario_mock.append({
        "id": codigo_barras,
        "precio": random.randint(500000, 20000000),
        "stock": random.randint(1, 50),
        "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
        "id_proveedor": proveedores_mock[i-1]["nit"],
        "id_robot": robots_mock[i-1]["id"]
    })

# =============================================
# 6. VENTAS (ID autoincremental)
# =============================================
ventas_mock = []
for i in range(1, 1001):
    cliente = random.choice(clientes_mock)
    empleado = random.choice(empleados_mock)
    ventas_mock.append({
        "id": i,
        "fecha_venta": (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 135))).strftime("%Y-%m-%d"),
        "total": 0,
        "id_cliente": cliente["nit"],
        "id_empleado": empleado["id"]
    })

# =============================================
# 7. DETALLE_VENTA (ID autoincremental)
# =============================================
detalle_ventas_mock = []
detalle_id = 1
for venta in ventas_mock:
    num_productos = random.randint(1, 3)
    productos_seleccionados = random.sample(inventario_mock, min(num_productos, len(inventario_mock)))
    total_venta = 0
    for producto in productos_seleccionados:
        cantidad = random.randint(1, 5)
        subtotal = producto["precio"] * cantidad
        detalle_ventas_mock.append({
            "id": detalle_id,
            "id_venta": venta["id"],
            "id_inventario": producto["id"],
            "cantidad": cantidad,
            "subtotal": subtotal
        })
        detalle_id += 1
        total_venta += subtotal
    venta["total"] = total_venta

# =============================================
# 8. SOPORTE_TECNICO (ID autoincremental)
# =============================================
soporte_mock = []
estados = ["Pendiente", "En proceso", "Resuelto", "Cancelado"]
for i in range(1, 1001):
    cliente = random.choice(clientes_mock)
    robot = random.choice(robots_mock)
    fecha_reporte = (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 135))).strftime("%Y-%m-%d")
    soporte_mock.append({
        "id": i,
        "fecha_reporte": fecha_reporte,
        "fecha_actualizacion": fecha_reporte,
        "problema": f"Falla reportada: {random.choice(['No enciende', 'Error de conexión', 'Batería baja', 'Sobrecalentamiento', 'Sensor dañado'])}",
        "estado": random.choice(estados),
        "id_cliente": cliente["nit"],
        "id_robot": robot["id"]
    })

# =============================================
# FUNCIÓN PARA EXPORTAR TODOS LOS DATOS
# =============================================
def get_all_mock_data():
    return {
        "clientes": clientes_mock,
        "proveedores": proveedores_mock,
        "robots": robots_mock,
        "empleados": empleados_mock,
        "inventario": inventario_mock,
        "ventas": ventas_mock,
        "detalle_ventas": detalle_ventas_mock,
        "soporte": soporte_mock
    }
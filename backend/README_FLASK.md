# Backend Flask

Backend Python para el Sistema de Comisiones, Agendas y Legalizaciones del SENA CBI
Palmira. La implementación utiliza exclusivamente Flask y PostgreSQL. Para ejecutar
Flask se usa `run.py`.

## Requisitos

- Python 3.11 o superior.
- PostgreSQL existente del proyecto.

## Instalación en PowerShell

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python run.py
```

Configure `backend/.env` antes de iniciar. El Compose actual publica PostgreSQL en
`localhost:5438`, por lo que el ejemplo Flask usa `DB_PORT=5438`. Si Flask corre
dentro de un contenedor de la misma red Docker, use `DB_HOST=db` y `DB_PORT=5432`.
No copie credenciales reales a Git.

## Catálogo de rutas de la API

Todas las rutas Flask comienzan con `/api`. La columna **rol** indica quién puede
usarla; `público` no requiere JWT. Las rutas marcadas como **futuras** son solamente
el catálogo funcional del módulo y todavía no existen en el servidor.

### Rutas implementadas

| Método | Ruta | Recibe | Devuelve | Rol | Estado |
|---|---|---|---|---|---|
| GET | `/api/salud` | Nada | `200`: `{"estado":"ok","base_datos":"conectada"}`. `503` si PostgreSQL no responde. | Público | Implementada |
| POST | `/api/auth/login` | JSON: `{"correo":"usuario@ejemplo.com","contrasena":"..."}` | `200`: `mensaje`, `token` JWT y `usuario` con `id`, `correo` y `rol`, sin hash. `401` por credenciales inválidas. `429` por exceso de intentos. | Público | Implementada |
| GET | `/api/dias-festivos?anio=2026` | Query `anio`, entero. | `200`: `{"anio":2026,"dias_festivos":[{"id":1,"fecha":"2026-01-01","nombre":"Año Nuevo","anio":2026}]}`. `400` si el año es inválido. `503` si la tabla o base no está disponible. | Público | Implementada si existe `dias_festivos` |

#### Ejemplo de respuesta del login

```json
{
  "mensaje": "Inicio de sesión exitoso",
  "token": "JWT_GENERADO",
  "usuario": {
    "id": "DEMO-S1-001",
    "correo": "usuario@ejemplo.com",
    "rol": "Comisionado contratista"
  }
}
```

El JWT contiene el identificador en `sub` y el rol en `rol`. Los hashes se verifican
contra `usuarios.contrasena_hash` y nunca se devuelven. El código utiliza las columnas
existentes del esquema y no presupone que los hashes de prueba correspondan a una
contraseña conocida.

### Rutas futuras del módulo

Las siguientes rutas documentan la API prevista para las tablas existentes, pero aún
no tienen Blueprint ni implementación. No deben probarse ni presentarse como
disponibles hasta que su lógica de negocio, permisos y validaciones sean aprobados.

| Método | Ruta futura | Recibe | Devolverá | Rol previsto | Estado |
|---|---|---|---|---|---|
| GET | `/api/contratos` | Filtros opcionales por año, contratista o estado. | Lista de contratos con fechas, contratista y supervisor. | Comisionado contratista, Supervisor del contrato | Futura |
| POST | `/api/contratos` | Sin procesamiento de datos en esta etapa. | HTTP 501 y mensaje de operación no implementada si la autorización supera. | Supervisor del contrato | Provisional S2-T02 |
| GET | `/api/agendas` | Filtros por usuario, estado y rango de fechas. | Lista de agendas y estado actual. | Todos los roles autenticados según permisos | Futura |
| GET | `/api/agendas/{id_agenda}` | Parámetro de ruta `id_agenda`. | Agenda, destinos, obligaciones, días y actividades. | Usuario autorizado sobre la agenda | Futura |
| POST | `/api/agendas` | JSON con tipo, contrato, fechas, objeto, destinos y actividades. | Agenda creada en estado inicial. | Comisionado contratista, Comisionado funcionario | Futura |
| PATCH | `/api/agendas/{id_agenda}/estado` | JSON con estado nuevo y comentario. | Agenda actualizada e historial del cambio. | Supervisor, Área de viáticos, Subdirector según transición | Futura |
| POST | `/api/agendas/{id_agenda}/revisiones` | JSON con decisión y observación. | Revisión registrada. | Supervisor del contrato, Área de viáticos | Futura |
| POST | `/api/agendas/{id_agenda}/firmas` | JSON con tipo de firma y referencia del archivo. | Firma registrada. | Subdirector del centro | Futura |
| GET | `/api/legalizaciones` | Filtros por agenda, responsable y estado. | Lista de legalizaciones. | Área de viáticos, responsables autorizados | Futura |
| GET | `/api/legalizaciones/{id_legalizacion}` | Parámetro de ruta `id_legalizacion`. | Legalización, gastos, soportes y revisiones. | Usuario autorizado | Futura |
| POST | `/api/legalizaciones` | JSON con agenda, responsable y observaciones. | Legalización creada en borrador. | Comisionado contratista, Comisionado funcionario | Futura |
| POST | `/api/legalizaciones/{id_legalizacion}/gastos` | JSON con tipo, fecha, descripción, valor y documento. | Gasto registrado. | Responsable de la legalización | Futura |
| POST | `/api/legalizaciones/{id_legalizacion}/revisiones` | JSON con decisión y observación. | Revisión de legalización registrada. | Área de viáticos | Futura |
| GET | `/api/viaticos` | Filtros por agenda, estado y fechas. | Comisiones y valores de viáticos calculados. | Área de viáticos | Futura |
| POST | `/api/viaticos/calcular` | JSON con agenda, fechas, destino y reglas aplicables. | Cálculo detallado de viáticos. | Área de viáticos | Futura |
| GET | `/api/notificaciones` | Filtros por destinatario y estado de lectura. | Notificaciones del usuario autenticado. | Todos los roles autenticados | Futura |
| PATCH | `/api/notificaciones/{id_notificacion}/leer` | Parámetro de ruta `id_notificacion`. | Notificación marcada como leída. | Destinatario autenticado | Futura |

Las rutas futuras se basan únicamente en las entidades observadas en el esquema:
`contratos`, `agendas`, `legalizaciones`, `gastos_legalizacion` y `notificaciones`.
Los nombres y contratos definitivos deben confirmarse antes de implementarlas.

El archivo [../database/S1_dias_festivos_2026_2027.sql](../database/S1_dias_festivos_2026_2027.sql)
debe revisarse y ejecutarse manualmente; Flask no ejecuta migraciones.

## Autorización por rol

Para futuras rutas protegidas se puede usar:

```python
from app.utils.permisos import requiere_roles

@ruta_protegida.get("")
@requiere_roles("Área de viáticos")
def vista_restringida():
    ...
```

El decorador verifica JWT y devuelve 403 cuando el rol no está autorizado.

## Pruebas

Con el entorno virtual activo:

```powershell
pytest -q
```

Las pruebas unitarias verifican salud, rechazo de credenciales, emisión de JWT con rol
y validación del año. La prueba de integración con PostgreSQL requiere la base
ejecutándose y credenciales válidas en `.env`.

Prueba manual:

```powershell
Invoke-RestMethod http://localhost:5000/api/salud

$body = @{
  correo = "prueba.s1.01@sena.edu.co"
  contrasena = "SenaDemo2026!"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/login `
  -ContentType "application/json" -Body $body

Invoke-RestMethod "http://localhost:5000/api/dias-festivos?anio=2026"
```

El dato de prueba anterior solo es válido si fue comprobado en la base de datos real.

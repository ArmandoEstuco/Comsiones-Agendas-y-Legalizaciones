# Backend Flask

Backend Python del Sistema de Comisiones, Agendas y Legalizaciones del SENA CBI
Palmira. La API utiliza Flask y PostgreSQL.

## Requisitos

- Python 3.11 o superior.
- PostgreSQL ejecutándose localmente o mediante Docker Compose.
- Las dependencias indicadas en `requirements.txt`.

## Instalación en PowerShell

Desde la raíz del proyecto:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure `backend/.env` antes de iniciar la aplicación. Con el Docker Compose
actual, PostgreSQL se publica en `localhost:5438`.

```dotenv
FLASK_DEBUG=false
PORT=5000
DB_HOST=localhost
DB_PORT=5438
DB_NAME=comisiones
DB_USER=admin_comisiones
DB_PASSWORD=
JWT_SECRET_KEY=
JWT_ACCESS_TOKEN_EXPIRES=8h
```

El valor de `JWT_SECRET_KEY` debe tener al menos 32 caracteres. Use la configuración
del `.env` raíz para compartir las credenciales de PostgreSQL sin publicar secretos.

## Inicio

Desde `backend/` con el entorno virtual activo:

```powershell
python run.py
```

La API queda disponible en `http://localhost:5000`.

## Documentación de la API REST

### Rutas implementadas

| Método | Ruta | Datos recibidos | Respuesta | Roles autorizados | Estado |
|---|---|---|---|---|---|
| `GET` | `/api/salud` | Ninguno | `200` con el estado de Flask y PostgreSQL; `503` si PostgreSQL no está disponible. | Público | Implementada |
| `POST` | `/api/auth/login` | JSON con `correo` y `contrasena`. | `200` con mensaje, JWT y usuario sin contraseña; `401` si las credenciales son inválidas; `429` por exceso de intentos; `503` si el servicio no puede consultar PostgreSQL. | Público | Implementada |
| `GET` | `/api/dias-festivos?anio=2026` | Query string `anio` con un año entero. | `200` con la lista de festivos; `400` si falta el parámetro o no es válido; `503` si no puede consultar PostgreSQL. | Público | Implementada |
| `GET` | `/api/perfil` | Ninguno. | Perfil del usuario autenticado. | Comisionado contratista | Implementada |
| `PATCH` | `/api/perfil` | JSON con `nombres`, `apellidos` y/o `correo`. | Perfil actualizado. | Comisionado contratista | Implementada |
| `GET` | `/api/perfil/contratos` | Ninguno. | Contratos asociados al usuario autenticado. | Comisionado contratista | Implementada |
| `GET` | `/api/perfil/contratos/<id_contrato>` | Ninguno. | Contrato propiedad del usuario autenticado. | Comisionado contratista | Implementada |
| `PATCH` | `/api/perfil/contratos/<id_contrato>` | Campos permitidos de contrato. | Contrato actualizado. | Comisionado contratista | Implementada |
| `GET` | `/api/perfil/contratos/<id_contrato>/obligaciones` | Ninguno. | Obligaciones del contrato propio. | Comisionado contratista | Implementada |
| `PUT` | `/api/perfil/contratos/<id_contrato>/obligaciones` | JSON `{"obligaciones":[{"descripcion":"..."}]}`. | Lista reemplazada en una transacción. | Comisionado contratista | Implementada |

No hay rutas protegidas por rol registradas actualmente en Flask. El decorador
`requiere_roles(...)` existe para uso futuro, pero no se le asignó a ninguna ruta.

### Ejemplos de peticiones y respuestas

#### Salud

Petición:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:5000/api/salud"
```

Respuesta exitosa, HTTP `200`:

```json
{
  "estado": "ok",
  "base_datos": "conectada"
}
```

Respuesta si PostgreSQL no está disponible, HTTP `503`:

```json
{
  "estado": "error",
  "base_datos": "no disponible",
  "mensaje": "La base de datos no está disponible"
}
```

#### Inicio de sesión

Petición:

```powershell
$body = @{
  correo = "prueba.s1.01@sena.edu.co"
  contrasena = "SenaDemo2026!"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:5000/api/auth/login" `
  -ContentType "application/json" `
  -Body $body
```

Cuerpo recibido por la API:

```json
{
  "correo": "prueba.s1.01@sena.edu.co",
  "contrasena": "SenaDemo2026!"
}
```

Respuesta exitosa, HTTP `200`:

```json
{
  "mensaje": "Inicio de sesión exitoso",
  "token": "JWT_GENERADO",
  "usuario": {
    "id": "DEMO-S1-001",
    "correo": "prueba.s1.01@sena.edu.co",
    "rol": "Comisionado contratista"
  }
}
```

Respuesta con credenciales inválidas, HTTP `401`:

```json
{
  "mensaje": "Credenciales inválidas"
}
```

#### Días festivos

Petición:

```powershell
Invoke-RestMethod -Method Get `
  -Uri "http://localhost:5000/api/dias-festivos?anio=2026"
```

Respuesta exitosa, HTTP `200`:

```json
{
  "anio": 2026,
  "dias_festivos": [
    {
      "id": 1,
      "fecha": "2026-01-01",
      "nombre": "Año Nuevo",
      "anio": 2026
    }
  ]
}
```

Respuesta si falta o no es válido el año, HTTP `400`:

```json
{
  "mensaje": "El parámetro anio es obligatorio"
}
```

### Rutas pendientes de desarrollar

Los siguientes módulos se mantienen como pendientes. Sus permisos, métodos exactos,
datos de entrada y respuestas no están implementados en Flask y, por tanto, no deben
considerarse endpoints disponibles:

| Método | Ruta | Datos recibidos | Respuesta esperada | Roles autorizados | Estado |
|---|---|---|---|---|---|
| POST | `/api/contratos` | No procesa datos en esta etapa. | HTTP 501 si el rol autorizado supera la autorización. | Supervisor del contrato | Provisional para comprobar autorización |
| Pendiente | Pendiente de definir para agendas | Pendiente de definir | Pendiente de definir | Pendiente de definir | Pendiente |
| Pendiente | Pendiente de definir para legalizaciones | Pendiente de definir | Pendiente de definir | Pendiente de definir | Pendiente |
| Pendiente | Pendiente de definir para viáticos | Pendiente de definir | Pendiente de definir | Pendiente de definir | Pendiente |
| Pendiente | Pendiente de definir para notificaciones | Pendiente de definir | Pendiente de definir | Pendiente de definir | Pendiente |

## PostgreSQL

La aplicación consulta PostgreSQL mediante `psycopg`.

- La ruta de salud ejecuta `SELECT 1`.
- El login consulta usuarios y roles, valida el estado activo y verifica bcrypt.
- El JWT incluye el documento del usuario en `sub` y el rol en `rol`.
- Los endpoints protegidos pueden usar `requiere_roles(...)`.

```python
from app.utils.permisos import SUPERVISOR_DEL_CONTRATO, requiere_roles

@requiere_roles(SUPERVISOR_DEL_CONTRATO)
def vista_restringida():
    ...
```

Los scripts SQL no se ejecutan automáticamente al iniciar Flask.

## Festivos

`GET /api/dias-festivos?anio=2026` consulta la tabla `dias_festivos`. Revise y
ejecute manualmente el archivo SQL correspondiente en el directorio `database/`;
no modifique ni ejecute SQL desde el proceso de arranque.

## Pruebas

Desde `backend/` con el entorno virtual activo:

```powershell
pytest -q
```

Las pruebas actuales cubren salud con PostgreSQL simulado, rechazo de credenciales,
emisión de JWT con rol, validación del año y rechazo de tokens inválidos.

## Rutas futuras

Las rutas de contratos, agendas, legalizaciones, viáticos y notificaciones se
documentan como futuras. No deben considerarse disponibles hasta que exista su
implementación en Flask.

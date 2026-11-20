# Sistema de Comisiones, Agendas y Legalizaciones

**SENA — Centro de Biotecnología Industrial (CBI), Palmira**  
**Sprint 1 · S1-T04 — Guía de instalación de la base de datos**  
**Responsable:** Luis David Riveros Orozco

## 1. Alcance

Esta guía permite a otro integrante preparar **la base de datos PostgreSQL** del proyecto y cargar los datos de prueba de S1-T03. Se basa en los scripts SQL elaborados y probados durante el Sprint 1.

> **Estado del proyecto:** todavía no se han proporcionado las instrucciones definitivas de instalación del backend ni del frontend. Por tanto, este README documenta la instalación de **la base de datos**, no una instalación completa de la aplicación. Para cerrar S1-T04 se deberá completar esa parte cuando estén definidos los proyectos y sus dependencias, y Juan deberá seguir la guía sin asistencia.

## 2. Requisitos previos

- PostgreSQL **16** (versión prevista en los scripts).
- **pgAdmin 4** o un cliente PostgreSQL equivalente, como Adminer.
- Acceso a un servidor PostgreSQL con permisos para crear una base de datos, tablas, claves foráneas y restricciones.
- Los tres archivos SQL descritos en la siguiente sección.

En un computador nuevo, instalar PostgreSQL 16 y pgAdmin 4 desde sus sitios oficiales: [PostgreSQL](https://www.postgresql.org/download/) y [pgAdmin](https://www.pgadmin.org/download/). Durante la instalación, conservar de forma segura la contraseña del usuario administrador de PostgreSQL. El puerto habitual es **5432**, salvo que se haya configurado otro.

## 3. Archivos necesarios

| Archivo | Función | Cuándo ejecutarlo |
| --- | --- | --- |
| `S1-T01_sql_actualizado.sql` | Crea todas las tablas, relaciones y estados iniciales del esquema actualizado. | **Solo en una base de datos nueva y vacía.** |
| `S1-T01_migracion.sql` | Actualiza el esquema anterior: crea `notificaciones` y agrega la restricción de observación obligatoria en `revisiones_agenda`. | **Solo si ya existe la base de datos con el esquema anterior.** |
| `S1-T03_datos_de_prueba.sql` | Inserta 5 roles, 2 usuarios ficticios por rol y 10 municipios del Valle del Cauca en `destinos`. | Después de preparar el esquema por una de las dos rutas anteriores. |

**Importante:** no ejecutar el esquema completo y la migración como si fueran dos pasos obligatorios. Son **alternativas**, según el estado inicial de la base de datos.

## 4. Instalar desde cero en un computador nuevo

1. Instalar PostgreSQL 16 y pgAdmin 4.
2. Abrir pgAdmin 4 y conectarse al servidor PostgreSQL con las credenciales configuradas durante la instalación.
3. En el árbol de navegación, hacer clic derecho en **Databases → Create → Database…**.
4. Escribir **`comisiones`** como nombre y guardar. Si ya existe una base de datos con ese nombre, no sobrescribirla; consultar la sección 5.
5. Seleccionar `comisiones` y abrir **Tools → Query Tool**.
6. Abrir `S1-T01_sql_actualizado.sql` desde Query Tool, o copiar y pegar su contenido completo.
7. Ejecutar el script y revisar **Messages**. No continuar si aparece algún error.
8. Abrir `S1-T03_datos_de_prueba.sql` y ejecutarlo sobre la **misma** base de datos `comisiones`.
9. Ejecutar las consultas de comprobación de la sección 6.

**Orden para instalación nueva:**

```text
1. S1-T01_sql_actualizado.sql
2. S1-T03_datos_de_prueba.sql
```

## 5. Actualizar una base de datos anterior

1. Antes de cualquier cambio, **hacer una copia de seguridad** de la base de datos existente desde pgAdmin: clic derecho sobre la base → **Backup…**. Guardar el respaldo en una ubicación segura.
2. Conectarse a la base de datos anterior y abrir **Query Tool**.
3. Ejecutar `S1-T01_migracion.sql` completo y verificar que la transacción finalice con `COMMIT`, sin errores de SQL.
4. Si la migración detecta revisiones `devuelta` sin observación, se detendrá. Corregir esos datos de forma justificada y volver a ejecutar la migración; no eliminar registros para forzarla.
5. Ejecutar `S1-T03_datos_de_prueba.sql` y revisar los resultados. El script está pensado para pruebas y evita volver a insertar usuarios con el mismo documento; los registros de `destinos` se comprueban por ciudad y departamento.
6. Ejecutar las consultas de la sección 6.

**Orden para base de datos anterior:**

```text
1. Respaldo de la base de datos
2. S1-T01_migracion.sql
3. S1-T03_datos_de_prueba.sql
```

**No ejecutar** `S1-T01_sql_actualizado.sql` sobre la base de datos anterior: contiene sentencias `CREATE TABLE` para el esquema completo y puede fallar porque las tablas ya existen.

## 6. Comprobaciones en pgAdmin 4

Abrir **Query Tool** conectado a `comisiones`. Ejecutar las consultas una por una para visualizar claramente sus resultados.

### 6.1. Verificar la migración

```sql
SELECT
    EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'notificaciones'
    ) AS tabla_notificaciones,
    EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.revisiones_agenda'::regclass
          AND conname = 'chk_revision_devolucion_observacion'
    ) AS validacion_observaciones;
```

**Resultado esperado:** `true` / `true` (algunos clientes lo muestran como `1` / `1`).

### 6.2. Verificar los usuarios por rol

```sql
SELECT r.nombre_rol, COUNT(u.documento_usuario) AS cantidad_usuarios
FROM public.roles r
LEFT JOIN public.usuarios u ON u.id_rol = r.id_rol
GROUP BY r.id_rol, r.nombre_rol
ORDER BY r.id_rol;
```

**Resultado esperado en una instalación nueva:** cinco filas, cada una con `cantidad_usuarios = 2`.

Roles oficiales: **Comisionado contratista**, **Comisionado funcionario**, **Supervisor del contrato**, **Área de viáticos** y **Subdirector del centro**.

### 6.3. Verificar el total de usuarios

```sql
SELECT COUNT(*) AS total_usuarios FROM public.usuarios;
```

**Resultado esperado en una instalación nueva:** `10`.

### 6.4. Verificar los municipios

```sql
SELECT ciudad, departamento
FROM public.destinos
WHERE departamento = 'Valle del Cauca'
ORDER BY ciudad;
```

**Resultado esperado en una instalación nueva:** 10 municipios: Cali, Candelaria, Cartago, Florida, Guadalajara de Buga, Jamundí, Palmira, Pradera, Tuluá y Yumbo.

> En una base de datos con información previa, los totales pueden ser mayores. En ese caso, comprobar que **existan los registros de prueba requeridos**, en lugar de exigir un total global exacto.

## 7. Usuarios de prueba y seguridad

El script `S1-T03_datos_de_prueba.sql` crea cuentas **ficticias** para pruebas. Sus correos siguen el patrón `prueba.s1.01@sena.edu.co` hasta `prueba.s1.10@sena.edu.co`. La contraseña temporal indicada en el script es **`SenaDemo2026!`**, almacenada mediante hashes bcrypt de demostración.

- Usar estas cuentas **únicamente en entornos de desarrollo**.
- No reutilizar contraseñas reales ni incorporar datos personales reales.
- Cuando se implemente el inicio de sesión (Sprint 2), **verificar** que el backend valide correctamente los hashes bcrypt antes de dar por funcionales las credenciales de prueba.
- No publicar respaldos de bases de datos que contengan información real.

## 8. Errores frecuentes

| Situación | Qué revisar |
| --- | --- |
| `relation ... already exists` | Se ejecutó el esquema completo sobre una base con tablas. Usar la ruta de migración de la sección 5. |
| `relation ... does not exist` | Falta ejecutar el esquema inicial o se está conectado a otra base de datos. |
| `permission denied` | El usuario de PostgreSQL no tiene los permisos necesarios. |
| La migración se detiene por devoluciones sin observación | Revisar `revisiones_agenda`; corregir observaciones faltantes antes de reintentar. |
| No aparecen los 10 usuarios o municipios | Comprobar que se ejecutó el script de datos en `comisiones` y consultar los mensajes de error. |
| El cliente muestra un error al ejecutar un comentario aislado | Revisar si las sentencias SQL anteriores, incluido `COMMIT`, terminaron correctamente; confirmar con las consultas de la sección 6. |

## 9. Evidencias y validación de S1-T03 / S1-T04

Guardar capturas de:

1. Ejecución correcta del esquema completo **o** de la migración, según corresponda.
2. Consulta de verificación de `notificaciones` y de la restricción de observaciones.
3. Cinco roles con dos usuarios cada uno.
4. Diez municipios del Valle del Cauca.

**Prueba de aceptación pendiente:** Juan debe seguir este README **en otro computador o entorno limpio**, sin asistencia, ejecutar el esquema actualizado y el script de datos de prueba, y registrar si hubo errores. Esta verificación es necesaria para cerrar S1-T03 y S1-T04 según el plan de sprints.

## 10. Instalación del backend y frontend — pendiente de completar

Cuando estén disponibles los proyectos del backend y frontend, agregar aquí: requisitos y versiones, dependencias, variables de entorno (sin contraseñas reales), comandos de instalación y ejecución, direcciones locales, endpoint de salud y procedimiento de prueba. No se incluyen comandos hipotéticos porque aún no se ha confirmado la tecnología y estructura definitiva de esos componentes.

---

**Proyecto:** Sistema de Comisiones, Agendas y Legalizaciones — SENA CBI Palmira.  
**Responsable de S1-T04:** Luis David Riveros Orozco.

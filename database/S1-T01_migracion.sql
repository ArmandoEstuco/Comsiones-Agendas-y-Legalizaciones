-- Sistema de Comisiones Agendas y Legalizaciones
-- Migracion Sprint 1: del esquema original (01-esquema.sql) al actualizado
-- PostgreSQL 16 Ejecutar sobre la base de datos EXISTENTE, no sobre una base vacia
-- Hacer una copia de seguridad antes de ejecutar
-- No elimina tablas, columnas ni registros existentes
-- Reejecutable si la estructura existente coincide con la esperada

BEGIN;

-- 1. Comprobar que los registros existentes cumplen la nueva regla.
-- Si hay devoluciones sin observacion, se detiene SIN cambiar la base de datos.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM public.revisiones_agenda
        WHERE decision = 'devuelta'
          AND NULLIF(BTRIM(observacion), '') IS NULL
    ) THEN
        RAISE EXCEPTION
            'Migracion cancelada: hay revisiones devueltas sin observacion. Corrija esos registros antes de volver a ejecutar.';
    END IF;
END
$$;

-- 2. Agregar la validacion nueva a la tabla existente.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.revisiones_agenda'::regclass
          AND conname = 'chk_revision_devolucion_observacion'
    ) THEN
        ALTER TABLE public.revisiones_agenda
            ADD CONSTRAINT chk_revision_devolucion_observacion
            CHECK (
                decision <> 'devuelta'
                OR NULLIF(BTRIM(observacion), '') IS NOT NULL
            );
    END IF;
END
$$;

-- 3. Crear la tabla nueva, igual a la del esquema completo actualizado.
CREATE TABLE IF NOT EXISTS public.notificaciones (
    id_notificacion BIGSERIAL PRIMARY KEY,
    id_agenda BIGINT NOT NULL REFERENCES public.agendas(id_agenda) ON DELETE CASCADE,
    documento_destinatario VARCHAR(30) NOT NULL REFERENCES public.usuarios(documento_usuario),
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    canal VARCHAR(20) NOT NULL CHECK (canal IN ('sistema','correo')),
    estado_envio VARCHAR(20) NOT NULL DEFAULT 'pendiente'
        CHECK (estado_envio IN ('pendiente','enviada','fallida')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_envio TIMESTAMP,
    fecha_lectura TIMESTAMP,
    CONSTRAINT chk_lectura_solo_notificacion_sistema
        CHECK (fecha_lectura IS NULL OR canal = 'sistema')
);

COMMIT;

-- Nota: IF NOT EXISTS no comprueba que una tabla preexistente tenga
-- exactamente las mismas columnas o restricciones. Esta migracion esta
-- destinada al esquema original entregado para el proyecto.

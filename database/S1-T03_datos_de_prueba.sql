
-- S1-T03: DATOS DE PRUEBA
-- Sistema de Comisiones, Agendas y Legalizaciones
-- PostgreSQL 16
-- Ejecutar después del esquema actualizado o la migración S1.
-- SOLO PARA DESARROLLO. No utilizar en producción.
-- Contraseña temporal de los 10 usuarios: SenaDemo2026!

BEGIN;

-- ============================================
-- 1. CREAR LOS CINCO ROLES OFICIALES
-- ============================================

INSERT INTO public.roles (nombre_rol, descripcion)
VALUES
('Comisionado contratista',
 'Contratista que se desplaza para cumplir una comisión'),
('Comisionado funcionario',
 'Funcionario de planta que se desplaza'),
('Supervisor del contrato',
 'Revisa y devuelve agendas de contratistas'),
('Área de viáticos',
 'Verifica agendas antes de la firma del subdirector'),
('Subdirector del centro',
 'Ordenador del gasto: firma y autoriza comisiones')
ON CONFLICT (nombre_rol) DO NOTHING;


-- ============================================
-- 2. CREAR DIEZ USUARIOS DE PRUEBA
-- DOS POR CADA ROL
-- ============================================

-- Los hashes bcrypt corresponden a la contraseña
-- temporal SenaDemo2026!
-- El backend debe verificar contraseñas con bcrypt.

INSERT INTO public.usuarios
(documento_usuario, id_rol, tipo_documento,
 nombres, apellidos, correo, contrasena_hash, estado)
VALUES
('DEMO-S1-001',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Comisionado contratista'),
 'CC', 'Prueba01', 'SENA',
 'prueba.s1.01@sena.edu.co',
 '$2y$10$bb3o7a9QgLYsQ0cOU3Jlt.1mBNSD3r26pbuLax/89ra8Xa6xhGO9i',
 'activo'),

('DEMO-S1-002',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Comisionado contratista'),
 'CC', 'Prueba02', 'SENA',
 'prueba.s1.02@sena.edu.co',
 '$2y$10$.TwKifaQ17/vkrJ3cogdzutZ0SRQBDaU5U1vuYVNsvtHv6rNzpB6.',
 'activo'),

('DEMO-S1-003',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Comisionado funcionario'),
 'CC', 'Prueba03', 'SENA',
 'prueba.s1.03@sena.edu.co',
 '$2y$10$U759ZseLA/F/5qzSearUQu8WVOHrkhkqwqd0Dzm9vElBGoIRyu65O',
 'activo'),

('DEMO-S1-004',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Comisionado funcionario'),
 'CC', 'Prueba04', 'SENA',
 'prueba.s1.04@sena.edu.co',
 '$2y$10$fbPZKR.1lLE/BPbHLXftpO.PO2YyY02rc6Qfcu6sJSGAEVAw5QMHO',
 'activo'),

('DEMO-S1-005',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Supervisor del contrato'),
 'CC', 'Prueba05', 'SENA',
 'prueba.s1.05@sena.edu.co',
 '$2y$10$DKNQkF3OLOfDrgdiNy5veunJhq6FeJHkrx7EHQF.B3iSTaUTNZxou',
 'activo'),

('DEMO-S1-006',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Supervisor del contrato'),
 'CC', 'Prueba06', 'SENA',
 'prueba.s1.06@sena.edu.co',
 '$2y$10$vuM8o2Dfc0u4U.yUFfAv7uvY4hFqkfKwkib.FF89Rpk2pC5aNQGY.',
 'activo'),

('DEMO-S1-007',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Área de viáticos'),
 'CC', 'Prueba07', 'SENA',
 'prueba.s1.07@sena.edu.co',
 '$2y$10$qmBmrj.MjU/opf.EKoFRWeHyklP28BXFjqnQ8uOTQ.bLZAQ3Cd6e.',
 'activo'),

('DEMO-S1-008',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Área de viáticos'),
 'CC', 'Prueba08', 'SENA',
 'prueba.s1.08@sena.edu.co',
 '$2y$10$6zoWhth8XSIUDdv13.dVjuuKjDSqfs9uTTQS3VEbd.QVxiumg8W02',
 'activo'),

('DEMO-S1-009',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Subdirector del centro'),
 'CC', 'Prueba09', 'SENA',
 'prueba.s1.09@sena.edu.co',
 '$2y$10$YXk.2xPEDQOREiIvnPx7Je8wnKeYwMCb3PM3cmveYDdp.UQWGG6Rq',
 'activo'),

('DEMO-S1-010',
 (SELECT id_rol FROM public.roles
  WHERE nombre_rol = 'Subdirector del centro'),
 'CC', 'Prueba10', 'SENA',
 'prueba.s1.10@sena.edu.co',
 '$2y$10$yCv9xWu.cY6hvZ8IfEJQA.DsYOAN5Vv97Gbsi6Qk4MBrUv8cuJZ1m',
 'activo')
ON CONFLICT (documento_usuario) DO NOTHING;


-- ============================================
-- 3. INSERTAR DIEZ MUNICIPIOS
-- DEL VALLE DEL CAUCA
-- ============================================

INSERT INTO public.destinos (ciudad, departamento)
SELECT v.ciudad, 'Valle del Cauca'
FROM (
    VALUES
    ('Palmira'),
    ('Cali'),
    ('Guadalajara de Buga'),
    ('Tuluá'),
    ('Cartago'),
    ('Jamundí'),
    ('Yumbo'),
    ('Candelaria'),
    ('Florida'),
    ('Pradera')
) AS v(ciudad)
WHERE NOT EXISTS (
    SELECT 1
    FROM public.destinos d
    WHERE LOWER(TRIM(d.ciudad)) = LOWER(v.ciudad)
      AND LOWER(TRIM(COALESCE(d.departamento, '')))
          = LOWER('Valle del Cauca')
);

COMMIT;


-- ============================================
-- 4. VERIFICAR LOS RESULTADOS
-- ============================================

-- Comprobar dos usuarios por rol
SELECT
    r.nombre_rol,
    COUNT(u.documento_usuario) AS cantidad_usuarios
FROM public.roles r
LEFT JOIN public.usuarios u
    ON u.id_rol = r.id_rol
GROUP BY r.id_rol, r.nombre_rol
ORDER BY r.id_rol;

-- Comprobar total de usuarios
SELECT COUNT(*) AS total_usuarios
FROM public.usuarios;

-- Comprobar municipios
SELECT ciudad, departamento
FROM public.destinos
ORDER BY ciudad;

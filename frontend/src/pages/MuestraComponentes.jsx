import Boton from '../components/boton';
import CampoTexto from '../components/campotexto';
import Selector from '../components/selector';
import Alerta from '../components/alerta';

export default function MuestraComponentes() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <h1 className="text-2xl font-bold text-sena mb-2">SENA - Muestra de Componentes (S1-T12)</h1>
        <p className="text-gray-600 mb-6">Prueba visual de los componentes reutilizables de la interfaz.</p>

        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800 border-b pb-1">1. Alertas</h2>
          <Alerta tipo="exito" mensaje="¡Operación realizada con éxito en el sistema!" />
          <Alerta tipo="error" mensaje="Ocurrió un error al procesar la solicitud." />
          <Alerta tipo="advertencia" mensaje="Atención: Los cambios no guardados se perderán." />

          <h2 className="text-lg font-semibold text-gray-800 border-b pb-1 pt-4">2. Campos de Texto y Selectores</h2>
          <CampoTexto label="Nombre completo" placeholder="Ej. Juan Pérez" />
          <Selector 
            label="Rol de usuario" 
            opciones={[
              { value: 'admin', label: 'Administrador' },
              { value: 'instructor', label: 'Instructor' },
              { value: 'aprendiz', label: 'Aprendiz' }
            ]} 
          />

          <h2 className="text-lg font-semibold text-gray-800 border-b pb-1 pt-4">3. Botones</h2>
          <div className="flex gap-3 flex-wrap">
            <Boton tipo="primario">Guardar Datos</Boton>
            <Boton tipo="secundario">Cancelar</Boton>
            <Boton tipo="peligro">Eliminar</Boton>
          </div>
        </section>
      </div>
    </div>
  );
}
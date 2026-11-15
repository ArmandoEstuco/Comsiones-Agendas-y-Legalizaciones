export default function Alerta({ tipo = "exito", mensaje }) {
  const estilosTipos = {
    exito: "bg-green-50 border-green-500 text-green-800",
    error: "bg-red-50 border-red-500 text-red-800",
    advertencia: "bg-yellow-50 border-yellow-500 text-yellow-800"
  };

  return (
    <div className={`border-l-4 p-4 rounded-r-lg my-2 ${estilosTipos[tipo]}`}>
      <p className="text-sm font-medium">{mensaje}</p>
    </div>
  );
}
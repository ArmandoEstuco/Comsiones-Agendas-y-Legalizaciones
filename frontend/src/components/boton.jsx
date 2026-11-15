export default function Boton({ children, onClick, tipo = "primario", className = "" }) {
  const estilosBase = "px-4 py-2 rounded-lg font-medium transition duration-200 cursor-pointer shadow-sm";
  const estilosTipos = {
    primario: "bg-[#39A900] hover:bg-[#2d8500] text-white",
    secundario: "bg-gray-200 hover:bg-gray-300 text-gray-800",
    peligro: "bg-red-600 hover:bg-red-700 text-white"
  };

  return (
    <button onClick={onClick} className={`${estilosBase} ${estilosTipos[tipo]} ${className}`}>
      {children}
    </button>
  );
}
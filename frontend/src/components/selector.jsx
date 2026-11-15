export default function Selector({ label, opciones = [], value, onChange, error }) {
  return (
    <div className="flex flex-col gap-1 mb-4">
      {label && <label className="text-sm font-semibold text-gray-700">{label}</label>}
      <select
        value={value}
        onChange={onChange}
        className={`px-3 py-2 rounded-lg border bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#39A900] ${
          error ? "border-red-500" : "border-gray-300"
        }`}
      >
        <option value="">Seleccione una opción</option>
        {opciones.map((op, index) => (
          <option key={index} value={op.value}>
            {op.label}
          </option>
        ))}
      </select>
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  );
}
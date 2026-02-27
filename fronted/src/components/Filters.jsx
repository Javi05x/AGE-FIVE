import React from "react";

export default function Filters({
  name, setName,
  temporada, setTemporada,
  squad, setSquad,
  comp, setComp,
  pos, setPos,
  rango, setRango,
  minMinutes, setMinMinutes,
  options
}) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr", gap: 8, alignItems: "end" }}>
      <div>
        <label>Nombre</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="contiene..." style={{ width: "100%" }} />
      </div>

      <div>
        <label>Temporada</label>
        <select value={temporada} onChange={(e) => setTemporada(e.target.value)} style={{ width: "100%" }}>
          <option value="">(todas)</option>
          {options.temporadas.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      <div>
        <label>Liga</label>
        <select value={comp} onChange={(e) => setComp(e.target.value)} style={{ width: "100%" }}>
          <option value="">(todas)</option>
          {options.comps.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div>
        <label>Equipo</label>
        <select value={squad} onChange={(e) => setSquad(e.target.value)} style={{ width: "100%" }}>
          <option value="">(todos)</option>
          {options.squads.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div>
        <label>Pos</label>
        <select value={pos} onChange={(e) => setPos(e.target.value)} style={{ width: "100%" }}>
          <option value="">(todas)</option>
          {options.pos.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      <div>
        <label>Rango edad</label>
        <select value={rango} onChange={(e) => setRango(e.target.value)} style={{ width: "100%" }}>
          <option value="">(todos)</option>
          {options.rangos.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      <div style={{ gridColumn: "1 / span 2" }}>
        <label>Min minutos</label>
        <input
          type="number"
          min="0"
          value={minMinutes}
          onChange={(e) => setMinMinutes(Number(e.target.value))}
          style={{ width: "100%" }}
        />
      </div>
    </div>
  );
}

import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { apiGet } from "../api.js";

function StatBlock({ title, obj }) {
  if (!obj) return null;
  return (
    <div style={{ border: "1px solid #eee", padding: 12, borderRadius: 8 }}>
      <h4 style={{ marginTop: 0 }}>{title}</h4>
      <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(obj, null, 2)}</pre>
    </div>
  );
}

export default function Player() {
  const [sp] = useSearchParams();
  const name = sp.get("name") || "";
  const squad = sp.get("squad") || "";

  const [data, setData] = useState(null);
  const [season, setSeason] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      setErr("");
      const res = await apiGet(`/api/player?name=${encodeURIComponent(name)}&squad=${encodeURIComponent(squad)}`);
      setData(res);
      const seasons = res.seasons || [];
      setSeason(seasons[0]?.team_info?.temporada || null);
    })().catch(e => setErr(String(e.message || e)));
  }, [name, squad]);

  const seasons = data?.seasons || [];
  const seasonOptions = useMemo(() => seasons.map(s => s?.team_info?.temporada).filter(Boolean), [seasons]);
  const current = seasons.find(s => s?.team_info?.temporada === season) || seasons[0];

  if (err) {
    return (
      <div>
        <Link to="/">← Volver</Link>
        <p style={{ color: "crimson" }}>{err}</p>
      </div>
    );
  }

  if (!data) return <div>Cargando...</div>;

  return (
    <div>
      <Link to="/">← Volver</Link>
      <h3 style={{ marginBottom: 4 }}>{data.player}</h3>
      <div style={{ color: "#555", marginBottom: 12 }}>{data.squad}</div>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {seasonOptions.map(t => (
          <button
            key={t}
            onClick={() => setSeason(t)}
            style={{ fontWeight: t === season ? "bold" : "normal" }}
          >
            {t}
          </button>
        ))}
      </div>

      {current ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <StatBlock title="team_info" obj={current.team_info} />
          <StatBlock title="Datos jugador" obj={{ nation: current.nation, pos: current.pos, age: current.age, rango_edad: current.rango_edad, born: current.born }} />
          <StatBlock title="stats_base" obj={current.stats_base} />
          <StatBlock title="stats_ataque" obj={current.stats_ataque} />
          <StatBlock title="stats_disciplina" obj={current.stats_disciplina} />
          <StatBlock title="stats_avanzadas" obj={current.stats_avanzadas} />
          <div style={{ gridColumn: "1 / span 2" }}>
            <StatBlock title="stats_por_90" obj={current.stats_por_90} />
          </div>
        </div>
      ) : (
        <div>No hay temporadas para mostrar.</div>
      )}
    </div>
  );
}

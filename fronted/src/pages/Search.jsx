import React, { useEffect, useState } from "react";
import { apiGet } from "../api.js";
import Filters from "../components/Filters.jsx";
import PlayerTable from "../components/PlayerTable.jsx";

export default function Search() {
  const [options, setOptions] = useState({ squads: [], comps: [], pos: [], rangos: [], temporadas: [] });

  const [name, setName] = useState("");
  const [temporada, setTemporada] = useState("");
  const [squad, setSquad] = useState("");
  const [comp, setComp] = useState("");
  const [pos, setPos] = useState("");
  const [rango, setRango] = useState("");
  const [minMinutes, setMinMinutes] = useState(0);

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      const [squads, comps, pos, rangos, temporadas] = await Promise.all([
        apiGet("/api/filters/squads"),
        apiGet("/api/filters/comps"),
        apiGet("/api/filters/pos"),
        apiGet("/api/filters/rangos"),
        apiGet("/api/filters/temporadas"),
      ]);
      setOptions({ squads, comps, pos, rangos, temporadas });
    })().catch(e => setErr(String(e.message || e)));
  }, []);

  async function doSearch() {
    setLoading(true);
    setErr("");
    try {
      const params = new URLSearchParams();
      if (name) params.set("name", name);
      if (temporada) params.set("temporada", temporada);
      if (squad) params.set("squad", squad);
      if (comp) params.set("comp", comp);
      if (pos) params.set("pos", pos);
      if (rango) params.set("rango_edad", rango);
      if (minMinutes > 0) params.set("min_minutes", String(minMinutes));
      params.set("page", "1");
      params.set("page_size", "25");

      const data = await apiGet(`/api/players/search?${params.toString()}`);
      setItems(data.items || []);
    } catch (e) {
      setErr(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Filters
        name={name} setName={setName}
        temporada={temporada} setTemporada={setTemporada}
        squad={squad} setSquad={setSquad}
        comp={comp} setComp={setComp}
        pos={pos} setPos={setPos}
        rango={rango} setRango={setRango}
        minMinutes={minMinutes} setMinMinutes={setMinMinutes}
        options={options}
      />

      <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
        <button onClick={doSearch} disabled={loading}>
          {loading ? "Buscando..." : "Buscar"}
        </button>
        {err ? <span style={{ color: "crimson" }}>{err}</span> : null}
      </div>

      <PlayerTable items={items} />
    </div>
  );
}

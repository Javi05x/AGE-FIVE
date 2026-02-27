import React from "react";
import { Link } from "react-router-dom";

export default function PlayerTable({ items }) {
  return (
    <table width="100%" cellPadding="8" style={{ borderCollapse: "collapse", marginTop: 12 }}>
      <thead>
        <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
          <th>Player</th>
          <th>Squad</th>
          <th>Comp</th>
          <th>Temp</th>
          <th>Age</th>
          <th>Pos</th>
          <th>Gls</th>
          <th>Ast</th>
          <th>Min</th>
        </tr>
      </thead>
      <tbody>
        {items.map((d) => {
          const ti = d.team_info || {};
          const gls = d?.stats_ataque?.gls ?? 0;
          const ast = d?.stats_ataque?.ast ?? 0;
          const min = d?.stats_base?.min ?? 0;

          const name = d.player;
          const squad = ti.squad;

          return (
            <tr key={d._id} style={{ borderBottom: "1px solid #f0f0f0" }}>
              <td>
                <Link to={`/player?name=${encodeURIComponent(name)}&squad=${encodeURIComponent(squad)}`}>
                  {name}
                </Link>
              </td>
              <td>{ti.squad}</td>
              <td>{ti.comp}</td>
              <td>{ti.temporada}</td>
              <td>{d.age}</td>
              <td>{d.pos}</td>
              <td>{gls}</td>
              <td>{ast}</td>
              <td>{min}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

// src/components/ProcessTable.jsx

import React from "react";

export default function ProcessTable({ data }) {
  // 1) filter for CPU% points
  const cpuRecs = data.filter(
    (d) => d.measurement === "process_info" && d.field === "cpu_pct"
  );

  // 2) group by PID and keep highest CPU% per process
  const byPid = {};
  cpuRecs.forEach((r) => {
    const pid = r.pid; // now available
    const name = r.name || ""; // now available
    if (!byPid[pid]) byPid[pid] = { pid, name, cpu_pct: 0 };
    if (r.value > byPid[pid].cpu_pct) {
      byPid[pid].cpu_pct = r.value;
    }
  });

  // 3) sort descending and take top 10
  const list = Object.values(byPid)
    .sort((a, b) => b.cpu_pct - a.cpu_pct)
    .slice(0, 10);

  return (
    <table>
      <thead>
        <tr>
          <th>PID</th>
          <th>Name</th>
          <th>CPU %</th>
        </tr>
      </thead>
      <tbody>
        {list.map((p) => (
          <tr key={p.pid}>
            <td>{p.pid}</td>
            <td>{p.name}</td>
            <td>{p.cpu_pct.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

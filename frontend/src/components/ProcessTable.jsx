import React from "react";

export default function ProcessTable({ data }) {
  const cpuRecs = data.filter(
    (d) => d.measurement === "process_info" && d.field === "cpu_pct"
  );
  const memRecs = data.filter(
    (d) => d.measurement === "process_info" && d.field === "mem_pct"
  );

  const byPid = {};
  cpuRecs.forEach((r) => {
    const pid = r.tags.pid;
    const name = r.tags.name;
    byPid[pid] = byPid[pid] || { pid, name };
    byPid[pid].cpu_pct = r.value;
  });
  memRecs.forEach((r) => {
    const pid = r.tags.pid;
    const name = r.tags.name;
    byPid[pid] = byPid[pid] || { pid, name };
    byPid[pid].mem_pct = r.value;
  });

  const list = Object.values(byPid)
    .sort((a, b) => (b.cpu_pct || 0) - (a.cpu_pct || 0))
    .slice(0, 10);

  return (
    <table>
      <thead>
        <tr>
          <th>PID</th>
          <th>Name</th>
          <th>CPU %</th>
          <th>Mem %</th>
        </tr>
      </thead>
      <tbody>
        {list.map((p) => (
          <tr key={p.pid}>
            <td>{p.pid}</td>
            <td>{p.name}</td>
            <td>{(p.cpu_pct || 0).toFixed(1)}</td>
            <td>{(p.mem_pct || 0).toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

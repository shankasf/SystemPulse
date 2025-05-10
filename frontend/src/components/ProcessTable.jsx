import React from "react";
import "./ProcessTable.css";

const NUM_CORES = 12; // adjust to match your system

export default function ProcessTable({ processes = [] }) {
  // Normalize CPU % to total cores (so max is 100%)
  const normalized = processes.map((p) => ({
    ...p,
    cpu_pct: Math.min(p.cpu_pct / NUM_CORES, 100),
  }));

  const list = normalized.sort((a, b) => b.cpu_pct - a.cpu_pct).slice(0, 10);

  return (
    <div className="process-table-wrapper">
      <table className="process-table">
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>PID</th>
            <th style={{ textAlign: "left" }}>Name</th>
            <th style={{ textAlign: "right" }}>CPU %</th>
            <th style={{ textAlign: "right" }}>Mem %</th>
          </tr>
        </thead>
        <tbody>
          {list.map((p, i) => (
            <tr key={`${p.pid}-${i}`}>
              <td>{p.pid}</td>
              <td>{p.name}</td>
              <td
                style={{
                  textAlign: "right",
                  color: p.cpu_pct > 50 ? "red" : "#333",
                }}
              >
                {p.cpu_pct.toFixed(1)}
              </td>
              <td
                style={{
                  textAlign: "right",
                  color: p.mem_pct > 20 ? "#c78300" : "#333",
                }}
              >
                {p.mem_pct.toFixed(1)}
              </td>
            </tr>
          ))}
          {list.length === 0 && (
            <tr>
              <td colSpan={4} style={{ textAlign: "center", color: "#888" }}>
                No active processes
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

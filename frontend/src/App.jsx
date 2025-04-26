// src/App.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";

import CPUChart from "./components/CPUChart";
import MemoryChart from "./components/MemoryChart";
import DiskChart from "./components/DiskChart";
import NetworkChart from "./components/NetworkChart";
import ProcessTable from "./components/ProcessTable";

function App() {
  const [metrics, setMetrics] = useState([]);
  const [alert, setAlert] = useState(null);

  // Fetch metrics & check alerts every 5 seconds
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get("/metrics");
        const all = res.data.data;
        setMetrics(all);

        // → Alert logic: trigger if any CPU usage > 90%
        const cpuValues = all
          .filter(
            (d) => d.measurement === "cpu_usage" && d.field === "usage_pct"
          )
          .map((d) => d.value);
        if (cpuValues.length) {
          const maxCpu = Math.max(...cpuValues);
          if (maxCpu > 90) {
            setAlert(`🚨 High CPU detected: ${maxCpu.toFixed(1)}%`);
          } else {
            setAlert(null);
          }
        }
      } catch (err) {
        console.error("Error fetching metrics:", err);
      }
    };

    fetchMetrics();
    const intervalId = setInterval(fetchMetrics, 5000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="container">
      <h1>SystemPulse Dashboard</h1>
      {alert && <div className="alert">{alert}</div>}

      <div className="grid">
        <div className="card">
          <CPUChart data={metrics} />
        </div>
        <div className="card">
          <MemoryChart data={metrics} />
        </div>
        <div className="card">
          <DiskChart data={metrics} />
        </div>
        <div className="card">
          <NetworkChart data={metrics} />
        </div>
      </div>

      <div className="card table-card">
        <h2>Top Processes</h2>
        <ProcessTable data={metrics} />
      </div>
    </div>
  );
}

export default App;

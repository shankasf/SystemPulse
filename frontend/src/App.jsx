// frontend/src/App.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";

import CPUChart from "./components/CPUChart";
import SystemLoadChart from "./components/SystemLoadChart";
import MemoryChart from "./components/MemoryChart";
import DiskIOChart from "./components/DiskIOChart";
import NetworkChart from "./components/NetworkChart";
import UptimeDisplay from "./components/UptimeDisplay";
import ProcessTable from "./components/ProcessTable";

import "./App.css";

export default function App() {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get("/metrics");
        console.log("fetched metrics:", res.data.data);
        setMetrics(res.data.data);
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };
    fetchMetrics();
    const id = setInterval(fetchMetrics, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="container">
      <h1>SystemPulse Dashboard</h1>

      <div className="grid">
        <div className="card">
          <CPUChart data={metrics} />
        </div>

        <div className="card">
          <SystemLoadChart data={metrics} />
        </div>

        <div className="card">
          <MemoryChart data={metrics} />
        </div>

        <div className="card">
          <DiskIOChart data={metrics} />
        </div>

        <div className="card">
          <NetworkChart data={metrics} />
        </div>

        <div className="card">
          <UptimeDisplay data={metrics} />
        </div>
      </div>

      <div className="card table-card">
        <h2>Top Processes</h2>
        <ProcessTable data={metrics} />
      </div>
    </div>
  );
}

// frontend/src/App.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

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
        setMetrics(res.data.data);

        // After setting metrics, check for high CPU
        const cpuPoints = res.data.data.filter(
          (d) => d.measurement === "cpu_usage" && d.field === "usage_pct"
        );
        const latestCpu = cpuPoints[cpuPoints.length - 1]?.value || 0;
        if (latestCpu > 10) {
          toast.error(`🚨 High CPU Usage: ${latestCpu.toFixed(1)}%`, {
            position: "top-right",
            autoClose: 5000,
          });
        }
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
      <ToastContainer />

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

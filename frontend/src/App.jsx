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
  const [processes, setProcesses] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1) Fetch all metrics for charts and alerts
        const { data: metricsResp } = await axios.get("/metrics");
        const allMetrics = metricsResp.data;
        setMetrics(allMetrics);

        // CPU alert (threshold matches backend: 72%)
        const cpuPts = allMetrics.filter(
          (d) => d.measurement === "cpu_usage" && d.field === "usage_pct"
        );
        const lastCpu = cpuPts[cpuPts.length - 1]?.value || 0;
        if (lastCpu > 72) {
          toast.error(`🚨 High CPU Usage: ${lastCpu.toFixed(1)}%`, {
            position: "top-right",
            autoClose: 5000,
          });
        }

        // Memory alert (backend threshold: 72%)
        const memPts = allMetrics.filter(
          (d) => d.measurement === "memory_usage" && d.field === "used_mb"
        );
        const lastMemMb = memPts[memPts.length - 1]?.value || 0;
        // If you want percent, backend could emit mem_pct; otherwise compare MB
        if (lastMemMb > /* e.g. convert 72% of total MB */ 0) {
          toast.error(`🚨 High Memory Used: ${lastMemMb.toFixed(1)} MB`, {
            position: "top-right",
            autoClose: 5000,
          });
        }

        // 2) Fetch process list for the table
        const { data: procResp } = await axios.get("/processes");
        setProcesses(procResp.processes);
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
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
        <ProcessTable processes={processes} />
      </div>
    </div>
  );
}

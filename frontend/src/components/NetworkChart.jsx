// frontend/src/components/NetworkChart.jsx

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export default function NetworkChart({ data }) {
  // filter for the actual measurement name coming from your backend
  const raw = data.filter((d) => d.measurement === "network_activity");

  // group by time and collect packets_sent, packets_recv, (and optionally err_out)
  const byTime = {};
  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t };
    if (field === "packets_sent") byTime[t].packets_sent = value;
    if (field === "packets_recv") byTime[t].packets_recv = value;
    if (field === "err_out") byTime[t].err_out = value; // optional
  });

  // convert into an array for the chart
  const series = Object.values(byTime);

  return (
    <>
      <h2>Network Activity</h2>
      <AreaChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Area
          type="monotone"
          dataKey="packets_sent"
          name="Packets Sent"
          fill="#8884d8"
          stroke="#8884d8"
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="packets_recv"
          name="Packets Recv"
          fill="#82ca9d"
          stroke="#82ca9d"
          dot={false}
        />
        {/*
        // If you want to display error counts too:
        <Area
          type="monotone"
          dataKey="err_out"
          name="Errors Out"
          fill="#d88484"
          stroke="#d88484"
          dot={false}
        />
        */}
      </AreaChart>
    </>
  );
}

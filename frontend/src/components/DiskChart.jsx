import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export default function DiskChart({ data }) {
  const raw = data.filter((d) => d.measurement === "disk_io");
  const byTime = {};
  raw.forEach(({ time, field, value }) => {
    const t = new Date(time).toLocaleTimeString();
    byTime[t] = byTime[t] || { time: t };
    byTime[t][field] = Number(value.toFixed(2));
  });
  const series = Object.values(byTime);

  return (
    <>
      <h2>Disk I/O</h2>
      <BarChart width={300} height={200} data={series}>
        <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
        <XAxis dataKey="time" hide />
        <YAxis />
        <Tooltip />
        <Legend verticalAlign="top" height={24} />
        <Bar dataKey="read_mb_s" name="Read MB/s" fill="#8884d8" />
        <Bar dataKey="write_mb_s" name="Write MB/s" fill="#82ca9d" />
      </BarChart>
    </>
  );
}

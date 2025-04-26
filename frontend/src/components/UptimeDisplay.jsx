import React from "react";

export default function UptimeDisplay({ data }) {
  const recs = data.filter(
    (d) => d.measurement === "system_uptime" && d.field === "uptime_s"
  );
  if (!recs.length) return null;

  const uptime = recs[recs.length - 1].value;
  const hrs = Math.floor(uptime / 3600);
  const mins = Math.floor((uptime % 3600) / 60);
  const secs = Math.floor(uptime % 60);

  return (
    <div>
      <h2>Uptime</h2>
      <p>
        {hrs}h {mins}m {secs}s
      </p>
    </div>
  );
}

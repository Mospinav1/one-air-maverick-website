/* One Air Maverick: flight request form handler.
   Receives the JSON the website posts, checks it, and emails it to TO_EMAIL with reply-to set to the customer. */

const MAX_BYTES = 20000;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
    const cors = {
      "Access-Control-Allow-Origin": allowed.includes(origin) ? origin : allowed[0] || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
      "Vary": "Origin",
    };
    const reply = (status, body) => new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "POST") return reply(405, { ok: false, error: "method" });
    if (allowed.length && !allowed.includes(origin)) return reply(403, { ok: false, error: "origin" });

    const raw = await request.text();
    if (raw.length > MAX_BYTES) return reply(413, { ok: false, error: "too_large" });
    let d;
    try { d = JSON.parse(raw); } catch { return reply(400, { ok: false, error: "json" }); }

    const str = (v, n = 200) => (typeof v === "string" ? v.trim().slice(0, n) : "");
    const int = (v, lo, hi) => { const x = Math.round(Number(v)); return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : lo; };
    const r = {
      origin: str(d.origin), destination: str(d.destination),
      depart: str(d.depart_date, 10), ret: str(d.return_date, 10), window: str(d.time_window, 20), trip: str(d.trip_type, 20),
      flexible: d.flexible === true, adults: int(d.adults, 1, 19), children: int(d.children, 0, 18), pets: str(d.pets, 20),
      notes: str(d.notes, 500), name: str(d.full_name, 120), email: str(d.email, 200), phone: str(d.phone, 40), pref: str(d.contact_pref, 20),
    };
    if (!r.origin || !r.destination || !r.depart || !r.name || !EMAIL_RE.test(r.email) || d.consent !== true) return reply(400, { ok: false, error: "missing" });

    if (env.TURNSTILE_SECRET) {
      const form = new FormData();
      form.append("secret", env.TURNSTILE_SECRET);
      form.append("response", str(d.turnstile_token, 4096));
      const ip = request.headers.get("CF-Connecting-IP"); if (ip) form.append("remoteip", ip);
      const v = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: form }).then((x) => x.json()).catch(() => ({}));
      if (!v.success) return reply(403, { ok: false, error: "turnstile" });
    }

    const pax = r.adults + " adult" + (r.adults > 1 ? "s" : "") + (r.children ? ", " + r.children + " child" + (r.children > 1 ? "ren" : "") : "");
    const rows = [
      ["Route", r.origin + "  →  " + r.destination],
      ["Trip", r.trip + (r.ret ? ", returning " + r.ret : "")],
      ["Departure", r.depart + " (" + (r.window || "Flexible") + ")" + (r.flexible ? ", dates flexible" : "")],
      ["Travelers", pax + (r.pets && r.pets !== "None" ? ", pet: " + r.pets : "")],
      ["Notes", r.notes || "None"],
      ["Name", r.name],
      ["Email", r.email],
      ["Phone", r.phone || "Not given"],
      ["Prefers", r.pref || "Email"],
    ];
    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const text = "New flight request from the website\n\n" + rows.map(([k, v]) => k.padEnd(10) + v).join("\n") + "\n\nReply to this email to answer " + r.name + " directly.";
    const html = '<div style="font-family:Helvetica,Arial,sans-serif;color:#101820;max-width:600px">' +
      '<p style="font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#55616D;margin:0 0 8px">One Air Maverick</p>' +
      '<h2 style="font-weight:500;margin:0 0 16px">New flight request</h2><table style="border-collapse:collapse;width:100%;font-size:15px">' +
      rows.map(([k, v]) => '<tr><td style="padding:8px 12px 8px 0;color:#55616D;vertical-align:top;white-space:nowrap;border-bottom:1px solid #E4E9EE">' + k + '</td><td style="padding:8px 0;border-bottom:1px solid #E4E9EE;white-space:pre-wrap">' + esc(v) + "</td></tr>").join("") +
      '</table><p style="color:#55616D;font-size:13px;margin-top:16px">Reply to this email to answer ' + esc(r.name) + " directly.</p></div>";

    try {
      await env.EMAIL.send({
        to: env.TO_EMAIL,
        from: env.FROM_EMAIL,
        replyTo: r.email,
        subject: "Flight request: " + r.origin.replace(/\s*\(.*\)$/, "") + " to " + r.destination.replace(/\s*\(.*\)$/, "") + ", " + r.depart + " (" + pax + ")",
        text, html,
      });
    } catch (e) {
      console.error("send failed", e && e.code, e && e.message);
      return reply(502, { ok: false, error: "send" });
    }
    return reply(200, { ok: true });
  },
};

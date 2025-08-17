import React from "react";

const PopupMonitor: React.FC = () => {
  const openMonitoredPopup = () => {
    const popup = window.open("", "monitored_popup", "width=800,height=600");
    if (!popup) {
      alert("Popup blocked. Allow popups.");
      return;
    }

    // Basic popup HTML
    const html = `
      <!doctype html>
      <html lang="en">
      <head><meta charset="utf-8"><title>Popup</title></head>
      <body>
        <h2>Popup</h2>
        <button id="btn-fetch">Test fetch</button>
        <button id="btn-xhr">Test XHR</button>
      </body>
      </html>`;
    popup.document.open();
    popup.document.write(html);
    popup.document.close();

    // Monitoring code
    const code = `(function(){
      function report(type, payload){
        try {
          window.opener.postMessage({__popupNetLog:true, type, payload, ts:Date.now()}, "*");
        } catch(e){}
      }

      // Hook fetch
      const origFetch = window.fetch;
      window.fetch = async function(input, init){
        report("fetch:request", {url: input});
        const res = await origFetch(input, init);
        report("fetch:response", {url: res.url, status: res.status});
        return res;
      };

      // Hook XHR
      const OrigXHR = window.XMLHttpRequest;
      window.XMLHttpRequest = function(){
        const xhr = new OrigXHR();
        let url = "";
        const open = xhr.open;
        xhr.open = function(m, u, ...rest){
          url = u;
          return open.call(this, m, u, ...rest);
        };
        xhr.addEventListener("loadend", function(){
          report("xhr", {url, status: xhr.status});
        });
        return xhr;
      };

      // Demo buttons
      document.getElementById("btn-fetch")?.addEventListener("click", () => fetch("https://httpbin.org/get"));
      document.getElementById("btn-xhr")?.addEventListener("click", () => {
        const x = new XMLHttpRequest();
        x.open("GET", "https://httpbin.org/headers");
        x.send();
      });
    })();`;

    // Inject script into popup
    const script = popup.document.createElement("script");
    script.textContent = code;
    popup.document.body.appendChild(script);

    // Listener in parent
    const onMessage = (ev: MessageEvent) => {
      if (ev.data && ev.data.__popupNetLog) {
        const { type, payload } = ev.data;
        console.log("[POPUP]", type, payload);
      }
    };
    window.addEventListener("message", onMessage);

    // Cleanup when popup closes
    const iv = setInterval(() => {
      if (popup.closed) {
        clearInterval(iv);
        window.removeEventListener("message", onMessage);
        console.info("[POPUP] closed, monitoring stopped.");
      }
    }, 1000);
  };

  return (
    <div style={{ padding: "1rem" }}>
      <button
        onClick={openMonitoredPopup}
        style={{
          padding: "8px 14px",
          borderRadius: "6px",
          background: "#2563eb",
          color: "white",
          border: "none",
          cursor: "pointer"
        }}
      >
        Open monitored popup
      </button>
    </div>
  );
};

export default PopupMonitor;

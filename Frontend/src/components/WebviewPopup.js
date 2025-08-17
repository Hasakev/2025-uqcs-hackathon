import React from "react";

type Props = {
  url: string; // website to open in popup
};

const WebviewPopup: React.FC<Props> = ({ url }) => {
  const openPopup = () => {
    const popup = window.open(url, "webview_popup", "width=1000,height=800");

    if (!popup) {
      alert("Popup blocked. Allow popups for this site.");
      return;
    }

    console.log("[POPUP] opened", url);

    // Poll to detect closure
    const iv = setInterval(() => {
      if (popup.closed) {
        clearInterval(iv);
        console.log("[POPUP] closed");
      }
    }, 1000);

    // ⚠️ Note: For cross-origin popups, you can't hook into fetch/XHR.
    // If the popup is same-origin with your React app, you could inject a script
    // (like in earlier examples) to override fetch/XMLHttpRequest and relay logs.
  };

  return (
    <div style={{ padding: "1rem" }}>
      <button
        onClick={openPopup}
        style={{
          padding: "8px 14px",
          borderRadius: "6px",
          background: "#2563eb",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        Open {url} in popup
      </button>
    </div>
  );
};

export default WebviewPopup;

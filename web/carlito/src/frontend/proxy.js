const net = require("net");

const BACKEND_HOST = process.env.BACKEND_HOST || "backend";
const BACKEND_PORT = Number(process.env.BACKEND_PORT || 3000);
const SMUGGLE_WINDOW_MS = Number(process.env.SMUGGLE_WINDOW_MS || 50);

const server = net.createServer((client) => {
  let buffer = Buffer.alloc(0);
  let handled = false;
  let backend = null;
  let flushTimer = null;
  let parsed = false;
  let totalNeeded = null;

  client.on("data", (chunk) => {
    if (handled) return;

    buffer = Buffer.concat([buffer, chunk]);
    const headerEnd = buffer.indexOf("\r\n\r\n");
    if (headerEnd === -1) return;

    const head = buffer.slice(0, headerEnd + 4).toString("latin1");

    if (!parsed) {
      const firstLineEnd = head.indexOf("\r\n");
      const firstLine = firstLineEnd === -1 ? head : head.slice(0, firstLineEnd);
      const parts = firstLine.split(" ");
      const path = parts[1] || "/";

      if (path.startsWith("/admin")) {
        const body = "Forbidden";
        client.write(
          "HTTP/1.1 403 Forbidden\r\n" +
            "Content-Length: " +
            body.length +
            "\r\n" +
            "Connection: close\r\n\r\n" +
            body
        );
        client.end();
        handled = true;
        return;
      }

      const match = head.match(/\r\ncontent-length:\s*(\d+)/i);
      const contentLength = match ? parseInt(match[1], 10) : 0;
      totalNeeded = headerEnd + 4 + contentLength;
      parsed = true;
    }

    if (totalNeeded === null || buffer.length < totalNeeded) return;

    if (flushTimer) clearTimeout(flushTimer);
    flushTimer = setTimeout(() => {
      if (handled) return;
      backend = net.connect(BACKEND_PORT, BACKEND_HOST, () => {
        backend.write(buffer);
        client.pause();
      });

      backend.on("data", (data) => client.write(data));
      backend.on("end", () => client.end());
      backend.on("error", () => client.end());
      handled = true;
    }, SMUGGLE_WINDOW_MS);
  });

  client.on("error", () => {
    if (backend) backend.end();
  });
});

server.listen(80);

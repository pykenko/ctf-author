<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hakurei Shrine Archive</title>
    <style>
      :root {
        --paper: #f6f0e6;
        --crimson: #c82232;
        --crimson-dark: #a21728;
        --gold: #d5b36a;
        --ink: #3b2a2f;
        --muted: rgba(59, 42, 47, 0.7);
        --shadow: 0 30px 60px rgba(62, 24, 32, 0.18);
      }

      *,
      *::before,
      *::after {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Cormorant Garamond", "Garamond", "Georgia", serif;
        color: var(--ink);
        background:
          radial-gradient(1200px 600px at 10% 0%, rgba(200, 34, 50, 0.12), transparent 60%),
          radial-gradient(900px 500px at 90% 10%, rgba(213, 179, 106, 0.2), transparent 55%),
          linear-gradient(180deg, #f9f5ee 0%, #efe4d3 100%);
        position: relative;
        overflow-x: hidden;
      }

      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background:
          repeating-linear-gradient(
            90deg,
            rgba(194, 34, 50, 0.04),
            rgba(194, 34, 50, 0.04) 1px,
            transparent 1px,
            transparent 24px
          );
        opacity: 0.6;
        pointer-events: none;
        z-index: 0;
      }

      .page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 48px 20px;
        position: relative;
        z-index: 1;
      }

      .card {
        width: min(1100px, 100%);
        background: var(--paper);
        border-radius: 28px;
        border: 1px solid rgba(194, 34, 50, 0.2);
        padding: 40px;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
      }

      .card::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -120px;
        top: -90px;
        background: radial-gradient(circle, rgba(194, 34, 50, 0.18), transparent 70%);
        transform: rotate(12deg);
      }

      .header {
        display: grid;
        gap: 10px;
      }

      .eyebrow {
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        font-size: 12px;
        color: var(--crimson);
      }

      h1 {
        margin: 0;
        font-size: clamp(2.1rem, 3.2vw, 3.1rem);
      }

      .lead {
        margin: 0;
        color: var(--muted);
        line-height: 1.6;
      }

      .content {
        margin-top: 32px;
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr);
        gap: 32px;
        align-items: center;
      }

      .upload {
        display: grid;
        gap: 16px;
      }

      .file-field {
        display: grid;
        gap: 8px;
      }

      .file-field label {
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.75rem;
        color: var(--crimson-dark);
      }

      input[type="file"] {
        width: 100%;
        padding: 14px;
        border-radius: 16px;
        border: 1px dashed rgba(194, 34, 50, 0.4);
        background: #fff;
        font-size: 0.95rem;
      }

      input[type="file"]::file-selector-button {
        margin-right: 12px;
        border: none;
        background: var(--crimson);
        color: #fff;
        padding: 10px 16px;
        border-radius: 999px;
        font-weight: 600;
        cursor: pointer;
      }

      button {
        border: none;
        background: linear-gradient(120deg, var(--crimson), var(--crimson-dark));
        color: #fff;
        padding: 14px 22px;
        border-radius: 999px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        cursor: pointer;
        box-shadow: 0 14px 30px rgba(194, 34, 50, 0.25);
        transition: transform 0.2s ease;
      }

      button:hover {
        transform: translateY(-1px);
      }

      .note {
        margin: 0;
        font-size: 0.85rem;
        color: var(--muted);
      }

      .portrait {
        background: #fff;
        border-radius: 20px;
        padding: 14px;
        border: 1px solid rgba(194, 34, 50, 0.3);
        box-shadow: 0 18px 40px rgba(59, 42, 47, 0.2);
      }

      .portrait img {
        display: block;
        width: 100%;
        height: auto;
        border-radius: 14px;
      }

      .ward {
        margin-top: 16px;
        border: 1px dashed rgba(194, 34, 50, 0.5);
        padding: 14px 16px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.7);
        display: grid;
        gap: 6px;
      }

      .ward span {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: var(--crimson-dark);
      }

      .ward strong {
        font-size: 1rem;
      }

      @media (max-width: 900px) {
        .card {
          padding: 30px;
        }

        .content {
          grid-template-columns: 1fr;
        }
      }

      @media (max-width: 600px) {
        .page {
          padding: 32px 16px;
        }

        .card {
          padding: 24px;
        }

        button {
          width: 100%;
        }
      }
    </style>
  </head>
  <body>
    <div class="page">
      <div class="card">
        <header class="header">
          <p class="eyebrow">Hakurei Shrine</p>
          <h1>Reimu's Ofuda Archive</h1>
          <p class="lead">
            Leave a new charm for safekeeping. The shrine keeps watch over every
            offering in Gensokyo.
          </p>
        </header>
        <div class="content">
          <form class="upload" method="POST" action="upload.php" enctype="multipart/form-data">
            <div class="file-field">
              <label for="file">Scroll Offering</label>
              <input id="file" type="file" name="file" required>
            </div>
            <button type="submit">Offer to Shrine</button>
            <p class="note">Note: .touhou scrolls are not accepted.</p>
          </form>
          <aside class="aside">
            <div class="portrait">
              <img src="reimu.png" alt="Reimu Hakurei">
            </div>
            <div class="ward">
              <span>Gensokyo Ward</span>
              <strong>Seal Level: High</strong>
            </div>
          </aside>
        </div>
      </div>
    </div>
  </body>
</html>

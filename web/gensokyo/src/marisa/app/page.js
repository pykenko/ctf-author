import Image from "next/image";
import marisa from "../marisa.png";

export async function fumo() {
  "use server";
  return;
}

export default function Page() {
  return (
    <main className="page">
      <section className="frame">
        <div className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Kirisame Atelier</p>
            <h1>Marisa's Star Workshop</h1>
            <p className="lead">
              The shrine sky is clear tonight. Align your request with the
              northern constellations and let the grimoire do the rest.
            </p>
            <div className="sigils">
              <span>Stardust</span>
              <span>Velocity</span>
              <span>Borrowed Magic</span>
            </div>
            <form action={fumo} className="spell-form">
              <button className="primary" type="submit">
                Cast Spell
              </button>
              <span className="hint">Offer a wish to the night sky.</span>
            </form>
          </div>
          <div className="hero-art">
            <div className="portrait">
              <Image src={marisa} alt="Marisa Kirisame" priority />
            </div>
          </div>
        </div>
        <div className="footer-row">
          <div className="detail-card">
            <h2>Workshop Log</h2>
            <p>
              Grimoire shelves are open. Make your mark and let the night
              archive the glow.
            </p>
          </div>
          <div className="detail-card">
            <h2>Constellation Notes</h2>
            <ul>
              <li>Altitude is steady at the Forest of Magic.</li>
              <li>Star dust reserves ready for a new burst.</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}

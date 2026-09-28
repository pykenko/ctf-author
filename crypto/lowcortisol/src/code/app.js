const AUTH_KEY = "lc_authed";
const AUTH_TTL = 1000 * 60 * 60 * 8; // 8 hours

const datasets = [
  {
    company: "Mikimiku",
    sector: "Media telemetry",
    region: "Tokyo cluster",
    e: "8978",
    n: "12072032443450416149161688505878942563158334470013119620672711114366426733051028059145278819205735638003892634005968890647290311799757213678352808250805979328250347735910734999790753583788867917756982066132072332309205290732957360339404816265939448513058332306241877060161848390334482417356867454621475819343964736521170444541257688957914136203686389377318976913185764989632954671827250572733699680686150818694666401390885723812598557308294283528290828025586886654442471005393408599699397162081059149617103827486531038660489863157726085585231231026831173964644744016761524823245554306624339652013402024159305306013001",
    c: "6949890131616568331672274433112755280635655331877504294750907615418202909491858599419587865886234131222761726898346195256137697595041517783818998652143229392279786658794296641192402818617129497557763473277744913989394007627015116703747046519898624166947069743130908216045612156629818215787334415824534373540191490577784432999736494049829277119782927010421133429369025976069621046180021912306970848541269041981986857515103947441550120840493023236644789457278480210076198391864526943723661374191669184457990404240956287735469229608044507336266809604894879492800972230559558919651398526084037985219882336645323543064494",
  },
  {
    company: "Wrth",
    sector: "Industrial QA",
    region: "Rhein line",
    e: "8978",
    n: "12072032443450416149161688505878942563158334470013119620672711114366426733051028059145278819205735638003892634005968890647290311799757213678352808250805979328250347735910734999790753583788867917756982066132072332309205290732957360339404816265939448513058332306241877060161848390334482417356867454621475819343964736521170444541257688957914136203686389377318976913185764989632954671827250572733699680686150818694666401390885723812598557308294283528290828025586886654442471005393408599699397162081059149617103827486531038660489863157726085585231231026831173964644744016761524823245554306624339652013402024159305306013001",
    c: "3740115458720302437537671236990234563283394581454946828638443216608296959417946636763041595890765011066362803967101465050104722809290501556414200991033791782097830397673350205101925319462443170080139792666641711056725203118006846373147638092108595460531643987545348924967360285176618319716321924279367875566843848115880364736044404453169957524175424889201858705219621042042358704720092854839566254084198001222702462960421019057013239904292550956667517596421511266717548525183295384896440099344831129665607213167412598651177363143376390091303009054054232949639025190824696997851751132805185027112383401356711812307008",
  },
  {
    company: "Auric",
    sector: "Industrial QA",
    region: "Singapore",
    e: "8978",
    n: "12072032443450416149161688505878942563158334470013119620672711114366426733051028059145278819205735638003892634005968890647290311799757213678352808250805979328250347735910734999790753583788867917756982066132072332309205290732957360339404816265939448513058332306241877060161848390334482417356867454621475819343964736521170444541257688957914136203686389377318976913185764989632954671827250572733699680686150818694666401390885723812598557308294283528290828025586886654442471005393408599699397162081059149617103827486531038660489863157726085585231231026831173964644744016761524823245554306624339652013402024159305306013001",
    c: "4195992529205735174609950197655873848504078179530709867477946535836707418963601848712651471985136773176513687872914153896479171042760777498522869619193838146115164268609261013794101930216985705220826927095942996096203902933280386033749690856349576657268332595395398937278148948534479226320208139432180662667600594356684885717210558009628651436651657485999039131426288419614379703453516771492629280825813583099551618353196451169673164573291390798875714226481838837496144881464570378901661914267298719057355076899407222505865690002800902131738117734940711357203549941728256056610206459707700444295016290579193201634428",
  },
];

const bugReports = [
  {
    reporter: "vxlx / external",
    ticket: "LC-CR-118",
    severity: "Unknown",
    status: "untriaged",
    summary: "Reporter shared RSA encryption logic and said: \"I think this is vulnerable.\"",
    code: `
e = 4489 *2

while True:
    p = getPrime(1024)
    if (p - 1) % 67 == 0:
        break

q = nextprime(p + 2**512)
while (q - 1) % 67 != 0:
    q = nextprime(q)

n = p * q

m = bytes_to_long(os.urandom(64) + data + os.urandom(32))

c = pow(m, e, n)

hey admin! i dont think this is low cortisol code its very high cortisol based on ctf standards!
`,
  },
];

const loginForm = document.getElementById("loginForm");
const loginStatus = document.getElementById("loginStatus");
const adminShell = document.querySelector("[data-admin-shell]");
const logoutBtn = document.getElementById("logoutBtn");
const datasetList = document.getElementById("datasetList");
const bugReportList = document.getElementById("bugReportList");
const requestAccessBtn = document.getElementById("requestAccessBtn");
const toast = document.getElementById("toast");

const now = () => new Date().getTime();

const setAuth = (enabled) => {
  if (enabled) {
    localStorage.setItem(AUTH_KEY, String(now()));
  } else {
    localStorage.removeItem(AUTH_KEY);
  }
};

const hasValidAuth = () => {
  const value = localStorage.getItem(AUTH_KEY);
  if (!value) return false;
  const timestamp = Number(value);
  return Number.isFinite(timestamp) && now() - timestamp < AUTH_TTL;
};

const showToast = (message) => {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2200);
};

const truncate = (value, head = 26, tail = 16) => {
  if (!value) return "";
  if (value.length <= head + tail + 3) return value;
  return `${value.slice(0, head)}...${value.slice(-tail)}`;
};

const createDataRow = (labelText, value) => {
  const row = document.createElement("div");
  row.className = "data-row";

  const label = document.createElement("label");
  label.textContent = labelText;

  const code = document.createElement("code");
  code.textContent = truncate(value);
  code.dataset.full = value;

  const actions = document.createElement("div");
  actions.className = "data-actions";

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.textContent = "Copy";
  copyBtn.addEventListener("click", () => {
    const payload = code.dataset.full || "";
    if (!payload) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(payload).then(() => showToast("Copied"));
      return;
    }
    const temp = document.createElement("textarea");
    temp.value = payload;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand("copy");
    temp.remove();
    showToast("Copied");
  });

  const toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.textContent = "Expand";
  toggleBtn.addEventListener("click", () => {
    const expanded = toggleBtn.dataset.expanded === "true";
    toggleBtn.dataset.expanded = expanded ? "false" : "true";
    toggleBtn.textContent = expanded ? "Expand" : "Collapse";
    code.textContent = expanded ? truncate(value) : value;
  });

  actions.appendChild(copyBtn);
  actions.appendChild(toggleBtn);

  row.appendChild(label);
  row.appendChild(code);
  row.appendChild(actions);

  return row;
};

const renderDatasets = () => {
  if (!datasetList) return;
  datasetList.innerHTML = "";

  datasets.forEach((item) => {
    const card = document.createElement("article");
    card.className = "dataset-card";

    const title = document.createElement("div");
    title.className = "dataset-title";

    const name = document.createElement("div");
    const h4 = document.createElement("h4");
    h4.textContent = item.company;
    const sub = document.createElement("p");
    sub.className = "dataset-sub";
    sub.textContent = `${item.sector} / ${item.region}`;

    name.appendChild(h4);
    name.appendChild(sub);

    const badge = document.createElement("span");
    badge.className = `chip${item.tagTone ? ` ${item.tagTone}` : ""}`;
    badge.textContent = item.tag || "Encrypted";

    title.appendChild(name);
    title.appendChild(badge);

    const fields = document.createElement("div");
    fields.className = "dataset-fields";
    fields.appendChild(createDataRow("e", item.e));
    fields.appendChild(createDataRow("n", item.n));
    fields.appendChild(createDataRow("c", item.c));

    card.appendChild(title);
    card.appendChild(fields);

    datasetList.appendChild(card);
  });
};

const renderBugReports = () => {
  if (!bugReportList) return;
  bugReportList.innerHTML = "";

  bugReports.forEach((report) => {
    const article = document.createElement("article");
    article.className = "bug-report";

    const summary = document.createElement("p");
    summary.className = "bug-summary";
    summary.textContent = report.summary;

    const meta = document.createElement("div");
    meta.className = "bug-meta";

    const metaItems = [
      { label: "Reporter", value: report.reporter },
      { label: "Ticket", value: report.ticket },
      { label: "Severity", value: report.severity },
      { label: "Status", value: report.status },
    ];

    metaItems.forEach((item) => {
      const wrap = document.createElement("div");
      const label = document.createElement("p");
      label.className = "meta-label";
      label.textContent = item.label;
      const value = document.createElement("p");
      value.className = "meta-value";
      value.textContent = item.value;
      wrap.appendChild(label);
      wrap.appendChild(value);
      meta.appendChild(wrap);
    });

    const pre = document.createElement("pre");
    const code = document.createElement("code");
    code.textContent = report.code;
    pre.appendChild(code);

    article.appendChild(summary);
    article.appendChild(meta);
    article.appendChild(pre);

    bugReportList.appendChild(article);
  });
};

const renderDashboard = () => {
  const vaultMetric = document.querySelector("[data-metric='vaults']");
  const bugMetric = document.querySelector("[data-metric='bugs']");
  if (vaultMetric) vaultMetric.textContent = String(datasets.length);
  if (bugMetric) bugMetric.textContent = String(bugReports.length);
};

if (loginForm && hasValidAuth()) {
  window.location.href = "index.html";
}

if (loginForm) {
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(loginForm);
    const adminId = String(formData.get("adminId") || "").trim().toLowerCase();
    const accessKey = String(formData.get("accessKey") || "").trim();

    if (adminId === "admin" && accessKey === "lowcortisol") {
      setAuth(true);
      localStorage.setItem("lc_audio_autoplay", "1");
      showToast("Access granted");
      window.location.href = "index.html";
      return;
    }

    if (loginStatus) {
      loginStatus.textContent = "Invalid credentials. Check username and password.";
    }
  });
}

if (adminShell) {
  if (!hasValidAuth()) {
    window.location.href = "login.html";
  } else {
    adminShell.removeAttribute("hidden");
    if (logoutBtn) logoutBtn.hidden = false;
    renderDatasets();
    renderBugReports();
    renderDashboard();

    const audio = document.getElementById("bgAudio");

    if (audio) {
      const shouldAutoplay = localStorage.getItem("lc_audio_autoplay") === "1";
      const alreadyPlaying = localStorage.getItem("lc_audio_playing") === "1";

      const savedTime = localStorage.getItem("lc_audio_time");
      if (savedTime) {
        audio.currentTime = parseFloat(savedTime);
      }

      if (shouldAutoplay || alreadyPlaying) {
        localStorage.setItem("lc_audio_playing", "1");

        audio.muted = true;

        audio.play().then(() => {
          audio.muted = false;
        }).catch(() => {
          console.log("Autoplay blocked");
        });

        localStorage.removeItem("lc_audio_autoplay");
      }

      if (!window._audioTrackerStarted) {
        window._audioTrackerStarted = true;

        setInterval(() => {
          if (!audio.paused) {
            localStorage.setItem("lc_audio_time", audio.currentTime);
          }
        }, 500);
      }
    }
    
  }
}

if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    setAuth(false);
    window.location.href = "login.html";
  });
}



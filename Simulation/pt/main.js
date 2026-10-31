var STAGE = "tests";
var PROBE_DEV = "R-DBP";
var PROBE_CMDS = ["configure terminal", "crypto ipsec transform-set TS-X esp-aes esp-sha-hmac", "exit", "exit", "show running-config | include hostname"];
var ONLY = ["R-WAN2","R-BHTQ"];
var BASE = ROOT + "../../";
var lw = ipc.appWindow().getActiveWorkspace().getLogicalWorkspace();
var net = ipc.network();
var fm = ipc.systemFileManager();
var LOGBUF = "";
var _log = log;
log = function (m) { LOGBUF += String(m) + "\n"; _log(m); };
function flush() { fm.writePlainTextToFile(BASE + "Simulation/pt/run.log", LOGBUF); }
var LICENSED = ["R-WAN2", "R-BHTQ"];


function toEnable(cl, name) {
    for (var k = 0; k < 6; k++) {
        var pr = String(cl.getPrompt());
        if (/initial configuration dialog/.test(pr)) { cl.enterCommand("no"); cl.enterCommand(""); continue; }
        if (/^Username/i.test(pr)) { cl.enterCommand("admin"); cl.enterCommand("Lab@2026"); continue; }
        if (/^Password/i.test(pr)) { cl.enterCommand("Lab@2026"); continue; }
        if (/#$/.test(pr)) break;
        if (/>$/.test(pr)) { cl.enterCommand("enable"); if (/^Password/i.test(String(cl.getPrompt()))) cl.enterCommand(name === "FW-HCM" ? "" : "Lab@2026"); continue; }
        cl.enterCommand("");
    }
    log(name + " prompt " + cl.getPrompt());
}

function license(name) {
    var d = net.getDevice(name);
    try { d.skipBoot(); } catch (e) {}
    var cl = d.getCommandLine();
    toEnable(cl, name);
    cl.enterCommand("configure terminal");
    cl.enterCommand("license boot module c2900 technology-package securityk9");
    cl.enterCommand("yes");
    cl.enterCommand("end");
    cl.enterCommand("write memory");
    cl.enterCommand("reload");
    cl.enterCommand("");
    log(name + " license sent, prompt " + cl.getPrompt());
}

function readLines(path) {
    var s = fm.getFileContents(path);
    return String(s).split(/\r?\n/);
}

function longPort(p) {
    p = p.replace(/^Gi/, "GigabitEthernet").replace(/^Fa/, "FastEthernet");
    return p;
}

function modelOf(name) {
    if (/^(ISP1|ISP2|INET|EDGE1|EDGE2|R-WAN1|R-WAN2|R-DBP|R-BHTQ)$/.test(name)) return ["2911", 0];
    if (name === "FW-HCM") return ["5506-X", 27];
    if (/^(CORE1|CORE2|DS-.*)$/.test(name)) return ["3650-24PS", 16];
    if (/^(ACC-.*|SW-.*)$/.test(name)) return ["2960-24TT", 1];
    if (/^AP-/.test(name)) return ["AccessPoint-PT", 7];
    if (/^(PORTAL|MAIL-GW|HIS-APP|PACS|AD-DNS|NMS|NVR|WEB-INET|SRV-.*)$/.test(name)) return ["Server-PT", 9];
    if (name === "WLC") return ["AccessPoint-PT", 7];
    return ["PC-PT", 8];
}

var FIXED = {
    "INET": [700, 40], "WEB-INET": [900, 40],
    "ISP1": [500, 140], "ISP2": [900, 140], "TELE-PC": [1100, 140],
    "EDGE1": [500, 240], "EDGE2": [900, 240],
    "FW-HCM": [600, 340], "SW-DMZ": [1000, 340], "SW-SRV": [1300, 340],
    "WLC": [200, 440], "CORE1": [400, 440], "CORE2": [600, 440],
    "PORTAL": [920, 440], "MAIL-GW": [1080, 440],
    "HIS-APP": [1200, 440], "PACS": [1280, 440], "AD-DNS": [1360, 440], "NMS": [1440, 440], "NVR": [1520, 440],
    "DS-A1": [150, 540], "DS-A2": [350, 540], "DS-B1": [650, 540], "DS-B2": [850, 540],
    "R-WAN1": [1000, 540], "R-WAN2": [1500, 540],
    "ACC-A": [250, 660], "ACC-B": [750, 660],
    "R-DBP": [1100, 660], "R-BHTQ": [1700, 660],
    "SW-DBP-1": [1000, 780], "SW-DBP-2": [1200, 780], "SW-BHTQ-1": [1600, 780], "SW-BHTQ-2": [1800, 780]
};

function parseWiring() {
    var rows = readLines(BASE + "docs/generated/wiring.md");
    var out = [];
    for (var i = 0; i < rows.length; i++) {
        var c = rows[i].split("|");
        if (c.length < 7) continue;
        if (!/^\s*\d+\s*$/.test(c[1])) continue;
        out.push({ a: c[2].trim(), pa: c[3].trim(), b: c[4].trim(), pb: c[5].trim(), kind: /thẳng/.test(c[6]) ? "straight" : "cross" });
    }
    return out;
}

function build() {
    var links = parseWiring();
    log("links parsed " + links.length);
    var names = {};
    for (var i = 0; i < links.length; i++) { names[links[i].a] = 1; names[links[i].b] = 1; }
    var pos = {};
    for (var n in FIXED) pos[n] = FIXED[n];
    var perSwitch = {};
    for (var i = 0; i < links.length; i++) {
        var l = links[i];
        var sw = /^(ACC-|SW-|DS-)/.test(l.a) ? l.a : null;
        if (sw && !pos[l.b] && /^(PC-|CAM-|MED-|PHONE-|AP-|SRV-)/.test(l.b)) {
            perSwitch[sw] = (perSwitch[sw] || 0) + 1;
            var k = perSwitch[sw] - 1;
            var s = FIXED[sw];
            var rowY = s[1] + 120 + (/-2$/.test(sw) ? 100 : 0) + (k % 2) * 0;
            pos[l.b] = [s[0] - 250 + k * 50, rowY + (k % 2) * 45];
        }
    }
    var made = 0;
    for (var nm in names) {
        if (!pos[nm]) { log("no position for " + nm); continue; }
        var m = modelOf(nm);
        var got = lw.addDevice(m[1], m[0], pos[nm][0], pos[nm][1]);
        if (!got) { log("add failed " + nm); continue; }
        var d = net.getDevice(got);
        d.setName(nm);
        made++;
    }
    log("devices made " + made);
    var ok = 0, bad = 0;
    for (var j = 0; j < links.length; j++) {
        var q = links[j];
        var types = q.kind === "straight" ? [8100, 8107] : [8101, 8107];
        var done = false;
        for (var t = 0; t < types.length && !done; t++) {
            try { done = lw.createLink(q.a, longPort(q.pa), q.b, longPort(q.pb), types[t]); } catch (e) { done = false; }
        }
        if (done) ok++; else { bad++; log("link failed " + q.a + " " + q.pa + " - " + q.b + " " + q.pb); }
    }
    log("links ok " + ok + " failed " + bad);
}


function pushConfig(name) {
    var path = BASE + "Configurations/" + name + ".txt";
    var lines = readLines(path);
    var d = net.getDevice(name);
    if (!d) { log("missing device " + name); return; }
    try { d.skipBoot(); } catch (e) { log("skipBoot " + name + " " + e); }
    var cl = d.getCommandLine();
    var buf = "";
    cl.registerEvent("outputWritten", null, function (src, args) {
        try { buf += String(args.newOutput); } catch (e1) {}
    });
    toEnable(cl, name);
    cl.enterCommand("");
    cl.enterCommand("terminal length 0");
    cl.enterCommand("");
    cl.enterCommand("configure terminal");
    var count = 0;
    for (var i = 0; i < lines.length; i++) {
        var ln = lines[i];
        if (!ln.replace(/\s/g, "")) continue;
        cl.enterCommand(ln);
        count++;
    }
    cl.enterCommand("end");
    cl.enterCommand("write memory");
    var errs = [];
    var rows = buf.split(/\r?\n/);
    for (var r = 0; r < rows.length; r++) {
        if (/^% |Invalid input|Incomplete command|Ambiguous command|ERROR:/.test(rows[r]) && !/^\s*\^?\s*$/.test(rows[r])) errs.push((rows[r - 2] || "") + " || " + (rows[r - 1] || "") + " || " + rows[r]);
    }
    log(name + " lines " + count + " prompt " + cl.getPrompt() + " errors " + errs.length);
    for (var e3 = 0; e3 < errs.length && e3 < 40; e3++) log("  " + errs[e3]);
}

function configure(list) {
    for (var i = 0; i < list.length; i++) {
        try { pushConfig(list[i]); } catch (e) { log("config error " + list[i] + " " + e); }
    }
}

function probe(name, cmds) {
    var d = net.getDevice(name);
    var cl = d.getCommandLine();
    var buf = "";
    cl.registerEvent("outputWritten", null, function (src, args) { try { buf += String(args.newOutput); } catch (e) {} });
    toEnable(cl, name);
    for (var i = 0; i < cmds.length; i++) cl.enterCommand(cmds[i]);
    log("PROBE OUTPUT\n" + buf);
}

function api() {
    var out = [];
    for (var k in lw) out.push(k);
    log("lw: " + out.join(" "));
    var w = ipc.appWindow();
    var o2 = [];
    for (var k2 in w) o2.push(k2);
    log("appWindow: " + o2.join(" "));
    var d = net.getDevice("DS-A1");
    var o3 = [];
    for (var k3 in d) o3.push(k3);
    log("device: " + o3.join(" "));
}

var SC = 0.8;
var LAYOUT = {
    "INET": [800, 60], "WEB-INET": [1050, 60],
    "ISP1": [500, 200], "ISP2": [1100, 200], "TELE-PC": [1350, 200],
    "EDGE1": [500, 340], "EDGE2": [1100, 340],
    "FW-HCM": [800, 480],
    "SW-DMZ": [250, 480], "PORTAL": [150, 580], "MAIL-GW": [350, 580],
    "SW-SRV": [1350, 480], "HIS-APP": [1200, 580], "PACS": [1300, 580], "AD-DNS": [1400, 580], "NMS": [1500, 580], "NVR": [1600, 580],
    "CORE1": [600, 720], "CORE2": [1000, 720], "WLC": [420, 720],
    "DS-A1": [250, 880], "DS-A2": [500, 880], "DS-B1": [1100, 880], "DS-B2": [1350, 880],
    "ACC-A": [375, 1040], "ACC-B": [1225, 1040],
    "R-WAN1": [1700, 720], "R-WAN2": [2500, 720],
    "R-DBP": [1700, 880], "R-BHTQ": [2500, 880],
    "SW-DBP-1": [1600, 1040], "SW-DBP-2": [1850, 1040], "SW-BHTQ-1": [2400, 1040], "SW-BHTQ-2": [2650, 1040],
    "SRV-DBP": [2125, 1200], "SRV-BHTQ": [3000, 1200]
};
var GROUPS = [
    ["ACC-A thiet bi", [450, 1200], /^(CAM-A|MED-A|PHONE-A)$/],
    ["ACC-B PC", [950, 1200], /^PC-B-/],
    ["ACC-B thiet bi", [1175, 1200], /^(AP-B|CAM-B|MED-B|PHONE-B)$/],
    ["DBP-1 PC", [1440, 1200], /^PC-DBP-(CLINIC|LABIMG)/],
    ["DBP-1 thiet bi", [1610, 1200], /^(AP-DBP-1|CAM-DBP|PHONE-DBP)$/],
    ["DBP-2 PC", [1780, 1200], /^PC-DBP-(ADMIN|IT)$/],
    ["DBP-2 thiet bi", [1940, 1200], /^(AP-DBP-2|MED-DBP)$/],
    ["BHTQ-1 PC", [2310, 1200], /^PC-BHTQ-(CLINIC|LABIMG)/],
    ["BHTQ-1 thiet bi", [2475, 1200], /^(AP-BHTQ-1|CAM-BHTQ|PHONE-BHTQ)$/],
    ["BHTQ-2 PC", [2640, 1200], /^PC-BHTQ-(ADMIN|IT)$/],
    ["BHTQ-2 thiet bi", [2800, 1200], /^(AP-BHTQ-2|MED-BHTQ)$/]
];

function layout() {
    var moved = 0;
    for (var n in LAYOUT) {
        var d = net.getDevice(n);
        if (!d) { log("no device " + n); continue; }
        d.moveToLocation(Math.round(LAYOUT[n][0] * SC), Math.round(LAYOUT[n][1] * SC));
        moved++;
    }
    log("moved " + moved);
    var links = parseWiring();
    var all = {};
    for (var i = 0; i < links.length; i++) { all[links[i].a] = 1; all[links[i].b] = 1; }
    for (var g = 0; g < GROUPS.length; g++) {
        var members = [];
        for (var nm in all) if (GROUPS[g][2].test(nm)) members.push(nm);
        members.sort();
        var bx = Math.round(GROUPS[g][1][0] * SC), by = Math.round(GROUPS[g][1][1] * SC);
        for (var m = 0; m < members.length; m++) {
            var dv = net.getDevice(members[m]);
            dv.moveToLocation(bx + (m % 4) * 42, by + Math.floor(m / 4) * 48);
        }
        log("block " + GROUPS[g][0] + " members " + members.length + " at " + bx + "," + by);
    }
}


function chk(list) {
    for (var i = 0; i < list.length; i++) {
        try {
            var d = net.getDevice(list[i]);
            var cl = d.getCommandLine();
            var buf = "";
            cl.registerEvent("outputWritten", null, function (src, args) { try { buf += String(args.newOutput); } catch (e) {} });
            toEnable(cl, list[i]);
            cl.enterCommand("terminal length 0");
            cl.enterCommand("show version");
            var rows = buf.split(/\r?\n/);
            for (var r = 0; r < rows.length; r++) if (/securityk9|ipbase|Technology Package/.test(rows[r])) log(list[i] + " :: " + rows[r]);
        } catch (e2) { log("chk error " + list[i] + " " + e2); }
    }
}

var VER = {
  "ACC-A": ["show vlan brief", "show interfaces trunk", "show interfaces status"],
  "DS-A1": ["show ip dhcp pool", "show ip interface brief"]
};
function verify() {
    for (var nm in VER) {
        try {
            var d = net.getDevice(nm);
            var cl = d.getCommandLine();
            var buf = "";
            cl.registerEvent("outputWritten", null, function (src, args) { try { buf += String(args.newOutput); } catch (e) {} });
            toEnable(cl, nm);
            for (var i = 0; i < VER[nm].length; i++) cl.enterCommand(VER[nm][i]);
            log("==== " + nm + "\n" + buf);
        } catch (e2) { log("ver error " + nm + " " + e2); }
    }
}

var STATIC = {
  "HIS-APP": ["10.10.36.66", "255.255.255.240", "10.10.36.65"],
  "PACS": ["10.10.36.68", "255.255.255.240", "10.10.36.65"],
  "AD-DNS": ["10.10.36.70", "255.255.255.240", "10.10.36.65"],
  "NMS": ["10.10.36.72", "255.255.255.240", "10.10.36.65"],
  "NVR": ["10.10.36.73", "255.255.255.240", "10.10.36.65"],
  "PORTAL": ["10.10.36.82", "255.255.255.240", "10.10.36.81"],
  "MAIL-GW": ["10.10.36.83", "255.255.255.240", "10.10.36.81"],
  "WEB-INET": ["192.0.2.10", "255.255.255.0", "192.0.2.1"],
  "TELE-PC": ["198.51.101.10", "255.255.255.0", "198.51.101.1"],
  "SRV-DBP": ["10.20.5.98", "255.255.255.248", "10.20.5.97"],
  "SRV-BHTQ": ["10.30.5.98", "255.255.255.248", "10.30.5.97"]
};
function hosts() {
    var n = net.getDeviceCount();
    for (var i = 0; i < n; i++) {
        var d = net.getDeviceAt(i);
        var nm = String(d.getName());
        try {
            if (STATIC[nm]) {
                var p = d.getPort("FastEthernet0");
                p.setIpSubnetMask(STATIC[nm][0], STATIC[nm][1]);
                p.setDefaultGateway(STATIC[nm][2]);
                log("static " + nm + " " + STATIC[nm][0]);
            } else if (modelOf(nm)[0] === "PC-PT" && !/^AP-|^WLC/.test(nm)) {
                var q = d.getPort("FastEthernet0");
                q.setDhcpClientFlag(true);
                log("dhcp " + nm);
            }
        } catch (eh) { log("host error " + nm + " " + eh); }
    }
}

var TESTS = [
  ["PC-A-OUTPATIENT-1", "ping -n 3 10.10.2.140"],
  ["PC-A-RECEPTION", "ping -n 3 10.10.3.229"],
  ["PC-A-RECEPTION", "tracert 10.10.3.229"],
  ["PC-A-OUTPATIENT-1", "ping -n 3 10.10.16.133"],
  ["PC-A-OUTPATIENT-1", "ping -n 3 10.20.0.11"],
  ["PC-A-OUTPATIENT-1", "tracert 10.20.0.11"],
  ["PC-A-OUTPATIENT-1", "ping -n 3 10.30.0.11"],
  ["PC-DBP-CLINIC-1", "ping -n 3 10.30.0.11"],
  ["PC-A-OUTPATIENT-1", "ping -n 3 10.10.36.82"],
  ["PORTAL", "ping -n 3 10.10.2.139"],
  ["PC-A-RECEPTION", "ping -n 3 192.0.2.10"],
  ["PC-A-RECEPTION", "tracert 192.0.2.10"],
  ["CAM-A", "ping -n 3 10.10.36.66"],
  ["CAM-A", "ping -n 3 10.10.36.73"],
  ["MED-A", "ping -n 3 10.10.2.139"],
  ["MED-A", "ping -n 3 10.10.36.66"]
];
var QI = 13, CUR = null, QDONE = false, QCL = {};
function qnext() {
    if (QI >= TESTS.length) { LOGBUF += "\n#### ALL TESTS DONE\n"; flush(); return; }
    var t = TESTS[QI++];
    CUR = t[0]; QDONE = false;
    LOGBUF += "\n#### " + t[0] + " >>> " + t[1] + "\n";
    flush();
    QCL[t[0]].enterCommand(t[1]);
}
function tests() {
    for (var t = 0; t < TESTS.length; t++) {
        var nm = TESTS[t][0];
        if (QCL[nm]) continue;
        var cl = net.getDevice(nm).getCommandLine();
        QCL[nm] = cl;
        (function (name) {
            cl.registerEvent("outputWritten", null, function (src, args) {
                try {
                    if (name !== CUR) return;
                    var o = String(args.newOutput);
                    LOGBUF += o;
                    flush();
                    if (/Packets: Sent|Trace complete|could not find host/.test(o)) QDONE = true;
                    if (QDONE && /C:\\>/.test(o)) { QDONE = false; qnext(); }
                } catch (e) {}
            });
        })(nm);
    }
    qnext();
}

function allPcs() {
    var out = [];
    var n = net.getDeviceCount();
    for (var i = 0; i < n; i++) {
        var nm = String(net.getDeviceAt(i).getName());
        if (/^Power/.test(nm)) continue;
        if (modelOf(nm)[0] === "PC-PT" && !/^AP-|^WLC/.test(nm)) out.push(nm);
    }
    return out;
}
function pcRun(cmds) {
    var names = allPcs();
    for (var i = 0; i < names.length; i++) {
        try {
            var cl = net.getDevice(names[i]).getCommandLine();
            (function (tag) { cl.registerEvent("outputWritten", null, function (src, args) { try { LOGBUF += String(args.newOutput).replace(/\n/g, "\n@" + tag + " "); flush(); } catch (e) {} }); })(names[i]);
            for (var k = 0; k < cmds.length; k++) cl.enterCommand(cmds[k]);
        } catch (e2) { log("pcRun error " + names[i] + " " + e2); }
    }
    flush();
}
if (STAGE === "renew") pcRun(["ipconfig /renew"]);
if (STAGE === "ips") pcRun(["ipconfig"]);
if (STAGE === "tests") tests();
if (STAGE === "hosts") hosts();
if (STAGE === "ver") verify();
if (STAGE === "chk") chk(["EDGE1","EDGE2","R-WAN1","R-WAN2","R-DBP","R-BHTQ","ISP1","ISP2"]);
if (STAGE === "layout") { try { layout(); } catch (eL) { log("layout error " + eL); } }
if (STAGE === "api") api();
if (STAGE === "build") build();
if (STAGE === "probe") probe(PROBE_DEV, PROBE_CMDS);
if (STAGE === "cfg") configure(ONLY);
if (STAGE === "lic") { for (var li = 0; li < LICENSED.length; li++) license(LICENSED[li]); }
flush();
log("stage " + STAGE + " finished");

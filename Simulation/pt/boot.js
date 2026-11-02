var ROOT = "/Users/khangnguyendinh/Desktop/Ka's Desktop/School/Computer Network/HK261/Assignments/Assignment2/Simulation/pt/";
function log(m) { try { dprint(String(m)); } catch (e) { print(String(m)); } }
try {
    var fm = ipc.systemFileManager();
    var src = fm.getFileContents(ROOT + "main.js");
    log("main.js bytes " + (src ? src.length : "null"));
    eval(src);
} catch (e) {
    log("boot error " + e);
}

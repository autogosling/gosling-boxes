import puppeteer from "puppeteer";
import * as fs from "node:fs/promises";
import path from "node:path";
import EventEmitter from "node:events";

const emitter = new EventEmitter()
emitter.setMaxListeners(100)


/**
 * @param {string} spec
 * @param {{ reactVersion: string, pixijsVersion: string, higlassVersion: string, goslingVersion: string }} pkgOptions
 * @returns {string}
 */
function html(spec, {
    reactVersion = "17",
    pixijsVersion = "6",
    higlassVersion = "1.11",
    goslingVersion = "0.9.22",
} = {}) {
    let baseUrl = "https://unpkg.com";
    return `\
<!DOCTYPE html>
<html>
	<link rel="stylesheet" href="${baseUrl}/higlass@${higlassVersion}/dist/hglib.css">
	<script src="${baseUrl}/react@${reactVersion}/umd/react.production.min.js"></script>
	<script src="${baseUrl}/react-dom@${reactVersion}/umd/react-dom.production.min.js"></script>
	<script src="${baseUrl}/pixi.js@${pixijsVersion}/dist/browser/pixi.min.js"></script>
	<script src="${baseUrl}/higlass@${higlassVersion}/dist/hglib.js"></script>
	<script src="${baseUrl}/gosling.js@${goslingVersion}/dist/gosling.js"></script>
<body>
	<div id="vis"></div>
	<script>
		let api = gosling.embed(document.getElementById("vis"), JSON.parse(\`${spec}\`))
		window.tracks = api.then(a=>a.getTracks())
        window.canvas = api.then(a=>a.getCanvas())
        
	</script>
</body>
</html>`;
}



/**
 * @param {string} spec
 * @param {string} apiName
 * @returns {Promise<Buffer>}
 */
async function callAPI(spec, output_dir) {

    let browser = await puppeteer.launch({
        headless: true,
        args: ["--use-gl=angle"], // more consistent rendering of transparent elements
    });

    let page = await browser.newPage();
    await page.setContent(html(spec), { waitUntil: "networkidle0" });
    let comp = await page.waitForSelector(".gosling-component");

    let canvas_elem = await page.$("canvas")
    await canvas_elem.screenshot({ path: output_dir["screenshots"], type: "png", omitBackground: true });

    let trackInfos = await page.evaluate(() => tracks)
    console.log(trackInfos)
    fs.writeFile(output_dir["tracks"], JSON.stringify(trackInfos.map(d => d['shape'])));
    fs.writeFile(output_dir["specs"], JSON.stringify(trackInfos.map(d => d['spec'])));
    fs.writeFile(output_dir["marks"], JSON.stringify(trackInfos.map(d=>d["spec"]["mark"])))
    fs.writeFile(output_dir["layouts"], JSON.stringify(trackInfos.map(d=>d["spec"]["layout"])))
    await browser.close();
}


const OUTPUT_DIR = "../data/extracted/bounding_box/"
const SPEC_DIR = "../data/extracted/specs/"
const SCNS_DIR = "../data/extracted/screenshot/"
const MARK_DIR = "../data/extracted/marks/"
const LAYOUT_DIR = "../data/extracted/layouts/"

async function runExamplePath(fp) {
    let name = path.parse(fp).name;
    let output = name + ".json";
    let output_spec = name + ".json";
    let screenshot_output = name + ".png";
    let mark_output = name +".json";
    let layout_output = name+".json";
    const output_dir = {
        "tracks": OUTPUT_DIR+output,
        "specs":SPEC_DIR+output_spec,
        "screenshots": SCNS_DIR+screenshot_output,
        "marks": MARK_DIR+mark_output,
        "layouts": LAYOUT_DIR+layout_output
    }
    let spec = await fs.readFile(fp, "utf8");
    await callAPI(spec, output_dir);
}

let input = process.argv[2];

if (!input) {
    console.error(
        "Usage: node gosling-boxes.js <input.json> <output.json>",
    );
    process.exit(1);
}

const stat = await fs.lstat(input)
if (stat.isFile()) {
    runExamplePath(input);
} else {
    var files = await (fs.readdir(input))
    console.log(files);
    for (const f of files){
        await runExamplePath(path.join(input, f));
    }
}

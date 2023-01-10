import puppeteer from "puppeteer";
import * as fs from "node:fs/promises";
import path from "node:path";
import * as fss from "node:fs";



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


function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
      currentDate = Date.now();
    } while (currentDate - date < milliseconds);
  }


/**
 * @param {string} spec
 * @param {string} apiName
 * @returns {Promise<Buffer>}
 */
async function callAPI(spec, output_dir) {

    let browser = await puppeteer.launch({
        headless: true,
        args: ["--use-gl=egl"], // more consistent rendering of transparent elements
    });

    let page = await browser.newPage();
    await page.setContent(html(spec), { waitUntil: "networkidle0" });
    //let comp = await page.waitForSelector(".gosling-component");
    
    let canvas_elem = await page.$("canvas");
    await canvas_elem.screenshot({ path: output_dir["screenshots"], type: "png", omitBackground: true });

    let trackInfos = await page.evaluate(() => tracks)
    console.log(trackInfos)
    console.log(trackInfos.map(d=>d['spec']['overlay']))

    trackInfos = trackInfos.filter(function(d){return d["spec"]["mark"] != "header" && (d["spec"]["mark"]!=null || d["spec"]["overlay"]!=null)})
    fs.writeFile(output_dir["tracks"], JSON.stringify(trackInfos.map(d => d['shape'])));
    fs.writeFile(output_dir["specs"], JSON.stringify(trackInfos.map(d => d['spec'])));
    fs.writeFile(output_dir["marks"], JSON.stringify(trackInfos.map(d=>{
        if ("overlay" in d["spec"]) return d["spec"]["overlay"].map(o=>{
            if (o["mark"] == null) return d["spec"]["mark"];
            else return o["mark"];
        }
            );
        else return [d["spec"]["mark"]];
    })))
    fs.writeFile(output_dir["layouts"], JSON.stringify(trackInfos.map(d=>d["spec"]["layout"])))
    fs.writeFile(output_dir["orientations"], JSON.stringify(trackInfos.map(d=>d["spec"]["orientation"])))
    fs.writeFile(output_dir["chart"], JSON.stringify(trackInfos.map(d=>{
        if ("overlay" in d["spec"]) return d["spec"]["overlay"].map(o=>{
            if (o["mark"] == "rect"){
                if (o["y"] == null) return "heatmap";
                else return "rect";
            }
            else if (o["mark"] == null) return d["spec"]["mark"];
            else return o["mark"];
        });
        else if ("xe" in d["spec"] && "ye" in d["spec"]) return ["heatmap"];
        else return [d["spec"]["mark"]];
    })))

    await browser.close();
}

function mkdir_if_not_exist(dir){
    if (!fss.existsSync(dir)){
        fss.mkdirSync(dir);
    }
}

function mkdirs(dirs){
    for (const dir of dirs){
        mkdir_if_not_exist(dir);
    }
}

const DATA_FOLDER = "/home/ec2-user/data/extracted-1/"
const OUTPUT_DIR = DATA_FOLDER+"bounding_box/"
const SPEC_DIR = DATA_FOLDER+"specs/"
const SCNS_DIR = DATA_FOLDER+"screenshot/"
const MARK_DIR = DATA_FOLDER+"marks/"
const LAYOUT_DIR = DATA_FOLDER+"layouts/"
const ORIENT_DIR = DATA_FOLDER+"orientations/"
const CHART_DIR = DATA_FOLDER+"chart/"

mkdir_if_not_exist(DATA_FOLDER)
mkdirs([OUTPUT_DIR,SPEC_DIR,SCNS_DIR,MARK_DIR,LAYOUT_DIR,ORIENT_DIR,CHART_DIR])


async function runExamplePath(fp) {
    let name = path.parse(fp).name;
    let output = name + ".json";
    let output_spec = name + ".json";
    let screenshot_output = name + ".png";
    let mark_output = name +".json";
    let layout_output = name+".json";
    let orient_output = name+".json";
    let chart_output = name+".json";
    const output_dir = {
        "tracks": OUTPUT_DIR+output,
        "specs":SPEC_DIR+output_spec,
        "screenshots": SCNS_DIR+screenshot_output,
        "marks": MARK_DIR+mark_output,
        "layouts": LAYOUT_DIR+layout_output,
        "orientations": ORIENT_DIR+orient_output,
        "chart": CHART_DIR+chart_output
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
        console.log(f);
        await runExamplePath(path.join(input, f));
    }
}

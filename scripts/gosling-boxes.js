import puppeteer from "puppeteer";
import * as fs from "node:fs/promises";
import path from "node:path";
//const path = require('node:path')


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

function blobCallback(){
    return b=>{
        const r = new FileReader();
        r.onloadend = () => {
            Cu.import('resource://gre/modules/osfile.jsm');
            const writePath = "test_canvas.png";
            const promise = OS.File.writeAtomic(writePath, new Uint8Array(r.result),
                                      {tmpPath:`${writePath}.tmp`});
        };
        r.readAsArrayBuffer(b);
    };
}



/**
 * @param {string} spec
 * @param {string} apiName
 * @returns {Promise<Buffer>}
 */
async function callAPI(spec, output, output_spec, img_path, screenshot_path) {
    fs.writeFile(output_spec, spec);

    let browser = await puppeteer.launch({
        headless: true,
        args: ["--use-gl=angle"], // more consistent rendering of transparent elements
    });

    let page = await browser.newPage();
    await page.setContent(html(spec), { waitUntil: "networkidle0" });
    let comp = await page.waitForSelector(".gosling-component");
    // await comp.screenshot({path:"test.png"})

    let canvas_elem = await page.$("canvas")
    await canvas_elem.screenshot({path: screenshot_path, type:"png", omitBackground:true});

    let canvas = await page.evaluate(()=> canvas);
    console.log(canvas);
    
    const dataUrl = await page.evaluate(async () => {
    
     return document.getElementsByTagName("canvas")[0].toDataURL();
    })
    const data = Buffer.from(dataUrl.split(',').pop(),"base64");
    fs.writeFile(img_path, data);

    let trackInfos = await page.evaluate(() => tracks)
    fs.writeFile(output, JSON.stringify(trackInfos.map(d => d['shape'])));

    await browser.close();
}



async function runExamplePath(fp){
    let name = path.parse(fp).name;
    let output = name+".json";
    let output_spec = name+".json";
    let img_output = name+".png";
    let screenshot_output = name+".png";
    let spec = await fs.readFile(fp, "utf8");
    await callAPI(spec, OUTPUT_DIR+output, SPEC_DIR+output_spec, IMG_DIR+img_output, SCNS_DIR+screenshot_output);
}

let input = process.argv[2];

if (!input ) {
    console.error(
        "Usage: node gosling-boxes.js <input.json> <output.json>",
    );
    process.exit(1);
}

const stat = await fs.lstat(input)
if (stat.isFile()){
    runExamplePath(input);
} else {
    var files = await(fs.readdir(input))
    console.log(files);
    files.forEach(s => runExamplePath(path.join(input,s)));
}




const OUTPUT_DIR = "../data/extracted/bounding_box/"
const IMG_DIR = "../data/extracted/images/"
const SPEC_DIR = "../data/extracted/specs/"
const SCNS_DIR = "../data/extracted/screenshot/"



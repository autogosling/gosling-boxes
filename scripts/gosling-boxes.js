import puppeteer from "puppeteer";
import * as fs from "node:fs/promises";

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
	</script>
</body>
</html>`;
}


/**
 * @param {string} spec
 * @param {string} apiName
 * @returns {Promise<Buffer>}
 */
async function callAPI(spec, output, output_spec) {
    let browser = await puppeteer.launch({
        headless: true,
        args: ["--use-gl=swiftshader"], // more consistent rendering of transparent elements
    });

    let page = await browser.newPage();
    await page.setContent(html(spec), { waitUntil: "networkidle0" });
    await page.waitForSelector(".gosling-component");
    let hg_wrapper = await page.$(".higlass-wrapper");
    await hg_wrapper.screenshot({path: "test.jpeg", type: "jpeg",quality:100, omitBackground:false});
    let trackInfos = await page.evaluate(() => tracks)
    console.log(trackInfos)
    fs.writeFile(output_spec, JSON.stringify(trackInfos))
    fs.writeFile(output, JSON.stringify(trackInfos.map(d => d['shape'])))
    //await page.screenshot({path: "test.png", type: "png", fullPage:true});
    await browser.close();
}

let input = process.argv[2];
let output = process.argv[3];
let output_spec = process.argv[4];

if (!input || !output|| !output_spec) {
    console.error(
        "Usage: node gosling-boxes.js <input.json> <output.json>",
    );
    process.exit(1);
}

let spec = await fs.readFile(input, "utf8");
await callAPI(spec, output, output_spec);

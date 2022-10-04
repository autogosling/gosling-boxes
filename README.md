 
# Gosling-Boxes

First, make sure you have installed node.js in your computer.

### how to run the node.js script

In the root folder (gosling-boxes),  
run `npm install`

Inside the script folder (gosling-boxes/scripts), run
`node gosling-boxes.js example.json tracks.json`  
example.json stores the visualization spec.  
tracks.json saves the outputs of api calls.  

**Update**: run 
`node gosling-boxes.js example.json`
will directly generate a file with bounding boxes information `example.json` in the `data/extracted/bounding_box` directory, a file with spec `example.json` in the `data/extracted/specs` directory, a file with canvas `example.png` in the `data/extracted/images` folder, and a file with screenshot view of canvas `example.png` in the `data/extracted/screeshot` folder.


### how to run the react app
`npm install`
`npm start`
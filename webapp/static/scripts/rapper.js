

function runVisualization(beaker){

// visualize words as nodes and words that rhyme in adjacent lines are connected by edges
d3.select("#graph").selectAll("*").remove();
var vis = d3.select("#graph")
            .append("svg");

var width = 800,
    height= 800;
vis.attr("width", width)
  .attr("height", height);
var border = 60;
var maxwidth = width - 2*border,
    maxheight = height;

// compute positions of words
var word_grid = beaker.words;
var node_pos = {}
var nodes = []

var max_row_length = 0;
for (var i=0; i<word_grid.length; i++){
  if (word_grid[i].length >= max_row_length){
    max_row_length = word_grid[i].length;
  }
}

for (var i=0; i<word_grid.length; i++){
  for (var j=0; j<word_grid[i].length; j++){
    var xpos = border + j*maxwidth/word_grid[i].length;
//     var xpos = border + j*maxwidth/max_row_length;
    var ypos = i*maxheight/word_grid.length;
    var node_obj = {x: xpos, y: ypos, data:word_grid[i][j]};
    nodes.push(node_obj);
    node_pos[i+","+j] = node_obj;
  }
}


var elem = vis.selectAll("g")
  .data(nodes);

var elemEnter = elem.enter()
  .append("g")
  .attr("transform", function(d) { return "translate("+d.x+","+d.y+")"})


elemEnter.append("text")
  .attr("dx", function(d){return -20})
  .attr("font-size", "15px")
  .text(function(d){return d.data})


// rhyme links
var rhymes = beaker.rhymes;
// list of list of (indexprev, indexcurr, weight)
var links = []
for (var i=0; i<rhymes.length; i++){
  for (var j=0; j<rhymes[i].length; j++){
    var src = node_pos[i+","+rhymes[i][j][0]];
    var tgt = node_pos[(i+1)+","+rhymes[i][j][1]];
    // emphasize high multiplicity connections
    var wt = Math.pow(rhymes[i][j][2], 1.5);
    links.push({source: src, target: tgt, weight: wt})
  }
}

vis.selectAll(".line")
  .data(links)
  .enter()
  .append("line")
  .attr("x1", function(d) { return d.source.x })
  .attr("y1", function(d) { return d.source.y })
  .attr("x2", function(d) { return d.target.x })
  .attr("y2", function(d) { return d.target.y })
  .style("stroke-width", function(d) { return d.weight; })
  .style("opacity", "0.7")
  .style("stroke", "rgb(6,120,155)");



// inline rhyme links
var inlines = beaker.inlines;
// list of list of (index, index, weight)
var inline_links = []
for (var i=0; i<inlines.length; i++){
  for (var j=0; j<inlines[i].length; j++){
    var src = node_pos[i+","+inlines[i][j][0]];
    var tgt = node_pos[i+","+inlines[i][j][1]];
    var wt = inlines[i][j][2];
    inline_links.push({source: src, target: tgt, weight: wt});
  }
}

vis.selectAll(".inline")
  .data(inline_links)
  .enter()
  .append("path")
  .attr("d", function(d) {
    // curved link
    var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy);
    return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
  })
  .style("stroke-width", function(d) { return d.weight; })
  .style("fill", "none")
  .style("opacity", "0.7")
  .style("stroke", "rgb(255,179,0)");

}

import { Node, Edge } from "reactflow";
import useGraphStore, { GraphState } from "../utils/GraphUtilities";
import axios from "axios";
import { useState } from "react";
import { shallow } from "zustand/shallow";

const selector = (state: GraphState) => ({
  setNodes: state.setNodes,
  setEdges: state.setEdges,
  generateRandomNodes: state.generateRandomNodes,
  generateDebugNodeGraph: state.generateDebugNodeGraph,
  // ClusterNodesAround: state.ClusterNodesAround,
  ClusterAroundNode: state.ClusterAroundNode,
});
const ToolBar = () => {
  const {
    setNodes,
    setEdges,
    generateRandomNodes,
    generateDebugNodeGraph,
    // ClusterNodesAround,
    ClusterAroundNode,
  } = useGraphStore(selector, shallow);
  const [numToGenerate, setGenerate] = useState(0);
  const [toggle, setToggle] = useState(false);

  const RequestGraph = async (_id: string) => {
    console.log("Fetching graph from backend");
    try {
      const { data, status } = await axios.get(
        "http://localhost:5000/api/graph/",
        {
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "http://localhost",
          },
        },
      );
      if (status === 200) {
        console.log("Request succeeded");
        console.log(data);
        setNodes(data.graph.nodes);
        setEdges(data.graph.edges);
      } else {
        console.log(`Request failed with status ${status}:\n data: ${data}`);
      }
    } catch (e: any) {
      console.log(`Request failed with error:\n data: ${e}`);
    }
  };
  return (
    <div className="chat-bar">
      <div id="toolbar" className="flex-item">
        {/* this will contain all of the files used in the current notebook */}
        <div id="toolbar-toggle">
          <button onClick={() => setToggle(!toggle)}>Toggle Toolbar</button>
        </div>
        {toggle && (
          <>
            <div id="fetch-graph" className="toolbar-item">
              <br />
              <button onClick={() => RequestGraph("")}>Fetch Graph</button>
            </div>
            <div id="add-url" className="toolbar-item">
              <button>Add Url</button>
            </div>
            <div id="add-file" className="toolbar-item">
              <button>Add File</button>
            </div>
            <div id="add-random-nodes" className="toolbar-item">
              <button
                onClick={() => {
                  generateRandomNodes(numToGenerate);
                }}
              >
                Generate Random Nodes
              </button>
              <input
                type="number"
                onChange={(e) => {
                  let i = parseInt(e.target.value);
                  i == undefined ? setGenerate(0) : setGenerate(i);
                }}
              />
            </div>
            <div id="add-starting-nodes" className="toolbar-item">
              <button
                onClick={() => {
                  generateDebugNodeGraph();
                }}
              >
                Generate Debug Nodes
              </button>
            </div>
            <div className="toolbar-item">
              <button
                onClick={() => {
                  ClusterAroundNode(`${0}`);
                }}
              >
                Cluster Nodes
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ToolBar;

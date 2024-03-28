import "reactflow/dist/style.css";

import ReactFlow, { Controls } from "reactflow";

import ChatNode from "../Nodes/ChatNode";
import DocumentNode from "../Nodes/DocumentNode";

import { GraphState } from "../../utils/GraphUtilities";
import useGraphStore from "../../utils/GraphUtilities";
import { shallow } from "zustand/shallow";
import { useMemo } from "react";

const selector = (state: GraphState) => ({
  nodes: state.nodes,
  edges: state.edges,
  onNodesChange: state.onNodesChange,
  onEdgesChange: state.onEdgesChange,
  onConnect: state.onConnect,
  nodeTypes: state.nodeTypes,
});

const BaseFlow = () => {
  const { nodes, edges, onNodesChange, onEdgesChange, nodeTypes } =
    useGraphStore(selector, shallow);
  // I am very sorry for what I have inflicted upon you, future developer.
  const temporaryfixNodeTypes = {
    ChatNode: ChatNode,
    DocumentNode: DocumentNode,
  };
  const customNodeTypes = useMemo(() => temporaryfixNodeTypes, []);
  return (
    <div id="flow-container" className="flex-item">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={customNodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default BaseFlow;

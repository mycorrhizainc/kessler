"use client";
import BaseFlow from "../../lib/components/Flows/BaseFlow";
import ToolBar from "../../lib/components/ToolBarLegacy";

const ExperimentsView = () => {
  // store the graph locally

  return (
    <div id="notebook-container">
      <div id="workspace">
        <BaseFlow />
      </div>
      <ToolBar />
    </div>
  );
};

export default ExperimentsView;

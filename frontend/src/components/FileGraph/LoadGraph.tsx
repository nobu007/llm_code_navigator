import { FileEdge, FileNode } from "@/types/types";
import { useCamera, useLoadGraph } from "@react-sigma/core";
import Graph from "graphology";
import { random } from "graphology-layout";
import React, { useEffect } from "react";

interface LoadGraphProps {
  files: FileNode[];
  relationships: FileEdge[];
}

const LoadGraph: React.FC<LoadGraphProps> = ({ files, relationships }) => {
  const loadGraph = useLoadGraph();
  const camera = useCamera();

  useEffect(() => {
    const graph = new Graph();

    files.forEach((file) => {
      graph.addNode(file.id, {
        label: file.name,
        size: file.type === "file" ? 10 : 15,
        color: file.type === "file" ? "#6366f1" : "#10b981",
      });
    });

    relationships.forEach((rel) => {
      if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
        graph.addEdge(rel.source, rel.target, { size: 2, color: "#94a3b8" });
      }
    });

    // Apply layout
    random.assign(graph);

    loadGraph(graph);

    // Center the camera
    if (graph.order > 0) {
      const { x, y } = graph.getNodeAttributes(graph.nodes()[0]);
      camera.goto({ x, y, ratio: 1 }, { duration: 500 });
    }

    console.log("Graph loaded:", graph.order, "nodes,", graph.size, "edges");
  }, [loadGraph, files, relationships, camera]);

  return null;
};

export default LoadGraph;
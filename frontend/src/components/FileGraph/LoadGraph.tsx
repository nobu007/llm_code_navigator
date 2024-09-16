import { FileEdge, FileNode } from "@/types/types";
import { useCamera, useLoadGraph, useSigma } from "@react-sigma/core";
import Graph from "graphology";
import { circular } from "graphology-layout";
import React, { useEffect, useRef } from "react";

interface LoadGraphProps {
  files: FileNode[];
  relationships: FileEdge[];
  onNodeClick: (file: FileNode) => void;
}

const LoadGraph: React.FC<LoadGraphProps> = ({ files, relationships, onNodeClick }) => {
  const loadGraph = useLoadGraph();
  const camera = useCamera();
  const sigma = useSigma();
  const graphRef = useRef<Graph | null>(null);

  useEffect(() => {
    const graph = new Graph();
    graphRef.current = graph;

    files.forEach((file) => {
      graph.addNode(file.id, {
        label: file.name,
        size: file.type === "file" ? 10 : 15,
        color: file.type === "file" ? "#6366f1" : "#10b981",
        file: file,
      });
    });

    relationships.forEach((rel) => {
      if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
        graph.addEdge(rel.source, rel.target, {
          size: 2,
          color: "#94a3b8",
          type: "arrow",
        });
      }
    });

    circular.assign(graph);
    loadGraph(graph);

    if (graph.order > 0) {
      const { x, y } = graph.getNodeAttributes(graph.nodes()[0]);
      camera.goto({ x, y, ratio: 1 }, { duration: 500 });
    }

    sigma.on("clickNode", (event) => {
      const nodeId = event.node;
      const nodeAttributes = graph.getNodeAttributes(nodeId);
      onNodeClick(nodeAttributes.file);
    });

    console.log("Graph loaded:", graph.order, "nodes,", graph.size, "edges");
    sigma.refresh();

    return () => {
      if (graphRef.current) {
        graphRef.current.clear();
      }
      sigma.removeAllListeners("clickNode");
    };
  }, [loadGraph, files, relationships, camera, sigma, onNodeClick]);

  return null;
};

export default LoadGraph;
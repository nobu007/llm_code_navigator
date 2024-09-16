import { FileData, FileEdge, FileNode } from "@/types/types";
import { Box, Text, useColorModeValue } from "@chakra-ui/react";
import {
  SigmaContainer,
  useCamera,
  useLoadGraph,
  useSigma,
} from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css";
import Graph, { MultiDirectedGraph } from "graphology";
import { random } from "graphology-layout";
import React, { useEffect, useState } from "react";

function SimpleGraphA() {
	// グラフ生成
	const graph = new MultiDirectedGraph();
	// ノード追加
	graph.addNode("A", { x: 0, y: 0, label: "Node A", size: 10 });
	graph.addNode("B", { x: 1, y: 1, label: "Node B", size: 10 });
	// エッジ追加
	// graph.addEdgeWithKey("rel1", "A", "B", { label: "REL_1" });

	return (
		<div className="SimpleGraphA">
			<h1>単純なグラフ</h1>
			<SigmaContainer
				style={{ height: "500px" }}
				settings={{
					allowInvalidContainer: true,
					renderEdgeLabels: true,
					labelSize: 12,
					labelWeight: "bold",
				}}
				graph={graph}
			></SigmaContainer>
		</div>
	);
}

// export default SimpleGraphA;

interface FileGraphProps {
	fileData: FileData;
}
const LoadGraph: React.FC<{ files: FileNode[]; relationships: FileEdge[] }> = ({
	files,
	relationships,
}) => {
	const loadGraph = useLoadGraph();
	const camera = useCamera();
	const sigma = useSigma();

	React.useEffect(() => {
		const graph = new Graph();

		files.forEach((file) => {
			graph.addNode(file.id, {
				label: file.name,
				size: file.type === "file" ? 10 : 15,
				color: file.type === "file" ? "#6366f1" : "#10b981",
				x: Math.random(),
				y: Math.random(),
			});
		});

		relationships.forEach((rel) => {
			if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
				graph.addEdge(rel.source, rel.target, { size: 2, color: "#94a3b8" });
			}
		});

		if (graph.size > 0) {
			random.assign(graph);
		}

		loadGraph(graph);

		// Center the camera
		if (graph.order > 0) {
			const nodePositions = graph
				.nodes()
				.map((node) => graph.getNodeAttributes(node));
			const xValues = nodePositions.map((pos) => pos.x);
			const yValues = nodePositions.map((pos) => pos.y);
			const xMin = Math.min(...xValues);
			const xMax = Math.max(...xValues);
			const yMin = Math.min(...yValues);
			const yMax = Math.max(...yValues);
			const xCenter = (xMin + xMax) / 2;
			const yCenter = (yMin + yMax) / 2;
			camera.goto({ x: xCenter, y: yCenter, ratio: 1 }, { duration: 500 });
		}

		// Force render
		sigma.refresh();
	}, [loadGraph, files, relationships, camera, sigma]);

	return null;
};

const DynamicFileGraph: React.FC<FileGraphProps> = ({ fileData }) => {
	const bgColor = useColorModeValue("white", "gray.800");
	const [containerReady, setContainerReady] = useState(false);

	useEffect(() => {
		setContainerReady(true);
	}, []);

	if (fileData.files.length === 0) {
		return (
			<Box
				width="100%"
				height="500px"
				bg={bgColor}
				borderRadius="md"
				display="flex"
				alignItems="center"
				justifyContent="center"
			>
				<Text>No files to display</Text>
			</Box>
		);
	}

	return (
		<Box
			width="100%"
			height="500px"
			bg={bgColor}
			borderRadius="md"
			overflow="hidden"
		>
			{containerReady && (
				<SigmaContainer
					style={{ width: "100%", height: "100%" }}
					settings={{
						allowInvalidContainer: true,
						renderEdgeLabels: true,
						labelSize: 12,
						labelWeight: "bold",
					}}
				>
					<LoadGraph
						files={fileData.files}
						relationships={fileData.relationships}
					/>
				</SigmaContainer>
			)}
		</Box>
	);
};

export default DynamicFileGraph

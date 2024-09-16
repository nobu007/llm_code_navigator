import { FileData, FileEdge, FileNode } from '@/types/types'
import { Box, useColorModeValue } from '@chakra-ui/react'
import { SigmaContainer, useCamera, useLoadGraph } from "@react-sigma/core"
import Graph from "graphology"
import { random } from "graphology-layout"
import React, { useEffect, useState } from 'react'

interface FileGraphProps {
  fileData: FileData
}

const LoadGraph: React.FC<{ files: FileNode[], relationships: FileEdge[] }> = ({ files, relationships }) => {
  const loadGraph = useLoadGraph()
  const camera = useCamera()

  React.useEffect(() => {
    const graph = new Graph()

    files.forEach((file) => {
      graph.addNode(file.id, {
        label: file.name,
        size: file.type === "file" ? 10 : 15,
        color: file.type === "file" ? "#6366f1" : "#10b981",
      })
    })

    relationships.forEach((rel) => {
      if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
        graph.addEdge(rel.source, rel.target, { size: 2, color: "#94a3b8" })
      }
    })

    // Apply layout
    random.assign(graph)

    loadGraph(graph)

    // Center the camera
    if (graph.order > 0) {
      const { x, y } = graph.getNodeAttributes(graph.nodes()[0])
      camera.goto({ x, y, ratio: 1 }, { duration: 500 })
    }

    console.log("Graph loaded:", graph.order, "nodes,", graph.size, "edges")
  }, [loadGraph, files, relationships, camera])

  return null
}

const DynamicFileGraph: React.FC<FileGraphProps> = ({ fileData }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const [containerReady, setContainerReady] = useState(false)

  useEffect(() => {
    setContainerReady(true)
  }, [])

  return (
    <Box width="100%" height="500px" bg={bgColor} borderRadius="md" overflow="hidden">
      {containerReady && (
        <SigmaContainer
          style={{ width: '100%', height: '100%' }}
          settings={{
            allowInvalidContainer: true,
            renderEdgeLabels: true,
          }}
        >
          <LoadGraph files={fileData.files} relationships={fileData.relationships} />
        </SigmaContainer>
      )}
    </Box>
  )
}

export default DynamicFileGraph
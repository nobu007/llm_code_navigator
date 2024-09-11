import { useLoadGraph, useSigma } from '@react-sigma/core'
import Graph from 'graphology'
import { circular } from 'graphology-layout'
import React, { useEffect } from 'react'

interface FileSystemProps {
  fileSystem: {
    files: Array<{
      id: string
      name: string
      type: 'file' | 'directory'
      path: string
    }>
    relationships: Array<{
      source: string
      target: string
    }>
  } | null
}

const LoadGraph: React.FC<FileSystemProps> = ({ fileSystem }) => {
  const loadGraph = useLoadGraph()
  const sigma = useSigma()

  useEffect(() => {
    if (!fileSystem || !sigma) return

    const graph = new Graph()

    fileSystem.files.forEach(file => {
      graph.addNode(file.id, {
        label: file.name,
        size: file.type === 'file' ? 5 : 10,
        color: file.type === 'file' ? '#6366f1' : '#10b981'
      })
    })

    fileSystem.relationships.forEach(rel => {
      if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
        graph.addEdge(rel.source, rel.target, { size: 2, color: '#94a3b8' })
      }
    })

    // Apply a circular layout
    circular.assign(graph)

    // Load the graph
    loadGraph(graph)

    // Update node positions
    graph.forEachNode((node, attributes) => {
      const { x, y } = attributes
      sigma.getNodeDisplayData(node).x = x
      sigma.getNodeDisplayData(node).y = y
    })

    // Refresh the rendering
    sigma.refresh()

    // Center the camera
    const camera = sigma.getCamera()
    camera.animate({ ratio: 1.2 }, { duration: 1000 })

    console.log('Graph loaded:', graph.order, 'nodes,', graph.size, 'edges')
  }, [fileSystem, loadGraph, sigma])

  return null
}

export default LoadGraph
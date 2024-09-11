import { useLoadGraph } from '@react-sigma/core'
import Graph from 'graphology'
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

  useEffect(() => {
    if (!fileSystem) return

    const graph = new Graph()

    fileSystem.files.forEach(file => {
      graph.addNode(file.id, {
        label: file.name,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: 10,
        color: file.type === 'file' ? '#6366f1' : '#10b981'
      })
    })

    fileSystem.relationships.forEach(rel => {
      if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
        graph.addEdge(rel.source, rel.target, { size: 2, color: '#94a3b8' })
      }
    })

    loadGraph(graph)

    console.log('Graph loaded:', graph.order, 'nodes,', graph.size, 'edges')
  }, [fileSystem, loadGraph])

  return null
}

export default LoadGraph
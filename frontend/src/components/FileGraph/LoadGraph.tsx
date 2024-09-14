import { FileNode, Relationship } from '@/types/types';
import { useLoadGraph, useSigma } from '@react-sigma/core';
import Graph from 'graphology';
import { circular } from 'graphology-layout';
import React, { useEffect, useState } from 'react';

interface LoadGraphProps {
  files: FileNode[] | undefined
  relationships: Relationship[] | undefined
}

const LoadGraph: React.FC<LoadGraphProps> = ({ files, relationships }) => {
  const loadGraph = useLoadGraph()
  const sigma = useSigma()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!files || !relationships) {
      console.log('Files or Relationships not available')
      return
    }

    if (!sigma || !loadGraph) {
      console.log('Sigma or loadGraph not available')
      return
    }

    try {
      const graph = new Graph()

      // Add nodes
      files.forEach(file => {
        graph.addNode(file.id, {
          label: file.name,
          size: file.type === 'file' ? 5 : 10,
          color: file.type === 'file' ? '#6366f1' : '#10b981'
        })
      })

      // Add edges
      relationships.forEach(rel => {
        if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
          graph.addEdge(rel.source, rel.target, { size: 2, color: '#94a3b8' })
        } else {
          console.warn(`Unable to add edge: ${rel.source} -> ${rel.target}`)
        }
      })

      console.log('Graph created with', graph.order, 'nodes and', graph.size, 'edges')

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
      console.log('Graph refreshed')

      // Center the camera
      const camera = sigma.getCamera()
      camera.animate({ ratio: 1.2 }, { duration: 1000 })
      console.log('Camera animated')

      setError(null)
    } catch (error) {
      console.error('Error creating graph:', error)
      setError('Failed to create graph. Please try again.')
    }
  }, [files, relationships, loadGraph, sigma])

  if (error) {
    return <div>Error: {error}</div>
  }

  return null
}

export default LoadGraph
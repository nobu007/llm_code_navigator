import { FileData } from '@/types/types'
import { useLoadGraph, useSigma } from '@react-sigma/core'
import Graph from 'graphology'
import { circular } from 'graphology-layout'
import React, { useEffect } from 'react'

interface LoadGraphProps {
  fileData: FileData | null
}

const LoadGraph: React.FC<LoadGraphProps> = ({ fileData }) => {
  const loadGraph = useLoadGraph()
  const sigma = useSigma()

  useEffect(() => {
    if (!fileData || !sigma) {
      console.log('FileData or Sigma not available')
      return
    }

    console.log('FileData:', fileData)

    try {
      const graph = new Graph()

      fileData.files.forEach(file => {
        graph.addNode(file.id, {
          label: file.name,
          size: file.type === 'file' ? 5 : 10,
          color: file.type === 'file' ? '#6366f1' : '#10b981',
          borderColor: '#000',
          borderWidth: 2
        })
      })

      fileData.relationships.forEach(rel => {
        if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
          graph.addEdge(rel.source, rel.target, { size: 2, color: '#94a3b8' })
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

    } catch (error) {
      console.error('Error creating graph:', error)
    }
  }, [fileData, loadGraph, sigma])

  return null
}

export default LoadGraph
import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl, useCamera, useLoadGraph } from '@react-sigma/core'
import Graph from 'graphology'
import { Random } from 'graphology-layout'
import React, { useEffect, useRef } from 'react'

interface File {
  id: string
  name: string
  type: 'file' | 'directory'
}

interface Relationship {
  source: string
  target: string
}

interface DynamicSigmaContainerProps {
  files: File[]
  relationships: Relationship[]
}

const LoadGraph: React.FC<DynamicSigmaContainerProps> = ({ files, relationships }) => {
  const loadGraph = useLoadGraph()
  const camera = useCamera()

  useEffect(() => {
    const graph = new Graph()

    files.forEach(file => {
      graph.addNode(file.id, {
        label: file.name,
        size: file.type === 'file' ? 10 : 15,
        color: file.type === 'file' ? '#6366f1' : '#10b981'
      })
    })

    relationships.forEach(rel => {
      if (graph.hasNode(rel.source) && graph.hasNode(rel.target)) {
        graph.addEdge(rel.source, rel.target, { size: 2, color: '#94a3b8' })
      }
    })

    // Apply layout
    const layout = new Random(graph, { center: 0.5, scale: 1 })
    layout.assign()

    loadGraph(graph)

    // Center the camera
    const { x, y } = graph.getNodeAttributes(graph.nodes()[0])
    camera.animate({ x, y, ratio: 1 }, { duration: 500 })

    console.log('Graph loaded:', graph.order, 'nodes,', graph.size, 'edges')
  }, [loadGraph, files, relationships, camera])

  return null
}

const DynamicSigmaContainer: React.FC<DynamicSigmaContainerProps> = ({ files, relationships }) => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.height = '100%'
      containerRef.current.style.width = '100%'
    }
  }, [])

  return (
    <div ref={containerRef} style={{ height: '100%', width: '100%' }}>
      <SigmaContainer
        style={{ height: '100%', width: '100%' }}
        settings={{
          renderLabels: true,
          labelSize: 12,
          labelWeight: 'bold',
          defaultNodeColor: '#999',
          defaultEdgeColor: '#ccc',
          defaultNodeBorderWidth: 2,
          defaultNodeBorderColor: '#000',
          labelRenderedSizeThreshold: 6,
          labelDensity: 0.07,
          labelGridCellSize: 60,
          zIndex: true
        }}
      >
        <LoadGraph files={files} relationships={relationships} />
        <ControlsContainer position={'bottom-right'}>
          <ZoomControl />
          <FullScreenControl />
        </ControlsContainer>
      </SigmaContainer>
    </div>
  )
}

export default DynamicSigmaContainer
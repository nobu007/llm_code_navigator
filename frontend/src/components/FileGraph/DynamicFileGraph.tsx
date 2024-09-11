import { ControlsContainer, FullScreenControl, SigmaContainer, ZoomControl } from '@react-sigma/core'
import React, { useEffect, useRef } from 'react'
import styles from './FileGraph.module.css'
import LoadGraph from './LoadGraph'

interface DynamicFileGraphProps {
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

const DynamicFileGraph: React.FC<DynamicFileGraphProps> = ({ fileSystem }) => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.height = '500px'
    }
  }, [])

  return (
    <div ref={containerRef} className={styles.graphContainer}>
      <SigmaContainer
        className={styles.sigmaContainer}
        settings={{
          allowInvalidContainer: true,
          renderLabels: true,
          labelSize: 12,
          labelWeight: 'bold',
          defaultNodeColor: '#999',
          defaultEdgeColor: '#ccc',
          defaultNodeBorderWidth: 2,
          defaultNodeBorderColor: '#000',
        }}
      >
        <LoadGraph fileSystem={fileSystem} />
        <ControlsContainer position={'bottom-right'}>
          <ZoomControl />
          <FullScreenControl />
        </ControlsContainer>
      </SigmaContainer>
    </div>
  )
}

export default DynamicFileGraph
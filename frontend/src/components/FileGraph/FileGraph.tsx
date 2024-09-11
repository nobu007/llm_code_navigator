import dynamic from 'next/dynamic'
import React, { useEffect, useRef } from 'react'
import { useFileSystem } from '../../hooks/useFileSystem'
import styles from './FileGraph.module.css'

const SigmaContainer = dynamic(
  () => import('@react-sigma/core').then((mod) => mod.SigmaContainer),
  { ssr: false }
)

const ControlsContainer = dynamic(
  () => import('@react-sigma/core').then((mod) => mod.ControlsContainer),
  { ssr: false }
)

const ZoomControl = dynamic(
  () => import('@react-sigma/core').then((mod) => mod.ZoomControl),
  { ssr: false }
)

const FullScreenControl = dynamic(
  () => import('@react-sigma/core').then((mod) => mod.FullScreenControl),
  { ssr: false }
)

const LoadGraph = dynamic(
  () => import('./LoadGraph').then((mod) => mod.default),
  { ssr: false }
)

const FileGraph: React.FC = () => {
  const { fileSystem, loading, error } = useFileSystem()
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.height = '500px'
    }
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

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

export default FileGraph
import Graph from 'graphology'
import dynamic from 'next/dynamic'
import React, { useEffect, useRef } from 'react'
import { useFileSystem } from '../../hooks/useFileSystem'
import styles from './FileGraph.module.css'

const SigmaContainer = dynamic(() => import('@react-sigma/core').then(mod => mod.SigmaContainer), { ssr: false })

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
  const sigmaRef = useRef<any>(null)

  useEffect(() => {
    if (!fileSystem || !sigmaRef.current) return

    const graph = new Graph()

    fileSystem.files.forEach(file => {
      graph.addNode(file.id, {
        label: file.name,
        x: Math.random(),
        y: Math.random(),
        size: 15,
        color: file.type === 'file' ? '#6366f1' : '#10b981'
      })
    })

    fileSystem.relationships.forEach(rel => {
      graph.addEdge(rel.source, rel.target, { type: 'arrow', size: 5, color: '#94a3b8' })
    })

    sigmaRef.current.getGraph().clear()
    sigmaRef.current.getGraph().import(graph.export())
    sigmaRef.current.refresh()
  }, [fileSystem])

  return null
}

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
      <SigmaContainer className={styles.sigmaContainer} settings={{ allowInvalidContainer: true }}>
        <LoadGraph fileSystem={fileSystem} />
      </SigmaContainer>
    </div>
  )
}

export default FileGraph
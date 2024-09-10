import { fetchFileContent, fetchFileData } from '@/lib/api'
import { FileData, FileNode } from '@/types'
import { Graph } from 'graphology'
import dynamic from 'next/dynamic'
import React, { useEffect, useRef, useState } from 'react'
import FileContent from './FileContent'
import FileList from './FileList'

const DynamicSigma = dynamic(
  () => import('react-sigma').then((mod) => mod.Sigma),
  { ssr: false }
)

const DynamicRandomizeNodePositions = dynamic(
  () => import('react-sigma').then((mod) => mod.RandomizeNodePositions),
  { ssr: false }
)

const DynamicForceAtlas2 = dynamic(
  () => import('react-sigma').then((mod) => mod.ForceAtlas2),
  { ssr: false }
)

const FileGraph: React.FC = () => {
  const [fileData, setFileData] = useState<FileData | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const graphRef = useRef<Graph | null>(null)

  useEffect(() => {
    const loadFileData = async () => {
      try {
        const data = await fetchFileData()
        setFileData(data)
        initializeGraph(data)
      } catch (error) {
        console.error('Error fetching file data:', error)
      }
    }

    loadFileData()
  }, [])

  const initializeGraph = (data: FileData) => {
    const graph = new Graph()
    data.nodes.forEach((node: FileNode) => {
      graph.addNode(node.id, { label: node.label, size: 10, color: '#6c757d' })
    })
    data.edges.forEach((edge) => {
      graph.addEdge(edge.source, edge.target)
    })
    graphRef.current = graph
  }

  const handleNodeClick = async (node: string) => {
    setSelectedFile(node)
    try {
      const content = await fetchFileContent(node)
      setFileContent(content)
    } catch (error) {
      console.error('Error fetching file content:', error)
      setFileContent('Error loading file content')
    }
  }

  if (!fileData) {
    return <div className="flex justify-center items-center h-64">Loading...</div>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2">
        <div className="bg-white rounded-lg shadow-md p-4" style={{ height: '600px' }}>
          {graphRef.current && (
            <DynamicSigma
              graph={graphRef.current}
              style={{ width: '100%', height: '100%' }}
              onClickNode={(e) => handleNodeClick(e.data.node.id)}
              settings={{
                drawEdges: true,
                clone: false,
              }}
            >
              <DynamicRandomizeNodePositions>
                <DynamicForceAtlas2 iterationsPerRender={1} timeout={3000} />
              </DynamicRandomizeNodePositions>
            </DynamicSigma>
          )}
        </div>
      </div>
      <div className="space-y-6">
        <FileList
          files={fileData.nodes}
          selectedFile={selectedFile}
          onSelectFile={handleNodeClick}
        />
        <FileContent fileName={selectedFile} content={fileContent} />
      </div>
    </div>
  )
}

export default FileGraph
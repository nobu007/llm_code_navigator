import FileGraph from '@/components/FileGraph/FileGraph'
import FileList from '@/components/FileGraph/FileList'

import Layout from '@/components/layout/Layout'
import { useFileSystem } from '@/hooks/useFileSystem'
import React from 'react'

const Home: React.FC = () => {
  const { fileSystem, loading, error, getFileContent } = useFileSystem()

  console.log('Home component state:', { loading, error, fileSystem }) // デバッグログ

  if (loading) {
    return <div>Loading file system data...</div>
  }

  if (error) {
    return <div>Error: {error.message}</div>
  }

  if (!fileSystem) {
    return <div>No file system data available</div>
  }

  console.log('FileSystem data:', JSON.stringify(fileSystem, null, 2)) // 詳細なデバッグログ

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">LLM Code Navigator</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-semibold mb-4">File Structure</h2>
            <FileList files={fileSystem.files} onFileSelect={getFileContent} />
          </div>
          <div>
            <h2 className="text-2xl font-semibold mb-4">File Graph</h2>
            {/* <FileGraph files={fileSystem.files} relationships={fileSystem.relationships} /> */}
            <FileGraph/>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default Home